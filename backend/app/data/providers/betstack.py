"""
BetStack API Provider.

Documentation: https://api.betstack.dev
Provides free consensus odds (rate limited to ~60s per endpoint).

Usage:
    async with BetStackProvider(api_key="xxx") as provider:
        odds = await provider.fetch_consensus_odds("nba")
"""

import os
import logging
from typing import Any, Optional

from app.data.base import BaseProvider, ProviderError

logger = logging.getLogger(__name__)


class BetStackProvider(BaseProvider):
    """
    BetStack API client for consensus odds.
    
    Features:
    - Free consensus odds
    - Good as a secondary/backup source
    
    Limitations:
    - Rate limited (60s per endpoint)
    - Consensus view, not book-specific
    """
    
    name = "betstack"
    base_url = "https://api.betstack.dev/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("BETSTACK_API_KEY"))
    
    def _add_auth(self, headers: dict, params: dict) -> dict:
        """Add API key as query parameter."""
        if self.api_key:
            params["apiKey"] = self.api_key
        return headers
    
    async def health_check(self) -> bool:
        """Check if API is accessible."""
        try:
            # Use a simple endpoint to check
            await self._request("GET", "/sports")
            return True
        except Exception as e:
            logger.warning(f"[{self.name}] Health check failed: {e}")
            return False
    
    async def fetch_sports(self) -> list[dict]:
        """Fetch available sports."""
        data = await self._request("GET", "/sports")
        return data if isinstance(data, list) else []
    
    async def fetch_consensus_odds(self, sport: str) -> list[dict]:
        """
        Fetch consensus odds for a sport.
        
        Args:
            sport: Sport name (e.g., "nba", "ncaab", "nfl")
        
        Returns:
            List of games with consensus odds
        """
        data = await self._request("GET", f"/odds/{sport}")
        return data if isinstance(data, list) else []
    
    async def fetch_games(self, sport_key: str) -> list[dict]:
        """
        Fetch games - maps sport_key to BetStack format.
        
        Args:
            sport_key: Standard sport key (e.g., "basketball_nba")
        
        Returns:
            List of games with odds
        """
        # Map standard sport keys to BetStack format
        sport_map = {
            "basketball_nba": "nba",
            "basketball_ncaab": "ncaab",
            "americanfootball_nfl": "nfl",
            "baseball_mlb": "mlb",
            "icehockey_nhl": "nhl",
        }
        
        sport = sport_map.get(sport_key, sport_key.split("_")[-1])
        return await self.fetch_consensus_odds(sport)
