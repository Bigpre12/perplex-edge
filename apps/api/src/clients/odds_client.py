import logging
import json
from typing import List, Dict, Any, Optional
from .base_client import ResilientBaseClient
from config import settings

logger = logging.getLogger(__name__)

class OddsApiClient(ResilientBaseClient):
    """
    Advanced Odds API Client with Multi-Key Rotation.
    Handles all sports markets and bookmakers with quota telemetry.
    """
    
    def __init__(self):
        super().__init__(
            name="OddsAPI",
            base_url="https://api.the-odds-api.com/v4",
            timeout=20,
            max_retries=3
        )
        self.api_keys = settings.ODDS_API_KEYS
        self.current_key_index = 0
        self.requests_remaining = 100000 # Default high, updated on calls

    def _get_active_key(self) -> str:
        return self.api_keys[self.current_key_index]

    def _rotate_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.info(f"[OddsAPI] Rotated to API Key #{self.current_key_index}")

    async def get_sports(self) -> List[Dict[str, Any]]:
        return await self.request("GET", "/sports", params={"apiKey": self._get_active_key()})

    async def get_odds(
        self, 
        sport: str, 
        regions: str = "us", 
        markets: str = "h2h,spreads,totals",
        odds_format: str = "decimal"
    ) -> List[Dict[str, Any]]:
        """
        Fetch odds for a specific sport and markets.
        """
        params = {
            "apiKey": self._get_active_key(),
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format
        }
        return await self.request("GET", f"/sports/{sport}/odds", params=params)

    async def get_event_odds(
        self,
        sport: str,
        event_id: str,
        regions: str = "us",
        markets: str = "h2h"
    ) -> Dict[str, Any]:
        params = {
            "apiKey": self._get_active_key(),
            "regions": regions,
            "markets": markets
        }
        return await self.request("GET", f"/sports/{sport}/events/{event_id}/odds", params=params)

    def _log_usage(self, response, latency):
        """
        Extract X-Requests-Remaining and X-Requests-Used from headers.
        """
        remaining = response.headers.get("x-requests-remaining")
        used = response.headers.get("x-requests-used")
        
        if remaining:
            self.requests_remaining = int(remaining)
            if self.requests_remaining < 10000:
                logger.warning(f"[OddsAPI] CRITICAL QUOTA: {self.requests_remaining} requests remaining!")
            
            # Rotation Logic if remaining is 0
            if self.requests_remaining <= 0 and len(self.api_keys) > 1:
                self._rotate_key()

    async def has_active_events(self, sport: str) -> bool:
        """Helper to check if a sport has events scheduled to avoid wasted calls"""
        # In production this might check a local cache of the schedule
        # For now we check the status of the sport
        try:
            res = await self.get_sports()
            for s in res:
                if s['key'] == sport:
                    return s.get('active', False)
        except:
            return False
        return False
