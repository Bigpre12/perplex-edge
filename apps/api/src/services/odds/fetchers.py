import json
import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timezone
from services.cache import cache
from .the_odds_client import fetch_odds

logger = logging.getLogger(__name__)

# Enforce 240 seconds to prevent wasted API calls between 4-min ingest intervals
CACHE_TTL = 240

# Rate limiting for concurrent event fetching
MAX_CONCURRENT_REQUESTS = 8 # Optimized for 20k+ Tier
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

SPORT_MARKETS = {
    "basketball_nba": "player_points,player_rebounds,player_assists,player_threes,player_blocks,player_steals,player_double_double,player_triple_double",
    "basketball_ncaab": "player_points,player_rebounds,player_assists",
    "americanfootball_nfl": "player_pass_yds,player_rush_yds,player_reception_yds,player_pass_tds,player_anytime_td",
    "baseball_mlb": "player_hits,player_strikeouts,player_home_runs",
    "icehockey_nhl": "player_points,player_goals,player_assists",
}

DEFAULT_MARKETS = "h2h,spreads,totals"

SPORT_KEY_MAP = {
    30: "basketball_nba",
    1: "basketball_nba", # Compatibility alias
    34: "basketball_ncaab",
    53: "basketball_wnba",
    31: "americanfootball_nfl",
    35: "americanfootball_ncaaf",
    32: "baseball_mlb",
    33: "icehockey_nhl",
    42: "tennis_atp_french_open",
    43: "tennis_wta_french_open",
    44: "tennis_atp_us_open",
    45: "tennis_wta_us_open",
    46: "tennis_atp_wimbledon",
    47: "tennis_wta_wimbledon",
    48: "tennis_atp_aus_open",
    49: "tennis_wta_aus_open",
    54: "mma_mixed_martial_arts",
    55: "boxing_boxing",
    60: "soccer_usa_mls",
    61: "soccer_epl",
    62: "soccer_uefa_champs_league",
    63: "soccer_spain_la_liga",
    64: "soccer_italy_serie_a",
    65: "soccer_germany_bundesliga",
    66: "soccer_france_ligue_one",
    67: "soccer_uefa_europa_league",
    70: "golf_pga_championship",
    71: "golf_the_masters",
    72: "golf_us_open",
    73: "golf_the_open_championship",
    80: "motorsport_formula_1",
    90: "rugbyleague_nrl",
    91: "rugbyunion_premiership",
    92: "cricket_icc_world_cup",
    93: "aussierules_afl",
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

    # Filter events: Only games starting within the next 8 hours
    now = datetime.utcnow()
    imminent_events = []
    for e in events:
        try:
            start_time = datetime.fromisoformat(e['commence_time'].replace('Z', '+00:00'))
            diff = (start_time - now.replace(tzinfo=timezone.utc)).total_seconds()
            if diff < 129600: # 36 hours
                imminent_events.append(e)
        except Exception as err:
            logger.error(f"Error parsing time for event {e.get('id')}: {err}")
            continue
    
    logger.info(f"DEBUG: Found {len(events)} total events, {len(imminent_events)} imminent.")

    # Step 2: Fetch props for each event ID
    # LIMIT: Only fetch props for the FIRST 5 imminent events per sport to conserve credits
    all_props = []
    markets = SPORT_MARKETS.get(sport_key, "player_points")
    
    async def fetch_event_props(event_id):
        async with semaphore:
            result = await fetch_odds(
                f"/sports/{sport_key}/events/{event_id}/odds",
                {
                    "regions": "us",
                    "markets": markets,
                    "oddsFormat": "american",
                    "dateFormat": "iso",
                }
            )
            await asyncio.sleep(0.5)
            return result

    # 🔓 LOCK REMOVAL: Fetch more events in dev mode
    from core.config import settings
    event_limit = len(imminent_events) if settings.DEVELOPMENT_MODE else 5
    tasks = [fetch_event_props(e['id']) for e in imminent_events[:event_limit]]
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
