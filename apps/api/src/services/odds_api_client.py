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
        # We accept a comma-separated list of keys for infinite scalability
        keys_env = os.getenv("THE_ODDS_API_KEY", "")
        self.keys = [k.strip() for k in keys_env.split(",") if k.strip()]
        
        # Fallback to backup key if explicitly set but not in list
        backup = os.getenv("THE_ODDS_API_KEY_BACKUP")
        if backup and backup.strip() and backup.strip() not in self.keys:
            self.keys.append(backup.strip())
            
        self.current_key_idx = 0
        
        # Circuit breaker — when all keys fail, skip Odds API for a cooldown period
        self._all_keys_failed = False
        self._cooldown_until = 0  # timestamp when we should retry
        self.cooldown_seconds = 1800  # 30 min cooldown after all keys exhaust
        
        # Simple in-memory cache
        # Format: { "endpoint_path": {"data": [...], "expires_at": 1700000000} }
        self._cache = {}
        
        # Default TTL for standard odds is 5 minutes to save quota
        self.default_ttl_seconds = 300
        
        # Timeout for API requests — reduced to prevent cascade delays
        self.timeout = 5.0

    async def _request(self, endpoint: str, params: Dict = None, use_cache: bool = True, ttl: int = None) -> Any:
        """
        Make a GET request to The Odds API with caching and round-robin fallback logic.
        """
        if not self.keys:
            logger.error("No API keys configured for The Odds API")
            return None

        # Circuit breaker — skip immediately if all keys recently failed
        if self._all_keys_failed and time.time() < self._cooldown_until:
            logger.debug("Odds API circuit breaker OPEN — skipping (cooldown active)")
            return None
        elif self._all_keys_failed:
            # Cooldown expired, retry
            self._all_keys_failed = False
            logger.info("Odds API circuit breaker RESET — retrying keys")

        if params is None:
            params = {}
            
        ttl = ttl if ttl is not None else self.default_ttl_seconds
        
        # Build cache key from endpoint and params
        cache_key = f"{endpoint}?{'&'.join([f'{k}={v}' for k, v in sorted(params.items()) if k != 'apiKey'])}"
        
        # Check cache
        if use_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() < entry["expires_at"]:
                logger.debug(f"Cache hit for {cache_key}")
                return entry["data"]
                
        # Cache miss - make the request
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                attempts = 0
                max_attempts = len(self.keys)
                
                while attempts < max_attempts:
                    current_key = self.keys[self.current_key_idx]
                    params["apiKey"] = current_key
                    
                    response = await client.get(url, params=params)
                    
                    # Handle rate limits / 401s by rolling over to next key
                    if response.status_code in (401, 429):
                        logger.warning(f"Odds API key {current_key[:4]}... exhausted or invalid. Switching to next key.")
                        self.current_key_idx = (self.current_key_idx + 1) % len(self.keys)
                        attempts += 1
                        continue # Try next key
                        
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
                        logger.info(f"Odds API Requests Remaining: {remaining} (Key: {current_key[:4]}...)")
                        
                    return data
                
                logger.error("All Odds API keys exhausted or invalid.")
                self._all_keys_failed = True
                self._cooldown_until = time.time() + self.cooldown_seconds
                logger.info(f"Circuit breaker TRIPPED — skipping Odds API for {self.cooldown_seconds}s")
                return None
                
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
