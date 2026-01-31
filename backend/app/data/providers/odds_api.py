"""
The Odds API Provider.

Official documentation: https://the-odds-api.com/
Provides live odds and player props from 40+ bookmakers.

Rate limits:
- Free tier: ~500 credits/month
- Each request costs credits based on markets requested

Usage:
    async with OddsAPIProvider(api_key="xxx") as provider:
        games = await provider.fetch_games("basketball_nba")
        props = await provider.fetch_player_props("basketball_nba", event_id)
"""

import os
import logging
from typing import Any, Optional
from datetime import datetime, timezone

from app.data.base import BaseProvider, ProviderError

logger = logging.getLogger(__name__)


class OddsAPIProvider(BaseProvider):
    """
    The Odds API client for live odds and player props.
    
    Features:
    - Fetches games/events by sport
    - Fetches odds (spreads, totals, moneylines)
    - Fetches player props
    - Tracks quota usage via response headers
    """
    
    name = "oddsapi"
    base_url = "https://api.the-odds-api.com/v4"
    
    # Sport keys for different leagues
    SPORT_KEYS = {
        "NBA": "basketball_nba",
        "NCAAB": "basketball_ncaab",
        "NFL": "americanfootball_nfl",
        "MLB": "baseball_mlb",
        "NHL": "icehockey_nhl",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("ODDS_API_KEY"))
        self.quota_remaining: Optional[int] = None
        self.quota_used: Optional[int] = None
    
    def _add_auth(self, headers: dict, params: dict) -> dict:
        """Add API key as query parameter."""
        params["apiKey"] = self.api_key
        return headers
    
    def _update_quota(self, headers: dict) -> None:
        """Update quota tracking from response headers."""
        if "x-requests-remaining" in headers:
            self.quota_remaining = int(headers["x-requests-remaining"])
        if "x-requests-used" in headers:
            self.quota_used = int(headers["x-requests-used"])
        
        # Also update rate limit state
        self.rate_limit.update_from_headers(headers)
    
    async def _request(self, *args, **kwargs) -> dict:
        """Override to track quota."""
        # Check if API key is set
        if not self.api_key:
            raise ProviderError("API key not configured", provider=self.name)
        
        response = await super()._request(*args, **kwargs)
        return response
    
    async def health_check(self) -> bool:
        """Check if API is accessible and key is valid."""
        try:
            # Use a minimal endpoint to check health
            await self._request("GET", "/sports", params={"apiKey": self.api_key})
            return True
        except Exception as e:
            logger.warning(f"[{self.name}] Health check failed: {e}")
            return False
    
    async def fetch_sports(self) -> list[dict]:
        """
        Fetch list of available sports.
        
        Returns:
            List of sport objects with keys: key, group, title, active
        """
        data = await self._request("GET", "/sports")
        return data if isinstance(data, list) else []
    
    async def fetch_games(
        self,
        sport_key: str,
        regions: str = "us",
        markets: str = "h2h,spreads,totals",
        odds_format: str = "american",
    ) -> list[dict]:
        """
        Fetch games and odds for a sport.
        
        Args:
            sport_key: Sport identifier (e.g., "basketball_nba")
            regions: Bookmaker regions (e.g., "us", "us,uk")
            markets: Markets to include (e.g., "h2h,spreads,totals")
            odds_format: Format for odds ("american" or "decimal")
        
        Returns:
            List of game objects with odds
        """
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
        }
        
        data = await self._request("GET", f"/sports/{sport_key}/odds", params=params)
        
        # Log quota status
        if self.quota_remaining is not None:
            logger.info(f"[{self.name}] Quota remaining: {self.quota_remaining}")
        
        return data if isinstance(data, list) else []
    
    async def fetch_player_props(
        self,
        sport_key: str,
        event_id: str,
        regions: str = "us",
        markets: Optional[str] = None,
        odds_format: str = "american",
    ) -> dict:
        """
        Fetch player props for a specific game.
        
        Args:
            sport_key: Sport identifier
            event_id: Event/game ID from fetch_games()
            regions: Bookmaker regions
            markets: Prop markets (default: common player props)
            odds_format: Format for odds
        
        Returns:
            Game object with player prop markets
        """
        # Default markets based on sport
        if markets is None:
            if "basketball" in sport_key:
                markets = "player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists"
            elif "football" in sport_key:
                markets = "player_pass_yds,player_rush_yds,player_reception_yds,player_receptions"
            else:
                markets = "player_points"
        
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
        }
        
        data = await self._request(
            "GET",
            f"/sports/{sport_key}/events/{event_id}/odds",
            params=params,
        )
        
        return data if isinstance(data, dict) else {}
    
    async def fetch_all_props_for_sport(
        self,
        sport_key: str,
        regions: str = "us",
        markets: Optional[str] = None,
    ) -> list[dict]:
        """
        Fetch player props for all games in a sport.
        
        Note: This can use many credits. Use sparingly.
        
        Args:
            sport_key: Sport identifier
            regions: Bookmaker regions
            markets: Prop markets
        
        Returns:
            List of game objects with player props
        """
        # First get all games
        games = await self.fetch_games(sport_key, regions=regions, markets="h2h")
        
        if not games:
            return []
        
        # Fetch props for each game
        results = []
        for game in games:
            try:
                props = await self.fetch_player_props(
                    sport_key,
                    game["id"],
                    regions=regions,
                    markets=markets,
                )
                if props:
                    results.append(props)
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to fetch props for {game['id']}: {e}")
                continue
        
        return results
    
    def get_quota_status(self) -> dict:
        """Get current quota status."""
        return {
            "remaining": self.quota_remaining,
            "used": self.quota_used,
            "provider": self.name,
        }
