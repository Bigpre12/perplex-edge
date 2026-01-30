"""Odds provider for fetching games, lines, and player props from external APIs."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from zoneinfo import ZoneInfo

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Eastern timezone (handles DST automatically)
EASTERN_TZ = ZoneInfo("America/New_York")


# =============================================================================
# Dynamic Stub Date Generation
# =============================================================================

def _get_stub_game_times() -> dict[str, str]:
    """
    Generate game times for today's date.
    
    Uses proper timezone handling to set games in the evening ET
    for the current day in Eastern time.
    
    Returns:
        Dictionary mapping time slots to ISO datetime strings (UTC)
    """
    # Get current time in Eastern timezone (handles DST automatically)
    now_et = datetime.now(EASTERN_TZ)
    today_et = now_et.date()
    
    # Create game times for evening Eastern time (7 PM - 10 PM ET range)
    # These are typical NBA game start times
    game_times = {
        "early": datetime(today_et.year, today_et.month, today_et.day, 19, 0, tzinfo=EASTERN_TZ),    # 7:00 PM ET
        "mid": datetime(today_et.year, today_et.month, today_et.day, 19, 30, tzinfo=EASTERN_TZ),    # 7:30 PM ET
        "late": datetime(today_et.year, today_et.month, today_et.day, 20, 0, tzinfo=EASTERN_TZ),    # 8:00 PM ET
        "night": datetime(today_et.year, today_et.month, today_et.day, 21, 0, tzinfo=EASTERN_TZ),   # 9:00 PM ET
        "west": datetime(today_et.year, today_et.month, today_et.day, 22, 0, tzinfo=EASTERN_TZ),    # 10:00 PM ET
    }
    
    # Convert to UTC ISO strings
    return {
        slot: dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for slot, dt in game_times.items()
    }


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
        
        # Handle HTTP errors gracefully
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                # 422 typically means validation error - log and return empty
                logger.warning(
                    f"Odds API returned 422 for {endpoint}: {e.response.text[:500]}"
                )
                return []
            elif e.response.status_code == 429:
                # Rate limited
                logger.warning(f"Odds API rate limited: {e.response.text[:200]}")
                return []
            elif e.response.status_code == 404:
                # Resource not found - not necessarily an error
                logger.info(f"Odds API resource not found: {endpoint}")
                return []
            else:
                # Re-raise other errors
                logger.error(f"Odds API error {e.response.status_code}: {e.response.text[:500]}")
                raise
        
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
                "regions": "us,us2",
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
                    "regions": "us,us2",
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
                    markets = "player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists,player_points_rebounds,player_points_assists,player_rebounds_assists,player_steals,player_blocks,player_turnovers"
                elif "football" in sport_key:
                    markets = "player_pass_yds,player_rush_yds,player_reception_yds,player_receptions"
                elif "baseball" in sport_key:
                    markets = "batter_total_bases,pitcher_strikeouts,batter_hits"
                else:
                    markets = "player_points"
            
            raw_data = await self._request(
                f"/sports/{sport_key}/events/{external_game_id}/odds",
                {
                    "regions": "us,us2",
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
        """Return realistic stub game data for testing with dynamic dates."""
        # Get dynamic game times based on today's date
        times = _get_stub_game_times()
        
        if sport_key == "basketball_ncaab":
            # College Basketball games (2025-26 Season) - 8 Games, 16 Top Teams
            return [
                # Game 1: Kansas vs Duke
                {
                    "id": "ncaab_game_1",
                    "sport_key": sport_key,
                    "sport_title": "NCAAB",
                    "commence_time": times["early"],
                    "home_team": "Kansas Jayhawks",
                    "away_team": "Duke Blue Devils",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Kansas Jayhawks", "price": -135},
                                {"name": "Duke Blue Devils", "price": 115}
                            ]}]
                        }
                    ],
                },
                # Game 2: Kentucky vs Houston
                {
                    "id": "ncaab_game_2",
                    "sport_key": sport_key,
                    "sport_title": "NCAAB",
                    "commence_time": times["early"],
                    "home_team": "Kentucky Wildcats",
                    "away_team": "Houston Cougars",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Kentucky Wildcats", "price": 110},
                                {"name": "Houston Cougars", "price": -130}
                            ]}]
                        }
                    ],
                },
                # Game 3: Gonzaga vs UConn
                {
                    "id": "ncaab_game_3",
                    "sport_key": sport_key,
                    "sport_title": "NCAAB",
                    "commence_time": times["late"],
                    "home_team": "Gonzaga Bulldogs",
                    "away_team": "UConn Huskies",
                    "bookmakers": [
                        {
                            "key": "betmgm",
                            "title": "BetMGM",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Gonzaga Bulldogs", "price": -120},
                                {"name": "UConn Huskies", "price": 100}
                            ]}]
                        }
                    ],
                },
                # Game 4: Purdue vs Florida
                {
                    "id": "ncaab_game_4",
                    "sport_key": sport_key,
                    "sport_title": "NCAAB",
                    "commence_time": times["late"],
                    "home_team": "Purdue Boilermakers",
                    "away_team": "Florida Gators",
                    "bookmakers": [
                        {
                            "key": "caesars",
                            "title": "Caesars",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Purdue Boilermakers", "price": -145},
                                {"name": "Florida Gators", "price": 125}
                            ]}]
                        }
                    ],
                },
                # Game 5: UCLA vs Arizona
                {
                    "id": "ncaab_game_5",
                    "sport_key": sport_key,
                    "sport_title": "NCAAB",
                    "commence_time": times["night"],
                    "home_team": "UCLA Bruins",
                    "away_team": "Arizona Wildcats",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "UCLA Bruins", "price": 105},
                                {"name": "Arizona Wildcats", "price": -125}
                            ]}]
                        }
                    ],
                },
                # Game 6: Alabama vs Tennessee
                {
                    "id": "ncaab_game_6",
                    "sport_key": sport_key,
                    "sport_title": "NCAAB",
                    "commence_time": times["night"],
                    "home_team": "Alabama Crimson Tide",
                    "away_team": "Tennessee Volunteers",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Alabama Crimson Tide", "price": -115},
                                {"name": "Tennessee Volunteers", "price": -105}
                            ]}]
                        }
                    ],
                },
                # Game 7: St. John's vs Michigan
                {
                    "id": "ncaab_game_7",
                    "sport_key": sport_key,
                    "sport_title": "NCAAB",
                    "commence_time": times["west"],
                    "home_team": "St. John's Red Storm",
                    "away_team": "Michigan Wolverines",
                    "bookmakers": [
                        {
                            "key": "betmgm",
                            "title": "BetMGM",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "St. John's Red Storm", "price": -140},
                                {"name": "Michigan Wolverines", "price": 120}
                            ]}]
                        }
                    ],
                },
                # Game 8: Arkansas vs Illinois
                {
                    "id": "ncaab_game_8",
                    "sport_key": sport_key,
                    "sport_title": "NCAAB",
                    "commence_time": times["west"],
                    "home_team": "Arkansas Razorbacks",
                    "away_team": "Illinois Fighting Illini",
                    "bookmakers": [
                        {
                            "key": "caesars",
                            "title": "Caesars",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Arkansas Razorbacks", "price": 100},
                                {"name": "Illinois Fighting Illini", "price": -120}
                            ]}]
                        }
                    ],
                },
            ]
        elif "basketball" in sport_key:
            # Real NBA Schedule for January 29, 2026
            return [
                # Game 1: Kings @ 76ers (7:00 PM ET)
                {
                    "id": "game_sac_phi_today",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": times["early"],
                    "home_team": "Philadelphia 76ers",
                    "away_team": "Sacramento Kings",
                    "bookmakers": [],
                },
                # Game 2: Bucks @ Wizards (8:00 PM ET)
                {
                    "id": "game_mil_was_today",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": times["late"],
                    "home_team": "Washington Wizards",
                    "away_team": "Milwaukee Bucks",
                    "bookmakers": [],
                },
                # Game 3: Heat @ Bulls (8:00 PM ET)
                {
                    "id": "game_mia_chi_today",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": times["late"],
                    "home_team": "Chicago Bulls",
                    "away_team": "Miami Heat",
                    "bookmakers": [],
                },
                # Game 4: Rockets @ Hawks (8:30 PM ET)
                {
                    "id": "game_hou_atl_today",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": times["night"],
                    "home_team": "Atlanta Hawks",
                    "away_team": "Houston Rockets",
                    "bookmakers": [],
                },
                # Game 5: Hornets @ Mavericks (9:00 PM ET)
                {
                    "id": "game_cha_dal_today",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": times["west"],
                    "home_team": "Dallas Mavericks",
                    "away_team": "Charlotte Hornets",
                    "bookmakers": [],
                },
                # Game 6: Nets @ Nuggets (9:00 PM ET)
                {
                    "id": "game_bkn_den_today",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": times["west"],
                    "home_team": "Denver Nuggets",
                    "away_team": "Brooklyn Nets",
                    "bookmakers": [],
                },
                # Game 7: Pistons @ Suns (9:30 PM ET)
                {
                    "id": "game_det_pho_today",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": times["west"],
                    "home_team": "Phoenix Suns",
                    "away_team": "Detroit Pistons",
                    "bookmakers": [],
                },
                # Game 8: Thunder @ Timberwolves (9:00 PM ET)
                {
                    "id": "game_okc_min_today",
                    "sport_key": sport_key,
                    "sport_title": "NBA",
                    "commence_time": times["west"],
                    "home_team": "Minnesota Timberwolves",
                    "away_team": "Oklahoma City Thunder",
                    "bookmakers": [],
                },
            ]
        elif "football" in sport_key:
            return [
                {
                    "id": "nfl_game_today",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["early"],
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
        """Return realistic stub betting lines for testing with dynamic dates.
        
        INJURY-ADJUSTED LINES - Jan 29, 2026:
        Lines reflect major injuries: Embiid, Giannis, Jokic, AD, Booker, Trae OUT
        """
        # Game-specific lines ADJUSTED FOR INJURIES - Jan 29, 2026
        # Based on DraftKings/FanDuel market research
        game_lines = {
            # Kings favored by 5.5 (EMBIID OUT since Jan 4, PG questionable)
            "game_sac_phi_today": {
                "home_team": "Philadelphia 76ers", "away_team": "Sacramento Kings",
                "home_spread": 5.5, "total": 226.5, "home_ml": 200, "away_ml": -245,
            },
            # Bucks favored by 2.5 (GIANNIS OUT but Bucks still deeper roster)
            "game_mil_was_today": {
                "home_team": "Washington Wizards", "away_team": "Milwaukee Bucks",
                "home_spread": 2.5, "total": 222.5, "home_ml": 120, "away_ml": -140,
            },
            # Bulls favored by 1.5 (HERRO OUT, home court)
            "game_mia_chi_today": {
                "home_team": "Chicago Bulls", "away_team": "Miami Heat",
                "home_spread": -1.5, "total": 218.5, "home_ml": -125, "away_ml": 105,
            },
            # Rockets favored by 7.5 (KD healthy vs gutted Hawks roster)
            "game_hou_atl_today": {
                "home_team": "Atlanta Hawks", "away_team": "Houston Rockets",
                "home_spread": 7.5, "total": 225.0, "home_ml": 280, "away_ml": -360,
            },
            # Hornets favored by 3.5 (AD OUT, LaMelo averaging 28.2 PPG)
            "game_cha_dal_today": {
                "home_team": "Dallas Mavericks", "away_team": "Charlotte Hornets",
                "home_spread": 3.5, "total": 225.5, "home_ml": 150, "away_ml": -175,
            },
            # Nuggets favored by 3.5 (JOKIC OUT, CAM THOMAS OUT, both depleted)
            "game_bkn_den_today": {
                "home_team": "Denver Nuggets", "away_team": "Brooklyn Nets",
                "home_spread": -3.5, "total": 218.0, "home_ml": -165, "away_ml": 140,
            },
            # Pistons favored by 8.5 (BOOKER OUT, Pistons 34-11 best record)
            "game_det_pho_today": {
                "home_team": "Phoenix Suns", "away_team": "Detroit Pistons",
                "home_spread": 8.5, "total": 215.5, "home_ml": 320, "away_ml": -420,
            },
            # Thunder favored by 5.5 (SGA MVP form, ANT EDWARDS DTD)
            "game_okc_min_today": {
                "home_team": "Minnesota Timberwolves", "away_team": "Oklahoma City Thunder",
                "home_spread": 5.5, "total": 218.5, "home_ml": 200, "away_ml": -245,
            },
        }
        
        # Get game-specific lines or use defaults
        lines = game_lines.get(external_game_id, {
            "home_team": "Home Team", "away_team": "Away Team",
            "home_spread": -3.0, "total": 220.0, "home_ml": -150, "away_ml": 130,
        })
        
        times = _get_stub_game_times()
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": lines["home_team"],
            "away_team": lines["away_team"],
            "commence_time": times["early"],
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
                                {"name": "Over", "price": -105, "point": lines["total"]},
                                {"name": "Under", "price": -115, "point": lines["total"]},
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
        """Return realistic stub player props for Jan 29, 2026 NBA games.
        
        INJURY REPORT - Jan 29, 2026:
        - Embiid OUT (knee) - hasn't played since Jan 4
        - Giannis OUT (calf strain 4-6 weeks) - injured Jan 23
        - Trae Young OUT (MCL sprain) - won't debut for Wizards until All-Star break
        - Tyler Herro OUT (toe) - missed 28 of 34 games
        - Anthony Davis OUT (hand ligament, 6 weeks) - injured Jan 8
        - Jokic OUT (knee hyperextension) - no timetable
        - Cam Thomas OUT (hamstring)
        - Booker OUT (ankle sprain, 1+ week) - injured Jan 24
        - Jalen Green DAY-TO-DAY (hamstring) - only 4 games this season
        - Anthony Edwards DAY-TO-DAY (foot maintenance)
        """
        times = _get_stub_game_times()
        
        # Define props with INJURY-ADJUSTED rosters for Jan 29, 2026
        # Stats: pts, reb, ast, pra, pr, pa, ra, 3pm, stl, blk, to
        game_props = {
            # Game 1: Kings @ 76ers - EMBIID OUT, Paul George questionable
            "game_sac_phi_today": {
                "home_team": "Philadelphia 76ers",
                "away_team": "Sacramento Kings",
                "commence_time": times["early"],
                "players": [
                    # 76ers (Embiid OUT)
                    {"name": "Tyrese Maxey", "pts": 29.5, "reb": 4.5, "ast": 7.5, "pra": 41.5, "pr": 34.0, "pa": 37.0, "ra": 12.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Paul George", "pts": 24.5, "reb": 6.5, "ast": 5.5, "pra": 36.5, "pr": 31.0, "pa": 30.0, "ra": 12.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Andre Drummond", "pts": 10.5, "reb": 10.5, "ast": 1.5, "pra": 22.5, "pr": 21.0, "pa": 12.0, "ra": 12.0, "3pm": 0.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
                    {"name": "Kyle Lowry", "pts": 8.5, "reb": 3.5, "ast": 5.5, "pra": 17.5, "pr": 12.0, "pa": 14.0, "ra": 9.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    # Kings
                    {"name": "Zach LaVine", "pts": 25.5, "reb": 4.5, "ast": 4.5, "pra": 34.5, "pr": 30.0, "pa": 30.0, "ra": 9.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "DeMar DeRozan", "pts": 24.5, "reb": 4.5, "ast": 5.5, "pra": 34.5, "pr": 29.0, "pa": 30.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Domantas Sabonis", "pts": 19.5, "reb": 13.5, "ast": 7.5, "pra": 40.5, "pr": 33.0, "pa": 27.0, "ra": 21.0, "3pm": 0.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                ],
            },
            # Game 2: Bucks @ Wizards - GIANNIS OUT (calf), TRAE YOUNG OUT (MCL)
            "game_mil_was_today": {
                "home_team": "Washington Wizards",
                "away_team": "Milwaukee Bucks",
                "commence_time": times["late"],
                "players": [
                    # Bucks (Giannis OUT)
                    {"name": "Kyle Kuzma", "pts": 22.5, "reb": 6.5, "ast": 3.5, "pra": 32.5, "pr": 29.0, "pa": 26.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Myles Turner", "pts": 16.5, "reb": 8.5, "ast": 2.5, "pra": 27.5, "pr": 25.0, "pa": 19.0, "ra": 11.0, "3pm": 1.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    {"name": "Bobby Portis", "pts": 15.5, "reb": 8.5, "ast": 1.5, "pra": 25.5, "pr": 24.0, "pa": 17.0, "ra": 10.0, "3pm": 1.5, "stl": 0.5, "blk": 0.5, "to": 1.5},
                    {"name": "Gary Trent Jr.", "pts": 14.5, "reb": 2.5, "ast": 1.5, "pra": 18.5, "pr": 17.0, "pa": 16.0, "ra": 4.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    # Wizards (Trae Young OUT)
                    {"name": "Khris Middleton", "pts": 18.5, "reb": 5.5, "ast": 5.5, "pra": 29.5, "pr": 24.0, "pa": 24.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Bilal Coulibaly", "pts": 12.5, "reb": 5.5, "ast": 3.5, "pra": 21.5, "pr": 18.0, "pa": 16.0, "ra": 9.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Alex Sarr", "pts": 13.5, "reb": 8.5, "ast": 2.5, "pra": 24.5, "pr": 22.0, "pa": 16.0, "ra": 11.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                ],
            },
            # Game 3: Heat @ Bulls - TYLER HERRO OUT (toe)
            "game_mia_chi_today": {
                "home_team": "Chicago Bulls",
                "away_team": "Miami Heat",
                "commence_time": times["late"],
                "players": [
                    # Heat (Herro OUT)
                    {"name": "Bam Adebayo", "pts": 21.5, "reb": 11.5, "ast": 5.5, "pra": 38.5, "pr": 33.0, "pa": 27.0, "ra": 17.0, "3pm": 0.5, "stl": 1.5, "blk": 1.5, "to": 2.5},
                    {"name": "Andrew Wiggins", "pts": 18.5, "reb": 5.5, "ast": 2.5, "pra": 26.5, "pr": 24.0, "pa": 21.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Terry Rozier", "pts": 17.5, "reb": 3.5, "ast": 5.5, "pra": 26.5, "pr": 21.0, "pa": 23.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Jaime Jaquez Jr.", "pts": 13.5, "reb": 4.5, "ast": 2.5, "pra": 20.5, "pr": 18.0, "pa": 16.0, "ra": 7.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    # Bulls
                    {"name": "Coby White", "pts": 20.5, "reb": 4.5, "ast": 5.5, "pra": 30.5, "pr": 25.0, "pa": 26.0, "ra": 10.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Nikola Vucevic", "pts": 18.5, "reb": 10.5, "ast": 3.5, "pra": 32.5, "pr": 29.0, "pa": 22.0, "ra": 14.0, "3pm": 1.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
                    {"name": "Josh Giddey", "pts": 15.5, "reb": 7.5, "ast": 7.5, "pra": 30.5, "pr": 23.0, "pa": 23.0, "ra": 15.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                ],
            },
            # Game 4: Rockets @ Hawks - KD healthy, Hawks gutted
            "game_hou_atl_today": {
                "home_team": "Atlanta Hawks",
                "away_team": "Houston Rockets",
                "commence_time": times["night"],
                "players": [
                    # Rockets (KD healthy)
                    {"name": "Kevin Durant", "pts": 28.5, "reb": 7.5, "ast": 5.5, "pra": 41.5, "pr": 36.0, "pa": 34.0, "ra": 13.0, "3pm": 2.5, "stl": 1.5, "blk": 1.5, "to": 2.5},
                    {"name": "Alperen Sengun", "pts": 19.5, "reb": 10.5, "ast": 5.5, "pra": 35.5, "pr": 30.0, "pa": 25.0, "ra": 16.0, "3pm": 0.5, "stl": 1.5, "blk": 1.5, "to": 3.5},
                    {"name": "Fred VanVleet", "pts": 17.5, "reb": 3.5, "ast": 7.5, "pra": 28.5, "pr": 21.0, "pa": 25.0, "ra": 11.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Amen Thompson", "pts": 12.5, "reb": 6.5, "ast": 3.5, "pra": 22.5, "pr": 19.0, "pa": 16.0, "ra": 10.0, "3pm": 0.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    # Hawks (gutted roster)
                    {"name": "CJ McCollum", "pts": 22.5, "reb": 4.5, "ast": 5.5, "pra": 32.5, "pr": 27.0, "pa": 28.0, "ra": 10.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Bogdan Bogdanovic", "pts": 17.5, "reb": 3.5, "ast": 4.5, "pra": 25.5, "pr": 21.0, "pa": 22.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Clint Capela", "pts": 11.5, "reb": 11.5, "ast": 1.5, "pra": 24.5, "pr": 23.0, "pa": 13.0, "ra": 13.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                ],
            },
            # Game 5: Hornets @ Mavericks - ANTHONY DAVIS OUT (hand)
            "game_cha_dal_today": {
                "home_team": "Dallas Mavericks",
                "away_team": "Charlotte Hornets",
                "commence_time": times["west"],
                "players": [
                    # Mavericks (AD OUT)
                    {"name": "Kyrie Irving", "pts": 28.5, "reb": 5.5, "ast": 7.5, "pra": 41.5, "pr": 34.0, "pa": 36.0, "ra": 13.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Klay Thompson", "pts": 17.5, "reb": 4.5, "ast": 2.5, "pra": 24.5, "pr": 22.0, "pa": 20.0, "ra": 7.0, "3pm": 3.5, "stl": 0.5, "blk": 0.5, "to": 1.5},
                    {"name": "PJ Washington", "pts": 15.5, "reb": 7.5, "ast": 2.5, "pra": 25.5, "pr": 23.0, "pa": 18.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Daniel Gafford", "pts": 11.5, "reb": 7.5, "ast": 1.5, "pra": 20.5, "pr": 19.0, "pa": 13.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    # Hornets (LaMelo healthy)
                    {"name": "LaMelo Ball", "pts": 28.5, "reb": 6.5, "ast": 9.5, "pra": 44.5, "pr": 35.0, "pa": 38.0, "ra": 16.0, "3pm": 4.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                    {"name": "Brandon Miller", "pts": 20.5, "reb": 5.5, "ast": 3.5, "pra": 29.5, "pr": 26.0, "pa": 24.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Miles Bridges", "pts": 18.5, "reb": 7.5, "ast": 4.5, "pra": 30.5, "pr": 26.0, "pa": 23.0, "ra": 12.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                ],
            },
            # Game 6: Nets @ Nuggets - JOKIC OUT (knee), CAM THOMAS OUT (hamstring)
            "game_bkn_den_today": {
                "home_team": "Denver Nuggets",
                "away_team": "Brooklyn Nets",
                "commence_time": times["west"],
                "players": [
                    # Nuggets (Jokic OUT)
                    {"name": "Jamal Murray", "pts": 26.5, "reb": 5.5, "ast": 8.5, "pra": 40.5, "pr": 32.0, "pa": 35.0, "ra": 14.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Aaron Gordon", "pts": 18.5, "reb": 8.5, "ast": 4.5, "pra": 31.5, "pr": 27.0, "pa": 23.0, "ra": 13.0, "3pm": 1.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
                    {"name": "Christian Braun", "pts": 15.5, "reb": 5.5, "ast": 3.5, "pra": 24.5, "pr": 21.0, "pa": 19.0, "ra": 9.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Peyton Watson", "pts": 11.5, "reb": 5.5, "ast": 1.5, "pra": 18.5, "pr": 17.0, "pa": 13.0, "ra": 7.0, "3pm": 1.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
                    # Nets (Cam Thomas OUT)
                    {"name": "Dennis Schroder", "pts": 19.5, "reb": 3.5, "ast": 7.5, "pra": 30.5, "pr": 23.0, "pa": 27.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Nic Claxton", "pts": 12.5, "reb": 9.5, "ast": 2.5, "pra": 24.5, "pr": 22.0, "pa": 15.0, "ra": 12.0, "3pm": 0.5, "stl": 1.5, "blk": 2.5, "to": 1.5},
                    {"name": "Day'Ron Sharpe", "pts": 10.5, "reb": 7.5, "ast": 1.5, "pra": 19.5, "pr": 18.0, "pa": 12.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                ],
            },
            # Game 7: Pistons @ Suns - BOOKER OUT (ankle)
            "game_det_pho_today": {
                "home_team": "Phoenix Suns",
                "away_team": "Detroit Pistons",
                "commence_time": times["west"],
                "players": [
                    # Suns (Booker OUT)
                    {"name": "Dillon Brooks", "pts": 20.5, "reb": 4.5, "ast": 3.5, "pra": 28.5, "pr": 25.0, "pa": 24.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Royce O'Neale", "pts": 12.5, "reb": 5.5, "ast": 3.5, "pra": 21.5, "pr": 18.0, "pa": 16.0, "ra": 9.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Nick Richards", "pts": 13.5, "reb": 9.5, "ast": 1.5, "pra": 24.5, "pr": 23.0, "pa": 15.0, "ra": 11.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Ryan Dunn", "pts": 9.5, "reb": 4.5, "ast": 1.5, "pra": 15.5, "pr": 14.0, "pa": 11.0, "ra": 6.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    # Pistons
                    {"name": "Cade Cunningham", "pts": 24.5, "reb": 5.5, "ast": 9.5, "pra": 39.5, "pr": 30.0, "pa": 34.0, "ra": 15.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                    {"name": "Jaden Ivey", "pts": 18.5, "reb": 4.5, "ast": 5.5, "pra": 28.5, "pr": 23.0, "pa": 24.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Jalen Duren", "pts": 13.5, "reb": 11.5, "ast": 2.5, "pra": 27.5, "pr": 25.0, "pa": 16.0, "ra": 14.0, "3pm": 0.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
                ],
            },
            # Game 8: Thunder @ Timberwolves - ANT EDWARDS DAY-TO-DAY (foot)
            "game_okc_min_today": {
                "home_team": "Minnesota Timberwolves",
                "away_team": "Oklahoma City Thunder",
                "commence_time": times["west"],
                "players": [
                    # Thunder (SGA MVP form)
                    {"name": "Shai Gilgeous-Alexander", "pts": 32.5, "reb": 5.5, "ast": 6.5, "pra": 44.5, "pr": 38.0, "pa": 39.0, "ra": 12.0, "3pm": 2.5, "stl": 2.5, "blk": 1.5, "to": 2.5},
                    {"name": "Chet Holmgren", "pts": 17.5, "reb": 9.5, "ast": 3.5, "pra": 30.5, "pr": 27.0, "pa": 21.0, "ra": 13.0, "3pm": 1.5, "stl": 1.5, "blk": 2.5, "to": 1.5},
                    {"name": "Jalen Williams", "pts": 21.5, "reb": 6.5, "ast": 6.5, "pra": 34.5, "pr": 28.0, "pa": 28.0, "ra": 13.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Alex Caruso", "pts": 8.5, "reb": 3.5, "ast": 4.5, "pra": 16.5, "pr": 12.0, "pa": 13.0, "ra": 8.0, "3pm": 1.5, "stl": 2.5, "blk": 0.5, "to": 1.5},
                    # Timberwolves
                    {"name": "Julius Randle", "pts": 23.5, "reb": 10.5, "ast": 5.5, "pra": 39.5, "pr": 34.0, "pa": 29.0, "ra": 16.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                    {"name": "Rudy Gobert", "pts": 12.5, "reb": 12.5, "ast": 1.5, "pra": 26.5, "pr": 25.0, "pa": 14.0, "ra": 14.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    {"name": "Naz Reid", "pts": 14.5, "reb": 6.5, "ast": 2.5, "pra": 23.5, "pr": 21.0, "pa": 17.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                ],
            },
            # =================================================================
            # NCAAB GAMES - College Basketball Player Props (2025-26 Season)
            # 8 Games, 16 Top Teams, 80 Players
            # =================================================================
            # Game 1: Kansas vs Duke
            "ncaab_game_1": {
                "home_team": "Kansas Jayhawks",
                "away_team": "Duke Blue Devils",
                "commence_time": times["early"],
                "players": [
                    # Kansas Jayhawks (2025-26)
                    {"name": "Darryn Peterson", "pts": 15.5, "reb": 5.5, "ast": 3.5, "pra": 24.5, "pr": 21.0, "pa": 19.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Melvin Council Jr.", "pts": 13.5, "reb": 3.5, "ast": 4.5, "pra": 21.5, "pr": 17.0, "pa": 18.0, "ra": 8.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Jayden Dawson", "pts": 11.5, "reb": 3.5, "ast": 2.5, "pra": 17.5, "pr": 15.0, "pa": 14.0, "ra": 6.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Tre White", "pts": 10.5, "reb": 6.5, "ast": 1.5, "pra": 18.5, "pr": 17.0, "pa": 12.0, "ra": 8.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Flory Bidunga", "pts": 12.5, "reb": 9.5, "ast": 1.5, "pra": 23.5, "pr": 22.0, "pa": 14.0, "ra": 11.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    # Duke Blue Devils (2025-26)
                    {"name": "Caleb Foster", "pts": 14.5, "reb": 3.5, "ast": 5.5, "pra": 23.5, "pr": 18.0, "pa": 20.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Isaiah Evans", "pts": 13.5, "reb": 5.5, "ast": 2.5, "pra": 21.5, "pr": 19.0, "pa": 16.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Dame Sarr", "pts": 11.5, "reb": 4.5, "ast": 3.5, "pra": 19.5, "pr": 16.0, "pa": 15.0, "ra": 8.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Cameron Boozer", "pts": 16.5, "reb": 8.5, "ast": 2.5, "pra": 27.5, "pr": 25.0, "pa": 19.0, "ra": 11.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 2.5},
                    {"name": "Patrick Ngongba", "pts": 8.5, "reb": 7.5, "ast": 1.5, "pra": 17.5, "pr": 16.0, "pa": 10.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                ],
            },
            # Game 2: Kentucky vs Houston
            "ncaab_game_2": {
                "home_team": "Kentucky Wildcats",
                "away_team": "Houston Cougars",
                "commence_time": times["early"],
                "players": [
                    # Kentucky Wildcats (2025-26)
                    {"name": "Jaland Lowe", "pts": 14.5, "reb": 3.5, "ast": 5.5, "pra": 23.5, "pr": 18.0, "pa": 20.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Otega Oweh", "pts": 15.5, "reb": 4.5, "ast": 3.5, "pra": 23.5, "pr": 20.0, "pa": 19.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Denzel Aberdeen", "pts": 12.5, "reb": 3.5, "ast": 4.5, "pra": 20.5, "pr": 16.0, "pa": 17.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Mo Dioubate", "pts": 11.5, "reb": 7.5, "ast": 1.5, "pra": 20.5, "pr": 19.0, "pa": 13.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Brandon Garrison", "pts": 9.5, "reb": 6.5, "ast": 1.5, "pra": 17.5, "pr": 16.0, "pa": 11.0, "ra": 8.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    # Houston Cougars (2025-26)
                    {"name": "Milos Uzan", "pts": 13.5, "reb": 4.5, "ast": 6.5, "pra": 24.5, "pr": 18.0, "pa": 20.0, "ra": 11.0, "3pm": 1.5, "stl": 2.5, "blk": 0.5, "to": 2.5},
                    {"name": "Emanuel Sharp", "pts": 14.5, "reb": 3.5, "ast": 2.5, "pra": 20.5, "pr": 18.0, "pa": 17.0, "ra": 6.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Isiah Harwell", "pts": 10.5, "reb": 3.5, "ast": 3.5, "pra": 17.5, "pr": 14.0, "pa": 14.0, "ra": 7.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Chris Cenac Jr.", "pts": 12.5, "reb": 6.5, "ast": 2.5, "pra": 21.5, "pr": 19.0, "pa": 15.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Joseph Tugler", "pts": 10.5, "reb": 8.5, "ast": 1.5, "pra": 20.5, "pr": 19.0, "pa": 12.0, "ra": 10.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                ],
            },
            # Game 3: Gonzaga vs UConn
            "ncaab_game_3": {
                "home_team": "Gonzaga Bulldogs",
                "away_team": "UConn Huskies",
                "commence_time": times["late"],
                "players": [
                    # Gonzaga Bulldogs (2025-26)
                    {"name": "Braeden Smith", "pts": 12.5, "reb": 3.5, "ast": 6.5, "pra": 22.5, "pr": 16.0, "pa": 19.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Adam Miller", "pts": 14.5, "reb": 3.5, "ast": 3.5, "pra": 21.5, "pr": 18.0, "pa": 18.0, "ra": 7.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Jalen Warley", "pts": 12.5, "reb": 4.5, "ast": 4.5, "pra": 21.5, "pr": 17.0, "pa": 17.0, "ra": 9.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Braden Huff", "pts": 14.5, "reb": 6.5, "ast": 2.5, "pra": 23.5, "pr": 21.0, "pa": 17.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Graham Ike", "pts": 17.5, "reb": 9.5, "ast": 2.5, "pra": 29.5, "pr": 27.0, "pa": 20.0, "ra": 12.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 2.5},
                    # UConn Huskies (2025-26)
                    {"name": "Silas Demary Jr.", "pts": 13.5, "reb": 3.5, "ast": 4.5, "pra": 21.5, "pr": 17.0, "pa": 18.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Solo Ball", "pts": 11.5, "reb": 3.5, "ast": 5.5, "pra": 20.5, "pr": 15.0, "pa": 17.0, "ra": 9.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Braylon Mullins", "pts": 10.5, "reb": 3.5, "ast": 2.5, "pra": 16.5, "pr": 14.0, "pa": 13.0, "ra": 6.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Alex Karaban", "pts": 15.5, "reb": 6.5, "ast": 3.5, "pra": 25.5, "pr": 22.0, "pa": 19.0, "ra": 10.0, "3pm": 2.5, "stl": 0.5, "blk": 1.5, "to": 2.5},
                    {"name": "Tarris Reed Jr.", "pts": 12.5, "reb": 8.5, "ast": 1.5, "pra": 22.5, "pr": 21.0, "pa": 14.0, "ra": 10.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                ],
            },
            # Game 4: Purdue vs Florida
            "ncaab_game_4": {
                "home_team": "Purdue Boilermakers",
                "away_team": "Florida Gators",
                "commence_time": times["late"],
                "players": [
                    # Purdue Boilermakers (2025-26)
                    {"name": "Braden Smith", "pts": 13.5, "reb": 4.5, "ast": 7.5, "pra": 25.5, "pr": 18.0, "pa": 21.0, "ra": 12.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "CJ Cox", "pts": 11.5, "reb": 3.5, "ast": 3.5, "pra": 18.5, "pr": 15.0, "pa": 15.0, "ra": 7.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Fletcher Loyer", "pts": 14.5, "reb": 2.5, "ast": 3.5, "pra": 20.5, "pr": 17.0, "pa": 18.0, "ra": 6.0, "3pm": 3.5, "stl": 0.5, "blk": 0.5, "to": 1.5},
                    {"name": "Trey Kaufman-Renn", "pts": 17.5, "reb": 6.5, "ast": 2.5, "pra": 26.5, "pr": 24.0, "pa": 20.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Oscar Cluff", "pts": 9.5, "reb": 7.5, "ast": 1.5, "pra": 18.5, "pr": 17.0, "pa": 11.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    # Florida Gators (2025-26)
                    {"name": "Xaivian Lee", "pts": 12.5, "reb": 3.5, "ast": 5.5, "pra": 21.5, "pr": 16.0, "pa": 18.0, "ra": 9.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Boogie Fland", "pts": 15.5, "reb": 3.5, "ast": 4.5, "pra": 23.5, "pr": 19.0, "pa": 20.0, "ra": 8.0, "3pm": 2.5, "stl": 2.5, "blk": 0.5, "to": 2.5},
                    {"name": "Thomas Haugh", "pts": 11.5, "reb": 5.5, "ast": 2.5, "pra": 19.5, "pr": 17.0, "pa": 14.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Alex Condon", "pts": 13.5, "reb": 6.5, "ast": 2.5, "pra": 22.5, "pr": 20.0, "pa": 16.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Rueben Chinyelu", "pts": 10.5, "reb": 8.5, "ast": 1.5, "pra": 20.5, "pr": 19.0, "pa": 12.0, "ra": 10.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                ],
            },
            # Game 5: UCLA vs Arizona
            "ncaab_game_5": {
                "home_team": "UCLA Bruins",
                "away_team": "Arizona Wildcats",
                "commence_time": times["night"],
                "players": [
                    # UCLA Bruins (2025-26)
                    {"name": "Donovan Dent", "pts": 14.5, "reb": 3.5, "ast": 5.5, "pra": 23.5, "pr": 18.0, "pa": 20.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Skyy Clark", "pts": 12.5, "reb": 3.5, "ast": 4.5, "pra": 20.5, "pr": 16.0, "pa": 17.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Eric Dailey Jr.", "pts": 13.5, "reb": 5.5, "ast": 2.5, "pra": 21.5, "pr": 19.0, "pa": 16.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Tyler Bilodeau", "pts": 14.5, "reb": 6.5, "ast": 2.5, "pra": 23.5, "pr": 21.0, "pa": 17.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Xavier Booker", "pts": 11.5, "reb": 7.5, "ast": 1.5, "pra": 20.5, "pr": 19.0, "pa": 13.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    # Arizona Wildcats (2025-26)
                    {"name": "Jaden Bradley", "pts": 14.5, "reb": 3.5, "ast": 5.5, "pra": 23.5, "pr": 18.0, "pa": 20.0, "ra": 9.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Brayden Burries", "pts": 12.5, "reb": 3.5, "ast": 2.5, "pra": 18.5, "pr": 16.0, "pa": 15.0, "ra": 6.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Anthony Dell'Orso", "pts": 13.5, "reb": 4.5, "ast": 2.5, "pra": 20.5, "pr": 18.0, "pa": 16.0, "ra": 7.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Koa Peat", "pts": 16.5, "reb": 7.5, "ast": 3.5, "pra": 27.5, "pr": 24.0, "pa": 20.0, "ra": 11.0, "3pm": 1.5, "stl": 1.5, "blk": 1.5, "to": 2.5},
                    {"name": "Tobe Awaka", "pts": 10.5, "reb": 8.5, "ast": 1.5, "pra": 20.5, "pr": 19.0, "pa": 12.0, "ra": 10.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                ],
            },
            # Game 6: Alabama vs Tennessee
            "ncaab_game_6": {
                "home_team": "Alabama Crimson Tide",
                "away_team": "Tennessee Volunteers",
                "commence_time": times["night"],
                "players": [
                    # Alabama Crimson Tide (2025-26)
                    {"name": "Labaron Philon", "pts": 14.5, "reb": 3.5, "ast": 5.5, "pra": 23.5, "pr": 18.0, "pa": 20.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Aden Holloway", "pts": 12.5, "reb": 3.5, "ast": 4.5, "pra": 20.5, "pr": 16.0, "pa": 17.0, "ra": 8.0, "3pm": 2.5, "stl": 2.5, "blk": 0.5, "to": 2.5},
                    {"name": "Latrell Wrightsell Jr.", "pts": 15.5, "reb": 4.5, "ast": 2.5, "pra": 22.5, "pr": 20.0, "pa": 18.0, "ra": 7.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Taylor Bol Bowen", "pts": 11.5, "reb": 6.5, "ast": 2.5, "pra": 20.5, "pr": 18.0, "pa": 14.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Aiden Sherrell", "pts": 12.5, "reb": 7.5, "ast": 1.5, "pra": 21.5, "pr": 20.0, "pa": 14.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    # Tennessee Volunteers (2025-26)
                    {"name": "Ja'Kobi Gillespie", "pts": 13.5, "reb": 3.5, "ast": 5.5, "pra": 22.5, "pr": 17.0, "pa": 19.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Amaree Abram", "pts": 14.5, "reb": 4.5, "ast": 2.5, "pra": 21.5, "pr": 19.0, "pa": 17.0, "ra": 7.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Nate Ament", "pts": 10.5, "reb": 5.5, "ast": 2.5, "pra": 18.5, "pr": 16.0, "pa": 13.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Cade Phillips", "pts": 12.5, "reb": 6.5, "ast": 2.5, "pra": 21.5, "pr": 19.0, "pa": 15.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Felix Okpara", "pts": 9.5, "reb": 8.5, "ast": 1.5, "pra": 19.5, "pr": 18.0, "pa": 11.0, "ra": 10.0, "3pm": 0.5, "stl": 0.5, "blk": 3.5, "to": 1.5},
                ],
            },
            # Game 7: St. John's vs Michigan
            "ncaab_game_7": {
                "home_team": "St. John's Red Storm",
                "away_team": "Michigan Wolverines",
                "commence_time": times["west"],
                "players": [
                    # St. John's Red Storm (2025-26)
                    {"name": "Ian Jackson", "pts": 16.5, "reb": 4.5, "ast": 4.5, "pra": 25.5, "pr": 21.0, "pa": 21.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Oziyah Sellers", "pts": 12.5, "reb": 3.5, "ast": 3.5, "pra": 19.5, "pr": 16.0, "pa": 16.0, "ra": 7.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Joson Sanon", "pts": 10.5, "reb": 3.5, "ast": 4.5, "pra": 18.5, "pr": 14.0, "pa": 15.0, "ra": 8.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Bryce Hopkins", "pts": 14.5, "reb": 6.5, "ast": 2.5, "pra": 23.5, "pr": 21.0, "pa": 17.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Zuby Ejiofor", "pts": 11.5, "reb": 8.5, "ast": 1.5, "pra": 21.5, "pr": 20.0, "pa": 13.0, "ra": 10.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    # Michigan Wolverines (2025-26)
                    {"name": "Elliot Cadeau", "pts": 13.5, "reb": 3.5, "ast": 6.5, "pra": 23.5, "pr": 17.0, "pa": 20.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Roddy Gayle Jr.", "pts": 14.5, "reb": 4.5, "ast": 3.5, "pra": 22.5, "pr": 19.0, "pa": 18.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Nimari Burnett", "pts": 12.5, "reb": 3.5, "ast": 2.5, "pra": 18.5, "pr": 16.0, "pa": 15.0, "ra": 6.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Yaxel Lendeborg", "pts": 11.5, "reb": 6.5, "ast": 2.5, "pra": 20.5, "pr": 18.0, "pa": 14.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Aday Mara", "pts": 10.5, "reb": 7.5, "ast": 1.5, "pra": 19.5, "pr": 18.0, "pa": 12.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                ],
            },
            # Game 8: Arkansas vs Illinois
            "ncaab_game_8": {
                "home_team": "Arkansas Razorbacks",
                "away_team": "Illinois Fighting Illini",
                "commence_time": times["west"],
                "players": [
                    # Arkansas Razorbacks (2025-26)
                    {"name": "DJ Wagner", "pts": 15.5, "reb": 3.5, "ast": 5.5, "pra": 24.5, "pr": 19.0, "pa": 21.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Darius Acuff", "pts": 11.5, "reb": 3.5, "ast": 4.5, "pra": 19.5, "pr": 15.0, "pa": 16.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Karter Knox", "pts": 13.5, "reb": 5.5, "ast": 2.5, "pra": 21.5, "pr": 19.0, "pa": 16.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Trevon Brazile", "pts": 12.5, "reb": 6.5, "ast": 2.5, "pra": 21.5, "pr": 19.0, "pa": 15.0, "ra": 9.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Nick Pringle", "pts": 10.5, "reb": 7.5, "ast": 1.5, "pra": 19.5, "pr": 18.0, "pa": 12.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                    # Illinois Fighting Illini (2025-26)
                    {"name": "Keaton Wagler", "pts": 12.5, "reb": 3.5, "ast": 5.5, "pra": 21.5, "pr": 16.0, "pa": 18.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Kylan Boswell", "pts": 14.5, "reb": 3.5, "ast": 4.5, "pra": 22.5, "pr": 18.0, "pa": 19.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                    {"name": "Andrej Stojakovic", "pts": 15.5, "reb": 4.5, "ast": 2.5, "pra": 22.5, "pr": 20.0, "pa": 18.0, "ra": 7.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                    {"name": "Ben Humrichous", "pts": 11.5, "reb": 5.5, "ast": 2.5, "pra": 19.5, "pr": 17.0, "pa": 14.0, "ra": 8.0, "3pm": 2.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                    {"name": "Tomislav Ivisic", "pts": 13.5, "reb": 8.5, "ast": 2.5, "pra": 24.5, "pr": 22.0, "pa": 16.0, "ra": 11.0, "3pm": 1.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                ],
            },
        }
        
        # Check if this game exists
        if external_game_id not in game_props:
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": "Unknown",
                "away_team": "Unknown",
                "commence_time": times["early"],
                "bookmakers": [],
            }
        
        game = game_props[external_game_id]
        
        # Build markets from player data
        points_outcomes = []
        rebounds_outcomes = []
        assists_outcomes = []
        pra_outcomes = []
        pr_outcomes = []
        pa_outcomes = []
        ra_outcomes = []
        threes_outcomes = []
        steals_outcomes = []
        blocks_outcomes = []
        turnovers_outcomes = []
        
        for player in game["players"]:
            # Points
            points_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pts"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pts"]},
            ])
            # Rebounds
            rebounds_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["reb"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["reb"]},
            ])
            # Assists
            assists_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["ast"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["ast"]},
            ])
            # PRA (Points + Rebounds + Assists)
            pra_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pra"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pra"]},
            ])
            # PR (Points + Rebounds)
            pr_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pr"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pr"]},
            ])
            # PA (Points + Assists)
            pa_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pa"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pa"]},
            ])
            # RA (Rebounds + Assists)
            ra_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["ra"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["ra"]},
            ])
            # 3PM (Three Pointers Made)
            threes_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["3pm"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["3pm"]},
            ])
            # Steals
            steals_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["stl"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["stl"]},
            ])
            # Blocks
            blocks_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["blk"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["blk"]},
            ])
            # Turnovers
            turnovers_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["to"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["to"]},
            ])
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": game["home_team"],
            "away_team": game["away_team"],
            "commence_time": game["commence_time"],
            "bookmakers": [
                {
                    "key": "draftkings",
                    "title": "DraftKings",
                    "markets": [
                        {"key": "player_points", "outcomes": points_outcomes},
                        {"key": "player_rebounds", "outcomes": rebounds_outcomes},
                        {"key": "player_assists", "outcomes": assists_outcomes},
                        {"key": "player_points_rebounds_assists", "outcomes": pra_outcomes},
                        {"key": "player_points_rebounds", "outcomes": pr_outcomes},
                        {"key": "player_points_assists", "outcomes": pa_outcomes},
                        {"key": "player_rebounds_assists", "outcomes": ra_outcomes},
                        {"key": "player_threes", "outcomes": threes_outcomes},
                        {"key": "player_steals", "outcomes": steals_outcomes},
                        {"key": "player_blocks", "outcomes": blocks_outcomes},
                        {"key": "player_turnovers", "outcomes": turnovers_outcomes},
                    ],
                },
            ],
        }


# =============================================================================
# BetStack Provider (Secondary Fallback)
# =============================================================================

class BetStackProvider(XYZOddsProvider):
    """
    Secondary odds provider using BetStack API.
    
    Inherits from XYZOddsProvider since BetStack uses the same format.
    Falls back to this when primary Odds API fails.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_stubs: bool = False,
    ):
        settings = get_settings()
        # Use BetStack credentials instead of primary Odds API
        self.api_key = api_key or settings.betstack_api_key
        self.base_url = base_url or settings.betstack_api_base_url
        self.use_stubs = use_stubs
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make an authenticated request to BetStack API."""
        if not self.api_key:
            raise ValueError("BETSTACK_API_KEY not configured")
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key
        
        response = await self.client.get(url, params=params)
        
        # Handle HTTP errors gracefully
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (422, 429, 404):
                logger.warning(f"BetStack API {e.response.status_code}: {e.response.text[:200]}")
                return []
            else:
                logger.error(f"BetStack API error {e.response.status_code}: {e.response.text[:500]}")
                raise
        
        # Log API usage
        remaining = response.headers.get("x-requests-remaining", "unknown")
        used = response.headers.get("x-requests-used", "unknown")
        logger.info(f"BetStack API: {used} used, {remaining} remaining")
        
        return response.json()
