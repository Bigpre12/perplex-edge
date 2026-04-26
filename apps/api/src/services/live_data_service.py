import asyncio
import logging
from typing import List, Set
from datetime import datetime, timezone

from services.odds_api_client import odds_api_client
from core.config import settings
from real_data_connector import real_data_connector
from db.session import AsyncSessionLocal
from services.live_scores_cache import upsert_live_scores_from_games

logger = logging.getLogger(__name__)

class LiveDataService:
    """
    High-frequency background polling service to keep the Redis cache warm
    for 'hot' sports and markets. This ensures the frontend gets 15-30s fresh 
    data via standard REST endpoints without calling external providers on demand.
    """
    
    def __init__(self):
        self.hot_sports = [
            "basketball_nba", 
            "americanfootball_nfl", 
            "baseball_mlb",
            "icehockey_nhl"
        ]
        self._stop_event = asyncio.Event()
        self.polling_interval = int(settings.LIVE_DATA_POLLING_INTERVAL) if hasattr(settings, "LIVE_DATA_POLLING_INTERVAL") else 120
        
    async def poll_odds(self):
        """Polls live odds for all hot sports to warm the cache."""
        if odds_api_client.all_keys_dead():
            logger.debug("Skipping poll_odds — all keys cooling down")
            return
        from services.external_api_gateway import external_api_gateway
        quota = await external_api_gateway.quota_status("theoddsapi")
        mode = str(quota.get("mode") or "normal")
        regions = "us"
        markets = None if mode == "normal" else "h2h"
        for sport in self.hot_sports:
            try:
                logger.info(f"🔥 [Live Polling] Refreshing cache for {sport} odds...")
                # Use use_cache=False to force a fetch from the provider; 
                # OddsApiClient._make_request will handle populating the cache.
                await odds_api_client.get_live_odds(sport, regions=regions, markets=markets)
            except Exception as e:
                logger.error(f"❌ [Live Polling] Failed to refresh odds for {sport}: {e}")

    async def poll_props(self):
        """Polls player props for active games in hot sports."""
        if odds_api_client.all_keys_dead():
            logger.debug("Skipping poll_props — all keys cooling down")
            return
        from services.external_api_gateway import external_api_gateway
        quota = await external_api_gateway.quota_status("theoddsapi")
        mode = str(quota.get("mode") or "normal")
        if mode in {"protection", "emergency_freeze"}:
            logger.info("Skipping poll_props due to quota mode: %s", mode)
            return
        for sport in self.hot_sports:
            try:
                # 1. Get active events first (uses cache)
                events = await odds_api_client.get_events(sport)
                if not events: continue
                
                # 2. Limit to first 5 active events to protect quota while warming hot games
                active_eids = [e['id'] for e in events[:5] if 'id' in e]
                
                logger.info(f"🔥 [Live Polling] Refreshing cache for {len(active_eids)} {sport} event props...")
                
                # Fetch props for these events
                markets = odds_api_client.get_markets_for_sport(sport)
                for eid in active_eids:
                    await odds_api_client.get_player_props(
                        sport=sport, 
                        event_id=eid, 
                        markets=markets,
                        use_cache=False, # Force refresh
                        ttl=60 
                    )
                    # Small sleep to avoid hitting provider rate limits too hard in one burst
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"❌ [Live Polling] Failed to refresh props for {sport}: {e}")

    async def poll_scores(self):
        """Refresh live_scores cache from the same waterfall used by /api/live (ESPN → …)."""
        for sport in self.hot_sports:
            try:
                games = await real_data_connector.fetch_games_by_sport(sport)
                if not games:
                    continue
                async with AsyncSessionLocal() as session:
                    n = await upsert_live_scores_from_games(session, sport, games)
                    if n:
                        logger.info(f"🔥 [Live Polling] Cached {n} score rows for {sport}")
            except Exception as e:
                logger.error(f"❌ [Live Polling] Failed to refresh live_scores for {sport}: {e}")

    async def run_loop(self):
        """Main orchestrator loop."""
        logger.info(f"🚀 [Live Polling] Service started. Interval: {self.polling_interval}s")
        
        # Initial wait to let main ingestion settle
        await asyncio.sleep(10)
        
        while not self._stop_event.is_set():
            try:
                start_time = datetime.now(timezone.utc)
                
                # Run polling (live_scores upsert runs on APScheduler in main.py)
                await self.poll_odds()
                await self.poll_props()
                
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                wait_time = max(0.0, float(self.polling_interval) - elapsed)
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"❌ [Live Polling] Loop error: {e}")
                await asyncio.sleep(60)

    def stop(self):
        self._stop_event.set()

# Singleton instance
live_data_service = LiveDataService()
