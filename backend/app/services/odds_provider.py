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
            # NFL Playoffs - Super Bowl LX (February 8, 2026)
            # Seahawks beat Rams 31-27 (NFC), Patriots beat Broncos 10-7 (AFC)
            return [
                # SUPER BOWL LX - February 8, 2026
                {
                    "id": "nfl_superbowl_lx",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["night"],
                    "home_team": "Seattle Seahawks",
                    "away_team": "New England Patriots",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Seattle Seahawks", "price": -120},
                                {"name": "New England Patriots", "price": 100}
                            ]}]
                        }
                    ],
                },
                # Game 2: Chiefs vs Bills - AFC Rivalry
                {
                    "id": "nfl_game_2",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["early"],
                    "home_team": "Kansas City Chiefs",
                    "away_team": "Buffalo Bills",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Kansas City Chiefs", "price": -145},
                                {"name": "Buffalo Bills", "price": 125}
                            ]}]
                        }
                    ],
                },
                # Game 3: 49ers vs Eagles - NFC Powerhouses
                {
                    "id": "nfl_game_3",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["early"],
                    "home_team": "San Francisco 49ers",
                    "away_team": "Philadelphia Eagles",
                    "bookmakers": [
                        {
                            "key": "betmgm",
                            "title": "BetMGM",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "San Francisco 49ers", "price": -135},
                                {"name": "Philadelphia Eagles", "price": 115}
                            ]}]
                        }
                    ],
                },
                # Game 4: Lions vs Cowboys - NFC Showdown
                {
                    "id": "nfl_game_4",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["late"],
                    "home_team": "Detroit Lions",
                    "away_team": "Dallas Cowboys",
                    "bookmakers": [
                        {
                            "key": "caesars",
                            "title": "Caesars",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Detroit Lions", "price": -155},
                                {"name": "Dallas Cowboys", "price": 135}
                            ]}]
                        }
                    ],
                },
                # Game 5: Ravens vs Bengals - AFC North
                {
                    "id": "nfl_game_5",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["late"],
                    "home_team": "Baltimore Ravens",
                    "away_team": "Cincinnati Bengals",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Baltimore Ravens", "price": -140},
                                {"name": "Cincinnati Bengals", "price": 120}
                            ]}]
                        }
                    ],
                },
                # Game 6: Dolphins vs Packers - Cross-Conference
                {
                    "id": "nfl_game_6",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["night"],
                    "home_team": "Miami Dolphins",
                    "away_team": "Green Bay Packers",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Miami Dolphins", "price": -130},
                                {"name": "Green Bay Packers", "price": 110}
                            ]}]
                        }
                    ],
                },
                # Game 7: Texans vs Rams - Young QBs
                {
                    "id": "nfl_game_7",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["west"],
                    "home_team": "Houston Texans",
                    "away_team": "Los Angeles Rams",
                    "bookmakers": [
                        {
                            "key": "betmgm",
                            "title": "BetMGM",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Houston Texans", "price": -125},
                                {"name": "Los Angeles Rams", "price": 105}
                            ]}]
                        }
                    ],
                },
                # Game 8: Buccaneers vs Jets - East Coast Battle
                {
                    "id": "nfl_game_8",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["west"],
                    "home_team": "Tampa Bay Buccaneers",
                    "away_team": "New York Jets",
                    "bookmakers": [
                        {
                            "key": "caesars",
                            "title": "Caesars",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Tampa Bay Buccaneers", "price": -110},
                                {"name": "New York Jets", "price": -110}
                            ]}]
                        }
                    ],
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
            # =================================================================
            # NFL GAMES - Super Bowl LX & Playoff Matchups (February 2026)
            # =================================================================
            # SUPER BOWL LX: Seahawks vs Patriots - February 8, 2026
            "nfl_superbowl_lx": {
                "home_team": "Seattle Seahawks",
                "away_team": "New England Patriots",
                "commence_time": times["night"],
                "players": [
                    # Seattle Seahawks
                    {"name": "Geno Smith", "pass_yds": 265.5, "pass_tds": 2.5, "pass_att": 34.5, "pass_comp": 23.5, "int": 0.5, "rush_yds": 18.5, "rush_att": 4.5},
                    {"name": "Kenneth Walker III", "rush_yds": 78.5, "rush_att": 17.5, "rush_tds": 0.5, "rec": 3.5, "rec_yds": 22.5},
                    {"name": "DK Metcalf", "rec": 5.5, "rec_yds": 72.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "Tyler Lockett", "rec": 4.5, "rec_yds": 55.5, "rec_tds": 0.5, "targets": 6.5},
                    {"name": "Jaxon Smith-Njigba", "rec": 5.5, "rec_yds": 58.5, "rec_tds": 0.5, "targets": 7.5},
                    # New England Patriots
                    {"name": "Drake Maye", "pass_yds": 245.5, "pass_tds": 1.5, "pass_att": 32.5, "pass_comp": 20.5, "int": 1.0, "rush_yds": 22.5, "rush_att": 5.5},
                    {"name": "Rhamondre Stevenson", "rush_yds": 72.5, "rush_att": 16.5, "rush_tds": 0.5, "rec": 3.5, "rec_yds": 18.5},
                    {"name": "Ja'Lynn Polk", "rec": 4.5, "rec_yds": 52.5, "rec_tds": 0.5, "targets": 7.5},
                    {"name": "Kendrick Bourne", "rec": 3.5, "rec_yds": 42.5, "rec_tds": 0.5, "targets": 5.5},
                    {"name": "Hunter Henry", "rec": 4.5, "rec_yds": 38.5, "rec_tds": 0.5, "targets": 6.5},
                ],
            },
            # Game 2: Chiefs vs Bills - AFC Rivalry
            "nfl_game_2": {
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "commence_time": times["early"],
                "players": [
                    # Kansas City Chiefs
                    {"name": "Patrick Mahomes", "pass_yds": 285.5, "pass_tds": 2.5, "pass_att": 36.5, "pass_comp": 25.5, "int": 0.5, "rush_yds": 28.5, "rush_att": 4.5},
                    {"name": "Isiah Pacheco", "rush_yds": 68.5, "rush_att": 15.5, "rush_tds": 0.5, "rec": 2.5, "rec_yds": 15.5},
                    {"name": "Travis Kelce", "rec": 6.5, "rec_yds": 68.5, "rec_tds": 0.5, "targets": 9.5},
                    {"name": "Rashee Rice", "rec": 5.5, "rec_yds": 62.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "Hollywood Brown", "rec": 3.5, "rec_yds": 42.5, "rec_tds": 0.5, "targets": 5.5},
                    # Buffalo Bills
                    {"name": "Josh Allen", "pass_yds": 275.5, "pass_tds": 2.5, "pass_att": 35.5, "pass_comp": 23.5, "int": 0.5, "rush_yds": 35.5, "rush_att": 6.5},
                    {"name": "James Cook", "rush_yds": 72.5, "rush_att": 14.5, "rush_tds": 0.5, "rec": 3.5, "rec_yds": 25.5},
                    {"name": "Stefon Diggs", "rec": 6.5, "rec_yds": 78.5, "rec_tds": 0.5, "targets": 10.5},
                    {"name": "Dalton Kincaid", "rec": 5.5, "rec_yds": 52.5, "rec_tds": 0.5, "targets": 7.5},
                    {"name": "Gabe Davis", "rec": 3.5, "rec_yds": 45.5, "rec_tds": 0.5, "targets": 5.5},
                ],
            },
            # Game 3: 49ers vs Eagles - NFC Powerhouses
            "nfl_game_3": {
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "commence_time": times["early"],
                "players": [
                    # San Francisco 49ers
                    {"name": "Brock Purdy", "pass_yds": 255.5, "pass_tds": 2.5, "pass_att": 28.5, "pass_comp": 20.5, "int": 0.5, "rush_yds": 12.5, "rush_att": 3.5},
                    {"name": "Christian McCaffrey", "rush_yds": 85.5, "rush_att": 18.5, "rush_tds": 1.0, "rec": 4.5, "rec_yds": 32.5},
                    {"name": "Deebo Samuel", "rec": 4.5, "rec_yds": 58.5, "rec_tds": 0.5, "targets": 7.5},
                    {"name": "Brandon Aiyuk", "rec": 5.5, "rec_yds": 68.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "George Kittle", "rec": 4.5, "rec_yds": 52.5, "rec_tds": 0.5, "targets": 6.5},
                    # Philadelphia Eagles
                    {"name": "Jalen Hurts", "pass_yds": 235.5, "pass_tds": 1.5, "pass_att": 30.5, "pass_comp": 19.5, "int": 0.5, "rush_yds": 42.5, "rush_att": 8.5},
                    {"name": "Saquon Barkley", "rush_yds": 88.5, "rush_att": 19.5, "rush_tds": 1.0, "rec": 3.5, "rec_yds": 25.5},
                    {"name": "AJ Brown", "rec": 5.5, "rec_yds": 72.5, "rec_tds": 0.5, "targets": 9.5},
                    {"name": "DeVonta Smith", "rec": 5.5, "rec_yds": 62.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "Dallas Goedert", "rec": 4.5, "rec_yds": 42.5, "rec_tds": 0.5, "targets": 6.5},
                ],
            },
            # Game 4: Lions vs Cowboys - NFC Showdown
            "nfl_game_4": {
                "home_team": "Detroit Lions",
                "away_team": "Dallas Cowboys",
                "commence_time": times["late"],
                "players": [
                    # Detroit Lions
                    {"name": "Jared Goff", "pass_yds": 275.5, "pass_tds": 2.5, "pass_att": 32.5, "pass_comp": 23.5, "int": 0.5, "rush_yds": 5.5, "rush_att": 2.5},
                    {"name": "Jahmyr Gibbs", "rush_yds": 75.5, "rush_att": 14.5, "rush_tds": 0.5, "rec": 4.5, "rec_yds": 35.5},
                    {"name": "Amon-Ra St. Brown", "rec": 7.5, "rec_yds": 82.5, "rec_tds": 0.5, "targets": 11.5},
                    {"name": "Sam LaPorta", "rec": 5.5, "rec_yds": 55.5, "rec_tds": 0.5, "targets": 7.5},
                    {"name": "David Montgomery", "rush_yds": 48.5, "rush_att": 12.5, "rush_tds": 0.5, "rec": 2.5, "rec_yds": 15.5},
                    # Dallas Cowboys
                    {"name": "Dak Prescott", "pass_yds": 268.5, "pass_tds": 2.5, "pass_att": 34.5, "pass_comp": 22.5, "int": 1.0, "rush_yds": 15.5, "rush_att": 3.5},
                    {"name": "Rico Dowdle", "rush_yds": 62.5, "rush_att": 14.5, "rush_tds": 0.5, "rec": 3.5, "rec_yds": 22.5},
                    {"name": "CeeDee Lamb", "rec": 7.5, "rec_yds": 92.5, "rec_tds": 0.5, "targets": 12.5},
                    {"name": "Jake Ferguson", "rec": 4.5, "rec_yds": 42.5, "rec_tds": 0.5, "targets": 6.5},
                    {"name": "Brandin Cooks", "rec": 3.5, "rec_yds": 38.5, "rec_tds": 0.5, "targets": 5.5},
                ],
            },
            # Game 5: Ravens vs Bengals - AFC North
            "nfl_game_5": {
                "home_team": "Baltimore Ravens",
                "away_team": "Cincinnati Bengals",
                "commence_time": times["late"],
                "players": [
                    # Baltimore Ravens
                    {"name": "Lamar Jackson", "pass_yds": 225.5, "pass_tds": 1.5, "pass_att": 28.5, "pass_comp": 18.5, "int": 0.5, "rush_yds": 65.5, "rush_att": 12.5},
                    {"name": "Derrick Henry", "rush_yds": 95.5, "rush_att": 22.5, "rush_tds": 1.0, "rec": 1.5, "rec_yds": 8.5},
                    {"name": "Zay Flowers", "rec": 5.5, "rec_yds": 62.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "Mark Andrews", "rec": 4.5, "rec_yds": 48.5, "rec_tds": 0.5, "targets": 6.5},
                    {"name": "Rashod Bateman", "rec": 3.5, "rec_yds": 42.5, "rec_tds": 0.5, "targets": 5.5},
                    # Cincinnati Bengals
                    {"name": "Joe Burrow", "pass_yds": 285.5, "pass_tds": 2.5, "pass_att": 38.5, "pass_comp": 26.5, "int": 0.5, "rush_yds": 15.5, "rush_att": 3.5},
                    {"name": "Zack Moss", "rush_yds": 58.5, "rush_att": 14.5, "rush_tds": 0.5, "rec": 2.5, "rec_yds": 18.5},
                    {"name": "Ja'Marr Chase", "rec": 7.5, "rec_yds": 98.5, "rec_tds": 1.0, "targets": 11.5},
                    {"name": "Tee Higgins", "rec": 5.5, "rec_yds": 68.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "Mike Gesicki", "rec": 3.5, "rec_yds": 35.5, "rec_tds": 0.5, "targets": 5.5},
                ],
            },
            # Game 6: Dolphins vs Packers - Cross-Conference
            "nfl_game_6": {
                "home_team": "Miami Dolphins",
                "away_team": "Green Bay Packers",
                "commence_time": times["night"],
                "players": [
                    # Miami Dolphins
                    {"name": "Tua Tagovailoa", "pass_yds": 275.5, "pass_tds": 2.5, "pass_att": 35.5, "pass_comp": 25.5, "int": 0.5, "rush_yds": 8.5, "rush_att": 2.5},
                    {"name": "De'Von Achane", "rush_yds": 72.5, "rush_att": 13.5, "rush_tds": 0.5, "rec": 4.5, "rec_yds": 35.5},
                    {"name": "Tyreek Hill", "rec": 6.5, "rec_yds": 88.5, "rec_tds": 0.5, "targets": 10.5},
                    {"name": "Jaylen Waddle", "rec": 5.5, "rec_yds": 65.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "Raheem Mostert", "rush_yds": 45.5, "rush_att": 10.5, "rush_tds": 0.5, "rec": 2.5, "rec_yds": 15.5},
                    # Green Bay Packers
                    {"name": "Jordan Love", "pass_yds": 265.5, "pass_tds": 2.5, "pass_att": 34.5, "pass_comp": 22.5, "int": 1.0, "rush_yds": 18.5, "rush_att": 4.5},
                    {"name": "Josh Jacobs", "rush_yds": 78.5, "rush_att": 18.5, "rush_tds": 0.5, "rec": 3.5, "rec_yds": 22.5},
                    {"name": "Jayden Reed", "rec": 5.5, "rec_yds": 68.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "Christian Watson", "rec": 3.5, "rec_yds": 52.5, "rec_tds": 0.5, "targets": 5.5},
                    {"name": "Romeo Doubs", "rec": 4.5, "rec_yds": 48.5, "rec_tds": 0.5, "targets": 6.5},
                ],
            },
            # Game 7: Texans vs Rams - Young QBs
            "nfl_game_7": {
                "home_team": "Houston Texans",
                "away_team": "Los Angeles Rams",
                "commence_time": times["west"],
                "players": [
                    # Houston Texans
                    {"name": "CJ Stroud", "pass_yds": 278.5, "pass_tds": 2.5, "pass_att": 35.5, "pass_comp": 24.5, "int": 0.5, "rush_yds": 15.5, "rush_att": 3.5},
                    {"name": "Joe Mixon", "rush_yds": 75.5, "rush_att": 17.5, "rush_tds": 0.5, "rec": 3.5, "rec_yds": 25.5},
                    {"name": "Nico Collins", "rec": 5.5, "rec_yds": 78.5, "rec_tds": 0.5, "targets": 9.5},
                    {"name": "Tank Dell", "rec": 4.5, "rec_yds": 55.5, "rec_tds": 0.5, "targets": 7.5},
                    {"name": "Stefon Diggs", "rec": 5.5, "rec_yds": 62.5, "rec_tds": 0.5, "targets": 8.5},
                    # Los Angeles Rams
                    {"name": "Matthew Stafford", "pass_yds": 268.5, "pass_tds": 2.5, "pass_att": 34.5, "pass_comp": 22.5, "int": 0.5, "rush_yds": 5.5, "rush_att": 2.5},
                    {"name": "Kyren Williams", "rush_yds": 72.5, "rush_att": 16.5, "rush_tds": 0.5, "rec": 3.5, "rec_yds": 25.5},
                    {"name": "Puka Nacua", "rec": 7.5, "rec_yds": 92.5, "rec_tds": 0.5, "targets": 11.5},
                    {"name": "Cooper Kupp", "rec": 6.5, "rec_yds": 72.5, "rec_tds": 0.5, "targets": 9.5},
                    {"name": "Tutu Atwell", "rec": 3.5, "rec_yds": 35.5, "rec_tds": 0.5, "targets": 5.5},
                ],
            },
            # Game 8: Buccaneers vs Jets - East Coast Battle
            "nfl_game_8": {
                "home_team": "Tampa Bay Buccaneers",
                "away_team": "New York Jets",
                "commence_time": times["west"],
                "players": [
                    # Tampa Bay Buccaneers
                    {"name": "Baker Mayfield", "pass_yds": 258.5, "pass_tds": 2.5, "pass_att": 33.5, "pass_comp": 21.5, "int": 1.0, "rush_yds": 15.5, "rush_att": 4.5},
                    {"name": "Rachaad White", "rush_yds": 65.5, "rush_att": 15.5, "rush_tds": 0.5, "rec": 4.5, "rec_yds": 32.5},
                    {"name": "Mike Evans", "rec": 5.5, "rec_yds": 78.5, "rec_tds": 0.5, "targets": 9.5},
                    {"name": "Chris Godwin", "rec": 6.5, "rec_yds": 72.5, "rec_tds": 0.5, "targets": 10.5},
                    {"name": "Cade Otton", "rec": 4.5, "rec_yds": 42.5, "rec_tds": 0.5, "targets": 6.5},
                    # New York Jets
                    {"name": "Aaron Rodgers", "pass_yds": 255.5, "pass_tds": 2.5, "pass_att": 32.5, "pass_comp": 21.5, "int": 0.5, "rush_yds": 8.5, "rush_att": 3.5},
                    {"name": "Breece Hall", "rush_yds": 78.5, "rush_att": 17.5, "rush_tds": 0.5, "rec": 4.5, "rec_yds": 35.5},
                    {"name": "Garrett Wilson", "rec": 6.5, "rec_yds": 78.5, "rec_tds": 0.5, "targets": 10.5},
                    {"name": "Allen Lazard", "rec": 3.5, "rec_yds": 42.5, "rec_tds": 0.5, "targets": 5.5},
                    {"name": "Mike Williams", "rec": 3.5, "rec_yds": 48.5, "rec_tds": 0.5, "targets": 6.5},
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
        
        # Check if this is an NFL game (has pass_yds instead of pts)
        is_nfl = game["players"] and "pass_yds" in game["players"][0]
        
        if is_nfl:
            # NFL-specific prop markets
            pass_yds_outcomes = []
            pass_tds_outcomes = []
            pass_att_outcomes = []
            rush_yds_outcomes = []
            rush_att_outcomes = []
            rec_outcomes = []
            rec_yds_outcomes = []
            
            for player in game["players"]:
                # Passing yards (QBs)
                if "pass_yds" in player:
                    pass_yds_outcomes.extend([
                        {"name": "Over", "description": player["name"], "price": -110, "point": player["pass_yds"]},
                        {"name": "Under", "description": player["name"], "price": -110, "point": player["pass_yds"]},
                    ])
                # Pass TDs
                if "pass_tds" in player:
                    pass_tds_outcomes.extend([
                        {"name": "Over", "description": player["name"], "price": -110, "point": player["pass_tds"]},
                        {"name": "Under", "description": player["name"], "price": -110, "point": player["pass_tds"]},
                    ])
                # Pass attempts
                if "pass_att" in player:
                    pass_att_outcomes.extend([
                        {"name": "Over", "description": player["name"], "price": -110, "point": player["pass_att"]},
                        {"name": "Under", "description": player["name"], "price": -110, "point": player["pass_att"]},
                    ])
                # Rushing yards
                if "rush_yds" in player:
                    rush_yds_outcomes.extend([
                        {"name": "Over", "description": player["name"], "price": -110, "point": player["rush_yds"]},
                        {"name": "Under", "description": player["name"], "price": -110, "point": player["rush_yds"]},
                    ])
                # Rushing attempts
                if "rush_att" in player:
                    rush_att_outcomes.extend([
                        {"name": "Over", "description": player["name"], "price": -110, "point": player["rush_att"]},
                        {"name": "Under", "description": player["name"], "price": -110, "point": player["rush_att"]},
                    ])
                # Receptions
                if "rec" in player:
                    rec_outcomes.extend([
                        {"name": "Over", "description": player["name"], "price": -110, "point": player["rec"]},
                        {"name": "Under", "description": player["name"], "price": -110, "point": player["rec"]},
                    ])
                # Receiving yards
                if "rec_yds" in player:
                    rec_yds_outcomes.extend([
                        {"name": "Over", "description": player["name"], "price": -110, "point": player["rec_yds"]},
                        {"name": "Under", "description": player["name"], "price": -110, "point": player["rec_yds"]},
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
                            {"key": "player_pass_yds", "outcomes": pass_yds_outcomes},
                            {"key": "player_pass_tds", "outcomes": pass_tds_outcomes},
                            {"key": "player_pass_att", "outcomes": pass_att_outcomes},
                            {"key": "player_rush_yds", "outcomes": rush_yds_outcomes},
                            {"key": "player_rush_att", "outcomes": rush_att_outcomes},
                            {"key": "player_receptions", "outcomes": rec_outcomes},
                            {"key": "player_rec_yds", "outcomes": rec_yds_outcomes},
                        ],
                    },
                ],
            }
        
        # Basketball prop markets (NBA/NCAAB)
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


# =============================================================================
# ESPN Schedule Provider (Free NCAAB & NFL Backup)
# =============================================================================

# NFL Team power ratings (higher = better) for generating realistic odds
NFL_TEAM_RATINGS = {
    # AFC
    "Kansas City Chiefs": 95, "Buffalo Bills": 94, "Baltimore Ravens": 93,
    "Cincinnati Bengals": 88, "Miami Dolphins": 87, "Pittsburgh Steelers": 85,
    "Cleveland Browns": 82, "Houston Texans": 84, "Indianapolis Colts": 78,
    "Jacksonville Jaguars": 80, "Tennessee Titans": 75, "Las Vegas Raiders": 74,
    "Los Angeles Chargers": 83, "Denver Broncos": 76, "New York Jets": 79,
    "New England Patriots": 72,
    # NFC
    "San Francisco 49ers": 94, "Philadelphia Eagles": 92, "Dallas Cowboys": 86,
    "Detroit Lions": 91, "Green Bay Packers": 85, "Seattle Seahawks": 82,
    "Los Angeles Rams": 84, "Arizona Cardinals": 73, "Minnesota Vikings": 83,
    "Chicago Bears": 77, "Tampa Bay Buccaneers": 81, "New Orleans Saints": 78,
    "Atlanta Falcons": 76, "Carolina Panthers": 70, "New York Giants": 71,
    "Washington Commanders": 80,
}

# NFL Rosters (key offensive players for props)
NFL_ROSTERS = {
    "Kansas City Chiefs": ["Patrick Mahomes", "Travis Kelce", "Rashee Rice", "Isiah Pacheco", "Hollywood Brown"],
    "Buffalo Bills": ["Josh Allen", "Stefon Diggs", "James Cook", "Dalton Kincaid", "Gabe Davis"],
    "Baltimore Ravens": ["Lamar Jackson", "Derrick Henry", "Zay Flowers", "Mark Andrews", "Rashod Bateman"],
    "San Francisco 49ers": ["Brock Purdy", "Christian McCaffrey", "Deebo Samuel", "Brandon Aiyuk", "George Kittle"],
    "Philadelphia Eagles": ["Jalen Hurts", "Saquon Barkley", "AJ Brown", "DeVonta Smith", "Dallas Goedert"],
    "Detroit Lions": ["Jared Goff", "Jahmyr Gibbs", "Amon-Ra St. Brown", "Sam LaPorta", "David Montgomery"],
    "Dallas Cowboys": ["Dak Prescott", "CeeDee Lamb", "Rico Dowdle", "Jake Ferguson", "Brandin Cooks"],
    "Miami Dolphins": ["Tua Tagovailoa", "Tyreek Hill", "Jaylen Waddle", "De'Von Achane", "Raheem Mostert"],
    "Cincinnati Bengals": ["Joe Burrow", "Ja'Marr Chase", "Tee Higgins", "Zack Moss", "Mike Gesicki"],
    "Green Bay Packers": ["Jordan Love", "Josh Jacobs", "Jayden Reed", "Christian Watson", "Romeo Doubs"],
    "Seattle Seahawks": ["Geno Smith", "Kenneth Walker III", "DK Metcalf", "Tyler Lockett", "Jaxon Smith-Njigba"],
    "Los Angeles Rams": ["Matthew Stafford", "Kyren Williams", "Puka Nacua", "Cooper Kupp", "Tutu Atwell"],
    "Minnesota Vikings": ["Sam Darnold", "Aaron Jones", "Justin Jefferson", "Jordan Addison", "TJ Hockenson"],
    "Houston Texans": ["CJ Stroud", "Joe Mixon", "Nico Collins", "Tank Dell", "Stefon Diggs"],
    "Pittsburgh Steelers": ["Russell Wilson", "Najee Harris", "George Pickens", "Pat Freiermuth", "Calvin Austin"],
    "Los Angeles Chargers": ["Justin Herbert", "JK Dobbins", "Keenan Allen", "Quentin Johnston", "Joshua Palmer"],
    "Tampa Bay Buccaneers": ["Baker Mayfield", "Rachaad White", "Mike Evans", "Chris Godwin", "Cade Otton"],
    "New Orleans Saints": ["Derek Carr", "Alvin Kamara", "Chris Olave", "Rashid Shaheed", "Juwan Johnson"],
    "Cleveland Browns": ["Deshaun Watson", "Nick Chubb", "Amari Cooper", "Jerry Jeudy", "David Njoku"],
    "Jacksonville Jaguars": ["Trevor Lawrence", "Travis Etienne", "Christian Kirk", "Gabe Davis", "Evan Engram"],
    "New York Jets": ["Aaron Rodgers", "Breece Hall", "Garrett Wilson", "Allen Lazard", "Mike Williams"],
    "Washington Commanders": ["Jayden Daniels", "Brian Robinson Jr.", "Terry McLaurin", "Jahan Dotson", "Zach Ertz"],
    "Indianapolis Colts": ["Anthony Richardson", "Jonathan Taylor", "Michael Pittman Jr.", "Josh Downs", "Adonai Mitchell"],
    "Denver Broncos": ["Bo Nix", "Javonte Williams", "Courtland Sutton", "Marvin Mims Jr.", "Troy Franklin"],
    "Chicago Bears": ["Caleb Williams", "D'Andre Swift", "DJ Moore", "Keenan Allen", "Rome Odunze"],
    "Arizona Cardinals": ["Kyler Murray", "James Conner", "Marvin Harrison Jr.", "Michael Wilson", "Trey McBride"],
    "Atlanta Falcons": ["Kirk Cousins", "Bijan Robinson", "Drake London", "Darnell Mooney", "Kyle Pitts"],
    "Tennessee Titans": ["Will Levis", "Tony Pollard", "DeAndre Hopkins", "Calvin Ridley", "Chig Okonkwo"],
    "Las Vegas Raiders": ["Gardner Minshew", "Zamir White", "Davante Adams", "Jakobi Meyers", "Brock Bowers"],
    "New York Giants": ["Daniel Jones", "Saquon Barkley", "Malik Nabers", "Wan'Dale Robinson", "Darius Slayton"],
    "Carolina Panthers": ["Bryce Young", "Chuba Hubbard", "Diontae Johnson", "Adam Thielen", "Jonathan Mingo"],
    "New England Patriots": ["Drake Maye", "Rhamondre Stevenson", "Ja'Lynn Polk", "Kendrick Bourne", "Hunter Henry"],
}

# Default NFL roster for teams not in the list
DEFAULT_NFL_ROSTER = ["QB Starter", "RB Starter", "WR1 Starter", "WR2 Starter", "TE Starter"]

# Team power ratings (higher = better) for generating realistic odds
NCAAB_TEAM_RATINGS = {
    # Top 25 teams with power ratings
    "Duke Blue Devils": 95, "Kansas Jayhawks": 94, "Houston Cougars": 93,
    "Kentucky Wildcats": 92, "Gonzaga Bulldogs": 91, "UConn Huskies": 90,
    "Purdue Boilermakers": 89, "Florida Gators": 88, "UCLA Bruins": 87,
    "Arizona Wildcats": 86, "Alabama Crimson Tide": 85, "Tennessee Volunteers": 84,
    "St. John's Red Storm": 83, "Michigan Wolverines": 82, "Arkansas Razorbacks": 81,
    "Illinois Fighting Illini": 80, "Iowa State Cyclones": 79, "BYU Cougars": 78,
    "Texas Tech Red Raiders": 77, "Louisville Cardinals": 76, "Marquette Golden Eagles": 75,
    "Michigan State Spartans": 74, "North Carolina Tar Heels": 73, "Ohio State Buckeyes": 72,
    "Wisconsin Badgers": 71, "Texas Longhorns": 70, "Auburn Tigers": 69,
    "Baylor Bears": 68, "Indiana Hoosiers": 67, "Creighton Bluejays": 66,
}

# Rosters for generating props (5 starters per team)
NCAAB_ROSTERS = {
    "Kansas Jayhawks": ["Darryn Peterson", "Melvin Council Jr.", "Jayden Dawson", "Tre White", "Flory Bidunga"],
    "Duke Blue Devils": ["Caleb Foster", "Isaiah Evans", "Dame Sarr", "Cameron Boozer", "Patrick Ngongba"],
    "Kentucky Wildcats": ["Jaland Lowe", "Otega Oweh", "Denzel Aberdeen", "Mo Dioubate", "Brandon Garrison"],
    "Houston Cougars": ["Milos Uzan", "Emanuel Sharp", "Isiah Harwell", "Chris Cenac Jr.", "Joseph Tugler"],
    "Gonzaga Bulldogs": ["Braeden Smith", "Adam Miller", "Jalen Warley", "Braden Huff", "Graham Ike"],
    "UConn Huskies": ["Silas Demary Jr.", "Solo Ball", "Braylon Mullins", "Alex Karaban", "Tarris Reed Jr."],
    "Purdue Boilermakers": ["Braden Smith", "CJ Cox", "Fletcher Loyer", "Trey Kaufman-Renn", "Oscar Cluff"],
    "Florida Gators": ["Xaivian Lee", "Boogie Fland", "Thomas Haugh", "Alex Condon", "Rueben Chinyelu"],
    "UCLA Bruins": ["Donovan Dent", "Skyy Clark", "Eric Dailey Jr.", "Tyler Bilodeau", "Xavier Booker"],
    "Arizona Wildcats": ["Jaden Bradley", "Brayden Burries", "Anthony Dell'Orso", "Koa Peat", "Tobe Awaka"],
    "Alabama Crimson Tide": ["Labaron Philon", "Aden Holloway", "Latrell Wrightsell Jr.", "Taylor Bol Bowen", "Aiden Sherrell"],
    "Tennessee Volunteers": ["Ja'Kobi Gillespie", "Amaree Abram", "Nate Ament", "Cade Phillips", "Felix Okpara"],
    "St. John's Red Storm": ["Ian Jackson", "Oziyah Sellers", "Joson Sanon", "Bryce Hopkins", "Zuby Ejiofor"],
    "Michigan Wolverines": ["Elliot Cadeau", "Roddy Gayle Jr.", "Nimari Burnett", "Yaxel Lendeborg", "Aday Mara"],
    "Arkansas Razorbacks": ["DJ Wagner", "Darius Acuff", "Karter Knox", "Trevon Brazile", "Nick Pringle"],
    "Illinois Fighting Illini": ["Keaton Wagler", "Kylan Boswell", "Andrej Stojakovic", "Ben Humrichous", "Tomislav Ivisic"],
    "Iowa State Cyclones": ["Tamin Lipsey", "Jamarion Batemon", "Milan Momcilovic", "Joshua Jefferson", "Blake Buchanan"],
    "BYU Cougars": ["Rob Wright", "Kennard Davis", "Richie Saunders", "AJ Dybantsa", "Keba Keita"],
    "Texas Tech Red Raiders": ["Christian Anderson", "Tyeree Bryan", "LeJuan Watts", "JT Toppin", "Luke Bamgboye"],
    "Louisville Cardinals": ["Mikel Brown Jr.", "Ryan Conwell", "Isaac McKneely", "J'Vonne Hadley", "Sananda Fru"],
    "North Carolina Tar Heels": ["RJ Davis", "Seth Trimble", "Elliot Cadeau", "Jalen Washington", "Jae'Lyn Withers"],
    "Auburn Tigers": ["Miles Kelly", "Chad Baker-Mazara", "Denver Jones", "Johni Broome", "Dylan Cardwell"],
    "Baylor Bears": ["Jayden Nunn", "VJ Edgecombe", "Jeremy Roach", "Josh Ojianwuna", "Norchad Omier"],
}

# Default roster for teams not in the list
DEFAULT_ROSTER = ["Player One", "Player Two", "Player Three", "Player Four", "Player Five"]


class ESPNScheduleProvider:
    """
    Free schedule provider using ESPN's public API.
    
    Supports NCAAB and NFL - fetches real game schedules and generates 
    realistic odds/props based on team power ratings.
    """
    
    # ESPN API base URLs by sport
    ESPN_URLS = {
        "basketball_ncaab": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball",
        "americanfootball_nfl": "https://site.api.espn.com/apis/site/v2/sports/football/nfl",
    }
    
    def __init__(self, sport_key: str = "basketball_ncaab"):
        self._client: Optional[httpx.AsyncClient] = None
        self.sport_key = sport_key
        self.base_url = self.ESPN_URLS.get(sport_key, self.ESPN_URLS["basketball_ncaab"])
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def fetch_todays_games(self) -> list[dict[str, Any]]:
        """
        Fetch today's games from ESPN for the configured sport.
        
        Returns:
            List of game dictionaries with teams, times, and generated odds
        """
        try:
            # ESPN scoreboard endpoint (today's games)
            url = f"{self.base_url}/scoreboard"
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            events = data.get("events", [])
            
            games = []
            times = _get_stub_game_times()
            time_slots = ["early", "mid", "late", "night", "west"]
            
            # Get sport-specific settings
            is_nfl = self.sport_key == "americanfootball_nfl"
            team_ratings = NFL_TEAM_RATINGS if is_nfl else NCAAB_TEAM_RATINGS
            home_advantage = 2.5 if is_nfl else 3  # NFL home field is ~2.5 pts
            sport_title = "NFL" if is_nfl else "NCAAB"
            game_prefix = "nfl_espn" if is_nfl else "ncaab_espn"
            max_games = 16 if is_nfl else 12
            
            for i, event in enumerate(events[:max_games]):
                try:
                    competition = event.get("competitions", [{}])[0]
                    competitors = competition.get("competitors", [])
                    
                    if len(competitors) < 2:
                        continue
                    
                    # ESPN uses homeAway field
                    home_comp = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
                    away_comp = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])
                    
                    home_team = home_comp.get("team", {}).get("displayName", "Unknown Home")
                    away_team = away_comp.get("team", {}).get("displayName", "Unknown Away")
                    
                    # Get game time or use slot time
                    game_time = event.get("date", times[time_slots[i % len(time_slots)]])
                    
                    # Generate odds based on team ratings
                    home_rating = team_ratings.get(home_team, 75 if is_nfl else 60)
                    away_rating = team_ratings.get(away_team, 75 if is_nfl else 60)
                    
                    # Home field/court advantage
                    home_adjusted = home_rating + home_advantage
                    
                    # Convert rating difference to American odds
                    diff = home_adjusted - away_rating
                    home_odds, away_odds = self._rating_diff_to_odds(diff)
                    
                    game_id = f"{game_prefix}_{event.get('id', i)}"
                    
                    games.append({
                        "id": game_id,
                        "sport_key": self.sport_key,
                        "sport_title": sport_title,
                        "commence_time": game_time,
                        "home_team": home_team,
                        "away_team": away_team,
                        "bookmakers": [
                            {
                                "key": "consensus",
                                "title": "Consensus",
                                "markets": [{"key": "h2h", "outcomes": [
                                    {"name": home_team, "price": home_odds},
                                    {"name": away_team, "price": away_odds}
                                ]}]
                            }
                        ],
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing ESPN event: {e}")
                    continue
            
            logger.info(f"ESPN fetched {len(games)} NCAAB games for today")
            return games
            
        except Exception as e:
            logger.error(f"ESPN API error: {e}")
            return []
    
    def _rating_diff_to_odds(self, diff: float) -> tuple[int, int]:
        """
        Convert rating difference to American odds.
        
        Args:
            diff: Rating difference (positive = home favored)
        
        Returns:
            Tuple of (home_odds, away_odds) in American format
        """
        # Clamp difference to reasonable range
        diff = max(-20, min(20, diff))
        
        if abs(diff) < 2:
            # Close game: near pick'em
            return -110, -110
        elif diff > 0:
            # Home favored
            fav_odds = int(-100 - (diff * 10))
            dog_odds = int(100 + (diff * 8))
            return fav_odds, dog_odds
        else:
            # Away favored
            diff = abs(diff)
            fav_odds = int(-100 - (diff * 10))
            dog_odds = int(100 + (diff * 8))
            return dog_odds, fav_odds
    
    async def fetch_player_props(self, game_id: str, home_team: str, away_team: str) -> dict[str, Any]:
        """
        Generate player props for a game based on team rosters.
        
        Args:
            game_id: Game identifier
            home_team: Home team name
            away_team: Away team name
        
        Returns:
            Props data structure matching stub format
        """
        times = _get_stub_game_times()
        is_nfl = self.sport_key == "americanfootball_nfl"
        
        if is_nfl:
            home_roster = NFL_ROSTERS.get(home_team, DEFAULT_NFL_ROSTER)
            away_roster = NFL_ROSTERS.get(away_team, DEFAULT_NFL_ROSTER)
        else:
            home_roster = NCAAB_ROSTERS.get(home_team, DEFAULT_ROSTER)
            away_roster = NCAAB_ROSTERS.get(away_team, DEFAULT_ROSTER)
        
        players = []
        
        # Generate props for home team
        for i, name in enumerate(home_roster):
            if is_nfl:
                players.append(self._generate_nfl_player_props(name, i))
            else:
                players.append(self._generate_ncaab_player_props(name, i))
        
        # Generate props for away team
        for i, name in enumerate(away_roster):
            if is_nfl:
                players.append(self._generate_nfl_player_props(name, i))
            else:
                players.append(self._generate_ncaab_player_props(name, i))
        
        return {
            "id": game_id,
            "sport_key": self.sport_key,
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": times["early"],
            "players": players,
        }
    
    def _generate_nfl_player_props(self, name: str, position_idx: int) -> dict[str, float]:
        """
        Generate realistic NFL player props based on position.
        
        Position index: 0=QB, 1=RB, 2-3=WR, 4=TE
        """
        import random
        
        if position_idx == 0:  # QB
            return {
                "name": name,
                "pass_yds": round(random.uniform(220.0, 280.0) * 2) / 2,
                "pass_tds": round(random.uniform(1.5, 2.5) * 2) / 2,
                "pass_att": round(random.uniform(28.0, 36.0) * 2) / 2,
                "pass_comp": round(random.uniform(18.0, 26.0) * 2) / 2,
                "int": round(random.uniform(0.5, 1.0) * 2) / 2,
                "rush_yds": round(random.uniform(8.0, 25.0) * 2) / 2,
                "rush_att": round(random.uniform(2.0, 5.0) * 2) / 2,
            }
        elif position_idx == 1:  # RB
            return {
                "name": name,
                "rush_yds": round(random.uniform(55.0, 85.0) * 2) / 2,
                "rush_att": round(random.uniform(12.0, 18.0) * 2) / 2,
                "rush_tds": round(random.uniform(0.5, 1.0) * 2) / 2,
                "rec": round(random.uniform(2.0, 4.0) * 2) / 2,
                "rec_yds": round(random.uniform(15.0, 35.0) * 2) / 2,
            }
        elif position_idx in (2, 3):  # WR
            return {
                "name": name,
                "rec": round(random.uniform(4.0, 7.0) * 2) / 2,
                "rec_yds": round(random.uniform(50.0, 85.0) * 2) / 2,
                "rec_tds": round(random.uniform(0.5, 1.0) * 2) / 2,
                "targets": round(random.uniform(6.0, 10.0) * 2) / 2,
            }
        else:  # TE (position_idx == 4)
            return {
                "name": name,
                "rec": round(random.uniform(3.0, 5.0) * 2) / 2,
                "rec_yds": round(random.uniform(35.0, 55.0) * 2) / 2,
                "rec_tds": round(random.uniform(0.5, 0.5) * 2) / 2,
                "targets": round(random.uniform(4.0, 7.0) * 2) / 2,
            }
    
    def _generate_ncaab_player_props(self, name: str, position_idx: int) -> dict[str, float]:
        """
        Generate realistic NCAAB player props based on position.
        
        Position index 0-1 = guards (more points/assists)
        Position index 2 = wing (balanced)
        Position index 3-4 = forwards/center (more rebounds/blocks)
        """
        import random
        
        # Base stats vary by position
        if position_idx <= 1:  # Guards
            pts = round(random.uniform(12.0, 16.0) * 2) / 2
            reb = round(random.uniform(3.0, 4.5) * 2) / 2
            ast = round(random.uniform(4.0, 6.0) * 2) / 2
            blk = 0.5
        elif position_idx == 2:  # Wing
            pts = round(random.uniform(11.0, 14.0) * 2) / 2
            reb = round(random.uniform(4.5, 6.0) * 2) / 2
            ast = round(random.uniform(2.0, 3.5) * 2) / 2
            blk = 0.5
        else:  # Forwards/Center
            pts = round(random.uniform(10.0, 14.0) * 2) / 2
            reb = round(random.uniform(6.5, 9.0) * 2) / 2
            ast = round(random.uniform(1.5, 2.5) * 2) / 2
            blk = round(random.uniform(1.5, 2.5) * 2) / 2
        
        pra = pts + reb + ast
        pr = pts + reb
        pa = pts + ast
        ra = reb + ast
        
        return {
            "name": name,
            "pts": pts,
            "reb": reb,
            "ast": ast,
            "pra": pra,
            "pr": pr,
            "pa": pa,
            "ra": ra,
            "3pm": round(random.uniform(1.0, 3.0) * 2) / 2,
            "stl": round(random.uniform(0.5, 1.5) * 2) / 2,
            "blk": blk,
            "to": round(random.uniform(1.5, 2.5) * 2) / 2,
        }
