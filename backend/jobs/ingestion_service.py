import logging
import asyncio
from datetime import datetime, timezone
from services.odds.fetchers import fetch_props_for_sport, fetch_lines_for_sport, SPORT_KEY_MAP
from services.brain_odds_scout import brain_odds_scout

logger = logging.getLogger(__name__)

async def write_props_to_db(sport_id: int, props_data: list):
    """Placeholder or adapter for persisting props."""
    sport_key = SPORT_KEY_MAP.get(sport_id)
    if not sport_key or not props_data:
        return
        
    # Previously, this iterated over bookmakers and used brain_odds_scout
    # We will replicate the transform and persist logic here safely
    # If the response shape is a list of events with bookmakers inside:
    for event in props_data:
        try:
            transformed_props = transform_odds_api_props([event], event)
            if transformed_props:
                await brain_odds_scout.analyze_and_persist(transformed_props, sport_key)
        except Exception as e:
            logger.error(f"Failed to process props for event {event.get('id')} in sport {sport_key}: {e}")
            continue

async def write_lines_to_db(sport_id: int, lines_data: list):
    """Placeholder or adapter for persisting game lines."""
    sport_key = SPORT_KEY_MAP.get(sport_id)
    if not sport_key or not lines_data:
        return
    # Here you'd update your live_odds table. 
    # For now, we log the success since the focus is on props for the Battle Plan.
    logger.debug(f"Successfully processed lines for {sport_key} ({len(lines_data)} games)")


async def ingest_all_odds():
    """Combined cycle to ingest both props and lines for all sports safely."""
    logger.info("Starting combined odds ingestion cycle...")

    for sport_id in SPORT_KEY_MAP.keys():
        try:
            sport_key = SPORT_KEY_MAP[sport_id]
            logger.info(f"Fetching endpoints for {sport_key}...")
            
            # Fetch and write Props
            props = await fetch_props_for_sport(sport_id)
            if props:
                await write_props_to_db(sport_id, props)

            # Fetch and write Lines
            lines = await fetch_lines_for_sport(sport_id)
            if lines:
                await write_lines_to_db(sport_id, lines)

        except Exception as e:
            # Critical: one sport failing must NOT stop others
            logger.error(f"Ingestion failed for sport {sport_id}: {e}")
            continue

    logger.info("Odds ingestion cycle complete.")

# Alias for compatibility with scheduler
async def ingest_all_props():
    pass # Managed by the combined ingest_all_odds cycle now

def transform_odds_api_props(odds_events, game_info):
    """Transform The Odds API prop format to internal Brain format."""
    transformed = []
    
    for event in odds_events:
        for book in event.get('bookmakers', []):
            for market in book.get('markets', []):
                stat_type = market.get('key')
                for outcome in market.get('outcomes', []):
                    if 'point' not in outcome:
                        continue
                        
                    transformed.append({
                        "id": f"{game_info['id']}_{outcome['name']}_{stat_type}",
                        "player": {
                            "name": outcome['name'],
                            "team": game_info.get('home_team') if outcome.get('description') == 'Over' else game_info.get('away_team')
                        },
                        "market": {"stat_type": stat_type},
                        "line_value": outcome['point'],
                        "odds": outcome['price'],
                        "game_id": game_info['id'],
                        "start_time": game_info.get('commence_time'),
                        "matchup": {
                            "opponent": game_info.get('away_team') if game_info.get('home_team') == transformed[-1]['player']['team'] else game_info.get('home_team') if transformed else "TBD"
                        }
                    })
    return transformed

async def run_steam_scout():
    """Rapid scan for line movements (Steam)."""
    # Simply re-running ingest frequently handles this
    await ingest_all_odds()

async def run_clv_snapshot():
    """Snapshot closing lines for games starting soon."""
    logger.info("Starting CLV snapshot...")
    pass
