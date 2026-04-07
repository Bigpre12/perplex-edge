import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from core.config import settings
from services.cache import cache

logger = logging.getLogger(__name__)

class SportMonksClient:
    """
    Client for Sportmonks V3 API.
    Uses api_token query parameter for authentication.
    """
    BASE_URL = "https://api.sportmonks.com/v3"

    def __init__(self):
        self.api_token = settings.SPORTMONKS_KEY
        self.timeout = 10.0

    def _get_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}{endpoint}"

    async def get_live_scores(self, sport: str) -> List[Dict]:
        """Fetch live scores and games for a sport."""
        if not self.api_token:
            return []

        # Map internal sport names to Sportmonks paths
        path = "football/fixtures" if sport == "soccer" else f"{sport}/scores"
        url = self._get_url(path)
        
        params = {
            "api_token": self.api_token,
            "include": "participants;scores",
            "filter[status]": "LIVE"
        }
        
        cache_key = f"sportmonks:{sport}:live"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"🌐 Calling Sportmonks: {url} (params: {list(params.keys())})")
                resp = await client.get(url, params=params)
                
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    await cache.set_json(cache_key, data, ttl=60)
                    return data
                else:
                    logger.error(f"❌ Sportmonks error {resp.status_code}: {resp.text}")
                    return []
        except Exception as e:
            logger.error(f"Sportmonks connection error: {e}")
            return []

sportmonks_client = SportMonksClient()
