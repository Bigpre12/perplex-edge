# backend/app/antigravity_edge_config.py
from dataclasses import dataclass, field
from typing import Optional, Literal, List
import logging
import os
from sqlalchemy import text
from database import async_session_maker

logger = logging.getLogger(__name__)

EdgeModelName = Literal["baseline", "sharp_v2"]

@dataclass
class EdgeFeedConfig:
    active_edge_model: EdgeModelName = "baseline"
    min_ev_threshold: float = 2.0          # min EV% to show a pick
    max_ev_threshold: float = 40.0         # sanity cap
    min_confidence: float = 0.55           # min model confidence
    max_edge_percent: float = 30.0         # display cap
    min_line_value: float = 0.5
    max_line_value: float = 999.0
    min_odds: int = -300
    max_odds: int = 300
    kelly_fraction: float = 0.25           # quarter-kelly default
    enabled_sports: List[int] = field(default_factory=lambda: [30, 31, 40, 22, 39, 41, 42, 43, 54, 55])
    max_picks_per_game: int = 5

    max_parlays: int = 10
    sharp_money_threshold: float = 0.65    # trigger for sharp flag


_config_cache: Optional[EdgeFeedConfig] = None


async def _load_config_from_db() -> Optional[EdgeFeedConfig]:
    """Load overrides from edge_config table. Falls back to defaults if missing."""
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT * FROM edge_config ORDER BY updated_at DESC LIMIT 1"))
            row = result.mappings().first()
            
            if not row:
                return None
                
            # Handle enabled_sports which might be a list or a string (Postgres vs SQLite/Raw)
            enabled_sports = row.get("enabled_sports")
            if isinstance(enabled_sports, str):
                try:
                    import json
                    enabled_sports = json.loads(enabled_sports)
                except:
                    enabled_sports = [30, 31, 1, 2, 53]
            elif not isinstance(enabled_sports, list):
                enabled_sports = [30, 31, 1, 2, 53]

            return EdgeFeedConfig(
                active_edge_model=row.get("active_edge_model", "baseline"),
                min_ev_threshold=float(row.get("min_ev_threshold", 2.0)),
                max_ev_threshold=float(row.get("max_ev_threshold", 40.0)),
                min_confidence=float(row.get("min_confidence", 0.55)),
                max_edge_percent=float(row.get("max_edge_percent", 30.0)),
                min_line_value=float(row.get("min_line_value", 0.5)),
                max_line_value=float(row.get("max_line_value", 999.0)),
                min_odds=int(row.get("min_odds", -300)),
                max_odds=int(row.get("max_odds", 300)),
                kelly_fraction=float(row.get("kelly_fraction", 0.25)),
                enabled_sports=enabled_sports,
                max_picks_per_game=int(row.get("max_picks_per_game", 5)),
                max_parlays=int(row.get("max_parlays", 10)),
                sharp_money_threshold=float(row.get("sharp_money_threshold", 0.65)),
            )
    except Exception as e:
        logger.warning(f"Could not load edge config from DB: {e} — using defaults")
        return None


async def get_edge_config() -> EdgeFeedConfig:
    """Returns config from DB if available, otherwise hardcoded defaults."""
    global _config_cache
    db_config = await _load_config_from_db()
    if db_config:
        _config_cache = db_config
    elif _config_cache is None:
        _config_cache = EdgeFeedConfig()
    return _config_cache


def invalidate_config_cache():
    global _config_cache
    _config_cache = None
