"""The Odds API client for fetching odds and props data."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Sport keys for The Odds API
SPORT_KEYS = {
    "NBA": "basketball_nba",
    "NFL": "americanfootball_nfl",
    "MLB": "baseball_mlb",
    "NHL": "icehockey_nhl",
    "NCAAB": "basketball_ncaab",
    "NCAAF": "americanfootball_ncaaf",
}

# Market keys
MARKETS = {
    "h2h": "moneyline",
    "spreads": "spread",
    "totals": "total",
}

# Common US sportsbooks
BOOKMAKERS = [
    "fanduel",
    "draftkings",
    "betmgm",
    "caesars",
    "pointsbetus",
    "betrivers",
    "unibet_us",
]


class OddsAPIClient:
    """Client for The Odds API."""

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.odds_api_key
        self.base_url = settings.odds_api_base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "OddsAPIClient":
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return self._client

    async def _request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a request to The Odds API."""
        if not self.api_key:
            raise ValueError("ODDS_API_KEY not configured")

        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        # Log remaining requests from headers
        remaining = response.headers.get("x-requests-remaining", "unknown")
        used = response.headers.get("x-requests-used", "unknown")
        logger.info(f"Odds API: {used} used, {remaining} remaining")

        return response.json()

    async def get_sports(self) -> list[dict[str, Any]]:
        """Get list of available sports."""
        return await self._request("/sports")

    async def get_odds(
        self,
        sport_key: str,
        regions: str = "us",
        markets: str = "h2h,spreads,totals",
        bookmakers: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """
        Get odds for a specific sport.
        
        Args:
            sport_key: The sport key (e.g., 'basketball_nba')
            regions: Comma-separated regions (us, us2, uk, eu, au)
            markets: Comma-separated markets (h2h, spreads, totals)
            bookmakers: Optional list of specific bookmakers
        
        Returns:
            List of games with odds
        """
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": "american",
        }
        
        if bookmakers:
            params["bookmakers"] = ",".join(bookmakers)

        return await self._request(f"/sports/{sport_key}/odds", params)

    async def get_events(self, sport_key: str) -> list[dict[str, Any]]:
        """Get upcoming events for a sport."""
        return await self._request(f"/sports/{sport_key}/events")

    async def get_event_odds(
        self,
        sport_key: str,
        event_id: str,
        regions: str = "us",
        markets: str = "h2h,spreads,totals",
    ) -> dict[str, Any]:
        """Get odds for a specific event."""
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": "american",
        }
        return await self._request(
            f"/sports/{sport_key}/events/{event_id}/odds",
            params,
        )

    async def get_player_props(
        self,
        sport_key: str,
        event_id: str,
        regions: str = "us",
        markets: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get player props for a specific event.
        
        Note: Requires a paid subscription to The Odds API.
        
        Args:
            sport_key: The sport key
            event_id: The event ID
            regions: Comma-separated regions
            markets: Prop markets (e.g., 'player_points,player_rebounds')
        """
        params = {
            "regions": regions,
            "oddsFormat": "american",
        }
        
        if markets:
            params["markets"] = markets
        else:
            # Default NBA prop markets
            if "basketball" in sport_key:
                params["markets"] = "player_points,player_rebounds,player_assists,player_threes"
            elif "football" in sport_key:
                params["markets"] = "player_pass_yds,player_rush_yds,player_reception_yds"
            elif "baseball" in sport_key:
                params["markets"] = "batter_total_bases,pitcher_strikeouts"

        return await self._request(
            f"/sports/{sport_key}/events/{event_id}/odds",
            params,
        )


def parse_game_from_odds(game_data: dict[str, Any], sport_id: int) -> dict[str, Any]:
    """Parse game data from odds response."""
    return {
        "sport_id": sport_id,
        "external_game_id": game_data["id"],
        "home_team_name": game_data["home_team"],
        "away_team_name": game_data["away_team"],
        "start_time": datetime.fromisoformat(
            game_data["commence_time"].replace("Z", "+00:00")
        ),
    }


def parse_lines_from_odds(
    game_data: dict[str, Any],
    game_id: int,
    market_map: dict[str, int],
) -> list[dict[str, Any]]:
    """Parse betting lines from odds response."""
    lines = []
    now = datetime.now(timezone.utc)

    for bookmaker in game_data.get("bookmakers", []):
        sportsbook = bookmaker["key"]

        for market in bookmaker.get("markets", []):
            market_key = market["key"]
            market_type = MARKETS.get(market_key, market_key)
            market_id = market_map.get(market_type)

            if not market_id:
                continue

            for outcome in market.get("outcomes", []):
                line_data = {
                    "game_id": game_id,
                    "market_id": market_id,
                    "sportsbook": sportsbook,
                    "odds": outcome["price"],
                    "is_current": True,
                    "fetched_at": now,
                }

                # Determine side and line value
                if market_type == "moneyline":
                    line_data["side"] = (
                        "home" if outcome["name"] == game_data["home_team"] else "away"
                    )
                elif market_type == "spread":
                    line_data["side"] = (
                        "home" if outcome["name"] == game_data["home_team"] else "away"
                    )
                    line_data["line_value"] = outcome.get("point")
                elif market_type == "total":
                    line_data["side"] = outcome["name"].lower()  # over/under
                    line_data["line_value"] = outcome.get("point")

                lines.append(line_data)

    return lines


def parse_props_from_response(
    props_data: dict[str, Any],
    game_id: int,
    market_map: dict[str, int],
    player_map: dict[str, int],
) -> list[dict[str, Any]]:
    """Parse player props from response."""
    lines = []
    now = datetime.now(timezone.utc)

    for bookmaker in props_data.get("bookmakers", []):
        sportsbook = bookmaker["key"]

        for market in bookmaker.get("markets", []):
            market_key = market["key"]
            # Map prop market to stat type (e.g., player_points -> PTS)
            stat_type = market_key.replace("player_", "").upper()
            market_id = market_map.get(f"player_prop_{stat_type}")

            if not market_id:
                continue

            for outcome in market.get("outcomes", []):
                player_name = outcome.get("description", "")
                player_id = player_map.get(player_name)

                line_data = {
                    "game_id": game_id,
                    "market_id": market_id,
                    "player_id": player_id,
                    "sportsbook": sportsbook,
                    "side": outcome["name"].lower(),  # over/under
                    "line_value": outcome.get("point"),
                    "odds": outcome["price"],
                    "is_current": True,
                    "fetched_at": now,
                }

                lines.append(line_data)

    return lines
