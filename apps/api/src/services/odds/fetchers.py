import json
import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from services.cache import cache
from .the_odds_client import fetch_odds

logger = logging.getLogger(__name__)

# Enforce 240 seconds to prevent wasted API calls between 4-min ingest intervals
CACHE_TTL = 240

# Rate limiting for concurrent event fetching
MAX_CONCURRENT_REQUESTS = 3 # More conservative
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

SPORT_KEY_MAP = {
    30: "basketball_nba",
    1: "basketball_nba", # Compatibility alias
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
    """Fetch player props for a specific sport using event-by-event fetching."""
    sport_key = SPORT_KEY_MAP.get(sport_id)
    if not sport_key:
        return []

    cache_key = f"odds:props:{sport_id}"
    cached = await cache.get(cache_key)
    if cached:
        logger.debug(f"Cache HIT — props for sport {sport_id}")
        return json.loads(cached)

    logger.info(f"Cache MISS — fetching events for sport {sport_id}")
    
    # Step 1: Get active events
    events = await fetch_odds(f"/sports/{sport_key}/events")
    if not events:
        logger.warning(f"No active events for {sport_key}")
        return []

    # Step 2: Fetch props for each event ID
    # We use a batch of concurrent requests to optimize
    all_props = []
    
    async def fetch_event_props(event_id):
        async with semaphore:
            result = await fetch_odds(
                f"/sports/{sport_key}/events/{event_id}/odds",
                {
                    "regions": "us",
                    "markets": "player_points,player_rebounds,player_assists,player_threes,player_blocks,player_steals",
                    "oddsFormat": "american",
                    "dateFormat": "iso",
                }
            )
            # Add a small delay between requests even with semaphore to be safe
            await asyncio.sleep(0.5)
            return result

    # Limit to first 10 events to avoid hitting rate limits too fast
    tasks = [fetch_event_props(e['id']) for e in events[:10]]
    results = await asyncio.gather(*tasks)

    for item in results:
        if item:
            all_props.append(item)

    if all_props:
        await cache.set(cache_key, json.dumps(all_props), CACHE_TTL)

    return all_props

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
