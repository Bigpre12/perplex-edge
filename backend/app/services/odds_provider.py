"""Odds provider for fetching games, lines, and player props from external APIs."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes for normalized structures
# =============================================================================

class GameData:
    """Normalized game data structure."""
    
    def __init__(
        self,
        external_game_id: str,
        sport_key: str,
        home_team: str,
        away_team: str,
        start_time: datetime,
        status: str = "scheduled",
    ):
        self.external_game_id = external_game_id
        self.sport_key = sport_key
        self.home_team = home_team
        self.away_team = away_team
        self.start_time = start_time
        self.status = status

    def to_dict(self) -> dict[str, Any]:
        return {
            "external_game_id": self.external_game_id,
            "sport_key": self.sport_key,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "start_time": self.start_time,
            "status": self.status,
        }


class LineData:
    """Normalized betting line data structure."""
    
    def __init__(
        self,
        sportsbook: str,
        market_type: str,
        side: str,
        odds: float,
        line_value: Optional[float] = None,
        player_name: Optional[str] = None,
        stat_type: Optional[str] = None,
        fetched_at: Optional[datetime] = None,
    ):
        self.sportsbook = sportsbook
        self.market_type = market_type
        self.side = side
        self.odds = odds
        self.line_value = line_value
        self.player_name = player_name
        self.stat_type = stat_type
        self.fetched_at = fetched_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sportsbook": self.sportsbook,
            "market_type": self.market_type,
            "side": self.side,
            "odds": self.odds,
            "line_value": self.line_value,
            "player_name": self.player_name,
            "stat_type": self.stat_type,
            "fetched_at": self.fetched_at,
        }


class PropData:
    """Normalized player prop data structure."""
    
    def __init__(
        self,
        player_name: str,
        player_external_id: Optional[str],
        stat_type: str,
        sportsbook: str,
        line_value: float,
        over_odds: float,
        under_odds: float,
        fetched_at: Optional[datetime] = None,
    ):
        self.player_name = player_name
        self.player_external_id = player_external_id
        self.stat_type = stat_type
        self.sportsbook = sportsbook
        self.line_value = line_value
        self.over_odds = over_odds
        self.under_odds = under_odds
        self.fetched_at = fetched_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        return {
            "player_name": self.player_name,
            "player_external_id": self.player_external_id,
            "stat_type": self.stat_type,
            "sportsbook": self.sportsbook,
            "line_value": self.line_value,
            "over_odds": self.over_odds,
            "under_odds": self.under_odds,
            "fetched_at": self.fetched_at,
        }


# =============================================================================
# Abstract Base Class
# =============================================================================

class OddsProvider(ABC):
    """Abstract base class for odds providers."""
    
    @abstractmethod
    async def fetch_games(self, sport_key: str) -> list[GameData]:
        """
        Fetch upcoming games for a sport.
        
        Args:
            sport_key: The sport identifier (e.g., 'basketball_nba', 'americanfootball_nfl')
        
        Returns:
            List of normalized GameData objects
        """
        pass
    
    @abstractmethod
    async def fetch_main_lines(
        self,
        sport_key: str,
        external_game_id: str,
    ) -> list[LineData]:
        """
        Fetch main betting lines (spread, total, moneyline) for a game.
        
        Args:
            sport_key: The sport identifier
            external_game_id: The external game ID from the API
        
        Returns:
            List of normalized LineData objects
        """
        pass
    
    @abstractmethod
    async def fetch_player_props(
        self,
        sport_key: str,
        external_game_id: str,
        prop_types: Optional[list[str]] = None,
    ) -> list[PropData]:
        """
        Fetch player props for a game.
        
        Args:
            sport_key: The sport identifier
            external_game_id: The external game ID
            prop_types: List of prop types to fetch (e.g., ['PTS', 'REB', 'AST'])
        
        Returns:
            List of normalized PropData objects
        """
        pass
    
    @abstractmethod
    def normalize_game(self, raw_game: dict[str, Any]) -> GameData:
        """Convert raw API response to normalized GameData."""
        pass
    
    @abstractmethod
    def normalize_line(self, raw_line: dict[str, Any]) -> LineData:
        """Convert raw API response to normalized LineData."""
        pass


# =============================================================================
# Concrete Implementation
# =============================================================================

# Sport key mappings
SPORT_KEYS = {
    "NBA": "basketball_nba",
    "NFL": "americanfootball_nfl",
    "MLB": "baseball_mlb",
    "NHL": "icehockey_nhl",
    "NCAAB": "basketball_ncaab",
    "NCAAF": "americanfootball_ncaaf",
}

# Market type mappings from API to internal
MARKET_MAPPINGS = {
    "h2h": "moneyline",
    "spreads": "spread",
    "totals": "total",
}

# Prop type mappings from API to internal stat types
PROP_MAPPINGS = {
    "player_points": "PTS",
    "player_rebounds": "REB",
    "player_assists": "AST",
    "player_threes": "3PM",
    "player_points_rebounds_assists": "PRA",
    "player_steals": "STL",
    "player_blocks": "BLK",
    "player_turnovers": "TO",
    "player_double_double": "DD",
    "player_triple_double": "TD",
    # NFL props
    "player_pass_yds": "PASS_YDS",
    "player_pass_tds": "PASS_TDS",
    "player_rush_yds": "RUSH_YDS",
    "player_reception_yds": "REC_YDS",
    "player_receptions": "REC",
    # MLB props
    "batter_total_bases": "TB",
    "pitcher_strikeouts": "K",
    "batter_hits": "H",
    "batter_rbis": "RBI",
}


class XYZOddsProvider(OddsProvider):
    """
    Concrete implementation of OddsProvider.
    
    Uses The Odds API format for fetching games, lines, and props.
    Includes stub methods for testing without API calls.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_stubs: bool = False,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.odds_api_key
        self.base_url = base_url or settings.odds_api_base_url
        self.use_stubs = use_stubs
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "XYZOddsProvider":
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
        """Make an authenticated request to the API."""
        if not self.api_key:
            raise ValueError("ODDS_API_KEY not configured")
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        # Log API usage
        remaining = response.headers.get("x-requests-remaining", "unknown")
        used = response.headers.get("x-requests-used", "unknown")
        logger.info(f"Odds API: {used} used, {remaining} remaining")
        
        return response.json()
    
    # =========================================================================
    # Public API Methods
    # =========================================================================
    
    async def fetch_games(self, sport_key: str) -> list[GameData]:
        """Fetch upcoming games for a sport."""
        if self.use_stubs:
            raw_games = self._stub_games_response(sport_key)
        else:
            raw_games = await self._request(f"/sports/{sport_key}/odds", {
                "regions": "us",
                "markets": "h2h",
                "oddsFormat": "american",
            })
        
        return [self.normalize_game(game) for game in raw_games]
    
    async def fetch_main_lines(
        self,
        sport_key: str,
        external_game_id: str,
    ) -> list[LineData]:
        """Fetch spread, total, and moneyline for a specific game."""
        if self.use_stubs:
            raw_data = self._stub_lines_response(sport_key, external_game_id)
        else:
            raw_data = await self._request(
                f"/sports/{sport_key}/events/{external_game_id}/odds",
                {
                    "regions": "us",
                    "markets": "h2h,spreads,totals",
                    "oddsFormat": "american",
                },
            )
        
        return self._parse_main_lines(raw_data)
    
    async def fetch_player_props(
        self,
        sport_key: str,
        external_game_id: str,
        prop_types: Optional[list[str]] = None,
    ) -> list[PropData]:
        """Fetch player props for a game."""
        if self.use_stubs:
            raw_data = self._stub_props_response(sport_key, external_game_id, prop_types)
        else:
            # Determine which prop markets to request
            if prop_types:
                markets = ",".join(
                    k for k, v in PROP_MAPPINGS.items() if v in prop_types
                )
            else:
                # Default props based on sport
                if "basketball" in sport_key:
                    markets = "player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists"
                elif "football" in sport_key:
                    markets = "player_pass_yds,player_rush_yds,player_reception_yds,player_receptions"
                elif "baseball" in sport_key:
                    markets = "batter_total_bases,pitcher_strikeouts,batter_hits"
                else:
                    markets = "player_points"
            
            raw_data = await self._request(
                f"/sports/{sport_key}/events/{external_game_id}/odds",
                {
                    "regions": "us",
                    "markets": markets,
                    "oddsFormat": "american",
                },
            )
        
        return self._parse_player_props(raw_data)
    
    # =========================================================================
    # Normalization Methods
    # =========================================================================
    
    def normalize_game(self, raw_game: dict[str, Any]) -> GameData:
        """Convert raw API game data to normalized GameData."""
        start_time = datetime.fromisoformat(
            raw_game["commence_time"].replace("Z", "+00:00")
        )
        
        return GameData(
            external_game_id=raw_game["id"],
            sport_key=raw_game.get("sport_key", ""),
            home_team=raw_game["home_team"],
            away_team=raw_game["away_team"],
            start_time=start_time,
            status="scheduled",
        )
    
    def normalize_line(self, raw_line: dict[str, Any]) -> LineData:
        """Convert raw API line data to normalized LineData."""
        return LineData(
            sportsbook=raw_line.get("sportsbook", ""),
            market_type=raw_line.get("market_type", ""),
            side=raw_line.get("side", ""),
            odds=raw_line.get("odds", 0),
            line_value=raw_line.get("line_value"),
        )
    
    def _parse_main_lines(self, raw_data: dict[str, Any]) -> list[LineData]:
        """Parse main betting lines from API response."""
        lines = []
        now = datetime.now(timezone.utc)
        home_team = raw_data.get("home_team", "")
        
        for bookmaker in raw_data.get("bookmakers", []):
            sportsbook = bookmaker["key"]
            
            for market in bookmaker.get("markets", []):
                market_key = market["key"]
                market_type = MARKET_MAPPINGS.get(market_key, market_key)
                
                for outcome in market.get("outcomes", []):
                    # Determine side
                    if market_type == "total":
                        side = outcome["name"].lower()  # over/under
                    else:
                        side = "home" if outcome["name"] == home_team else "away"
                    
                    lines.append(LineData(
                        sportsbook=sportsbook,
                        market_type=market_type,
                        side=side,
                        odds=outcome["price"],
                        line_value=outcome.get("point"),
                        fetched_at=now,
                    ))
        
        return lines
    
    def _parse_player_props(self, raw_data: dict[str, Any]) -> list[PropData]:
        """Parse player props from API response."""
        props = []
        now = datetime.now(timezone.utc)
        
        for bookmaker in raw_data.get("bookmakers", []):
            sportsbook = bookmaker["key"]
            
            for market in bookmaker.get("markets", []):
                market_key = market["key"]
                stat_type = PROP_MAPPINGS.get(market_key, market_key.upper())
                
                # Group outcomes by player
                player_outcomes: dict[str, dict] = {}
                
                for outcome in market.get("outcomes", []):
                    player_name = outcome.get("description", "")
                    side = outcome["name"].lower()
                    
                    if player_name not in player_outcomes:
                        player_outcomes[player_name] = {
                            "player_name": player_name,
                            "line_value": outcome.get("point"),
                        }
                    
                    if side == "over":
                        player_outcomes[player_name]["over_odds"] = outcome["price"]
                    else:
                        player_outcomes[player_name]["under_odds"] = outcome["price"]
                
                # Create PropData for each player
                for player_data in player_outcomes.values():
                    if "over_odds" in player_data and "under_odds" in player_data:
                        props.append(PropData(
                            player_name=player_data["player_name"],
                            player_external_id=None,
                            stat_type=stat_type,
                            sportsbook=sportsbook,
                            line_value=player_data["line_value"],
                            over_odds=player_data["over_odds"],
                            under_odds=player_data["under_odds"],
                            fetched_at=now,
                        ))
        
        return props
    
    # =========================================================================
    # Stub Methods for Testing
    # =========================================================================
    
    def _stub_games_response(self, sport_key: str) -> list[dict[str, Any]]:
        """Return realistic stub game data for testing."""
        if "basketball" in sport_key:
            return [
                {
                    "id": "e912304a8b234c56d789ef0123456789",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T00:10:00Z",
                    "home_team": "Los Angeles Lakers",
                    "away_team": "Golden State Warriors",
                    "bookmakers": [],
                },
                {
                    "id": "f823415b9c345d67e890fa1234567890",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T00:40:00Z",
                    "home_team": "Boston Celtics",
                    "away_team": "Miami Heat",
                    "bookmakers": [],
                },
                {
                    "id": "a734526c0d456e78f901ab2345678901",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T02:10:00Z",
                    "home_team": "Phoenix Suns",
                    "away_team": "Denver Nuggets",
                    "bookmakers": [],
                },
            ]
        elif "football" in sport_key:
            return [
                {
                    "id": "nfl_game_001",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": "2026-01-28T18:00:00Z",
                    "home_team": "Kansas City Chiefs",
                    "away_team": "Buffalo Bills",
                    "bookmakers": [],
                },
            ]
        else:
            return []
    
    def _stub_lines_response(
        self,
        sport_key: str,
        external_game_id: str,
    ) -> dict[str, Any]:
        """Return realistic stub betting lines for testing."""
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": "Los Angeles Lakers",
            "away_team": "Golden State Warriors",
            "commence_time": "2026-01-28T00:10:00Z",
            "bookmakers": [
                {
                    "key": "draftkings",
                    "title": "DraftKings",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": -150},
                                {"name": "Golden State Warriors", "price": 130},
                            ],
                        },
                        {
                            "key": "spreads",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": -110, "point": -3.5},
                                {"name": "Golden State Warriors", "price": -110, "point": 3.5},
                            ],
                        },
                        {
                            "key": "totals",
                            "outcomes": [
                                {"name": "Over", "price": -110, "point": 228.5},
                                {"name": "Under", "price": -110, "point": 228.5},
                            ],
                        },
                    ],
                },
                {
                    "key": "fanduel",
                    "title": "FanDuel",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": -145},
                                {"name": "Golden State Warriors", "price": 125},
                            ],
                        },
                        {
                            "key": "spreads",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": -108, "point": -3.5},
                                {"name": "Golden State Warriors", "price": -112, "point": 3.5},
                            ],
                        },
                        {
                            "key": "totals",
                            "outcomes": [
                                {"name": "Over", "price": -108, "point": 229.0},
                                {"name": "Under", "price": -112, "point": 229.0},
                            ],
                        },
                    ],
                },
                {
                    "key": "betmgm",
                    "title": "BetMGM",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": -155},
                                {"name": "Golden State Warriors", "price": 135},
                            ],
                        },
                        {
                            "key": "spreads",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": -110, "point": -4.0},
                                {"name": "Golden State Warriors", "price": -110, "point": 4.0},
                            ],
                        },
                        {
                            "key": "totals",
                            "outcomes": [
                                {"name": "Over", "price": -105, "point": 228.0},
                                {"name": "Under", "price": -115, "point": 228.0},
                            ],
                        },
                    ],
                },
            ],
        }
    
    def _stub_props_response(
        self,
        sport_key: str,
        external_game_id: str,
        prop_types: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Return realistic stub player props for testing."""
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": "Los Angeles Lakers",
            "away_team": "Golden State Warriors",
            "commence_time": "2026-01-28T00:10:00Z",
            "bookmakers": [
                {
                    "key": "draftkings",
                    "title": "DraftKings",
                    "markets": [
                        {
                            "key": "player_points",
                            "outcomes": [
                                {"name": "Over", "description": "LeBron James", "price": -115, "point": 26.5},
                                {"name": "Under", "description": "LeBron James", "price": -105, "point": 26.5},
                                {"name": "Over", "description": "Stephen Curry", "price": -110, "point": 28.5},
                                {"name": "Under", "description": "Stephen Curry", "price": -110, "point": 28.5},
                                {"name": "Over", "description": "Anthony Davis", "price": -120, "point": 24.5},
                                {"name": "Under", "description": "Anthony Davis", "price": 100, "point": 24.5},
                            ],
                        },
                        {
                            "key": "player_rebounds",
                            "outcomes": [
                                {"name": "Over", "description": "LeBron James", "price": -110, "point": 7.5},
                                {"name": "Under", "description": "LeBron James", "price": -110, "point": 7.5},
                                {"name": "Over", "description": "Anthony Davis", "price": -130, "point": 11.5},
                                {"name": "Under", "description": "Anthony Davis", "price": 110, "point": 11.5},
                                {"name": "Over", "description": "Draymond Green", "price": -105, "point": 6.5},
                                {"name": "Under", "description": "Draymond Green", "price": -115, "point": 6.5},
                            ],
                        },
                        {
                            "key": "player_assists",
                            "outcomes": [
                                {"name": "Over", "description": "LeBron James", "price": -125, "point": 8.5},
                                {"name": "Under", "description": "LeBron James", "price": 105, "point": 8.5},
                                {"name": "Over", "description": "Stephen Curry", "price": -110, "point": 5.5},
                                {"name": "Under", "description": "Stephen Curry", "price": -110, "point": 5.5},
                            ],
                        },
                        {
                            "key": "player_threes",
                            "outcomes": [
                                {"name": "Over", "description": "Stephen Curry", "price": -115, "point": 4.5},
                                {"name": "Under", "description": "Stephen Curry", "price": -105, "point": 4.5},
                                {"name": "Over", "description": "Klay Thompson", "price": -110, "point": 3.5},
                                {"name": "Under", "description": "Klay Thompson", "price": -110, "point": 3.5},
                            ],
                        },
                        {
                            "key": "player_points_rebounds_assists",
                            "outcomes": [
                                {"name": "Over", "description": "LeBron James", "price": -110, "point": 42.5},
                                {"name": "Under", "description": "LeBron James", "price": -110, "point": 42.5},
                                {"name": "Over", "description": "Stephen Curry", "price": -115, "point": 38.5},
                                {"name": "Under", "description": "Stephen Curry", "price": -105, "point": 38.5},
                            ],
                        },
                    ],
                },
                {
                    "key": "fanduel",
                    "title": "FanDuel",
                    "markets": [
                        {
                            "key": "player_points",
                            "outcomes": [
                                {"name": "Over", "description": "LeBron James", "price": -118, "point": 27.5},
                                {"name": "Under", "description": "LeBron James", "price": -102, "point": 27.5},
                                {"name": "Over", "description": "Stephen Curry", "price": -108, "point": 29.5},
                                {"name": "Under", "description": "Stephen Curry", "price": -112, "point": 29.5},
                            ],
                        },
                        {
                            "key": "player_rebounds",
                            "outcomes": [
                                {"name": "Over", "description": "Anthony Davis", "price": -125, "point": 12.5},
                                {"name": "Under", "description": "Anthony Davis", "price": 105, "point": 12.5},
                            ],
                        },
                    ],
                },
            ],
        }
