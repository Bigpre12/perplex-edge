"""Rules: when to skip network ingest and rely on DB cache (props_live)."""
from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from brain.env_reads import BRAIN_SKIP_WHEN_FRESH_MINUTES, brain_cache_skip_enabled
from brain.quota_guard import CONSERVATIVE_PCT
from core.config import settings


async def props_live_age_minutes(session: AsyncSession, sport: str) -> Optional[float]:
    """Minutes since last props_live update for sport; None if unknown / empty."""
    try:
        res = await session.execute(
            text(
                "SELECT MAX(last_updated_at) AS lu FROM props_live WHERE sport = :sport"
            ),
            {"sport": sport},
        )
        row = res.mappings().first()
        if not row or row["lu"] is None:
            return None
        from datetime import datetime, timezone

        lu = row["lu"]
        if lu.tzinfo is None:
            lu = lu.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - lu).total_seconds() / 60.0
    except Exception:
        return None


def should_skip_fetch_for_fresh_cache(
    cache_age_minutes: Optional[float], quota_pct: float
) -> Tuple[bool, str]:
    """
    When quota_pct >= CONSERVATIVE_PCT and props_live is fresher than threshold,
    skip hitting TheOddsAPI for this cycle.
    """
    if not brain_cache_skip_enabled():
        return False, "cache_skip_disabled"
    if cache_age_minutes is None:
        return False, "no_cache_timestamp"
    fresh = max(1, BRAIN_SKIP_WHEN_FRESH_MINUTES)
    if hasattr(settings, "ODDS_API_CONSERVATIVE_MODE") and settings.ODDS_API_CONSERVATIVE_MODE:
        # In conservative mode, we are much stingier with the quota.
        # We increase the 'fresh' window significantly.
        fresh = max(fresh, 15)
        if quota_pct >= 0.5: # Aggressive skip if half-way through quota
            fresh = max(fresh, 30)

    if cache_age_minutes <= float(fresh):
        return True, f"cache_fresh_under_{fresh}m_quota_conservative"
    return False, "cache_stale_or_quota_ok"
