import logging
import json
from typing import List, Dict, Any, Optional
from .base_client import ResilientBaseClient
from core.config import settings

logger = logging.getLogger(__name__)

class OddsAPIClient(ResilientBaseClient):
    """
    Single source for all Odds API calls.
    Handles: quota tracking, rate limiting, backoff, circuit breaker.
    """
    QUOTA_WARN_THRESHOLD = 10_000

    def __init__(self):
        super().__init__(
            name="OddsAPI",
            base_url="https://api.the-odds-api.com/v4",
            timeout=20,
            max_retries=3
        )
        # Support multiple keys for rotation
        self.api_keys = [k.strip() for k in settings.ODDS_API_KEYS if k.strip()]
        if not self.api_keys:
            self.api_keys = [settings.ODDS_API_KEY.strip()]
        
        # Add backup key if not already present
        if settings.ODDS_API_KEY_BACKUP:
            backup = settings.ODDS_API_KEY_BACKUP.strip()
            if backup and backup not in self.api_keys:
                self.api_keys.append(backup)
            
        self.current_key_index = 0
        self.api_key = self.api_keys[0].strip()
        print(f"DEBUG: OddsAPIClient initialized with {len(self.api_keys)} keys. Current: [{self.api_key}]")
        self.requests_remaining = 100000

    def _rotate_key(self):
        """Switch to next available API key"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_index]
        logger.warning(f"OddsAPI: Rotated to next API key (index {self.current_key_index})")

    async def request(
        self, 
        method: str, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Any:
        """Override request to handle key rotation on auth errors"""
        for _ in range(len(self.api_keys)):
            try:
                # Ensure apiKey is always in params
                req_params = params.copy() if params else {}
                req_params["apiKey"] = self.api_key
                
                return await super().request(
                    method, 
                    path, 
                    params=req_params, 
                    json_data=json_data, 
                    headers=headers, 
                    retry_count=retry_count
                )
            except Exception as e:
                # If 401, 403, or 429, try next key
                err_str = str(e).lower()
                if "401" in err_str or "403" in err_str or "429" in err_str:
                    logger.error(f"OddsAPI key failure ({err_str}). Rotating...")
                    self._rotate_key()
                    continue
                raise e
        raise Exception("All OddsAPI keys exhausted or invalid.")

    async def fetch_sports(self) -> list:
        """GET /sports — returns all active sports"""
        return await self.request("GET", "/sports", params={"apiKey": self.api_key})

    async def fetch_events(self, sport: str) -> list:
        """GET /sports/{sport}/events — get game schedule"""
        return await self.request("GET", f"/sports/{sport}/events", params={"apiKey": self.api_key})

    async def fetch_odds(
        self,
        sport: str,
        markets: list[str],
        regions: str = "us",
        odds_format: str = "american"
    ) -> list:
        """GET /sports/{sport}/odds — game lines for multiple books/markets"""
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": ",".join(markets),
            "oddsFormat": odds_format,
            "dateFormat": "iso"
        }
        return await self.request("GET", f"/sports/{sport}/odds", params=params)

    async def fetch_player_props(
        self,
        sport: str,
        event_id: str,
        markets: list[str],
        regions: str = "us",
        odds_format: str = "american"
    ) -> dict:
        """GET /sports/{sport}/events/{event_id}/odds — deep player props"""
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": ",".join(markets),
            "oddsFormat": odds_format,
            "dateFormat": "iso"
        }
        return await self.request("GET", f"/sports/{sport}/events/{event_id}/odds", params=params)

    async def has_active_events(self, sport: str) -> bool:
        """Check if sport has games today — use to gate polling"""
        # Optimized: Check if we have events within next 24h
        try:
            events = await self.fetch_events(sport)
            return len(events) > 0
        except:
            return False

    def _log_usage(self, response, latency):
        """Log x-requests-remaining and x-requests-used on every call"""
        headers = response.headers
        remaining = headers.get("x-requests-remaining")
        used = headers.get("x-requests-used")
        
        if remaining:
            self.requests_remaining = int(remaining)
            logger.info(f"OddsAPI quota → used: {used} | remaining: {remaining} (Latency: {latency:.2f}ms)")
            if self.requests_remaining < self.QUOTA_WARN_THRESHOLD:
                logger.warning(f"⚠️ OddsAPI quota low: {remaining} remaining")

odds_api_client = OddsAPIClient()
fetch_odds = odds_api_client.fetch_odds # For backward compat or simple use
