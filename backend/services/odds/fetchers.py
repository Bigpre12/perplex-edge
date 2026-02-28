import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from services.cache import cache
from .the_odds_client import fetch_odds

logger = logging.getLogger(__name__)

# Enforce 240 seconds to prevent wasted API calls between 4-min ingest intervals
CACHE_TTL = 240

SPORT_KEY_MAP = {
    30: "basketball_nba",
    39: "basketball_ncaab",
    53: "basketball_wnba",
    31: "americanfootball_nfl",
    41: "americanfootball_ncaaf",
    40: "baseball_mlb",
    22: "icehockey_nhl",
    42: "tennis_atp",
    43: "tennis_wta",
    54: "mma_mixed_martial_arts",
    55: "boxing_boxing",
}

async def fetch_props_for_sport(sport_id: int) -> list:
    """Fetch player props for a specific sport with Redis caching."""
    sport_key = SPORT_KEY_MAP.get(sport_id)
    if not sport_key:
        return []

    cache_key = f"odds:props:{sport_id}"
    cached = await cache.get(cache_key)
    if cached:
        logger.debug(f"Cache HIT — props for sport {sport_id}")
        return json.loads(cached)

    logger.info(f"Cache MISS — fetching props for sport {sport_id} from TheOddsAPI")
    data = await fetch_odds(
        f"/sports/{sport_key}/odds",
        {
            "regions": "us",
            "markets": "player_points,player_rebounds,player_assists,player_threes,player_props",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }
    )

    if data:
        await cache.set(cache_key, json.dumps(data), CACHE_TTL)

    return data or []

async def fetch_lines_for_sport(sport_id: int) -> list:
    """Fetch game lines (moneyline/spread/total) for a specific sport with Redis caching."""
    sport_key = SPORT_KEY_MAP.get(sport_id)
    if not sport_key:
        return []

    cache_key = f"odds:lines:{sport_id}"
    cached = await cache.get(cache_key)
    if cached:
        logger.debug(f"Cache HIT — lines for sport {sport_id}")
        return json.loads(cached)

    logger.info(f"Cache MISS — fetching lines for sport {sport_id} from TheOddsAPI")
    data = await fetch_odds(
        f"/sports/{sport_key}/odds",
        {
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }
    )

    if data:
        await cache.set(cache_key, json.dumps(data), CACHE_TTL)

    return data or []
