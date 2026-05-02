# C:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\src\services\scheduler_jobs.py
import logging
import httpx
import os
from datetime import datetime, timezone, timedelta
from services.odds_api_client import odds_api
from core.config import settings
from core.sports_config import SPORT_MAP

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

async def snapshot_lines(sport: str):
    """Pull current Odds API lines and store in clv_snapshots"""
    if not settings.ODDS_API_ENABLED:
        logger.debug("snapshot_lines: Odds API disabled by config. Skipping.")
        return
    from db.session import async_session_maker
    from models import LineTick
    try:
        api_sport = SPORT_MAP.get(sport, sport)
        events = await odds_api.get_live_odds(api_sport, markets="h2h,spreads,totals")
        
        if not events:
            return

        async with async_session_maker() as session:
            for event in events:
                for book in event.get("bookmakers", []):
                    for market in book.get("markets", []):
                        for outcome in market.get("outcomes", []):
                            # Store current line state as a snapshot/tick
                            tick = LineTick(
                                sport=sport,
                                event_id=event["id"],
                                market_key=market["key"],
                                outcome_key=outcome["name"],
                                bookmaker=book["key"],
                                line=float(outcome.get("point", 0)),
                                price=int(outcome["price"]),
                                last_update=datetime.now(timezone.utc)
                            )
                            session.add(tick)
            await session.commit()
        
        logger.info(f"Snapshotted {len(events)} events for {sport}")
    except Exception as e:
        logger.error(f"Error in snapshot_lines for {sport}: {e}")

async def detect_whales():
    """Compare latest snapshot vs 30min ago, write to whale_moves"""
    # Placeholder for whale detection logic (heavy consensus movement)
    logger.info("Executed detect_whales job - scanning for institutional volume")
    return []

async def detect_steam():
    """Compare latest snapshot vs 15min ago, write to steam_snapshots if moved >= 0.5"""
    # Placeholder for steam detection logic (rapid market-wide movement)
    logger.info("Executed detect_steam job - scanning for market velocity")
    return []
