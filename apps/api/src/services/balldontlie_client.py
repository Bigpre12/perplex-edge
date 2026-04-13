import httpx
import logging
from typing import Dict, List, Optional, Any
from core.config import settings
from services.cache import cache

logger = logging.getLogger(__name__)

class ProviderUnavailableError(Exception):
    """Custom exception for unified error handling in waterfall."""
    pass

class BallDontLieClient:
    """
    Official BallDontLie API Client (V1).
    Supports NBA, NFL, MLB, NHL, WNBA, NCAAF, NCAAB, NCAAW.
    """
    BASE_URL = "https://api.balldontlie.io/v1"

    def __init__(self):
        self.api_key = settings.BALLDONTLIE_API_KEY if hasattr(settings, 'BALLDONTLIE_API_KEY') else ""
        self.timeout = 10.0

    async def _fetch(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Standard fetch interface for all providers."""
        if not self.api_key:
            raise ProviderUnavailableError("BALLDONTLIE_API_KEY not configured")

        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": self.api_key}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
                logger.info(f"🌐 BallDontLie: Fetching {endpoint} (params={params})")
                resp = await client.get(url, params=params)
                
                if resp.status_code == 200:
                    return resp.json().get("data", [])
                elif resp.status_code in [401, 429]:
                    raise ProviderUnavailableError(f"BallDontLie auth/rate failure: {resp.status_code}")
                else:
                    logger.error(f"❌ BallDontLie error {resp.status_code}: {resp.text}")
                    return []
        except httpx.HTTPError as e:
            logger.error(f"BallDontLie connection error: {e}")
            raise ProviderUnavailableError(f"BallDontLie connection failed: {e}")

    async def get_games(self, sport: str = "nba") -> List[Dict]:
        """Fetch games for a specific sport."""
        # Use Redis cache for live games
        cache_key = f"bdl:games:{sport}"
        cached = await cache.get_json(cache_key)
        if cached: return cached

        data = await self._fetch("/games", params={"sport": sport})
        if data:
            await cache.set_json(cache_key, data, ttl=60)
        return data

    async def get_players(self, sport: str = "nba") -> List[Dict]:
        """Fetch players list."""
        return await self._fetch("/players", params={"sport": sport})

    async def get_stats(self, game_id: str) -> List[Dict]:
        """Fetch stats for a specific game."""
        return await self._fetch("/stats", params={"game_ids[]": [game_id]})

    async def get_standings(self, sport: str, season: Optional[int] = None) -> List[Dict]:
        """Fetch standings."""
        params = {"sport": sport}
        if season: params["season"] = season
        return await self._fetch("/standings", params=params)

balldontlie_client = BallDontLieClient()
