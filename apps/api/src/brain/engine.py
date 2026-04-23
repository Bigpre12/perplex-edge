"""
Central ingest governor: decides whether this cycle should hit the network (TheOddsAPI / waterfall)
or rely on existing DB state. Logs decisions to brain_decisions when the table exists.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from brain.decisions import props_live_age_minutes, should_skip_fetch_for_fresh_cache
from services.odds_quota_store import fetch_usage_summary, raise_if_quota_blocked

logger = logging.getLogger(__name__)


@dataclass
class IngestPlan:
    sport: str
    skip_network: bool
    reason: str
    quota_pct: float
    cache_age_minutes: Optional[float] = None
    blocked_quota: bool = False

    def to_metrics_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class BrainGovernor:
    async def plan_ingest(self, session: AsyncSession, sport: str) -> IngestPlan:
        blocked, reason = await raise_if_quota_blocked(session)
        usage = await fetch_usage_summary(session)
        quota_pct = float(usage.get("percent_used") or 0) / 100.0

        if blocked:
            return IngestPlan(
                sport=sport,
                skip_network=True,
                reason=reason or "odds_api_quota_blocked",
                quota_pct=quota_pct,
                cache_age_minutes=await props_live_age_minutes(session, sport),
                blocked_quota=True,
            )

        age = await props_live_age_minutes(session, sport)
        skip, skip_reason = should_skip_fetch_for_fresh_cache(age, quota_pct)
        if skip:
            return IngestPlan(
                sport=sport,
                skip_network=True,
                reason=skip_reason,
                quota_pct=quota_pct,
                cache_age_minutes=age,
                blocked_quota=False,
            )

        return IngestPlan(
            sport=sport,
            skip_network=False,
            reason="full_network_ingest",
            quota_pct=quota_pct,
            cache_age_minutes=age,
            blocked_quota=False,
        )

    async def log_decision(self, session: AsyncSession, plan: IngestPlan) -> None:
        try:
            await session.execute(
                text(
                    """
                    INSERT INTO brain_decisions (
                        sport, should_fetch, should_compute_clv, should_run_monte_carlo,
                        reason, data_age_minutes, quota_pct_used
                    ) VALUES (
                        :sport, :should_fetch, :should_compute_clv, :should_run_monte_carlo,
                        :reason, :data_age, :quota_pct
                    )
                    """
                ),
                {
                    "sport": plan.sport,
                    "should_fetch": not plan.skip_network,
                    "should_compute_clv": True,
                    "should_run_monte_carlo": False,
                    "reason": plan.reason,
                    "data_age": plan.cache_age_minutes,
                    "quota_pct": plan.quota_pct,
                },
            )
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.debug("brain_decisions log skipped: %s", e)

    async def persist_odds_cache_snapshot(
        self,
        session: AsyncSession,
        sport: str,
        odds_raw: list,
        source_name: str,
    ) -> None:
        """Lightweight row for debugging / future full cache — not a full API payload."""
        try:
            payload = {
                "source": source_name,
                "event_count": len(odds_raw),
                "event_ids": [
                    e.get("id")
                    for e in odds_raw
                    if isinstance(e, dict) and e.get("id")
                ][:400],
            }
            await session.execute(
                text(
                    """
                    INSERT INTO odds_cache (sport, market, data, fetched_at, expires_at)
                    VALUES (
                        :sport, 'all', CAST(:data AS jsonb), NOW(),
                        NOW() + INTERVAL '15 minutes'
                    )
                    """
                ),
                {"sport": sport, "data": json.dumps(payload)},
            )
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.debug("odds_cache snapshot skipped: %s", e)


brain_governor = BrainGovernor()
