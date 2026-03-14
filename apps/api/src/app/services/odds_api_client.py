import os, time, httpx, logging, json
from typing import Any, Dict, List, Optional
from config import settings

logger = logging.getLogger(__name__)

class OddsApiClient:
    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self):
        # Use settings for keys
        self.keys = [settings.ODDS_API_KEY]
        if settings.ODDS_API_KEY_BACKUP and settings.ODDS_API_KEY_BACKUP not in self.keys:
            self.keys.append(settings.ODDS_API_KEY_BACKUP)
        
        # Also check common env vars just in case
        env_key = os.getenv("THE_ODDS_API_KEY")
        if env_key and env_key not in self.keys:
            self.keys.append(env_key)

        self.current_key_idx = 0
        self._cache: dict = {}
        self.default_ttl  = 300
        self.timeout      = 10.0
        
        self._all_keys_failed = False
        self._cooldown_until = 0
        self.cooldown_seconds = 10 if settings.DEVELOPMENT_MODE else 1800

    def _get_mock_fallback(self, endpoint: str) -> Any:
        """Helper to return local mock data when API is unavailable."""
        try:
            # Adjusted path to match app/services structure
            # __file__ is apps/api/src/app/services/odds_api_client.py
            # apps/api/data/raw_props.json
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            mock_path = os.path.join(base_dir, "data", "raw_props.json")
            if os.path.exists(mock_path):
                with open(mock_path, "r") as f:
                    mock_data = json.load(f)
            else:
                logger.warning(f"Mock file not found at {mock_path}")
                mock_data = {}
        except Exception as mock_err:
            logger.error(f"Failed to load mock data: {mock_err}")
            mock_data = {}

        if "/events" in endpoint:
            if mock_data:
                logger.info("Using local mock data as fallback for props.")
                return mock_data
            return {}
            
        if "/odds" in endpoint:
            return [mock_data] if mock_data else []
            
        if "/sports" in endpoint:
            return [{"key": "basketball_nba", "active": True, "group": "Basketball", "title": "NBA"}]

        return []

    async def request(self, endpoint: str, params: Optional[Dict] = None,
                      use_cache: bool = True, ttl: Optional[int] = None) -> Any:
        if not self.keys or not any(self.keys):
            logger.error("No Odds API keys configured")
            return self._get_mock_fallback(endpoint)

        if self._all_keys_failed and time.time() < self._cooldown_until:
             return self._get_mock_fallback(endpoint)

        params = params or {}
        ttl = ttl if ttl is not None else self.default_ttl
        
        param_str = '&'.join(f'{k}={v}' for k,v in sorted(params.items()))
        cache_key = f"{endpoint}?{param_str}"

        if use_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() < entry["expires_at"]:
                return entry["data"]

        url = f"{self.BASE_URL}/{endpoint}" if not endpoint.startswith("/") else f"{self.BASE_URL}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                attempts = 0
                while attempts < len(self.keys):
                    current_key = self.keys[self.current_key_idx]
                    if not current_key:
                        self.current_key_idx = (self.current_key_idx + 1) % len(self.keys)
                        attempts += 1
                        continue
                        
                    full_params = {**params, "apiKey": current_key}
                    r = await client.get(url, params=full_params)
                    
                    if r.status_code in (401, 429):
                        logger.warning(f"Odds API key {current_key[:4]}... exhausted. Trying next.")
                        self.current_key_idx = (self.current_key_idx + 1) % len(self.keys)
                        attempts += 1
                        continue
                        
                    r.raise_for_status()
                    data = r.json()
                    
                    if use_cache:
                        self._cache[cache_key] = {"data": data, "expires_at": time.time() + ttl}
                    return data
                
                self._all_keys_failed = True
                self._cooldown_until = time.time() + self.cooldown_seconds
                return self._get_mock_fallback(endpoint)
        except Exception as e:
            logger.error(f"Odds API error on {endpoint}: {e}")
            return self._get_mock_fallback(endpoint)

    async def get_player_props(self, sport_key: str, event_id: str, markets: str, regions: str = "us"):
        return await self.request(
            f"sports/{sport_key}/events/{event_id}/odds",
            params={"regions": regions, "markets": markets, "oddsFormat": "american"},
        )

    async def get_active_sports(self) -> List[Dict]:
        return await self.request("sports", ttl=3600) or []

    async def get_live_odds(self, sport_key: str, regions: str = "us", markets: str = "h2h,spreads") -> List[Dict]:
        return await self.request(
            f"sports/{sport_key}/odds",
            params={"regions": regions, "markets": markets, "oddsFormat": "american"}
        ) or []

odds_api = OddsApiClient()
