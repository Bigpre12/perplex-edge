"""
Unified ingestion scheduler: legacy single-interval vs tiered (active / inactive / disabled).

See docs/RAILWAY_PRODUCTION.md for env reference.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

from core.sports_config import ingest_interval_minutes_for_sport

# Canonical sport keys (The Odds API style) — keep in sync with main scheduler expectations.
ALL_SPORTS: Tuple[str, ...] = (
    "americanfootball_nfl",
    "americanfootball_ncaaf",
    "basketball_nba",
    "baseball_mlb",
    "icehockey_nhl",
    "soccer_usa_mls",
    "soccer_uefa_champs_league",
    "soccer_epl",
    "mma_mixed_martial_arts",
    "aussierules_afl",
    "rugbyleague_nrl",
)

# Default “active” tier when INGEST_ACTIVE_SPORTS is unset (higher polling frequency).
DEFAULT_ACTIVE_SPORTS: Tuple[str, ...] = (
    "basketball_nba",
    "icehockey_nhl",
    "soccer_usa_mls",
    "soccer_epl",
    "soccer_uefa_champs_league",
)

_KNOWN = set(ALL_SPORTS)


def _truthy(val: Optional[str]) -> bool:
    if val is None:
        return False
    return val.strip().lower() in ("1", "true", "yes", "on")


def _split_csv(name: str) -> List[str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


@dataclass(frozen=True)
class IngestJobSpec:
    sport_key: str
    minutes: Optional[int] = None
    hours: Optional[int] = None

    def __post_init__(self) -> None:
        if (self.minutes is None) == (self.hours is None):
            raise ValueError("IngestJobSpec requires exactly one of minutes or hours")
        if self.minutes is not None and self.minutes < 1:
            raise ValueError("minutes must be >= 1")
        if self.hours is not None and self.hours < 1:
            raise ValueError("hours must be >= 1")


def build_unified_ingest_schedule() -> Tuple[List[IngestJobSpec], Dict[str, Any]]:
    """
    Returns (job_specs, meta) where meta includes mode and human-readable settings for logging.
    """
    disabled = set(_split_csv("INGEST_DISABLED_SPORTS"))

    if _truthy(os.getenv("INGEST_USE_LEGACY_SCHEDULER")):
        minutes = max(1, int(os.getenv("INGEST_INTERVAL_MINUTES", "5")))
        sports = [s for s in ALL_SPORTS if s not in disabled]
        for s in sports:
            if s not in _KNOWN:
                logger.warning("ingest_scheduler_config: unknown sport in legacy list context: %s", s)
        jobs = [IngestJobSpec(sport_key=s, minutes=minutes) for s in sports]
        meta: Dict[str, Any] = {
            "mode": "legacy",
            "interval_minutes": minutes,
            "disabled": sorted(disabled),
            "sport_count": len(jobs),
        }
        return jobs, meta

    # Tiered mode (default)
    active_explicit = os.getenv("INGEST_ACTIVE_SPORTS", "").strip()
    if active_explicit:
        active = _split_csv("INGEST_ACTIVE_SPORTS")
    else:
        active = [s for s in DEFAULT_ACTIVE_SPORTS if s not in disabled]

    inactive_explicit = os.getenv("INGEST_INACTIVE_SPORTS", "").strip()
    if inactive_explicit:
        inactive = _split_csv("INGEST_INACTIVE_SPORTS")
    else:
        active_set = set(active)
        inactive = [s for s in ALL_SPORTS if s not in active_set and s not in disabled]

    # Remove overlap (prefer active tier)
    inactive = [s for s in inactive if s not in set(active)]

    env_active_floor = os.getenv("INGEST_INTERVAL_ACTIVE_MINUTES", "").strip()
    active_floor = max(1, int(env_active_floor)) if env_active_floor else None
    inactive_h = max(1, int(os.getenv("INGEST_INTERVAL_INACTIVE_HOURS", "6")))

    for bucket, label in ((active, "INGEST_ACTIVE_SPORTS"), (inactive, "INGEST_INACTIVE_SPORTS")):
        for s in bucket:
            if s not in _KNOWN:
                logger.warning(
                    "ingest_scheduler_config: sport %r not in canonical ALL_SPORTS — scheduling anyway (%s)",
                    s,
                    label,
                )

    jobs: List[IngestJobSpec] = []
    for s in active:
        if s in disabled:
            continue
        per_sport = ingest_interval_minutes_for_sport(s)
        minutes = per_sport if active_floor is None else max(per_sport, active_floor)
        jobs.append(IngestJobSpec(sport_key=s, minutes=max(1, minutes)))
    for s in inactive:
        if s in disabled:
            continue
        jobs.append(IngestJobSpec(sport_key=s, hours=inactive_h))

    meta = {
        "mode": "tiered",
        "active_sports": list(active),
        "inactive_sports": list(inactive),
        "disabled": sorted(disabled),
        "active_interval_minutes_floor": active_floor,
        "inactive_interval_hours": inactive_h,
        "sport_count": len(jobs),
    }
    return jobs, meta


def scheduled_sport_keys(job_specs: Sequence[IngestJobSpec]) -> List[str]:
    """Ordered unique sport keys for initial parallel ingest."""
    seen: set[str] = set()
    out: List[str] = []
    for j in job_specs:
        if j.sport_key not in seen:
            seen.add(j.sport_key)
            out.append(j.sport_key)
    return out
