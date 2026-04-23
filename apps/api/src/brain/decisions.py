"""Rules: when to skip network ingest and rely on DB cache (props_live)."""
from __future__ import annotations

import os
from typing import Optional, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from brain.quota_guard import CONSERVATIVE_PCT

# If props_live for this sport is newer than this, we may skip a fetch when quota is tight.
_DEFAULT_FRESH = int(os.getenv("BRAIN_SKIP_WHEN_FRESH_MINUTES", "7"))


def cache_skip_enabled() -> bool:
    return os.getenv("BRAIN_CACHE_SKIP", "true").strip().lower() in ("1", "true", "yes", "on")


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
    if not cache_skip_enabled():
        return False, "cache_skip_disabled"
    if cache_age_minutes is None:
        return False, "no_cache_timestamp"
    if quota_pct < CONSERVATIVE_PCT:
        return False, "quota_comfortable"
    fresh = max(1, _DEFAULT_FRESH)
    if cache_age_minutes <= float(fresh):
        return True, f"cache_fresh_under_{fresh}m_quota_conservative"
    return False, "cache_stale_or_quota_ok"
