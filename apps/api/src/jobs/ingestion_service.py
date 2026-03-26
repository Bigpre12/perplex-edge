import logging
import asyncio
import random
import re
import traceback
from datetime import datetime, timezone
from services.odds.fetchers import fetch_props_for_sport, fetch_lines_for_sport, SPORT_KEY_MAP
from services.brain_odds_scout import brain_odds_scout
from services.props_models import PropRecord
from services.props_persistence import (
    prop_group_to_records,
    records_to_rows,
    upsert_props_live,
    insert_props_history,
)

logger = logging.getLogger(__name__)

async def write_props_to_db(sport_id: int, props_data: list):
    """Persist props to DB and pass grouped data to BrainOddsScout."""
    sport_key = SPORT_KEY_MAP.get(sport_id)
    if not sport_key or not props_data:
        return

    league = "NBA"  # TODO: derive per sport_key

    for event in props_data:
        try:
            logger.debug(f"Ingesting event data for {sport_key}")
            home_team = event.get("home_team", "TBD")
            away_team = event.get("away_team", "TBD")

            # existing grouped format for brain
            grouped_props = transform_odds_api_props([event], event, home_team, away_team)

            # NEW: map grouped_props -> PropRecords -> DB rows
            all_records: list[PropRecord] = []
            for gp in grouped_props:
                all_records.extend(prop_group_to_records(gp, sport_key=sport_key, league=league))

            rows = records_to_rows(all_records)
            if rows:
                await upsert_props_live(rows)
                await insert_props_history(rows)

            # keep existing brain behaviour
            if grouped_props:
                await brain_odds_scout.analyze_and_persist(grouped_props, sport_key)

        except Exception as e:
            logger.error(
                f"Failed to process props for event {event.get('id')} in sport {sport_key}: {e}"
            )
            logger.debug(traceback.format_exc())
            continue

async def write_lines_to_db(sport_id: int, lines_data: list):
    """Persist game lines to DB via OddsScout."""
    sport_key = SPORT_KEY_MAP.get(sport_id)
    if not sport_key or not lines_data:
        return
    
    try:
        await brain_odds_scout.analyze_game_lines(lines_data, sport_key)
        logger.debug(f"Successfully processed lines for {sport_key} ({len(lines_data)} games)")
    except Exception as e:
        logger.error(f"Failed to write lines to DB for {sport_key}: {e}")


async def ingest_all_odds():
    """Combined cycle to ingest both props and lines for all sports safely into the Unified model."""
    from services.unified_ingestion import unified_ingestion
    logger.info("Starting combined odds ingestion cycle (Unified)...")

    for sport_id in list(SPORT_KEY_MAP.keys()):
        try:
            sport_key = SPORT_KEY_MAP[sport_id]
            logger.info(f"Syncing {sport_key} via UnifiedIngestion...")
            await unified_ingestion.run(sport_key)
        except Exception as e:
            logger.error(f"Ingestion failed for sport {sport_id}: {e}")
            continue

    logger.info("Odds ingestion cycle complete.")

def transform_odds_api_props(odds_events, game_info, home_team='TBD', away_team='TBD'):
    """Transform The Odds API prop format to internal Brain format."""
    transformed = []
    
    game_id = game_info.get('id', 'unknown_game')
    commence_time_str = game_info.get('commence_time')
    commence_time = None
    if commence_time_str:
        try:
            # Handle 'Z' suffix for Python versions < 3.11
            commence_time = datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Failed to parse commence_time {commence_time_str}: {e}")

    for event in odds_events:
        # Group outcomes by (player, market) across all books to pass to BrainOddsScout
        grouped_props = {} # key: (player, market)
        
        for book in event.get('bookmakers', []):
            book_key = book.get('key')
            book_name = book.get('title')
            for market in book.get('markets', []):
                stat_type = market.get('key')
                for outcome in market.get('outcomes', []):
                    # For player props, description is the player name, name is Over/Under
                    player_name = outcome.get('description', outcome.get('name'))
                    side = outcome.get('name', 'Over').lower()
                    price = outcome.get('price', -110)
                    line = outcome.get('point')
                    
                    if line is None and 'description' in outcome:
                        match = re.search(r'(\d+\.?\d*)', outcome['description'])
                        if match: line = float(match.group(1))

                    if line is None: continue
                    
                    prop_key = (player_name, stat_type)
                    if prop_key not in grouped_props:
                        grouped_props[prop_key] = {
                            "player": {"name": player_name, "team": home_team},
                            "market": {"stat_type": stat_type},
                            "line_value": line,
                            "game_id": game_id,
                            "start_time": commence_time,
                            "matchup": {"opponent": away_team},
                            "books": {} # book_key -> {over, under, line}
                        }
                    
                    if book_key not in grouped_props[prop_key]["books"]:
                        grouped_props[prop_key]["books"][book_key] = {
                            "title": book_name,
                            "over": -110,
                            "under": -110,
                            "line": line
                        }
                    
                    if "over" in side:
                        grouped_props[prop_key]["books"][book_key]["over"] = price
                    else:
                        grouped_props[prop_key]["books"][book_key]["under"] = price

        # Convert grouped props to list for BrainOddsScout
        for (p_name, s_type), data in grouped_props.items():
            transformed.append(data)

    return transformed

async def run_steam_scout():
    """Rapid scan for line movements (Steam) for imminent games."""
    from services.alert_writer import run_alert_detection
    logger.info("Starting Steam Scout scan for NBA/NFL imminent games...")
    # Trigger the optimized database-backed detection
    for sport_key in ["basketball_nba", "americanfootball_nfl"]:
        try:
            await run_alert_detection(sport_key)
            logger.debug(f"Steam scan complete for {sport_key}")
        except Exception as e:
            logger.error(f"Steam scout failed for {sport_key}: {e}")

async def run_clv_snapshot():
    """Snapshot closing lines for games starting within 2 hours."""
    from db.session import async_session_maker
    from sqlalchemy import text
    from services.persistence_helpers import insert_clv_trades
    
    logger.info("Starting CLV snapshot for games starting within 2h...")
    
    async with async_session_maker() as session:
        try:
            # Query UnifiedOdds for games starting within 2h
            query = text("""
                SELECT sport, league, event_id as game_id, game_time, player_name, market_key, 
                       line, bookmaker as book, price as odds, outcome_key as side
                FROM unified_odds
                WHERE game_time BETWEEN NOW() AND NOW() + INTERVAL '2 hours'
            """)
            result = await session.execute(query)
            rows = result.mappings().all()
            
            if rows:
                clv_records = []
                for r in rows:
                    clv_records.append({
                        **dict(r),
                        "snapshot_type": "closing",
                        "recorded_at": datetime.now(timezone.utc)
                    })
                await insert_clv_trades(clv_records)
                logger.info(f"CLV: Snapshotted {len(clv_records)} lines.")
        except Exception as e:
            logger.error(f"CLV snapshot failed: {e}")
