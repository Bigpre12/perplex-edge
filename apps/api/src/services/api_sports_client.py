import httpx
from services.api_telemetry import InstrumentedAsyncClient
import logging
from typing import Dict, List, Optional, Any
from core.config import settings
from services.cache import cache

logger = logging.getLogger(__name__)

class ProviderUnavailableError(Exception):
    """Custom exception for unified error handling in waterfall."""
    pass

class ApiSportsClient:
    """
    Subdomain-Aware Client for API-Sports.
    Toggles subdomains based on sport key.
    """
    SPORT_SUBDOMAINS = {
        "nba": "v1.basketball",
        "basketball": "v1.basketball",
        "nfl": "v1.american-football",
        "american-football": "v1.american-football",
        "mlb": "v1.baseball",
        "baseball": "v1.baseball",
        "soccer": "v3.football",
        "football": "v3.football",
        "ufc": "v1.mma",
        "mma": "v1.mma"
    }

    def __init__(self):
        self.api_key = settings.API_SPORTS_KEY if hasattr(settings, 'API_SPORTS_KEY') else ""
        self.timeout = 10.0

    def _get_base_url(self, sport: str) -> str:
        """Determines the correct API-Sports subdomain based on sport."""
        sub = self.SPORT_SUBDOMAINS.get(sport.lower(), "v3.football")
        return f"https://{sub}.api-sports.io"

    async def _fetch(self, sport: str, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Unified fetch with subdomain awareness."""
        if not self.api_key:
            raise ProviderUnavailableError("API_SPORTS_KEY not configured")

        base_url = self._get_base_url(sport)
        url = f"{base_url}{endpoint}"
        
        try:
            async with InstrumentedAsyncClient(provider="api-sports", timeout=self.timeout, headers={"x-apisports-key": self.api_key}) as client:
                logger.info(f"🌐 API-Sports: Fetching {endpoint} on {url}")
                resp = await client.get(url, params=params)
                
                if resp.status_code == 200:
                    return resp.json().get("response", [])
                elif resp.status_code in [401, 403, 429]:
                    raise ProviderUnavailableError(f"API-Sports auth/rate failure: {resp.status_code}")
                else:
                    return []
        except httpx.HTTPError as e:
            raise ProviderUnavailableError(f"API-Sports connection failed: {e}")

    async def get_games(self, sport: str, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch games for a specific sport."""
        # Endpoint varies: /fixtures for soccer, /games for US sports
        endpoint = "/fixtures" if "soccer" in sport or "football" in sport else "/games"
        return await self._fetch(sport, endpoint, params=params)

    async def get_standings(self, sport: str, season: int) -> List[Dict]:
        """Fetch standings."""
        return await self._fetch(sport, "/standings", params={"season": season})

    async def get_players(self, sport: str, team_id: int) -> List[Dict]:
        """Fetch players for a team."""
        return await self._fetch(sport, "/players", params={"team": team_id})

    async def get_odds(self, sport: str, fixture_id: int) -> List[Dict]:
        """Fetch odds for a fixture."""
        return await self._fetch(sport, "/odds", params={"fixture": fixture_id})

api_sports_client = ApiSportsClient()
