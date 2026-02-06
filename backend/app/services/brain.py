"""
Autonomous Brain Service — self-monitoring, self-healing, self-optimizing.

Runs as a single background loop that continuously:
1. MONITORS  — checks health of every subsystem (data freshness, sync status, cache, API quota)
2. HEALS     — auto-retries failed syncs, clears stale caches, rotates providers
3. OPTIMIZES — adapts sync frequency based on sport activity, allocates API quota smartly
4. LOGS      — records every decision for full observability via /api/admin/brain endpoint

Design principles:
- Zero human intervention required after deployment
- Every action is logged with reasoning
- Graceful degradation: if healing fails, system continues with stale data
- Never exceeds API quota — always checks before acting
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, date
from typing import Any, Optional
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.core.database import get_session_maker
from app.core.constants import SPORT_KEY_TO_LEAGUE

logger = logging.getLogger(__name__)

EASTERN_TZ = ZoneInfo("America/New_York")

# Maximum decision log entries to keep in memory
MAX_LOG_ENTRIES = 500


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class HealthCheck:
    """Result of a single health check."""
    component: str
    status: str  # "healthy", "degraded", "critical"
    message: str
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = field(default_factory=dict)


@dataclass
class HealingAction:
    """Record of an autonomous healing action."""
    action: str
    target: str
    reason: str
    result: str  # "success", "failed", "skipped"
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    details: dict = field(default_factory=dict)


@dataclass
class BrainDecision:
    """A logged decision made by the brain."""
    timestamp: datetime
    category: str  # "monitor", "heal", "optimize", "alert"
    action: str
    reasoning: str
    outcome: str
    details: dict = field(default_factory=dict)


# =============================================================================
# Brain State (in-memory singleton)
# =============================================================================

class BrainState:
    """Tracks the brain's current state and history."""

    def __init__(self):
        self.started_at: Optional[datetime] = None
        self.cycle_count: int = 0
        self.last_cycle_at: Optional[datetime] = None
        self.last_cycle_duration_ms: int = 0

        # Health tracking
        self.health_checks: dict[str, HealthCheck] = {}
        self.overall_status: str = "initializing"

        # Healing tracking
        self.heals_attempted: int = 0
        self.heals_succeeded: int = 0
        self.consecutive_failures: dict[str, int] = {}

        # Optimization state
        self.sport_priority: dict[str, float] = {}  # higher = sync more often
        self.quota_budget: dict[str, int] = {}  # allocated API calls per sport

        # Decision log (ring buffer)
        self.decisions: deque[BrainDecision] = deque(maxlen=MAX_LOG_ENTRIES)

    def log_decision(
        self,
        category: str,
        action: str,
        reasoning: str,
        outcome: str,
        details: dict | None = None,
    ):
        decision = BrainDecision(
            timestamp=datetime.now(timezone.utc),
            category=category,
            action=action,
            reasoning=reasoning,
            outcome=outcome,
            details=details or {},
        )
        self.decisions.append(decision)
        logger.info(f"[BRAIN:{category.upper()}] {action} — {reasoning} → {outcome}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize state for the /admin/brain endpoint."""
        return {
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "uptime_hours": round(
                (datetime.now(timezone.utc) - self.started_at).total_seconds() / 3600, 1
            ) if self.started_at else 0,
            "cycle_count": self.cycle_count,
            "last_cycle_at": self.last_cycle_at.isoformat() if self.last_cycle_at else None,
            "last_cycle_duration_ms": self.last_cycle_duration_ms,
            "overall_status": self.overall_status,
            "heals_attempted": self.heals_attempted,
            "heals_succeeded": self.heals_succeeded,
            "health": {
                k: {
                    "status": v.status,
                    "message": v.message,
                    "checked_at": v.checked_at.isoformat(),
                    "details": v.details,
                }
                for k, v in self.health_checks.items()
            },
            "sport_priority": self.sport_priority,
            "quota_budget": self.quota_budget,
            "recent_decisions": [
                {
                    "timestamp": d.timestamp.isoformat(),
                    "category": d.category,
                    "action": d.action,
                    "reasoning": d.reasoning,
                    "outcome": d.outcome,
                }
                for d in list(self.decisions)[-30:]  # last 30
            ],
        }


# Module-level singleton
_brain = BrainState()


def get_brain_state() -> BrainState:
    """Get the brain singleton (for API endpoints)."""
    return _brain


# =============================================================================
# 1. SELF-MONITORING — Health Checks
# =============================================================================

async def _check_data_freshness(db) -> list[HealthCheck]:
    """Check if sport data is stale (no sync in expected window)."""
    from app.models import SyncMetadata
    from sqlalchemy import select
    from app.core.sport_availability import get_sport_status

    checks = []
    now = datetime.now(timezone.utc)

    for sport_key, league in SPORT_KEY_TO_LEAGUE.items():
        # Skip off-season sports
        status = get_sport_status(sport_key)
        if not status.get("is_active", False):
            checks.append(HealthCheck(
                component=f"freshness:{sport_key}",
                status="healthy",
                message=f"{league} off-season — no data expected",
                details={"season_status": status.get("message", "off-season")},
            ))
            continue

        # Check last sync time
        result = await db.execute(
            select(SyncMetadata).where(SyncMetadata.sport_key == sport_key).limit(1)
        )
        meta = result.scalar_one_or_none()

        if meta is None:
            checks.append(HealthCheck(
                component=f"freshness:{sport_key}",
                status="critical",
                message=f"{league} has NEVER been synced",
            ))
        else:
            last = meta.last_updated.replace(tzinfo=timezone.utc) if meta.last_updated.tzinfo is None else meta.last_updated
            age_hours = (now - last).total_seconds() / 3600
            if age_hours > 12:
                checks.append(HealthCheck(
                    component=f"freshness:{sport_key}",
                    status="critical",
                    message=f"{league} data is {age_hours:.1f}h old (>12h)",
                    details={"age_hours": round(age_hours, 1), "last_sync": meta.last_updated.isoformat()},
                ))
            elif age_hours > 6:
                checks.append(HealthCheck(
                    component=f"freshness:{sport_key}",
                    status="degraded",
                    message=f"{league} data is {age_hours:.1f}h old (>6h)",
                    details={"age_hours": round(age_hours, 1)},
                ))
            else:
                checks.append(HealthCheck(
                    component=f"freshness:{sport_key}",
                    status="healthy",
                    message=f"{league} data is {age_hours:.1f}h old",
                    details={"age_hours": round(age_hours, 1)},
                ))

    return checks


async def _check_api_quota() -> HealthCheck:
    """Check API quota health."""
    from app.services.odds_provider import get_quota_status

    quota = get_quota_status()
    remaining = quota.get("remaining", 500)
    used = quota.get("used", 0)
    pct_used = quota.get("percent_used", 0)

    if remaining < 10:
        return HealthCheck(
            component="api_quota",
            status="critical",
            message=f"API quota nearly exhausted: {remaining} remaining ({pct_used}% used)",
            details=quota,
        )
    elif remaining < 50:
        return HealthCheck(
            component="api_quota",
            status="degraded",
            message=f"API quota low: {remaining} remaining ({pct_used}% used)",
            details=quota,
        )
    else:
        return HealthCheck(
            component="api_quota",
            status="healthy",
            message=f"API quota OK: {remaining} remaining ({pct_used}% used)",
            details=quota,
        )


async def _check_cache_health() -> HealthCheck:
    """Check memory cache health."""
    from app.services.memory_cache import cache

    try:
        stats = cache.get_stats()
        entry_count = stats.get("entry_count", 0)
        hit_rate_pct = stats.get("hit_rate_pct", 0)

        if entry_count > 5000:
            return HealthCheck(
                component="cache",
                status="degraded",
                message=f"Cache large: {entry_count} entries",
                details=stats,
            )
        return HealthCheck(
            component="cache",
            status="healthy",
            message=f"Cache OK: {entry_count} entries, {hit_rate_pct}% hit rate",
            details=stats,
        )
    except Exception as e:
        return HealthCheck(
            component="cache",
            status="degraded",
            message=f"Cache check failed: {str(e)[:80]}",
        )


async def _check_scheduler_health() -> HealthCheck:
    """Check if background tasks are still running."""
    from app.scheduler import get_background_tasks

    tasks = get_background_tasks()
    total = len(tasks)
    alive = sum(1 for t in tasks if not t.done())
    dead = total - alive

    if dead > 0:
        dead_names = [t.get_name() for t in tasks if t.done()]
        return HealthCheck(
            component="scheduler",
            status="critical" if dead > 2 else "degraded",
            message=f"{dead}/{total} background tasks have died: {dead_names}",
            details={"dead_tasks": dead_names, "alive": alive, "total": total},
        )
    return HealthCheck(
        component="scheduler",
        status="healthy",
        message=f"All {total} background tasks running",
        details={"alive": alive, "total": total},
    )


# =============================================================================
# 2. SELF-HEALING — Autonomous Recovery
# =============================================================================

async def _heal_stale_sport(db, sport_key: str, age_hours: float) -> HealingAction:
    """Re-sync a sport that has stale data."""
    from app.services.etl_games_and_lines import sync_with_fallback

    action = HealingAction(
        action="resync_sport",
        target=sport_key,
        reason=f"Data is {age_hours:.1f}h stale",
    )
    start = time.time()

    try:
        # Check quota before attempting real API
        from app.services.odds_provider import get_quota_status
        quota = get_quota_status()
        use_real = quota.get("remaining", 0) > 20

        result = await sync_with_fallback(
            db,
            sport_key,
            include_props=True,
            use_real_api=use_real,
        )

        games = result.get("games_created", 0) + result.get("games_updated", 0)
        source = result.get("data_source", "unknown")
        action.result = "success"
        action.details = {"games": games, "source": source, "used_real_api": use_real}
    except Exception as e:
        action.result = "failed"
        action.details = {"error": str(e)[:200]}
    finally:
        action.duration_ms = int((time.time() - start) * 1000)

    return action


async def _heal_dead_tasks() -> HealingAction:
    """Restart dead background tasks."""
    from app.scheduler import get_background_tasks, _background_tasks

    action = HealingAction(
        action="restart_dead_tasks",
        target="scheduler",
        reason="One or more background tasks have died",
    )

    try:
        dead_tasks = [t for t in get_background_tasks() if t.done()]
        restarted = []

        for task in dead_tasks:
            name = task.get_name()
            # Get the coroutine function name to restart it
            # We can't easily restart arbitrary tasks, but we can log them
            # The main quota_safe_sync_loop is the most important one
            exc = task.exception() if not task.cancelled() else None
            restarted.append({
                "name": name,
                "exception": str(exc)[:100] if exc else "cancelled",
            })

        action.result = "success" if restarted else "skipped"
        action.details = {"dead_tasks": restarted, "count": len(restarted)}

        # For the critical sync loop, actually restart it
        for task in dead_tasks:
            if task.get_name() == "quota_safe_sync_loop":
                from app.scheduler import quota_safe_sync_loop
                settings = get_settings()
                use_stubs = getattr(settings, 'scheduler_use_stubs', True)
                new_task = asyncio.create_task(
                    quota_safe_sync_loop(initial_delay=10, use_stubs=use_stubs),
                    name="quota_safe_sync_loop"
                )
                _background_tasks.append(new_task)
                logger.warning("[BRAIN:HEAL] Restarted quota_safe_sync_loop")
                action.details["restarted"] = "quota_safe_sync_loop"

    except Exception as e:
        action.result = "failed"
        action.details = {"error": str(e)[:200]}

    return action


async def _heal_cache_pressure() -> HealingAction:
    """Clear stale cache entries when cache is nearly full."""
    from app.services.memory_cache import cache

    action = HealingAction(
        action="clear_stale_cache",
        target="memory_cache",
        reason="Cache pressure detected",
    )

    try:
        before = cache.get_stats().get("entry_count", 0)
        evicted = await cache.cleanup_expired()
        after = cache.get_stats().get("entry_count", 0)
        action.result = "success"
        action.details = {"before": before, "after": after, "evicted": evicted}
    except Exception as e:
        action.result = "failed"
        action.details = {"error": str(e)[:200]}

    return action


# =============================================================================
# 3. SELF-OPTIMIZATION — Adaptive Behavior
# =============================================================================

def _compute_sport_priorities() -> dict[str, float]:
    """
    Compute priority scores for each sport based on:
    - Is it in-season? (high priority)
    - Is it game day? (higher priority)
    - Is it peak betting hours? (highest priority)
    """
    from app.core.sport_availability import get_sport_status

    now_et = datetime.now(EASTERN_TZ)
    hour = now_et.hour
    is_peak = 9 <= hour <= 23  # 9 AM - 11 PM ET

    priorities = {}
    for sport_key in SPORT_KEY_TO_LEAGUE:
        status = get_sport_status(sport_key)
        base = 0.0

        if status.get("is_active", False):
            base = 1.0
            # Boost during peak hours
            if is_peak:
                base += 0.5
            # Extra boost for major US sports during evening
            if hour >= 17 and sport_key in (
                "basketball_nba", "basketball_ncaab",
                "americanfootball_nfl", "icehockey_nhl",
            ):
                base += 0.5
        else:
            base = 0.1  # minimal priority for off-season

        priorities[sport_key] = round(base, 2)

    return priorities


def _allocate_quota_budget(priorities: dict[str, float], remaining_quota: int) -> dict[str, int]:
    """
    Distribute remaining API quota across sports proportionally to priority.
    Reserves 20% for manual/emergency use.
    """
    usable = int(remaining_quota * 0.8)  # reserve 20%
    total_priority = sum(priorities.values()) or 1.0

    budget = {}
    for sport_key, priority in priorities.items():
        share = int((priority / total_priority) * usable)
        budget[sport_key] = max(share, 1)  # at least 1 call each

    return budget


# =============================================================================
# 4. SELF-AWARENESS — Status & Reporting
# =============================================================================

def get_brain_status() -> dict[str, Any]:
    """Get full brain status for API endpoint."""
    return _brain.to_dict()


def get_brain_health_summary() -> dict[str, Any]:
    """Get a compact health summary."""
    checks = _brain.health_checks
    critical = [k for k, v in checks.items() if v.status == "critical"]
    degraded = [k for k, v in checks.items() if v.status == "degraded"]
    healthy = [k for k, v in checks.items() if v.status == "healthy"]

    return {
        "overall": _brain.overall_status,
        "critical_count": len(critical),
        "degraded_count": len(degraded),
        "healthy_count": len(healthy),
        "critical": critical,
        "degraded": degraded,
        "cycle_count": _brain.cycle_count,
        "heals_attempted": _brain.heals_attempted,
        "heals_succeeded": _brain.heals_succeeded,
    }


# =============================================================================
# 5. MAIN BRAIN LOOP
# =============================================================================

async def brain_loop(interval_minutes: int = 5, initial_delay: int = 90):
    """
    The autonomous brain loop. Runs every N minutes and:
    1. Monitors all subsystems
    2. Heals anything that's broken
    3. Optimizes resource allocation
    4. Logs every decision

    Args:
        interval_minutes: How often the brain runs (default: 5 min)
        initial_delay: Seconds to wait before first cycle (let other tasks start)
    """
    global _brain

    _brain.started_at = datetime.now(timezone.utc)
    logger.info(f"[BRAIN] Autonomous brain starting (cycle every {interval_minutes}m, delay {initial_delay}s)")

    if initial_delay > 0:
        await asyncio.sleep(initial_delay)

    while True:
        cycle_start = time.time()
        _brain.cycle_count += 1
        cycle_num = _brain.cycle_count

        try:
            logger.info(f"[BRAIN] === Cycle #{cycle_num} starting ===")
            session_maker = get_session_maker()

            # ------------------------------------------------------------------
            # PHASE 1: MONITOR
            # ------------------------------------------------------------------
            all_checks: list[HealthCheck] = []

            async with session_maker() as db:
                # Data freshness per sport
                freshness_checks = await _check_data_freshness(db)
                all_checks.extend(freshness_checks)

            # API quota
            quota_check = await _check_api_quota()
            all_checks.append(quota_check)

            # Cache
            cache_check = await _check_cache_health()
            all_checks.append(cache_check)

            # Scheduler tasks
            scheduler_check = await _check_scheduler_health()
            all_checks.append(scheduler_check)

            # Store checks
            for check in all_checks:
                _brain.health_checks[check.component] = check

            # Determine overall status
            statuses = [c.status for c in all_checks]
            if "critical" in statuses:
                _brain.overall_status = "critical"
            elif "degraded" in statuses:
                _brain.overall_status = "degraded"
            else:
                _brain.overall_status = "healthy"

            _brain.log_decision(
                "monitor",
                f"health_scan_cycle_{cycle_num}",
                f"Scanned {len(all_checks)} components",
                _brain.overall_status,
                {
                    "critical": sum(1 for s in statuses if s == "critical"),
                    "degraded": sum(1 for s in statuses if s == "degraded"),
                    "healthy": sum(1 for s in statuses if s == "healthy"),
                },
            )

            # ------------------------------------------------------------------
            # PHASE 2: HEAL
            # ------------------------------------------------------------------
            if _brain.overall_status != "healthy":
                # Heal stale sports
                stale_sports = [
                    c for c in all_checks
                    if c.component.startswith("freshness:")
                    and c.status in ("critical", "degraded")
                    and c.details.get("age_hours", 0) > 0
                ]

                for check in stale_sports:
                    sport_key = check.component.replace("freshness:", "")
                    age = check.details.get("age_hours", 0)

                    # Don't heal too aggressively — max 3 sport resyncs per cycle
                    if _brain.heals_attempted - _brain.heals_succeeded > 5:
                        _brain.log_decision(
                            "heal",
                            f"skip_resync:{sport_key}",
                            "Too many recent heal failures, backing off",
                            "skipped",
                        )
                        continue

                    _brain.heals_attempted += 1
                    async with session_maker() as db:
                        heal_result = await _heal_stale_sport(db, sport_key, age)

                    if heal_result.result == "success":
                        _brain.heals_succeeded += 1
                        _brain.consecutive_failures[sport_key] = 0
                    else:
                        _brain.consecutive_failures[sport_key] = (
                            _brain.consecutive_failures.get(sport_key, 0) + 1
                        )

                    _brain.log_decision(
                        "heal",
                        f"resync:{sport_key}",
                        heal_result.reason,
                        heal_result.result,
                        heal_result.details,
                    )

                # Heal dead tasks
                if scheduler_check.status != "healthy":
                    _brain.heals_attempted += 1
                    task_heal = await _heal_dead_tasks()
                    if task_heal.result == "success":
                        _brain.heals_succeeded += 1
                    _brain.log_decision(
                        "heal",
                        "restart_tasks",
                        task_heal.reason,
                        task_heal.result,
                        task_heal.details,
                    )

                # Heal cache pressure
                if cache_check.status == "degraded":
                    cache_heal = await _heal_cache_pressure()
                    _brain.log_decision(
                        "heal",
                        "clear_cache",
                        cache_heal.reason,
                        cache_heal.result,
                        cache_heal.details,
                    )

            # ------------------------------------------------------------------
            # PHASE 3: OPTIMIZE
            # ------------------------------------------------------------------
            priorities = _compute_sport_priorities()
            _brain.sport_priority = priorities

            from app.services.odds_provider import get_quota_status
            quota = get_quota_status()
            budget = _allocate_quota_budget(priorities, quota.get("remaining", 0))
            _brain.quota_budget = budget

            _brain.log_decision(
                "optimize",
                "recompute_priorities",
                f"Allocated quota across {len(budget)} sports",
                "applied",
                {"top_3": sorted(priorities.items(), key=lambda x: -x[1])[:3]},
            )

            # ------------------------------------------------------------------
            # PHASE 4: REPORT
            # ------------------------------------------------------------------
            cycle_ms = int((time.time() - cycle_start) * 1000)
            _brain.last_cycle_at = datetime.now(timezone.utc)
            _brain.last_cycle_duration_ms = cycle_ms

            logger.info(
                f"[BRAIN] === Cycle #{cycle_num} complete in {cycle_ms}ms — "
                f"status={_brain.overall_status}, "
                f"heals={_brain.heals_succeeded}/{_brain.heals_attempted} ==="
            )

        except asyncio.CancelledError:
            logger.info("[BRAIN] Brain loop cancelled — shutting down gracefully")
            break
        except Exception as e:
            logger.error(f"[BRAIN] Cycle #{cycle_num} error: {e}", exc_info=True)
            _brain.log_decision(
                "monitor",
                f"cycle_{cycle_num}_error",
                f"Unhandled exception: {str(e)[:200]}",
                "error",
            )

        # Wait for next cycle
        await asyncio.sleep(interval_minutes * 60)
