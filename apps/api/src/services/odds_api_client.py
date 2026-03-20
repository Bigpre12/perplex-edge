"""
Odds API Client stub - wraps the real sports API client.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OddsApiClient:
    """Lightweight wrapper around the real sports data API."""

    async def get_events(self, sport: str) -> list:
        try:
            from real_sports_api import get_events
            return await get_events(sport)
        except Exception as e:
            logger.warning(f"get_events({sport}) failed: {e}")
            return []

    async def get_player_props(self, sport: str, event_id: str, markets: str = "player_points", regions: str = "us") -> dict:
        try:
            from real_sports_api import get_player_props
            return await get_player_props(sport, event_id, markets=markets, regions=regions)
        except Exception as e:
            logger.warning(f"get_player_props({sport},{event_id}) failed: {e}")
            return {"bookmakers": []}

    async def get_odds(self, sport: str, regions: str = "us", markets: str = "h2h,spreads") -> list:
        try:
            from real_sports_api import get_odds
            return await get_odds(sport, regions=regions, markets=markets)
        except Exception as e:
            logger.warning(f"get_odds({sport}) failed: {e}")
            return []

odds_api_client = OddsApiClient()
odds_api = odds_api_client
