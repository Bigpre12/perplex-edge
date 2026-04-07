import httpx
import logging
from typing import Dict, List, Optional, Any
from core.config import settings
from services.cache import cache

logger = logging.getLogger(__name__)

class ProviderUnavailableError(Exception):
    """Custom exception for unified error handling in waterfall."""
    pass

class SportMonksClient:
    """
    Official Sportmonks API Client (V3).
    Soccer-focused, uses api_token query param.
    """
    BASE_URL = "https://api.sportmonks.com/v3"

    def __init__(self):
        self.api_token = settings.SPORTMONKS_KEY if hasattr(settings, 'SPORTMONKS_KEY') else ""
        self.timeout = 10.0

    async def _fetch(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Unified fetch with api_token query parameter."""
        if not self.api_token:
            raise ProviderUnavailableError("SPORTMONKS_KEY not configured")

        url = f"{self.BASE_URL}{endpoint}"
        query_params = params or {}
        query_params["api_token"] = self.api_token
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"🌐 Sportmonks: Fetching {endpoint} (params={list(query_params.keys())})")
                resp = await client.get(url, params=query_params)
                
                if resp.status_code == 200:
                    return resp.json().get("data", [])
                elif resp.status_code in [401, 429]:
                    raise ProviderUnavailableError(f"Sportmonks auth/rate failure: {resp.status_code}")
                else:
                    return []
        except httpx.HTTPError as e:
            raise ProviderUnavailableError(f"Sportmonks connection failed: {e}")

    async def get_fixtures(self, date: Optional[str] = None) -> List[Dict]:
        """Fetch fixtures for a specific date."""
        path = f"/football/fixtures/date/{date}" if date else "/football/fixtures"
        return await self._fetch(path)

    async def get_standings(self, season_id: int) -> List[Dict]:
        """Fetch standings for a season."""
        return await self._fetch(f"/football/standings/seasons/{season_id}")

    async def get_odds(self, fixture_id: int) -> List[Dict]:
        """Fetch odds for a fixture."""
        return await self._fetch(f"/football/odds/fixtures/{fixture_id}")

sportmonks_client = SportMonksClient()
