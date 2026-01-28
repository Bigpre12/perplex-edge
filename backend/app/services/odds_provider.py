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
    "player_points_rebounds": "PR",
    "player_points_assists": "PA",
    "player_rebounds_assists": "RA",
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
                    markets = "player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists,player_points_rebounds,player_points_assists,player_rebounds_assists"
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
        """Return realistic stub game data for testing - January 28, 2026 actual slate."""
        if "basketball" in sport_key:
            # Use January 28 UTC times so picks generator finds them for "today"
            # (Real 7PM ET = midnight UTC next day, but we use 23:00 UTC same day for testing)
            return [
                # Game 1: Bulls @ Pacers (7:00 PM ET)
                {
                    "id": "game_chi_ind_20260128",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T19:00:00Z",
                    "home_team": "Indiana Pacers",
                    "away_team": "Chicago Bulls",
                    "bookmakers": [],
                },
                # Game 2: Lakers @ Cavaliers (7:00 PM ET)
                {
                    "id": "game_lal_cle_20260128",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T19:00:00Z",
                    "home_team": "Cleveland Cavaliers",
                    "away_team": "Los Angeles Lakers",
                    "bookmakers": [],
                },
                # Game 3: Hawks @ Celtics (7:30 PM ET)
                {
                    "id": "game_atl_bos_20260128",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T19:30:00Z",
                    "home_team": "Boston Celtics",
                    "away_team": "Atlanta Hawks",
                    "bookmakers": [],
                },
                # Game 4: Magic @ Heat (7:30 PM ET)
                {
                    "id": "game_orl_mia_20260128",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T19:30:00Z",
                    "home_team": "Miami Heat",
                    "away_team": "Orlando Magic",
                    "bookmakers": [],
                },
                # Game 5: Knicks @ Raptors (7:30 PM ET)
                {
                    "id": "game_nyk_tor_20260128",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T19:30:00Z",
                    "home_team": "Toronto Raptors",
                    "away_team": "New York Knicks",
                    "bookmakers": [],
                },
                # Game 6: Hornets @ Grizzlies (8:00 PM ET)
                {
                    "id": "game_cha_mem_20260128",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T20:00:00Z",
                    "home_team": "Memphis Grizzlies",
                    "away_team": "Charlotte Hornets",
                    "bookmakers": [],
                },
                # Game 7: Timberwolves @ Mavericks (8:30 PM ET)
                {
                    "id": "game_min_dal_20260128",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T20:30:00Z",
                    "home_team": "Dallas Mavericks",
                    "away_team": "Minnesota Timberwolves",
                    "bookmakers": [],
                },
                # Game 8: Warriors @ Jazz (9:00 PM ET)
                {
                    "id": "game_gsw_uta_20260128",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": "2026-01-28T21:00:00Z",
                    "home_team": "Utah Jazz",
                    "away_team": "Golden State Warriors",
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
        """Return realistic stub betting lines for testing - January 28, 2026 slate."""
        # Game-specific lines based on actual January 28, 2026 slate
        game_lines = {
            "game_chi_ind_20260128": {
                "home_team": "Indiana Pacers", "away_team": "Chicago Bulls",
                "home_spread": 1.5, "total": 224.5, "home_ml": 105, "away_ml": -125,
            },
            "game_lal_cle_20260128": {
                "home_team": "Cleveland Cavaliers", "away_team": "Los Angeles Lakers",
                "home_spread": -3.5, "total": 231.5, "home_ml": -160, "away_ml": 140,
            },
            "game_atl_bos_20260128": {
                "home_team": "Boston Celtics", "away_team": "Atlanta Hawks",
                "home_spread": -6.5, "total": 226.0, "home_ml": -275, "away_ml": 225,
            },
            "game_orl_mia_20260128": {
                "home_team": "Miami Heat", "away_team": "Orlando Magic",
                "home_spread": -3.0, "total": 212.5, "home_ml": -150, "away_ml": 130,
            },
            "game_nyk_tor_20260128": {
                "home_team": "Toronto Raptors", "away_team": "New York Knicks",
                "home_spread": 1.5, "total": 228.0, "home_ml": 105, "away_ml": -125,
            },
            "game_cha_mem_20260128": {
                "home_team": "Memphis Grizzlies", "away_team": "Charlotte Hornets",
                "home_spread": 2.0, "total": 218.5, "home_ml": 115, "away_ml": -135,
            },
            "game_min_dal_20260128": {
                "home_team": "Dallas Mavericks", "away_team": "Minnesota Timberwolves",
                "home_spread": 6.5, "total": 224.0, "home_ml": 240, "away_ml": -300,
            },
            "game_gsw_uta_20260128": {
                "home_team": "Utah Jazz", "away_team": "Golden State Warriors",
                "home_spread": 10.5, "total": 232.0, "home_ml": 420, "away_ml": -550,
            },
        }
        
        # Get game-specific lines or use defaults
        lines = game_lines.get(external_game_id, {
            "home_team": "Home Team", "away_team": "Away Team",
            "home_spread": -3.0, "total": 220.0, "home_ml": -150, "away_ml": 130,
        })
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": lines["home_team"],
            "away_team": lines["away_team"],
            "commence_time": "2026-01-28T19:00:00Z",
            "bookmakers": [
                {
                    "key": "draftkings",
                    "title": "DraftKings",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": lines["home_team"], "price": lines["home_ml"]},
                                {"name": lines["away_team"], "price": lines["away_ml"]},
                            ],
                        },
                        {
                            "key": "spreads",
                            "outcomes": [
                                {"name": lines["home_team"], "price": -110, "point": lines["home_spread"]},
                                {"name": lines["away_team"], "price": -110, "point": -lines["home_spread"]},
                            ],
                        },
                        {
                            "key": "totals",
                            "outcomes": [
                                {"name": "Over", "price": -110, "point": lines["total"]},
                                {"name": "Under", "price": -110, "point": lines["total"]},
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
                                {"name": lines["home_team"], "price": lines["home_ml"] - 5},
                                {"name": lines["away_team"], "price": lines["away_ml"] + 5},
                            ],
                        },
                        {
                            "key": "spreads",
                            "outcomes": [
                                {"name": lines["home_team"], "price": -108, "point": lines["home_spread"]},
                                {"name": lines["away_team"], "price": -112, "point": -lines["home_spread"]},
                            ],
                        },
                        {
                            "key": "totals",
                            "outcomes": [
                                {"name": "Over", "price": -108, "point": lines["total"] + 0.5},
                                {"name": "Under", "price": -112, "point": lines["total"] + 0.5},
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
                                {"name": lines["home_team"], "price": lines["home_ml"] + 5},
                                {"name": lines["away_team"], "price": lines["away_ml"] - 5},
                            ],
                        },
                        {
                            "key": "spreads",
                            "outcomes": [
                                {"name": lines["home_team"], "price": -110, "point": lines["home_spread"] - 0.5},
                                {"name": lines["away_team"], "price": -110, "point": -(lines["home_spread"] - 0.5)},
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
        """Return realistic stub player props for January 28, 2026 games."""
        
        # Game: Lakers @ Cavaliers (Luka-led Lakers vs Mitchell-led Cavs)
        if external_game_id == "game_lal_cle_20260128":
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Cleveland Cavaliers",
                "away_team": "Los Angeles Lakers",
                "commence_time": "2026-01-28T19:00:00Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "player_points",
                                "outcomes": [
                                    {"name": "Over", "description": "Luka Doncic", "price": -115, "point": 32.5},
                                    {"name": "Under", "description": "Luka Doncic", "price": -105, "point": 32.5},
                                    {"name": "Over", "description": "Donovan Mitchell", "price": -110, "point": 26.5},
                                    {"name": "Under", "description": "Donovan Mitchell", "price": -110, "point": 26.5},
                                    {"name": "Over", "description": "LeBron James", "price": -108, "point": 24.5},
                                    {"name": "Under", "description": "LeBron James", "price": -112, "point": 24.5},
                                    {"name": "Over", "description": "Darius Garland", "price": -110, "point": 19.5},
                                    {"name": "Under", "description": "Darius Garland", "price": -110, "point": 19.5},
                                ],
                            },
                            {
                                "key": "player_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Jarrett Allen", "price": -125, "point": 10.5},
                                    {"name": "Under", "description": "Jarrett Allen", "price": 105, "point": 10.5},
                                    {"name": "Over", "description": "Deandre Ayton", "price": -110, "point": 10.5},
                                    {"name": "Under", "description": "Deandre Ayton", "price": -110, "point": 10.5},
                                    {"name": "Over", "description": "Evan Mobley", "price": -115, "point": 8.5},
                                    {"name": "Under", "description": "Evan Mobley", "price": -105, "point": 8.5},
                                ],
                            },
                            {
                                "key": "player_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Luka Doncic", "price": -120, "point": 9.5},
                                    {"name": "Under", "description": "Luka Doncic", "price": 100, "point": 9.5},
                                    {"name": "Over", "description": "Darius Garland", "price": -115, "point": 6.5},
                                    {"name": "Under", "description": "Darius Garland", "price": -105, "point": 6.5},
                                ],
                            },
                            # Combination props
                            {
                                "key": "player_points_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Luka Doncic", "price": -110, "point": 50.5},
                                    {"name": "Under", "description": "Luka Doncic", "price": -110, "point": 50.5},
                                    {"name": "Over", "description": "Donovan Mitchell", "price": -115, "point": 38.5},
                                    {"name": "Under", "description": "Donovan Mitchell", "price": -105, "point": 38.5},
                                    {"name": "Over", "description": "LeBron James", "price": -110, "point": 40.5},
                                    {"name": "Under", "description": "LeBron James", "price": -110, "point": 40.5},
                                ],
                            },
                            {
                                "key": "player_points_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Luka Doncic", "price": -108, "point": 40.5},
                                    {"name": "Under", "description": "Luka Doncic", "price": -112, "point": 40.5},
                                    {"name": "Over", "description": "Donovan Mitchell", "price": -110, "point": 31.5},
                                    {"name": "Under", "description": "Donovan Mitchell", "price": -110, "point": 31.5},
                                ],
                            },
                            {
                                "key": "player_points_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Luka Doncic", "price": -115, "point": 42.5},
                                    {"name": "Under", "description": "Luka Doncic", "price": -105, "point": 42.5},
                                    {"name": "Over", "description": "Darius Garland", "price": -110, "point": 26.5},
                                    {"name": "Under", "description": "Darius Garland", "price": -110, "point": 26.5},
                                ],
                            },
                            {
                                "key": "player_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Luka Doncic", "price": -110, "point": 17.5},
                                    {"name": "Under", "description": "Luka Doncic", "price": -110, "point": 17.5},
                                    {"name": "Over", "description": "Darius Garland", "price": -108, "point": 10.5},
                                    {"name": "Under", "description": "Darius Garland", "price": -112, "point": 10.5},
                                ],
                            },
                            # Defensive/misc props
                            {
                                "key": "player_steals",
                                "outcomes": [
                                    {"name": "Over", "description": "Luka Doncic", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Luka Doncic", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "LeBron James", "price": -110, "point": 1.5},
                                    {"name": "Under", "description": "LeBron James", "price": -110, "point": 1.5},
                                    {"name": "Over", "description": "Donovan Mitchell", "price": -108, "point": 1.5},
                                    {"name": "Under", "description": "Donovan Mitchell", "price": -112, "point": 1.5},
                                ],
                            },
                            {
                                "key": "player_blocks",
                                "outcomes": [
                                    {"name": "Over", "description": "Jarrett Allen", "price": -120, "point": 1.5},
                                    {"name": "Under", "description": "Jarrett Allen", "price": 100, "point": 1.5},
                                    {"name": "Over", "description": "Evan Mobley", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Evan Mobley", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Deandre Ayton", "price": -110, "point": 0.5},
                                    {"name": "Under", "description": "Deandre Ayton", "price": -110, "point": 0.5},
                                ],
                            },
                            {
                                "key": "player_turnovers",
                                "outcomes": [
                                    {"name": "Over", "description": "Luka Doncic", "price": -115, "point": 4.5},
                                    {"name": "Under", "description": "Luka Doncic", "price": -105, "point": 4.5},
                                    {"name": "Over", "description": "LeBron James", "price": -110, "point": 3.5},
                                    {"name": "Under", "description": "LeBron James", "price": -110, "point": 3.5},
                                    {"name": "Over", "description": "Darius Garland", "price": -108, "point": 2.5},
                                    {"name": "Under", "description": "Darius Garland", "price": -112, "point": 2.5},
                                ],
                            },
                        ],
                    },
                ],
            }
        
        # Game: Hawks @ Celtics (CJ McCollum/Porzingis Hawks vs Tatum-less Celtics)
        elif external_game_id == "game_atl_bos_20260128":
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Boston Celtics",
                "away_team": "Atlanta Hawks",
                "commence_time": "2026-01-28T19:30:00Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "player_points",
                                "outcomes": [
                                    {"name": "Over", "description": "Jaylen Brown", "price": -115, "point": 27.5},
                                    {"name": "Under", "description": "Jaylen Brown", "price": -105, "point": 27.5},
                                    {"name": "Over", "description": "CJ McCollum", "price": -110, "point": 22.5},
                                    {"name": "Under", "description": "CJ McCollum", "price": -110, "point": 22.5},
                                    {"name": "Over", "description": "Kristaps Porzingis", "price": -108, "point": 19.5},
                                    {"name": "Under", "description": "Kristaps Porzingis", "price": -112, "point": 19.5},
                                    {"name": "Over", "description": "Anfernee Simons", "price": -110, "point": 18.5},
                                    {"name": "Under", "description": "Anfernee Simons", "price": -110, "point": 18.5},
                                ],
                            },
                            {
                                "key": "player_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Kristaps Porzingis", "price": -115, "point": 7.5},
                                    {"name": "Under", "description": "Kristaps Porzingis", "price": -105, "point": 7.5},
                                    {"name": "Over", "description": "Jalen Johnson", "price": -110, "point": 6.5},
                                    {"name": "Under", "description": "Jalen Johnson", "price": -110, "point": 6.5},
                                ],
                            },
                            # Combination props
                            {
                                "key": "player_points_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Jaylen Brown", "price": -110, "point": 39.5},
                                    {"name": "Under", "description": "Jaylen Brown", "price": -110, "point": 39.5},
                                    {"name": "Over", "description": "CJ McCollum", "price": -108, "point": 32.5},
                                    {"name": "Under", "description": "CJ McCollum", "price": -112, "point": 32.5},
                                    {"name": "Over", "description": "Kristaps Porzingis", "price": -110, "point": 31.5},
                                    {"name": "Under", "description": "Kristaps Porzingis", "price": -110, "point": 31.5},
                                ],
                            },
                            {
                                "key": "player_points_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Jaylen Brown", "price": -115, "point": 33.5},
                                    {"name": "Under", "description": "Jaylen Brown", "price": -105, "point": 33.5},
                                    {"name": "Over", "description": "Kristaps Porzingis", "price": -110, "point": 27.5},
                                    {"name": "Under", "description": "Kristaps Porzingis", "price": -110, "point": 27.5},
                                ],
                            },
                            {
                                "key": "player_points_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "CJ McCollum", "price": -110, "point": 28.5},
                                    {"name": "Under", "description": "CJ McCollum", "price": -110, "point": 28.5},
                                    {"name": "Over", "description": "Anfernee Simons", "price": -108, "point": 24.5},
                                    {"name": "Under", "description": "Anfernee Simons", "price": -112, "point": 24.5},
                                ],
                            },
                            # Defensive/misc props
                            {
                                "key": "player_steals",
                                "outcomes": [
                                    {"name": "Over", "description": "Jaylen Brown", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Jaylen Brown", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "CJ McCollum", "price": -110, "point": 1.5},
                                    {"name": "Under", "description": "CJ McCollum", "price": -110, "point": 1.5},
                                ],
                            },
                            {
                                "key": "player_blocks",
                                "outcomes": [
                                    {"name": "Over", "description": "Kristaps Porzingis", "price": -120, "point": 1.5},
                                    {"name": "Under", "description": "Kristaps Porzingis", "price": 100, "point": 1.5},
                                    {"name": "Over", "description": "Jalen Johnson", "price": -110, "point": 0.5},
                                    {"name": "Under", "description": "Jalen Johnson", "price": -110, "point": 0.5},
                                ],
                            },
                            {
                                "key": "player_turnovers",
                                "outcomes": [
                                    {"name": "Over", "description": "Jaylen Brown", "price": -110, "point": 2.5},
                                    {"name": "Under", "description": "Jaylen Brown", "price": -110, "point": 2.5},
                                    {"name": "Over", "description": "CJ McCollum", "price": -108, "point": 2.5},
                                    {"name": "Under", "description": "CJ McCollum", "price": -112, "point": 2.5},
                                ],
                            },
                        ],
                    },
                ],
            }
        
        # Game: Magic @ Heat (Bane/Banchero Magic vs Bam/Herro/Wiggins Heat)
        elif external_game_id == "game_orl_mia_20260128":
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Miami Heat",
                "away_team": "Orlando Magic",
                "commence_time": "2026-01-28T19:30:00Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "player_points",
                                "outcomes": [
                                    {"name": "Over", "description": "Paolo Banchero", "price": -115, "point": 24.5},
                                    {"name": "Under", "description": "Paolo Banchero", "price": -105, "point": 24.5},
                                    {"name": "Over", "description": "Tyler Herro", "price": -110, "point": 22.5},
                                    {"name": "Under", "description": "Tyler Herro", "price": -110, "point": 22.5},
                                    {"name": "Over", "description": "Desmond Bane", "price": -108, "point": 20.5},
                                    {"name": "Under", "description": "Desmond Bane", "price": -112, "point": 20.5},
                                    {"name": "Over", "description": "Andrew Wiggins", "price": -110, "point": 17.5},
                                    {"name": "Under", "description": "Andrew Wiggins", "price": -110, "point": 17.5},
                                ],
                            },
                            {
                                "key": "player_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Bam Adebayo", "price": -125, "point": 10.5},
                                    {"name": "Under", "description": "Bam Adebayo", "price": 105, "point": 10.5},
                                    {"name": "Over", "description": "Franz Wagner", "price": -110, "point": 5.5},
                                    {"name": "Under", "description": "Franz Wagner", "price": -110, "point": 5.5},
                                ],
                            },
                            # Combination props
                            {
                                "key": "player_points_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Paolo Banchero", "price": -110, "point": 38.5},
                                    {"name": "Under", "description": "Paolo Banchero", "price": -110, "point": 38.5},
                                    {"name": "Over", "description": "Bam Adebayo", "price": -115, "point": 32.5},
                                    {"name": "Under", "description": "Bam Adebayo", "price": -105, "point": 32.5},
                                    {"name": "Over", "description": "Tyler Herro", "price": -108, "point": 32.5},
                                    {"name": "Under", "description": "Tyler Herro", "price": -112, "point": 32.5},
                                ],
                            },
                            {
                                "key": "player_points_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Paolo Banchero", "price": -110, "point": 32.5},
                                    {"name": "Under", "description": "Paolo Banchero", "price": -110, "point": 32.5},
                                    {"name": "Over", "description": "Bam Adebayo", "price": -115, "point": 28.5},
                                    {"name": "Under", "description": "Bam Adebayo", "price": -105, "point": 28.5},
                                ],
                            },
                            {
                                "key": "player_points_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Tyler Herro", "price": -110, "point": 28.5},
                                    {"name": "Under", "description": "Tyler Herro", "price": -110, "point": 28.5},
                                    {"name": "Over", "description": "Desmond Bane", "price": -108, "point": 26.5},
                                    {"name": "Under", "description": "Desmond Bane", "price": -112, "point": 26.5},
                                ],
                            },
                            # Defensive/misc props
                            {
                                "key": "player_steals",
                                "outcomes": [
                                    {"name": "Over", "description": "Bam Adebayo", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Bam Adebayo", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Paolo Banchero", "price": -110, "point": 0.5},
                                    {"name": "Under", "description": "Paolo Banchero", "price": -110, "point": 0.5},
                                ],
                            },
                            {
                                "key": "player_blocks",
                                "outcomes": [
                                    {"name": "Over", "description": "Bam Adebayo", "price": -120, "point": 1.5},
                                    {"name": "Under", "description": "Bam Adebayo", "price": 100, "point": 1.5},
                                    {"name": "Over", "description": "Franz Wagner", "price": -110, "point": 0.5},
                                    {"name": "Under", "description": "Franz Wagner", "price": -110, "point": 0.5},
                                ],
                            },
                            {
                                "key": "player_turnovers",
                                "outcomes": [
                                    {"name": "Over", "description": "Tyler Herro", "price": -110, "point": 2.5},
                                    {"name": "Under", "description": "Tyler Herro", "price": -110, "point": 2.5},
                                    {"name": "Over", "description": "Paolo Banchero", "price": -108, "point": 3.5},
                                    {"name": "Under", "description": "Paolo Banchero", "price": -112, "point": 3.5},
                                ],
                            },
                        ],
                    },
                ],
            }
        
        # Game: Knicks @ Raptors (KAT/Brunson/Bridges Knicks vs Barnes/Ingram Raptors)
        elif external_game_id == "game_nyk_tor_20260128":
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Toronto Raptors",
                "away_team": "New York Knicks",
                "commence_time": "2026-01-28T19:30:00Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "player_points",
                                "outcomes": [
                                    {"name": "Over", "description": "Jalen Brunson", "price": -115, "point": 26.5},
                                    {"name": "Under", "description": "Jalen Brunson", "price": -105, "point": 26.5},
                                    {"name": "Over", "description": "Scottie Barnes", "price": -110, "point": 22.5},
                                    {"name": "Under", "description": "Scottie Barnes", "price": -110, "point": 22.5},
                                    {"name": "Over", "description": "Brandon Ingram", "price": -108, "point": 21.5},
                                    {"name": "Under", "description": "Brandon Ingram", "price": -112, "point": 21.5},
                                    {"name": "Over", "description": "Karl-Anthony Towns", "price": -110, "point": 24.5},
                                    {"name": "Under", "description": "Karl-Anthony Towns", "price": -110, "point": 24.5},
                                ],
                            },
                            {
                                "key": "player_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Karl-Anthony Towns", "price": -120, "point": 11.5},
                                    {"name": "Under", "description": "Karl-Anthony Towns", "price": 100, "point": 11.5},
                                    {"name": "Over", "description": "Jakob Poeltl", "price": -115, "point": 9.5},
                                    {"name": "Under", "description": "Jakob Poeltl", "price": -105, "point": 9.5},
                                ],
                            },
                            # Combination props
                            {
                                "key": "player_points_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Jalen Brunson", "price": -110, "point": 36.5},
                                    {"name": "Under", "description": "Jalen Brunson", "price": -110, "point": 36.5},
                                    {"name": "Over", "description": "Karl-Anthony Towns", "price": -115, "point": 42.5},
                                    {"name": "Under", "description": "Karl-Anthony Towns", "price": -105, "point": 42.5},
                                    {"name": "Over", "description": "Scottie Barnes", "price": -108, "point": 35.5},
                                    {"name": "Under", "description": "Scottie Barnes", "price": -112, "point": 35.5},
                                ],
                            },
                            {
                                "key": "player_points_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Karl-Anthony Towns", "price": -110, "point": 36.5},
                                    {"name": "Under", "description": "Karl-Anthony Towns", "price": -110, "point": 36.5},
                                    {"name": "Over", "description": "Scottie Barnes", "price": -115, "point": 29.5},
                                    {"name": "Under", "description": "Scottie Barnes", "price": -105, "point": 29.5},
                                ],
                            },
                            {
                                "key": "player_points_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Jalen Brunson", "price": -115, "point": 33.5},
                                    {"name": "Under", "description": "Jalen Brunson", "price": -105, "point": 33.5},
                                    {"name": "Over", "description": "Brandon Ingram", "price": -110, "point": 27.5},
                                    {"name": "Under", "description": "Brandon Ingram", "price": -110, "point": 27.5},
                                ],
                            },
                            # Defensive/misc props
                            {
                                "key": "player_steals",
                                "outcomes": [
                                    {"name": "Over", "description": "Scottie Barnes", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Scottie Barnes", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Jalen Brunson", "price": -110, "point": 0.5},
                                    {"name": "Under", "description": "Jalen Brunson", "price": -110, "point": 0.5},
                                ],
                            },
                            {
                                "key": "player_blocks",
                                "outcomes": [
                                    {"name": "Over", "description": "Karl-Anthony Towns", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Karl-Anthony Towns", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Jakob Poeltl", "price": -120, "point": 1.5},
                                    {"name": "Under", "description": "Jakob Poeltl", "price": 100, "point": 1.5},
                                ],
                            },
                            {
                                "key": "player_turnovers",
                                "outcomes": [
                                    {"name": "Over", "description": "Jalen Brunson", "price": -110, "point": 2.5},
                                    {"name": "Under", "description": "Jalen Brunson", "price": -110, "point": 2.5},
                                    {"name": "Over", "description": "Karl-Anthony Towns", "price": -108, "point": 2.5},
                                    {"name": "Under", "description": "Karl-Anthony Towns", "price": -112, "point": 2.5},
                                ],
                            },
                        ],
                    },
                ],
            }
        
        # Game: Timberwolves @ Mavericks (Edwards/Randle Wolves vs AD/Klay Mavs)
        elif external_game_id == "game_min_dal_20260128":
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Dallas Mavericks",
                "away_team": "Minnesota Timberwolves",
                "commence_time": "2026-01-28T20:30:00Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "player_points",
                                "outcomes": [
                                    {"name": "Over", "description": "Anthony Edwards", "price": -115, "point": 28.5},
                                    {"name": "Under", "description": "Anthony Edwards", "price": -105, "point": 28.5},
                                    {"name": "Over", "description": "Anthony Davis", "price": -120, "point": 25.5},
                                    {"name": "Under", "description": "Anthony Davis", "price": 100, "point": 25.5},
                                    {"name": "Over", "description": "Julius Randle", "price": -110, "point": 21.5},
                                    {"name": "Under", "description": "Julius Randle", "price": -110, "point": 21.5},
                                    {"name": "Over", "description": "Klay Thompson", "price": -108, "point": 14.5},
                                    {"name": "Under", "description": "Klay Thompson", "price": -112, "point": 14.5},
                                ],
                            },
                            {
                                "key": "player_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Anthony Davis", "price": -130, "point": 11.5},
                                    {"name": "Under", "description": "Anthony Davis", "price": 110, "point": 11.5},
                                    {"name": "Over", "description": "Rudy Gobert", "price": -125, "point": 11.5},
                                    {"name": "Under", "description": "Rudy Gobert", "price": 105, "point": 11.5},
                                    {"name": "Over", "description": "Julius Randle", "price": -110, "point": 8.5},
                                    {"name": "Under", "description": "Julius Randle", "price": -110, "point": 8.5},
                                ],
                            },
                            # Combination props
                            {
                                "key": "player_points_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Anthony Edwards", "price": -110, "point": 42.5},
                                    {"name": "Under", "description": "Anthony Edwards", "price": -110, "point": 42.5},
                                    {"name": "Over", "description": "Anthony Davis", "price": -115, "point": 44.5},
                                    {"name": "Under", "description": "Anthony Davis", "price": -105, "point": 44.5},
                                    {"name": "Over", "description": "Julius Randle", "price": -108, "point": 36.5},
                                    {"name": "Under", "description": "Julius Randle", "price": -112, "point": 36.5},
                                ],
                            },
                            {
                                "key": "player_points_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Anthony Davis", "price": -115, "point": 37.5},
                                    {"name": "Under", "description": "Anthony Davis", "price": -105, "point": 37.5},
                                    {"name": "Over", "description": "Julius Randle", "price": -110, "point": 30.5},
                                    {"name": "Under", "description": "Julius Randle", "price": -110, "point": 30.5},
                                ],
                            },
                            {
                                "key": "player_points_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Anthony Edwards", "price": -110, "point": 34.5},
                                    {"name": "Under", "description": "Anthony Edwards", "price": -110, "point": 34.5},
                                    {"name": "Over", "description": "Klay Thompson", "price": -108, "point": 18.5},
                                    {"name": "Under", "description": "Klay Thompson", "price": -112, "point": 18.5},
                                ],
                            },
                            # Defensive/misc props
                            {
                                "key": "player_steals",
                                "outcomes": [
                                    {"name": "Over", "description": "Anthony Edwards", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Anthony Edwards", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Anthony Davis", "price": -110, "point": 1.5},
                                    {"name": "Under", "description": "Anthony Davis", "price": -110, "point": 1.5},
                                ],
                            },
                            {
                                "key": "player_blocks",
                                "outcomes": [
                                    {"name": "Over", "description": "Anthony Davis", "price": -115, "point": 2.5},
                                    {"name": "Under", "description": "Anthony Davis", "price": -105, "point": 2.5},
                                    {"name": "Over", "description": "Rudy Gobert", "price": -120, "point": 2.5},
                                    {"name": "Under", "description": "Rudy Gobert", "price": 100, "point": 2.5},
                                ],
                            },
                            {
                                "key": "player_turnovers",
                                "outcomes": [
                                    {"name": "Over", "description": "Anthony Edwards", "price": -110, "point": 3.5},
                                    {"name": "Under", "description": "Anthony Edwards", "price": -110, "point": 3.5},
                                    {"name": "Over", "description": "Julius Randle", "price": -108, "point": 2.5},
                                    {"name": "Under", "description": "Julius Randle", "price": -112, "point": 2.5},
                                ],
                            },
                        ],
                    },
                ],
            }
        
        # Game: Warriors @ Jazz (Curry/Butler Warriors vs Markkanen Jazz)
        elif external_game_id == "game_gsw_uta_20260128":
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Utah Jazz",
                "away_team": "Golden State Warriors",
                "commence_time": "2026-01-28T21:00:00Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "player_points",
                                "outcomes": [
                                    {"name": "Over", "description": "Stephen Curry", "price": -115, "point": 27.5},
                                    {"name": "Under", "description": "Stephen Curry", "price": -105, "point": 27.5},
                                    {"name": "Over", "description": "Lauri Markkanen", "price": -110, "point": 24.5},
                                    {"name": "Under", "description": "Lauri Markkanen", "price": -110, "point": 24.5},
                                    {"name": "Over", "description": "Jimmy Butler", "price": -108, "point": 21.5},
                                    {"name": "Under", "description": "Jimmy Butler", "price": -112, "point": 21.5},
                                ],
                            },
                            {
                                "key": "player_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Jusuf Nurkic", "price": -115, "point": 9.5},
                                    {"name": "Under", "description": "Jusuf Nurkic", "price": -105, "point": 9.5},
                                    {"name": "Over", "description": "Lauri Markkanen", "price": -110, "point": 7.5},
                                    {"name": "Under", "description": "Lauri Markkanen", "price": -110, "point": 7.5},
                                    {"name": "Over", "description": "Draymond Green", "price": -105, "point": 6.5},
                                    {"name": "Under", "description": "Draymond Green", "price": -115, "point": 6.5},
                                ],
                            },
                            {
                                "key": "player_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Stephen Curry", "price": -115, "point": 5.5},
                                    {"name": "Under", "description": "Stephen Curry", "price": -105, "point": 5.5},
                                ],
                            },
                            {
                                "key": "player_threes",
                                "outcomes": [
                                    {"name": "Over", "description": "Stephen Curry", "price": -115, "point": 4.5},
                                    {"name": "Under", "description": "Stephen Curry", "price": -105, "point": 4.5},
                                    {"name": "Over", "description": "Lauri Markkanen", "price": -110, "point": 2.5},
                                    {"name": "Under", "description": "Lauri Markkanen", "price": -110, "point": 2.5},
                                ],
                            },
                            # Combination props
                            {
                                "key": "player_points_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Stephen Curry", "price": -110, "point": 38.5},
                                    {"name": "Under", "description": "Stephen Curry", "price": -110, "point": 38.5},
                                    {"name": "Over", "description": "Lauri Markkanen", "price": -115, "point": 36.5},
                                    {"name": "Under", "description": "Lauri Markkanen", "price": -105, "point": 36.5},
                                    {"name": "Over", "description": "Jimmy Butler", "price": -108, "point": 34.5},
                                    {"name": "Under", "description": "Jimmy Butler", "price": -112, "point": 34.5},
                                ],
                            },
                            {
                                "key": "player_points_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Lauri Markkanen", "price": -110, "point": 32.5},
                                    {"name": "Under", "description": "Lauri Markkanen", "price": -110, "point": 32.5},
                                    {"name": "Over", "description": "Stephen Curry", "price": -115, "point": 32.5},
                                    {"name": "Under", "description": "Stephen Curry", "price": -105, "point": 32.5},
                                ],
                            },
                            {
                                "key": "player_points_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Stephen Curry", "price": -115, "point": 33.5},
                                    {"name": "Under", "description": "Stephen Curry", "price": -105, "point": 33.5},
                                    {"name": "Over", "description": "Jimmy Butler", "price": -110, "point": 28.5},
                                    {"name": "Under", "description": "Jimmy Butler", "price": -110, "point": 28.5},
                                ],
                            },
                            # Defensive/misc props
                            {
                                "key": "player_steals",
                                "outcomes": [
                                    {"name": "Over", "description": "Stephen Curry", "price": -110, "point": 1.5},
                                    {"name": "Under", "description": "Stephen Curry", "price": -110, "point": 1.5},
                                    {"name": "Over", "description": "Draymond Green", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Draymond Green", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Jimmy Butler", "price": -108, "point": 1.5},
                                    {"name": "Under", "description": "Jimmy Butler", "price": -112, "point": 1.5},
                                ],
                            },
                            {
                                "key": "player_blocks",
                                "outcomes": [
                                    {"name": "Over", "description": "Draymond Green", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Draymond Green", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Jusuf Nurkic", "price": -110, "point": 0.5},
                                    {"name": "Under", "description": "Jusuf Nurkic", "price": -110, "point": 0.5},
                                ],
                            },
                            {
                                "key": "player_turnovers",
                                "outcomes": [
                                    {"name": "Over", "description": "Stephen Curry", "price": -110, "point": 3.5},
                                    {"name": "Under", "description": "Stephen Curry", "price": -110, "point": 3.5},
                                    {"name": "Over", "description": "Lauri Markkanen", "price": -108, "point": 2.5},
                                    {"name": "Under", "description": "Lauri Markkanen", "price": -112, "point": 2.5},
                                ],
                            },
                        ],
                    },
                ],
            }
        
        # Game: Bulls @ Pacers (Giddey/Vucevic Bulls vs Siakam/Haliburton Pacers)
        elif external_game_id == "game_chi_ind_20260128":
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Indiana Pacers",
                "away_team": "Chicago Bulls",
                "commence_time": "2026-01-28T19:00:00Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "player_points",
                                "outcomes": [
                                    {"name": "Over", "description": "Pascal Siakam", "price": -115, "point": 22.5},
                                    {"name": "Under", "description": "Pascal Siakam", "price": -105, "point": 22.5},
                                    {"name": "Over", "description": "Coby White", "price": -110, "point": 19.5},
                                    {"name": "Under", "description": "Coby White", "price": -110, "point": 19.5},
                                    {"name": "Over", "description": "Nikola Vucevic", "price": -108, "point": 17.5},
                                    {"name": "Under", "description": "Nikola Vucevic", "price": -112, "point": 17.5},
                                    {"name": "Over", "description": "Josh Giddey", "price": -110, "point": 18.5},
                                    {"name": "Under", "description": "Josh Giddey", "price": -110, "point": 18.5},
                                ],
                            },
                            {
                                "key": "player_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Pascal Siakam", "price": -115, "point": 7.5},
                                    {"name": "Under", "description": "Pascal Siakam", "price": -105, "point": 7.5},
                                    {"name": "Over", "description": "Nikola Vucevic", "price": -120, "point": 9.5},
                                    {"name": "Under", "description": "Nikola Vucevic", "price": 100, "point": 9.5},
                                    {"name": "Over", "description": "Josh Giddey", "price": -110, "point": 8.5},
                                    {"name": "Under", "description": "Josh Giddey", "price": -110, "point": 8.5},
                                ],
                            },
                            {
                                "key": "player_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Josh Giddey", "price": -115, "point": 8.5},
                                    {"name": "Under", "description": "Josh Giddey", "price": -105, "point": 8.5},
                                ],
                            },
                            # Combination props
                            {
                                "key": "player_points_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Pascal Siakam", "price": -110, "point": 36.5},
                                    {"name": "Under", "description": "Pascal Siakam", "price": -110, "point": 36.5},
                                    {"name": "Over", "description": "Josh Giddey", "price": -115, "point": 35.5},
                                    {"name": "Under", "description": "Josh Giddey", "price": -105, "point": 35.5},
                                    {"name": "Over", "description": "Nikola Vucevic", "price": -108, "point": 32.5},
                                    {"name": "Under", "description": "Nikola Vucevic", "price": -112, "point": 32.5},
                                ],
                            },
                            {
                                "key": "player_points_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Nikola Vucevic", "price": -110, "point": 27.5},
                                    {"name": "Under", "description": "Nikola Vucevic", "price": -110, "point": 27.5},
                                    {"name": "Over", "description": "Pascal Siakam", "price": -115, "point": 30.5},
                                    {"name": "Under", "description": "Pascal Siakam", "price": -105, "point": 30.5},
                                ],
                            },
                            {
                                "key": "player_points_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "Josh Giddey", "price": -115, "point": 27.5},
                                    {"name": "Under", "description": "Josh Giddey", "price": -105, "point": 27.5},
                                    {"name": "Over", "description": "Coby White", "price": -110, "point": 25.5},
                                    {"name": "Under", "description": "Coby White", "price": -110, "point": 25.5},
                                ],
                            },
                            # Defensive/misc props
                            {
                                "key": "player_steals",
                                "outcomes": [
                                    {"name": "Over", "description": "Pascal Siakam", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "Pascal Siakam", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Josh Giddey", "price": -110, "point": 1.5},
                                    {"name": "Under", "description": "Josh Giddey", "price": -110, "point": 1.5},
                                ],
                            },
                            {
                                "key": "player_blocks",
                                "outcomes": [
                                    {"name": "Over", "description": "Nikola Vucevic", "price": -110, "point": 0.5},
                                    {"name": "Under", "description": "Nikola Vucevic", "price": -110, "point": 0.5},
                                    {"name": "Over", "description": "Pascal Siakam", "price": -115, "point": 0.5},
                                    {"name": "Under", "description": "Pascal Siakam", "price": -105, "point": 0.5},
                                ],
                            },
                            {
                                "key": "player_turnovers",
                                "outcomes": [
                                    {"name": "Over", "description": "Josh Giddey", "price": -110, "point": 3.5},
                                    {"name": "Under", "description": "Josh Giddey", "price": -110, "point": 3.5},
                                    {"name": "Over", "description": "Pascal Siakam", "price": -108, "point": 2.5},
                                    {"name": "Under", "description": "Pascal Siakam", "price": -112, "point": 2.5},
                                ],
                            },
                        ],
                    },
                ],
            }
        
        # Game: Hornets @ Grizzlies (LaMelo/Miller Hornets vs Ja/JJJ Grizzlies)
        elif external_game_id == "game_cha_mem_20260128":
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Memphis Grizzlies",
                "away_team": "Charlotte Hornets",
                "commence_time": "2026-01-28T20:00:00Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "player_points",
                                "outcomes": [
                                    {"name": "Over", "description": "LaMelo Ball", "price": -115, "point": 24.5},
                                    {"name": "Under", "description": "LaMelo Ball", "price": -105, "point": 24.5},
                                    {"name": "Over", "description": "Ja Morant", "price": -110, "point": 23.5},
                                    {"name": "Under", "description": "Ja Morant", "price": -110, "point": 23.5},
                                    {"name": "Over", "description": "Jaren Jackson Jr.", "price": -108, "point": 22.5},
                                    {"name": "Under", "description": "Jaren Jackson Jr.", "price": -112, "point": 22.5},
                                    {"name": "Over", "description": "Brandon Miller", "price": -110, "point": 18.5},
                                    {"name": "Under", "description": "Brandon Miller", "price": -110, "point": 18.5},
                                ],
                            },
                            {
                                "key": "player_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "LaMelo Ball", "price": -120, "point": 8.5},
                                    {"name": "Under", "description": "LaMelo Ball", "price": 100, "point": 8.5},
                                    {"name": "Over", "description": "Ja Morant", "price": -115, "point": 7.5},
                                    {"name": "Under", "description": "Ja Morant", "price": -105, "point": 7.5},
                                ],
                            },
                            # Combination props
                            {
                                "key": "player_points_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "LaMelo Ball", "price": -110, "point": 40.5},
                                    {"name": "Under", "description": "LaMelo Ball", "price": -110, "point": 40.5},
                                    {"name": "Over", "description": "Ja Morant", "price": -115, "point": 38.5},
                                    {"name": "Under", "description": "Ja Morant", "price": -105, "point": 38.5},
                                    {"name": "Over", "description": "Jaren Jackson Jr.", "price": -108, "point": 32.5},
                                    {"name": "Under", "description": "Jaren Jackson Jr.", "price": -112, "point": 32.5},
                                ],
                            },
                            {
                                "key": "player_points_rebounds",
                                "outcomes": [
                                    {"name": "Over", "description": "Jaren Jackson Jr.", "price": -110, "point": 28.5},
                                    {"name": "Under", "description": "Jaren Jackson Jr.", "price": -110, "point": 28.5},
                                    {"name": "Over", "description": "LaMelo Ball", "price": -115, "point": 31.5},
                                    {"name": "Under", "description": "LaMelo Ball", "price": -105, "point": 31.5},
                                ],
                            },
                            {
                                "key": "player_points_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "LaMelo Ball", "price": -115, "point": 33.5},
                                    {"name": "Under", "description": "LaMelo Ball", "price": -105, "point": 33.5},
                                    {"name": "Over", "description": "Ja Morant", "price": -110, "point": 31.5},
                                    {"name": "Under", "description": "Ja Morant", "price": -110, "point": 31.5},
                                ],
                            },
                            {
                                "key": "player_rebounds_assists",
                                "outcomes": [
                                    {"name": "Over", "description": "LaMelo Ball", "price": -110, "point": 15.5},
                                    {"name": "Under", "description": "LaMelo Ball", "price": -110, "point": 15.5},
                                    {"name": "Over", "description": "Ja Morant", "price": -108, "point": 14.5},
                                    {"name": "Under", "description": "Ja Morant", "price": -112, "point": 14.5},
                                ],
                            },
                            # Defensive/misc props
                            {
                                "key": "player_steals",
                                "outcomes": [
                                    {"name": "Over", "description": "LaMelo Ball", "price": -115, "point": 1.5},
                                    {"name": "Under", "description": "LaMelo Ball", "price": -105, "point": 1.5},
                                    {"name": "Over", "description": "Ja Morant", "price": -110, "point": 1.5},
                                    {"name": "Under", "description": "Ja Morant", "price": -110, "point": 1.5},
                                ],
                            },
                            {
                                "key": "player_blocks",
                                "outcomes": [
                                    {"name": "Over", "description": "Jaren Jackson Jr.", "price": -120, "point": 2.5},
                                    {"name": "Under", "description": "Jaren Jackson Jr.", "price": 100, "point": 2.5},
                                    {"name": "Over", "description": "Brandon Miller", "price": -110, "point": 0.5},
                                    {"name": "Under", "description": "Brandon Miller", "price": -110, "point": 0.5},
                                ],
                            },
                            {
                                "key": "player_turnovers",
                                "outcomes": [
                                    {"name": "Over", "description": "LaMelo Ball", "price": -110, "point": 3.5},
                                    {"name": "Under", "description": "LaMelo Ball", "price": -110, "point": 3.5},
                                    {"name": "Over", "description": "Ja Morant", "price": -108, "point": 3.5},
                                    {"name": "Under", "description": "Ja Morant", "price": -112, "point": 3.5},
                                ],
                            },
                        ],
                    },
                ],
            }
        
        # Default empty response for unknown games
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": "Unknown",
            "away_team": "Unknown",
            "commence_time": "2026-01-28T19:00:00Z",
            "bookmakers": [],
        }
