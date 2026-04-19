"""
Parse provider commence/start fields to UTC and reject impossible far-future game times.

Prevents bad schedule placeholders or mis-joined metadata from poisoning props_live.game_start_time.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def parse_commence_to_utc(value: Any) -> Optional[datetime]:
    """Coerce commence_time / start_time values to aware UTC, or None if unparseable."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            return None
    return None


def event_commence_utc(event: Dict[str, Any]) -> Optional[datetime]:
    ct = event.get("commence_time") or event.get("commenceTime") or event.get("start_time")
    return parse_commence_to_utc(ct)


def reject_absurd_future(
    dt: Optional[datetime],
    *,
    now: Optional[datetime] = None,
    max_future_days: Optional[int] = None,
) -> Optional[datetime]:
    """
    Return dt if within [now - 1d, now + max_future_days], else None.
    Default max_future_days from INGEST_MAX_FUTURE_GAME_DAYS (21).
    """
    if dt is None:
        return None
    now = now or datetime.now(timezone.utc)
    if max_future_days is None:
        max_future_days = int(os.getenv("INGEST_MAX_FUTURE_GAME_DAYS", "21"))
    if max_future_days < 1:
        max_future_days = 21
    earliest = now - timedelta(days=1)
    latest = now + timedelta(days=max_future_days)
    if earliest <= dt <= latest:
        return dt
    logger.warning(
        "commence_time: rejecting timestamp outside ingest window (%s .. %s): %s",
        earliest.isoformat(),
        latest.isoformat(),
        dt.isoformat(),
    )
    return None
