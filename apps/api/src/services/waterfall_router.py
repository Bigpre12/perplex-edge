import logging
from typing import Dict, List, Optional, Any
from services.balldontlie_client import balldontlie_client
from services.api_sports_client import api_sports_client
from services.sportmonks_client import sportmonks_client
from services.isports_client import isports_client
from services.statsbomb_client import statsbomb_client
from services.odds_api_client import odds_api
from services.thesportsdb_client import thesportsdb_client
from services.espn_client import espn_client
from services.cache import cache

logger = logging.getLogger(__name__)

class ProviderUnavailableError(Exception):
    """Custom exception for unified error handling in waterfall."""
    pass

class WaterfallRouter:
    """
    Branched Waterfall Orchestrator.
    Routes requests based on sport type and data type.
    """
    
    # TTL Definitions
    TTL_LIVE = 60
    TTL_STATS = 900 # 15 minutes
    TTL_SCHEDULE = 86400 # 24 hours

    US_SPORTS = ["nba", "nfl", "mlb", "nhl", "wnba", "ncaaf", "ncaab", "ncaaw"]
    SOCCER_SPORTS = ["epl", "uefa", "mls", "la_liga", "bundesliga", "serie_a", "ligue_1"]

    async def get_data(self, sport: str, data_type: str = "stats") -> Any:
        """Entry point for all waterfall data requests."""
        sport_lower = sport.lower()
        
        # Determine the waterfall chain based on sport and data type
        if data_type == "odds":
            chain = self._get_odds_chain(sport_lower)
        else:
            chain = self._get_stats_chain(sport_lower)
            
        return await self._execute_waterfall(sport_lower, data_type, chain)

    def _get_odds_chain(self, sport: str) -> List[str]:
        if sport in self.SOCCER_SPORTS or "soccer" in sport:
            return ["the_odds_api", "isports", "sportmonks"]
        return ["the_odds_api", "isports", "api_sports"]

    def _get_stats_chain(self, sport: str) -> List[str]:
        if sport in self.US_SPORTS or "basketball" in sport or "americanfootball" in sport:
            return ["balldontlie", "api_sports", "thesportsdb", "espn"]
        if sport in self.SOCCER_SPORTS or "soccer" in sport:
            return ["api_sports", "sportmonks", "thesportsdb", "espn"]
        if "ufc" in sport or "mma" in sport:
            return ["api_sports", "thesportsdb", "espn"]
        return ["thesportsdb", "espn"]

    async def _execute_waterfall(self, sport: str, data_type: str, chain: List[str]) -> Any:
        """Executes the provider chain with try/except and caching logic."""
        cache_key = f"wf:{data_type}:{sport}"
        
        # 1. Check Redis Cache
        cached = await cache.get_json(cache_key)
        if cached:
            return cached

        # 2. Iterate through providers
        for provider_key in chain:
            try:
                data = await self._call_provider(provider_key, sport, data_type)
                if data:
                    # 3. Label source and cache
                    for item in data:
                        if isinstance(item, dict):
                            item["source_provider"] = provider_key
                            
                    # 4. Apply dynamic TTL
                    ttl = self.TTL_LIVE if data_type == "live" else self.TTL_STATS
                    if data_type == "schedule": ttl = self.TTL_SCHEDULE
                    
                    await cache.set_json(cache_key, data, ttl=ttl)
                    logger.info(f"✅ Waterfall: {provider_key} served {sport} {data_type}")
                    return data
            except Exception as e:
                logger.warning(f"⚠️ Waterfall: {provider_key} failed for {sport}: {e}")
                continue

        logger.error(f"❌ Waterfall: All providers exhausted for {sport} {data_type}")
        return []

    async def _call_provider(self, provider: str, sport: str, data_type: str) -> Any:
        """Bridges generic waterfall request to specific provider client."""
        if provider == "balldontlie":
            return await balldontlie_client.get_games(sport)
        elif provider == "api_sports":
            return await api_sports_client.get_games(sport)
        elif provider == "sportmonks":
            return await sportmonks_client.get_fixtures()
        elif provider == "isports":
            return await isports_client.get_games(sport)
        elif provider == "the_odds_api":
            return await odds_api.get_live_odds(sport)
        elif provider == "thesportsdb":
            return await thesportsdb_client.get_events_by_day(sport)
        elif provider == "espn":
            return await espn_client.get_scoreboard(sport)
        return None

    async def get_historical_soccer(self, match_id: int) -> Any:
        """Special bypass handler for StatsBomb."""
        # StatsBomb is NOT in the live waterfall branch per instructions
        # Always serve from Supabase permanently
        return await statsbomb_client.get_events(match_id)

waterfall_router = WaterfallRouter()
