"""
The Odds API REST Client

Fetches live sports data, betting odds, and player props.
Handles API keys, rate-limit retries, fallback keys, and in-memory caching
to prevent burning through the free tier quota (500 requests/month).

Docs: https://the-odds-api.com/liveapi/guides/v4/
"""
import os
import time
import httpx
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class OddsApiClient:
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    def __init__(self):
        # We accept a primary and backup key
        self.primary_key = os.getenv("THE_ODDS_API_KEY")
        self.backup_key = os.getenv("THE_ODDS_API_KEY_BACKUP")
        
        self.current_key = self.primary_key
        
        # Simple in-memory cache
        # Format: { "endpoint_path": {"data": [...], "expires_at": 1700000000} }
        self._cache = {}
        
        # Default TTL for standard odds is 5 minutes to save quota
        self.default_ttl_seconds = 300
        
        # Timeout for API requests
        self.timeout = 10.0

    async def _request(self, endpoint: str, params: Dict = None, use_cache: bool = True, ttl: int = None) -> Any:
        """
        Make a GET request to The Odds API with caching and fallback logic.
        """
        if not self.current_key:
            logger.error("No API key configured for The Odds API")
            return None

        if params is None:
            params = {}
            
        ttl = ttl if ttl is not None else self.default_ttl_seconds
        
        # Build cache key from endpoint and params
        cache_key = f"{endpoint}?{'&'.join([f'{k}={v}' for k, v in sorted(params.items())])}"
        
        # Check cache
        if use_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() < entry["expires_at"]:
                logger.debug(f"Cache hit for {cache_key}")
                return entry["data"]
                
        # Cache miss - make the request
        params["apiKey"] = self.current_key
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                # Handle rate limits / 401s by rolling over to backup key
                if response.status_code in (401, 429) and self.current_key == self.primary_key and self.backup_key:
                    logger.warning("Primary Odds API key exhausted or invalid. Switching to backup key.")
                    self.current_key = self.backup_key
                    params["apiKey"] = self.current_key
                    response = await client.get(url, params=params)
                    
                response.raise_for_status()
                data = response.json()
                
                # Save to cache
                if use_cache:
                    self._cache[cache_key] = {
                        "data": data,
                        "expires_at": time.time() + ttl
                    }
                    
                # Log quota usage headers if present
                remaining = response.headers.get("x-requests-remaining")
                if remaining:
                    logger.info(f"Odds API Requests Remaining: {remaining}")
                    
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Odds API: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch from Odds API: {e}")
            return None

    async def get_active_sports(self) -> List[Dict]:
        """Get all currently in-season sports."""
        # Sports rarely change, cache for 1 hour
        return await self._request("/sports", use_cache=True, ttl=3600) or []

    async def get_live_odds(self, sport_key: str, regions: str = "us", markets: str = "h2h,spreads") -> List[Dict]:
        """
        Get live games and main market odds for a specific sport.
        
        Args:
            sport_key: e.g. 'basketball_nba' or 'americanfootball_nfl'
            regions: 'us', 'uk', 'eu', 'au'
            markets: comma separated list of markets like 'h2h,spreads,totals'
        """
        endpoint = f"/sports/{sport_key}/odds"
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": "american"
        }
        return await self._request(endpoint, params=params) or []
        
    async def get_player_props(self, sport_key: str, event_id: str, markets: str, regions: str = "us") -> List[Dict]:
        """
        Get player prop markets for a specific game event.
        
        Args:
            sport_key: e.g. 'basketball_nba'
            event_id: The specific game ID from the Odds API
            markets: comma separated list (e.g. 'player_points,player_rebounds')
        """
        endpoint = f"/sports/{sport_key}/events/{event_id}/odds"
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": "american"
        }
        return await self._request(endpoint, params=params) or []

# Singleton instance
odds_api = OddsApiClient()
