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
        
        if "basketball" in sport_key:
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
        """Return realistic stub betting lines for testing with dynamic dates."""
        # Game-specific lines for Jan 29, 2026 games (updated with current rosters)
        game_lines = {
            # 76ers favored at home (Embiid/Maxey/PG vs LaVine/DeRozan/Sabonis)
            "game_sac_phi_today": {
                "home_team": "Philadelphia 76ers", "away_team": "Sacramento Kings",
                "home_spread": -6.5, "total": 228.5, "home_ml": -260, "away_ml": 215,
            },
            # Bucks favored on road (Giannis without Dame vs rebuilding Wizards w/Trae)
            "game_mil_was_today": {
                "home_team": "Washington Wizards", "away_team": "Milwaukee Bucks",
                "home_spread": 5.5, "total": 224.5, "home_ml": 200, "away_ml": -245,
            },
            # Close game (Heat with Wiggins vs Bulls without LaVine)
            "game_mia_chi_today": {
                "home_team": "Chicago Bulls", "away_team": "Miami Heat",
                "home_spread": 1.5, "total": 218.5, "home_ml": 105, "away_ml": -125,
            },
            # Rockets favored (KD/Sengun/VanVleet vs rebuilding Hawks)
            "game_hou_atl_today": {
                "home_team": "Atlanta Hawks", "away_team": "Houston Rockets",
                "home_spread": 6.5, "total": 226.0, "home_ml": 230, "away_ml": -280,
            },
            # Mavs favored (AD/Kyrie/Klay vs young Hornets)
            "game_cha_dal_today": {
                "home_team": "Dallas Mavericks", "away_team": "Charlotte Hornets",
                "home_spread": -7.5, "total": 222.5, "home_ml": -320, "away_ml": 260,
            },
            # Nuggets heavy favorites (Jokic vs rebuilding Nets)
            "game_bkn_den_today": {
                "home_team": "Denver Nuggets", "away_team": "Brooklyn Nets",
                "home_spread": -12.5, "total": 224.0, "home_ml": -650, "away_ml": 475,
            },
            # Close game (Booker/Jalen Green vs surging Pistons w/Cade)
            "game_det_pho_today": {
                "home_team": "Phoenix Suns", "away_team": "Detroit Pistons",
                "home_spread": -2.5, "total": 226.5, "home_ml": -135, "away_ml": 115,
            },
            # Thunder favored (Defending champs SGA/Chet/JWill vs Ant/Randle/Gobert)
            "game_okc_min_today": {
                "home_team": "Minnesota Timberwolves", "away_team": "Oklahoma City Thunder",
                "home_spread": 4.5, "total": 218.5, "home_ml": 175, "away_ml": -210,
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
        
        UPDATED with accurate 2025-26 rosters after major trades:
        - KD to Rockets, Jalen Green to Suns (July 2025)
        - Luka to Lakers, AD to Mavs (Feb 2025)
        - De'Aaron Fox to Spurs, Zach LaVine to Kings (Feb 2025)
        - Trae Young to Wizards (Jan 2026)
        - KAT to Knicks (Oct 2024)
        - Dame waived by Bucks (Achilles)
        - Jimmy Butler to Warriors (Feb 2025)
        """
        times = _get_stub_game_times()
        
        # Define props for each real game with CURRENT 2025-26 rosters
        game_props = {
            # Game 1: Kings @ 76ers
            "game_sac_phi_today": {
                "home_team": "Philadelphia 76ers",
                "away_team": "Sacramento Kings",
                "commence_time": times["early"],
                "players": [
                    # 76ers
                    {"name": "Joel Embiid", "pts": 32.5, "reb": 11.5, "ast": 4.5, "pra": 48.5},
                    {"name": "Tyrese Maxey", "pts": 26.5, "reb": 3.5, "ast": 6.5, "pra": 36.5},
                    {"name": "Paul George", "pts": 22.5, "reb": 5.5, "ast": 4.5, "pra": 32.5},
                    # Kings (Fox traded to Spurs, got Zach LaVine)
                    {"name": "Zach LaVine", "pts": 24.5, "reb": 4.5, "ast": 4.5, "pra": 33.5},
                    {"name": "DeMar DeRozan", "pts": 23.5, "reb": 4.5, "ast": 5.5, "pra": 33.5},
                    {"name": "Domantas Sabonis", "pts": 19.5, "reb": 13.5, "ast": 7.5, "pra": 40.5},
                ],
            },
            # Game 2: Bucks @ Wizards
            "game_mil_was_today": {
                "home_team": "Washington Wizards",
                "away_team": "Milwaukee Bucks",
                "commence_time": times["late"],
                "players": [
                    # Bucks (Dame waived - Achilles, got Kyle Kuzma from Wizards)
                    {"name": "Giannis Antetokounmpo", "pts": 31.5, "reb": 11.5, "ast": 6.5, "pra": 49.5},
                    {"name": "Kyle Kuzma", "pts": 18.5, "reb": 5.5, "ast": 2.5, "pra": 26.5},
                    {"name": "Myles Turner", "pts": 14.5, "reb": 6.5, "ast": 1.5, "pra": 22.5},
                    # Wizards (Got Trae Young Jan 2026, Khris Middleton from Bucks)
                    {"name": "Trae Young", "pts": 26.5, "reb": 3.5, "ast": 10.5, "pra": 40.5},
                    {"name": "Khris Middleton", "pts": 17.5, "reb": 4.5, "ast": 4.5, "pra": 26.5},
                    {"name": "Alex Sarr", "pts": 12.5, "reb": 7.5, "ast": 2.5, "pra": 22.5},
                ],
            },
            # Game 3: Heat @ Bulls
            "game_mia_chi_today": {
                "home_team": "Chicago Bulls",
                "away_team": "Miami Heat",
                "commence_time": times["late"],
                "players": [
                    # Heat (Butler to Warriors, got Andrew Wiggins)
                    {"name": "Bam Adebayo", "pts": 19.5, "reb": 10.5, "ast": 4.5, "pra": 34.5},
                    {"name": "Tyler Herro", "pts": 22.5, "reb": 5.5, "ast": 4.5, "pra": 32.5},
                    {"name": "Andrew Wiggins", "pts": 17.5, "reb": 4.5, "ast": 2.5, "pra": 24.5},
                    # Bulls (LaVine traded to Kings, kept core)
                    {"name": "Coby White", "pts": 19.5, "reb": 4.5, "ast": 5.5, "pra": 29.5},
                    {"name": "Nikola Vucevic", "pts": 18.5, "reb": 10.5, "ast": 3.5, "pra": 32.5},
                    {"name": "Josh Giddey", "pts": 14.5, "reb": 6.5, "ast": 6.5, "pra": 27.5},
                ],
            },
            # Game 4: Rockets @ Hawks
            "game_hou_atl_today": {
                "home_team": "Atlanta Hawks",
                "away_team": "Houston Rockets",
                "commence_time": times["night"],
                "players": [
                    # Rockets (Got Kevin Durant July 2025!)
                    {"name": "Kevin Durant", "pts": 27.5, "reb": 6.5, "ast": 5.5, "pra": 39.5},
                    {"name": "Alperen Sengun", "pts": 18.5, "reb": 9.5, "ast": 5.5, "pra": 33.5},
                    {"name": "Fred VanVleet", "pts": 17.5, "reb": 3.5, "ast": 6.5, "pra": 27.5},
                    # Hawks (Trae traded to Wizards, Murray to Pelicans - got CJ McCollum)
                    {"name": "CJ McCollum", "pts": 21.5, "reb": 3.5, "ast": 4.5, "pra": 29.5},
                    {"name": "Bogdan Bogdanovic", "pts": 16.5, "reb": 3.5, "ast": 3.5, "pra": 23.5},
                    {"name": "Zaccharie Risacher", "pts": 14.5, "reb": 5.5, "ast": 2.5, "pra": 22.5},
                ],
            },
            # Game 5: Hornets @ Mavericks
            "game_cha_dal_today": {
                "home_team": "Dallas Mavericks",
                "away_team": "Charlotte Hornets",
                "commence_time": times["west"],
                "players": [
                    # Mavericks (Luka traded to Lakers Feb 2025, got Anthony Davis!)
                    {"name": "Anthony Davis", "pts": 25.5, "reb": 11.5, "ast": 3.5, "pra": 40.5},
                    {"name": "Kyrie Irving", "pts": 24.5, "reb": 4.5, "ast": 5.5, "pra": 34.5},
                    {"name": "Klay Thompson", "pts": 14.5, "reb": 3.5, "ast": 2.5, "pra": 20.5},
                    # Hornets
                    {"name": "LaMelo Ball", "pts": 23.5, "reb": 5.5, "ast": 8.5, "pra": 37.5},
                    {"name": "Brandon Miller", "pts": 18.5, "reb": 4.5, "ast": 2.5, "pra": 25.5},
                    {"name": "Miles Bridges", "pts": 17.5, "reb": 6.5, "ast": 3.5, "pra": 27.5},
                ],
            },
            # Game 6: Nets @ Nuggets
            "game_bkn_den_today": {
                "home_team": "Denver Nuggets",
                "away_team": "Brooklyn Nets",
                "commence_time": times["west"],
                "players": [
                    # Nuggets
                    {"name": "Nikola Jokic", "pts": 26.5, "reb": 12.5, "ast": 9.5, "pra": 48.5},
                    {"name": "Jamal Murray", "pts": 21.5, "reb": 4.5, "ast": 6.5, "pra": 32.5},
                    {"name": "Aaron Gordon", "pts": 14.5, "reb": 6.5, "ast": 3.5, "pra": 24.5},
                    # Nets (Mikal Bridges traded to Knicks July 2024, rebuilding)
                    {"name": "Cam Thomas", "pts": 24.5, "reb": 3.5, "ast": 3.5, "pra": 31.5},
                    {"name": "Nic Claxton", "pts": 11.5, "reb": 8.5, "ast": 2.5, "pra": 22.5},
                    {"name": "Dennis Schroder", "pts": 15.5, "reb": 2.5, "ast": 5.5, "pra": 23.5},
                ],
            },
            # Game 7: Pistons @ Suns
            "game_det_pho_today": {
                "home_team": "Phoenix Suns",
                "away_team": "Detroit Pistons",
                "commence_time": times["west"],
                "players": [
                    # Suns (KD traded to Rockets July 2025, got Jalen Green + Dillon Brooks)
                    {"name": "Devin Booker", "pts": 26.5, "reb": 4.5, "ast": 6.5, "pra": 37.5},
                    {"name": "Jalen Green", "pts": 22.5, "reb": 4.5, "ast": 3.5, "pra": 30.5},
                    {"name": "Dillon Brooks", "pts": 15.5, "reb": 3.5, "ast": 2.5, "pra": 21.5},
                    # Pistons
                    {"name": "Cade Cunningham", "pts": 23.5, "reb": 4.5, "ast": 9.5, "pra": 37.5},
                    {"name": "Jaden Ivey", "pts": 17.5, "reb": 3.5, "ast": 4.5, "pra": 25.5},
                    {"name": "Jalen Duren", "pts": 12.5, "reb": 9.5, "ast": 2.5, "pra": 24.5},
                ],
            },
            # Game 8: Thunder @ Timberwolves
            "game_okc_min_today": {
                "home_team": "Minnesota Timberwolves",
                "away_team": "Oklahoma City Thunder",
                "commence_time": times["west"],
                "players": [
                    # Thunder (2025 NBA Champs!)
                    {"name": "Shai Gilgeous-Alexander", "pts": 31.5, "reb": 5.5, "ast": 6.5, "pra": 43.5},
                    {"name": "Chet Holmgren", "pts": 16.5, "reb": 8.5, "ast": 2.5, "pra": 27.5},
                    {"name": "Jalen Williams", "pts": 20.5, "reb": 5.5, "ast": 5.5, "pra": 31.5},
                    # Timberwolves (KAT traded to Knicks Oct 2024, got Julius Randle)
                    {"name": "Anthony Edwards", "pts": 26.5, "reb": 5.5, "ast": 5.5, "pra": 37.5},
                    {"name": "Julius Randle", "pts": 21.5, "reb": 9.5, "ast": 4.5, "pra": 35.5},
                    {"name": "Rudy Gobert", "pts": 11.5, "reb": 11.5, "ast": 1.5, "pra": 24.5},
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
            # PRA
            pra_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pra"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pra"]},
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
                    ],
                },
            ],
        }
