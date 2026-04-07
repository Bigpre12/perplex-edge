import httpx
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from core.config import settings
from services.cache import cache

logger = logging.getLogger(__name__)

class ApiSportsClient:
    """
    Unified Client for API-Sports (Football, Basketball, Baseball, Hockey).
    Uses x-apisports-key for direct authentication.
    """
    SPORT_BASE_URLS = {
        "soccer": "https://v3.football.api-sports.io",
        "basketball": "https://v1.basketball.api-sports.io",
        "baseball": "https://v1.baseball.api-sports.io",
        "hockey": "https://v1.hockey.api-sports.io"
    }

    # League IDs for major competitions
    LEAGUE_IDS = {
        "basketball_nba": 12,
        "americanfootball_nfl": 1, # Use Football V3 for NFL if possible, or another? 
        # Actually API-Sports NFL is usually a separate API: v1.american-football.api-sports.io
        "baseball_mlb": 1,
        "icehockey_nhl": 57,
        "soccer_epl": 39,
        "soccer_usa_mls": 253,
    }

    def __init__(self):
        self.api_key = settings.API_SPORTS_KEY
        self.timeout = 10.0

    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-apisports-key": self.api_key,
            "Accept": "application/json"
        }

    def _get_base_url(self, sport_key: str) -> str:
        if "soccer" in sport_key or "football" in sport_key:
            return self.SPORT_BASE_URLS["soccer"]
        if "basketball" in sport_key:
            return self.SPORT_BASE_URLS["basketball"]
        if "baseball" in sport_key:
            return self.SPORT_BASE_URLS["baseball"]
        if "hockey" in sport_key or "nhl" in sport_key:
            return self.SPORT_BASE_URLS["hockey"]
        return self.SPORT_BASE_URLS["soccer"] # Fallback

    async def get_live_scores(self, sport_key: str) -> List[Dict]:
        """Fetch live scores and games for today."""
        if not self.api_key:
            return []

        base_url = self._get_base_url(sport_key)
        league_id = self.LEAGUE_IDS.get(sport_key)
        
        # Determine endpoint based on sport
        endpoint = "/fixtures" if "soccer" in sport_key else "/games"
        
        params = {}
        if league_id:
            params["league"] = league_id
            params["season"] = datetime.now(timezone.utc).year # Simplified season resolution
        
        # For live scores only
        params["live"] = "all"
        
        cache_key = f"api_sports:{sport_key}:live"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached

        try:
            async with httpx.AsyncClient(headers=self._get_headers(), timeout=self.timeout) as client:
                url = f"{base_url}{endpoint}"
                logger.info(f"🌐 Calling API-Sports: {url} (params: {params})")
                resp = await client.get(url, params=params)
                
                if resp.status_code == 200:
                    data = resp.json().get("response", [])
                    await cache.set_json(cache_key, data, ttl=60) # Short cache for live
                    return data
                else:
                    logger.error(f"❌ API-Sports error {resp.status_code}: {resp.text}")
                    return []
        except Exception as e:
            logger.error(f"API-Sports connection error: {e}")
            return []

api_sports_client = ApiSportsClient()
