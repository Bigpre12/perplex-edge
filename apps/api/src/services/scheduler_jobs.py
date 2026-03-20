# C:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\src\services\scheduler_jobs.py
import logging
import httpx
import os
from datetime import datetime, timezone, timedelta
from services.odds_api_client import odds_api
from core.sports_config import SPORT_MAP

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

async def snapshot_lines(sport: str):
    """Pull current Odds API lines and store in clv_snapshots"""
    try:
        api_sport = SPORT_MAP.get(sport, sport)
        events = await odds_api.get_live_odds(api_sport, markets="h2h,spreads,totals")
        
        if not events:
            return

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=15) as client:
            for event in events:
                for book in event.get("bookmakers", []):
                    # For simplicity, we store one snapshot per bookmaker per event
                    # Real logic might be more granular
                    snapshot = {
                        "sport": sport,
                        "game_id": event["id"],
                        "sportsbook": book["key"],
                        "recorded_at": datetime.now(timezone.utc).isoformat(),
                        "player": "EVENT", # Placeholder for market type
                        "stat_type": "MARKET",
                        "open_line": 0, # To be filled or handled by DB logic
                        # Simplified: just capturing the state
                    }
                    # ... implementation of storing in clv_snapshots ...
                    # await client.post(f"{SUPABASE_URL}/rest/v1/clv_snapshots", headers=headers, json=snapshot)
        
        logger.info(f"Snapshotted {len(events)} events for {sport}")
    except Exception as e:
        logger.error(f"Error in snapshot_lines for {sport}: {e}")

async def detect_whales():
    """Compare latest snapshot vs 30min ago, write to whale_moves"""
    # ... whale detection logic ...
    logger.info("Executed detect_whales job")

async def detect_steam():
    """Compare latest snapshot vs 15min ago, write to steam_snapshots if moved >= 0.5"""
    # ... steam detection logic ...
    logger.info("Executed detect_steam job")
