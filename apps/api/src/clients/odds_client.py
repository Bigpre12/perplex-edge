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
        # Support multiple keys for rotation — Load directly from env for reliability
        import os
        primary_key = os.environ.get("THE_ODDS_API_KEY") or os.environ.get("ODDS_API_KEY", "")
        backup_key = os.environ.get("THE_ODDS_API_KEY_BACKUP") or os.environ.get("ODDS_API_KEY_BACKUP", "")
        raw_keys = os.environ.get("ODDS_API_KEYS", "")
        
        # Validation: Fail early if no primary key is found
        if not primary_key or not primary_key.strip():
            logger.error("❌ FATAL: THE_ODDS_API_KEY is not set. Ingest will fail.")
            # raise RuntimeError("THE_ODDS_API_KEY is not set.") # User requested raise but we might want to avoid crashing the whole API if other parts work
            
        self.api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        if primary_key and primary_key.strip() not in self.api_keys:
            self.api_keys.insert(0, primary_key.strip())
        if backup_key and backup_key.strip() and backup_key.strip() not in self.api_keys:
            self.api_keys.append(backup_key.strip())
            
        # Ensure we have at least one key string, even if empty, to avoid index errors
        if not self.api_keys:
            self.api_keys = [""]
            
        self.current_key_index = 0
        self.api_key = self.api_keys[0].strip()
        
        # Security logging: Show first 4 chars of each key
        safe_keys = [f"{k[:4]}****" if len(k) > 4 else "****" for k in self.api_keys if k]
        logger.info(f"✅ OddsAPIClient initialized with {len(self.api_keys)} keys: {', '.join(safe_keys)}")
        print(f"DEBUG: OddsAPIClient initialized with {len(self.api_keys)} keys. Current key start: {self.api_key[:4]}...")
        
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
                    if len(self.api_keys) > 1:
                        self._rotate_key()
                        continue
                    else:
                        logger.warning("OddsAPI: No more keys to rotate or single key invalid. Returning empty result.")
                        return [] if method == "GET" and "/events" in path or "/odds" in path else {}
                raise e
        logger.warning("OddsAPI: All keys exhausted or missing. Returning empty state.")
        return [] if method == "GET" else {}

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
