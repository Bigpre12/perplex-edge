import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from core.config import settings
from services.cache import cache

logger = logging.getLogger(__name__)

class ISportsApiClient:
    """
    Client for iSports API.
    Uses api_key query parameter for authentication.
    """
    BASE_URL = "https://api.isportsapi.com"

    def __init__(self):
        self.api_key = settings.ISPORTS_API_KEY
        self.timeout = 10.0

    def _get_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}{endpoint}"

    async def get_schedule(self, sport: str) -> List[Dict]:
        """Fetch today's schedule and scores."""
        if not self.api_key:
            return []

        # Map internal sport names to iSports API paths
        path = f"/sport/{sport}/schedule"
        url = self._get_url(path)
        
        params = {
            "api_key": self.api_key,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
        }
        
        cache_key = f"isports:{sport}:schedule"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"🌐 Calling iSports API: {url} (params: {list(params.keys())})")
                resp = await client.get(url, params=params)
                
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    await cache.set_json(cache_key, data, ttl=300) # Longer cache for schedule
                    return data
                else:
                    logger.error(f"❌ iSports API error {resp.status_code}: {resp.text}")
                    return []
        except Exception as e:
            logger.error(f"iSports API connection error: {e}")
            return []

isports_api_client = ISportsApiClient()
