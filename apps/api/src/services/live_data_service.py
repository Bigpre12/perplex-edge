import asyncio
import logging
from typing import List, Set
from datetime import datetime, timezone

from services.odds_api_client import odds_api_client
from core.config import settings

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
        self.polling_interval = int(settings.LIVE_DATA_POLLING_INTERVAL) if hasattr(settings, "LIVE_DATA_POLLING_INTERVAL") else 30
        
    async def poll_odds(self):
        """Polls live odds for all hot sports to warm the cache."""
        for sport in self.hot_sports:
            try:
                logger.info(f"🔥 [Live Polling] Warming cache for {sport} odds...")
                # Calling this updates the Redis cache inside OddsApiClient._make_request
                await odds_api_client.get_live_odds(sport, use_cache=True, ttl=self.polling_interval + 10)
            except Exception as e:
                logger.error(f"❌ [Live Polling] Failed to warm odds for {sport}: {e}")

    async def poll_props(self):
        """Polls player props for active games in hot sports."""
        for sport in self.hot_sports:
            try:
                # 1. Get active events first (uses cache)
                events = await odds_api_client.get_events(sport)
                if not events: continue
                
                # 2. Limit to first 5 active events to protect quota while warming hot games
                active_eids = [e['id'] for e in events[:5] if 'id' in e]
                
                logger.info(f"🔥 [Live Polling] Warming cache for {len(active_eids)} {sport} event props...")
                
                # Fetch props for these events
                markets = odds_api_client.get_markets_for_sport(sport)
                for eid in active_eids:
                    await odds_api_client.get_player_props(
                        sport=sport, 
                        event_id=eid, 
                        markets=markets,
                        use_cache=True,
                        ttl=60 # Props can be slightly slower
                    )
                    # Small sleep to avoid hitting provider rate limits too hard in one burst
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"❌ [Live Polling] Failed to warm props for {sport}: {e}")

    async def run_loop(self):
        """Main orchestrator loop."""
        logger.info(f"🚀 [Live Polling] Service started. Interval: {self.polling_interval}s")
        
        # Initial wait to let main ingestion settle
        await asyncio.sleep(10)
        
        while not self._stop_event.is_set():
            try:
                start_time = datetime.now(timezone.utc)
                
                # Run polling
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
