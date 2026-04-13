"""
Betstack API Client
Data source: https://betstack.dev/ or https://betstack.io/ (integrated as v1)
"""
import os
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from core.config import settings
from api_utils.http import build_headers

class BetstackClient:
    def __init__(self):
        self.api_key = settings.BETSTACK_API_KEY
        self.base_url = settings.BETSTACK_BASE_URL
        self.timeout = 15.0

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def _make_request(self, endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Any:
        if not self.available:
            logger.warning("Betstack API missing credentials: BETSTACK_API_KEY not set")
            return None

        headers = build_headers({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })

        async with httpx.AsyncClient() as client:
            try:
                if method == "GET":
                    response = await client.get(f"{self.base_url}/{endpoint}", headers=headers, params=params, timeout=self.timeout)
                else:
                    response = await client.post(f"{self.base_url}/{endpoint}", headers=headers, json=json_data, timeout=self.timeout)
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Betstack API error {e.response.status_code}: {e.response.text}")
                return None
            except Exception as e:
                logger.error(f"Betstack request failed: {e}")
                return None

    async def get_player_props(self, sport: str = "nba") -> List[Dict]:
        """Fetch player props for a given sport."""
        # Endpoint pattern from real_sports_api.py: /props/{sport}
        result = await self._make_request(f"props/{sport}")
        return result if isinstance(result, list) else []

    async def get_odds(self, sport: str = "nba") -> List[Dict]:
        """Fetch general betting odds."""
        result = await self._make_request(f"odds/{sport}")
        return result if isinstance(result, list) else []

# Singleton instance
betstack_client = BetstackClient()

def get_betstack_client() -> Optional[BetstackClient]:
    """Factory function for safe client access."""
    if not betstack_client.available:
        logger.warning("Betstack API client requested but credentials not set.")
        return None
    return betstack_client
