"""
OddsPapi Provider.

Documentation: https://oddspapi.io/
Provides historical odds data and WebSocket live odds.

Best used for:
- Historical odds for backtesting
- Building projections and baselines
- (Optionally) WebSocket for lower latency live odds

Usage:
    async with OddsPapiProvider(api_key="xxx") as provider:
        historical = await provider.fetch_historical_odds("basketball_nba", date(2026, 1, 15))
"""

import os
import logging
from datetime import date, datetime
from typing import Any, Optional

from app.data.base import BaseProvider, ProviderError

logger = logging.getLogger(__name__)


class OddsPapiProvider(BaseProvider):
    """
    OddsPapi API client for historical odds.
    
    Features:
    - Historical odds snapshots
    - Settlement data
    - Live scores
    
    Best for:
    - Backtesting models
    - Building projections
    - Historical analysis
    
    NOT recommended for:
    - Live pricing (use REST cache + TheOddsAPI instead)
    """
    
    name = "oddspapi"
    base_url = "https://api.oddspapi.io/v1"
    
    # Rate limits per endpoint (milliseconds between requests)
    RATE_LIMITS = {
        "historical": 5000,
        "settlements": 2000,
        "scores": 1000,
    }
    
    # Sport IDs in OddsPapi
    SPORT_IDS = {
        "basketball_nba": 10,
        "basketball_ncaab": 10,  # Same category
        "americanfootball_nfl": 12,
        "baseball_mlb": 16,
        "icehockey_nhl": 17,
    }
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("ODDSPAPI_API_KEY"))
    
    def _add_auth(self, headers: dict, params: dict) -> dict:
        """Add API key as header."""
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def health_check(self) -> bool:
        """Check if API is accessible."""
        try:
            await self._request("GET", "/sports")
            return True
        except Exception as e:
            logger.warning(f"[{self.name}] Health check failed: {e}")
            return False
    
    async def fetch_historical_odds(
        self,
        sport_key: str,
        game_date: date,
        market: str = "spreads",
    ) -> list[dict]:
        """
        Fetch historical odds for a date.
        
        Args:
            sport_key: Standard sport key
            game_date: Date to fetch
            market: Market type (spreads, totals, h2h)
        
        Returns:
            List of historical odds entries
        """
        sport_id = self.SPORT_IDS.get(sport_key, 10)
        
        params = {
            "sport_id": sport_id,
            "date": game_date.isoformat(),
            "market": market,
        }
        
        data = await self._request("GET", "/historical/odds", params=params)
        return data.get("odds", []) if isinstance(data, dict) else []
    
    async def fetch_settlements(
        self,
        sport_key: str,
        game_date: date,
    ) -> list[dict]:
        """
        Fetch settlement/results data for a date.
        
        Args:
            sport_key: Standard sport key
            game_date: Date to fetch
        
        Returns:
            List of settled game results
        """
        sport_id = self.SPORT_IDS.get(sport_key, 10)
        
        params = {
            "sport_id": sport_id,
            "date": game_date.isoformat(),
        }
        
        data = await self._request("GET", "/settlements", params=params)
        return data.get("settlements", []) if isinstance(data, dict) else []
    
    async def fetch_live_scores(
        self,
        sport_key: str,
    ) -> list[dict]:
        """
        Fetch current live scores.
        
        Args:
            sport_key: Standard sport key
        
        Returns:
            List of live game scores
        """
        sport_id = self.SPORT_IDS.get(sport_key, 10)
        
        params = {"sport_id": sport_id}
        
        data = await self._request("GET", "/scores/live", params=params)
        return data.get("scores", []) if isinstance(data, dict) else []
