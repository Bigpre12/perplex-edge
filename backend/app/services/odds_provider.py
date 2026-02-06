"""Odds provider for fetching games, lines, and player props from external APIs."""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

import httpx

from app.core.config import get_settings
from app.core.constants import LEAGUE_TO_SPORT_KEY_EXTENDED
from app.core.rate_limiter import (
    get_odds_api_limiter,
    get_betstack_api_limiter,
    get_espn_api_limiter,
)
from app.config.sports import (
    SportKey,
    StatType,
    is_valid_stat_for_sport,
    get_stat_type_from_api_market,
)

# Path to schedule data files
SCHEDULES_DIR = Path(__file__).parent.parent.parent / "data" / "schedules"

logger = logging.getLogger(__name__)

# Eastern timezone (handles DST automatically)
EASTERN_TZ = ZoneInfo("America/New_York")

# =============================================================================
# API Quota Tracking (Module-level, updates from response headers)
# =============================================================================

_quota_remaining: int = 500  # Default free tier limit
_quota_used: int = 0
_quota_last_updated: Optional[datetime] = None


def get_quota_status() -> dict[str, Any]:
    """
    Get current API quota status.
    
    Returns:
        Dictionary with remaining, used, and last_updated fields
    """
    return {
        "remaining": _quota_remaining,
        "used": _quota_used,
        "last_updated": _quota_last_updated.isoformat() if _quota_last_updated else None,
        "monthly_limit": 500,
        "percent_used": round((_quota_used / 500) * 100, 1) if _quota_used else 0,
    }


def _update_quota_from_headers(remaining: str | None, used: str | None) -> None:
    """Update quota tracking from API response headers."""
    global _quota_remaining, _quota_used, _quota_last_updated
    
    if remaining is not None:
        try:
            _quota_remaining = int(remaining)
        except ValueError:
            pass
    
    if used is not None:
        try:
            _quota_used = int(used)
        except ValueError:
            pass
    
    _quota_last_updated = datetime.now(timezone.utc)


# =============================================================================
# Team Power Ratings (for generating realistic moneylines from schedule data)
# Based on current 2025-26 season performance
# =============================================================================

NBA_POWER_RATINGS = {
    # Elite tier (contenders)
    "Cleveland Cavaliers": 8.5,
    "Boston Celtics": 7.8,
    "Oklahoma City Thunder": 7.5,
    "Denver Nuggets": 6.2,
    "New York Knicks": 5.8,
    "Milwaukee Bucks": 5.5,
    "Memphis Grizzlies": 5.2,
    "Houston Rockets": 4.8,
    # Playoff tier
    "Dallas Mavericks": 4.5,
    "Los Angeles Lakers": 4.2,
    "Phoenix Suns": 4.0,
    "Golden State Warriors": 3.8,
    "Minnesota Timberwolves": 3.5,
    "Los Angeles Clippers": 3.2,
    "Indiana Pacers": 3.0,
    "Orlando Magic": 2.8,
    "Miami Heat": 2.5,
    # Middle tier
    "Sacramento Kings": 1.5,
    "San Antonio Spurs": 1.2,
    "Atlanta Hawks": 0.8,
    "Detroit Pistons": 0.5,
    "Chicago Bulls": 0.0,
    "Philadelphia 76ers": -0.5,
    "Toronto Raptors": -1.0,
    # Lower tier
    "Brooklyn Nets": -2.5,
    "Utah Jazz": -3.0,
    "Portland Trail Blazers": -4.5,
    "Charlotte Hornets": -5.0,
    "New Orleans Pelicans": -5.5,
    "Washington Wizards": -7.0,
}

NCAAB_POWER_RATINGS = {
    # Top 10
    "Auburn Tigers": 9.0,
    "Duke Blue Devils": 8.8,
    "Iowa State Cyclones": 8.5,
    "Alabama Crimson Tide": 8.2,
    "Florida Gators": 8.0,
    "Tennessee Volunteers": 7.8,
    "Houston Cougars": 7.5,
    "Kansas Jayhawks": 7.2,
    "Michigan State Spartans": 7.0,
    "Texas A&M Aggies": 6.8,
    # 11-25
    "Kentucky Wildcats": 6.5,
    "Purdue Boilermakers": 6.2,
    "UConn Huskies": 6.0,
    "Gonzaga Bulldogs": 5.8,
    "Marquette Golden Eagles": 5.5,
    "Oregon Ducks": 5.2,
    "Wisconsin Badgers": 5.0,
    "St. John's Red Storm": 4.8,
    "Missouri Tigers": 4.5,
    "Texas Longhorns": 4.2,
    "Louisville Cardinals": 4.0,
    "UCLA Bruins": 3.8,
    "Arizona Wildcats": 3.5,
    "Illinois Fighting Illini": 3.2,
    "Michigan Wolverines": 3.0,
    # Strong programs
    "North Carolina Tar Heels": 2.8,
    "Baylor Bears": 2.5,
    "Ohio State Buckeyes": 2.2,
    "Creighton Bluejays": 2.0,
    "Villanova Wildcats": 1.8,
    "Virginia Cavaliers": 1.5,
    "Indiana Hoosiers": 1.2,
    "Texas Tech Red Raiders": 1.0,
    "Arkansas Razorbacks": 0.8,
    "BYU Cougars": 0.5,
    # Mid-major powers
    "Saint Mary's Gaels": 0.2,
    "San Diego State Aztecs": 0.0,
    "Memphis Tigers": -0.5,
    "Xavier Musketeers": -1.0,
    "Cincinnati Bearcats": -1.5,
    # Default for unrated teams
    "Miami Hurricanes": -2.0,
    "NC State Wolfpack": -2.5,
    "Wake Forest Demon Deacons": -3.0,
    "Georgia Bulldogs": -3.5,
    "Vanderbilt Commodores": -4.0,
    "LSU Tigers": -1.8,
    "Ole Miss Rebels": -2.2,
    "Mississippi State Bulldogs": -2.8,
    "South Carolina Gamecocks": -3.2,
    "Oklahoma Sooners": -2.0,
    "West Virginia Mountaineers": -2.5,
    "Oklahoma State Cowboys": -3.0,
    "TCU Horned Frogs": -3.5,
    "Kansas State Wildcats": 1.5,
    "Colorado Buffaloes": -1.5,
    "Utah Utes": -2.0,
    "Arizona State Sun Devils": -2.5,
    "USC Trojans": 0.5,
    "Stanford Cardinal": -3.0,
    "Oregon State Beavers": -4.0,
    "Washington Huskies": -3.5,
    "California Golden Bears": -4.5,
    "Georgetown Hoyas": -4.0,
    "Seton Hall Pirates": -2.0,
    "Pittsburgh Panthers": -1.5,
    "Florida State Seminoles": -2.5,
    "Penn State Nittany Lions": -1.0,
    "Rutgers Scarlet Knights": -2.0,
    "Iowa Hawkeyes": 1.0,
    "Minnesota Golden Gophers": -3.0,
    "San Francisco Dons": -1.5,
    "Pepperdine Waves": -5.0,
}


def _spread_to_moneyline(spread: float) -> tuple[int, int]:
    """
    Convert point spread to moneyline odds.
    
    Uses approximate conversion:
    - 3pt favorite ~= -150/+130
    - 7pt favorite ~= -300/+250
    - Even ~= -110/-110
    
    Args:
        spread: Point spread (positive = home favorite)
    
    Returns:
        Tuple of (home_odds, away_odds) in American format
    """
    import math
    
    if abs(spread) < 0.5:
        return (-110, -110)
    
    # Approximate conversion formula
    if spread > 0:
        # Home is favorite
        fav_ml = int(-100 - (spread * 15))
        dog_ml = int(100 + (spread * 12))
        return (fav_ml, dog_ml)
    else:
        # Away is favorite
        spread = abs(spread)
        fav_ml = int(-100 - (spread * 15))
        dog_ml = int(100 + (spread * 12))
        return (dog_ml, fav_ml)


# =============================================================================
# Dynamic Stub Date Generation
# =============================================================================

def _get_stub_game_times() -> dict[str, str]:
    """
    Generate game times for today and tomorrow.
    
    Uses proper timezone handling to set games in the evening ET.
    Includes both today and tomorrow so the "Tomorrow's Slate Review"
    also has data in stub/demo mode.
    
    Returns:
        Dictionary mapping time slots to ISO datetime strings (UTC).
        Today slots: early, mid, late, night, west
        Tomorrow slots: tmrw_early, tmrw_mid, tmrw_late, tmrw_night, tmrw_west
    """
    # Get current time in Eastern timezone (handles DST automatically)
    now_et = datetime.now(EASTERN_TZ)
    today_et = now_et.date()
    tomorrow_et = today_et + timedelta(days=1)
    
    # Create game times for evening Eastern time (7 PM - 10 PM ET range)
    game_times = {
        # Today's games
        "early": datetime(today_et.year, today_et.month, today_et.day, 19, 0, tzinfo=EASTERN_TZ),    # 7:00 PM ET
        "mid": datetime(today_et.year, today_et.month, today_et.day, 19, 30, tzinfo=EASTERN_TZ),    # 7:30 PM ET
        "late": datetime(today_et.year, today_et.month, today_et.day, 20, 0, tzinfo=EASTERN_TZ),    # 8:00 PM ET
        "night": datetime(today_et.year, today_et.month, today_et.day, 21, 0, tzinfo=EASTERN_TZ),   # 9:00 PM ET
        "west": datetime(today_et.year, today_et.month, today_et.day, 22, 0, tzinfo=EASTERN_TZ),    # 10:00 PM ET
        # Tomorrow's games (for slate preview)
        "tmrw_early": datetime(tomorrow_et.year, tomorrow_et.month, tomorrow_et.day, 19, 0, tzinfo=EASTERN_TZ),
        "tmrw_mid": datetime(tomorrow_et.year, tomorrow_et.month, tomorrow_et.day, 19, 30, tzinfo=EASTERN_TZ),
        "tmrw_late": datetime(tomorrow_et.year, tomorrow_et.month, tomorrow_et.day, 20, 0, tzinfo=EASTERN_TZ),
        "tmrw_night": datetime(tomorrow_et.year, tomorrow_et.month, tomorrow_et.day, 21, 0, tzinfo=EASTERN_TZ),
        "tmrw_west": datetime(tomorrow_et.year, tomorrow_et.month, tomorrow_et.day, 22, 0, tzinfo=EASTERN_TZ),
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

# Sport key mappings (use centralized constants)
SPORT_KEYS = LEAGUE_TO_SPORT_KEY_EXTENDED

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
    "player_pass_attempts": "PASS_ATT",
    "player_pass_completions": "PASS_COMP",
    "player_pass_interceptions": "INT",
    "player_rush_yds": "RUSH_YDS",
    "player_rush_attempts": "RUSH_ATT",
    "player_rush_tds": "RUSH_TDS",
    "player_reception_yds": "REC_YDS",
    "player_receptions": "REC",
    "player_reception_tds": "REC_TDS",
    "player_rush_reception_yds": "RUSH_REC_YDS",
    "player_anytime_td": "ANYTIME_TD",
    # MLB props
    "batter_total_bases": "TB",
    "pitcher_strikeouts": "K",
    "batter_hits": "H",
    "batter_rbis": "RBI",
    "batter_runs": "R",
    "batter_home_runs": "HR",
    "pitcher_outs": "OUTS",
    # Tennis props
    "player_aces": "ACES",
    "player_double_faults": "DF",
    "player_games_won": "GAMES",
    "player_sets_won": "SETS",
    "player_total_games": "TOTAL_GAMES",
    # NHL props
    "player_goals": "GOALS",
    "player_shots_on_goal": "SOG",
    "player_blocked_shots": "BLK_SHOTS",
    "player_saves": "SAVES",
    "player_power_play_points": "PPP",
    "player_penalty_minutes": "PIM",
    # Golf props
    "golfer_finish_position": "FINISH_POS",
    "golfer_make_cut": "MAKE_CUT",
    "golfer_top_5": "TOP_5",
    "golfer_top_10": "TOP_10",
    "golfer_top_20": "TOP_20",
    "golfer_first_round_leader": "FRL",
    "golfer_matchup": "MATCHUP",
    # Soccer props
    "player_anytime_goalscorer": "ANYTIME_GOAL",
    "player_shots": "SHOTS",
    "player_shots_on_target": "SOT",
    "player_fouls_committed": "FOULS",
    "player_cards": "CARDS",
    "player_tackles": "TACKLES",
    "player_passes": "PASSES",
    # MMA/UFC props
    "fighter_to_win": "WINNER",
    "fight_method": "METHOD",
    "fight_total_rounds": "TOTAL_ROUNDS",
    "fighter_significant_strikes": "SIG_STRIKES",
    "fighter_takedowns": "TAKEDOWNS",
    "fight_goes_distance": "GOES_DISTANCE",
}

# Sport-specific overrides for shared API market keys.
# The Odds API reuses keys like "player_points" and "player_assists" across sports,
# but our internal stat types differ (e.g., PTS vs PTS_H for hockey).
SPORT_PROP_OVERRIDES: dict[str, dict[str, str]] = {
    "icehockey_nhl": {
        "player_points": "PTS_H",
        "player_assists": "AST_H",
    },
}


# Shared bookmaker configs for all stub generators.
# Each tuple: (api_key, display_title, odds_offset_from_base)
STUB_BOOKMAKER_CONFIGS = [
    ("draftkings", "DraftKings", 0),
    ("fanduel", "FanDuel", -2),
    ("betmgm", "BetMGM", 2),
    ("caesars", "Caesars", 1),
    ("betrivers", "BetRivers", -1),
    ("fanatics", "Fanatics", 3),
    ("hardrock", "Hard Rock Bet", -3),
    ("espnbet", "ESPN BET", 1),
    ("fliff", "Fliff", -2),
    ("prizepicks", "PrizePicks", 0),
]


def _resolve_stat_type(market_key: str, sport_key: str | None) -> str:
    """Resolve API market key to internal stat type, with sport-specific overrides."""
    if sport_key:
        # Check for sport-specific override first
        overrides = SPORT_PROP_OVERRIDES.get(sport_key)
        if overrides and market_key in overrides:
            return overrides[market_key]
    return PROP_MAPPINGS.get(market_key, market_key.upper())


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
        """Make an authenticated request to the API with full monitoring."""
        from app.services.api_monitor import log_api_call
        import time
        
        if not self.api_key:
            raise ValueError("ODDS_API_KEY not configured")
        
        # Enforce rate limiting before making request
        await get_odds_api_limiter().wait()
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key
        
        start_time = time.time()
        status_code = 0
        response_count = 0
        error_msg = None
        
        try:
            response = await self.client.get(url, params=params)
            status_code = response.status_code
            
            # Handle HTTP errors gracefully
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                error_msg = str(e)[:100]
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
            
            # Track and log API usage
            remaining = response.headers.get("x-requests-remaining")
            used = response.headers.get("x-requests-used")
            _update_quota_from_headers(remaining, used)
            logger.info(f"Odds API: {used or '?'} used, {remaining or '?'} remaining")
            
            result = response.json()
            
            # Count response items
            if isinstance(result, list):
                response_count = len(result)
            elif isinstance(result, dict) and "data" in result:
                response_count = len(result["data"])
            
            return result
            
        except httpx.TimeoutException as e:
            status_code = 408
            error_msg = "Request timeout"
            raise
        except httpx.ConnectError as e:
            status_code = 503
            error_msg = "Connection error"
            raise
        except Exception as e:
            if status_code == 0:
                status_code = 500
            error_msg = str(e)[:100]
            raise
        finally:
            # Always log the API call
            latency_ms = int((time.time() - start_time) * 1000)
            log_api_call(
                provider="odds_api",
                endpoint=endpoint,
                status_code=status_code,
                latency_ms=latency_ms,
                response_count=response_count,
                method="GET",
                error=error_msg,
            )
    
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
                    markets = "player_pass_yds,player_pass_tds,player_pass_attempts,player_pass_completions,player_pass_interceptions,player_rush_yds,player_rush_attempts,player_rush_tds,player_reception_yds,player_receptions,player_reception_tds,player_anytime_td"
                elif "baseball" in sport_key:
                    markets = "batter_total_bases,pitcher_strikeouts,batter_hits,batter_runs,batter_rbis,batter_home_runs,pitcher_outs"
                elif "tennis" in sport_key:
                    markets = "player_aces,player_double_faults,player_games_won,player_sets_won,player_total_games"
                elif "icehockey" in sport_key:
                    markets = "player_goals,player_assists,player_points,player_shots_on_goal,player_blocked_shots,player_saves,player_power_play_points,player_penalty_minutes"
                elif "golf" in sport_key:
                    markets = "golfer_finish_position,golfer_make_cut,golfer_top_5,golfer_top_10,golfer_top_20,golfer_first_round_leader,golfer_matchup"
                elif "soccer" in sport_key:
                    markets = "player_anytime_goalscorer,player_shots,player_shots_on_target,player_fouls_committed,player_cards,player_tackles,player_passes"
                elif "mma" in sport_key:
                    markets = "fighter_to_win,fight_method,fight_total_rounds,fighter_significant_strikes,fighter_takedowns,fight_goes_distance"
                else:
                    logger.warning(f"No prop market mapping for sport_key={sport_key}, skipping props")
                    return []
            
            raw_data = await self._request(
                f"/sports/{sport_key}/events/{external_game_id}/odds",
                {
                    "regions": "us,us2",
                    "markets": markets,
                    "oddsFormat": "american",
                },
            )
        
        return self._parse_player_props(raw_data, sport_key)
    
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
    
    def _parse_player_props(
        self,
        raw_data: dict[str, Any],
        sport_key: str | None = None,
    ) -> list[PropData]:
        """
        Parse player props from API response.
        
        Args:
            raw_data: Raw API response data
            sport_key: Optional sport key for stat type validation.
                       If provided, props with invalid stat types for the sport
                       will be filtered out.
        
        Returns:
            List of PropData objects
        """
        props = []
        now = datetime.now(timezone.utc)
        skipped_stats = set()  # Track skipped stat types for logging
        
        for bookmaker in raw_data.get("bookmakers", []):
            sportsbook = bookmaker["key"]
            
            for market in bookmaker.get("markets", []):
                market_key = market["key"]
                stat_type = _resolve_stat_type(market_key, sport_key)
                
                # Validate stat type for sport if sport_key is provided
                if sport_key is not None:
                    if not is_valid_stat_for_sport(sport_key, stat_type):
                        # Track for logging but don't spam
                        if stat_type not in skipped_stats:
                            skipped_stats.add(stat_type)
                        continue
                
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
        
        # Log skipped stat types if any
        if skipped_stats and sport_key:
            logger.debug(
                f"[{sport_key}] Skipped {len(skipped_stats)} invalid stat types: {sorted(skipped_stats)}"
            )
        
        return props
    
    # =========================================================================
    # Stub Methods for Testing
    # =========================================================================
    
    def _load_season_schedule(self, sport_key: str) -> dict[str, Any]:
        """
        Load season schedule from JSON file.
        
        Dynamically determines the correct season file based on current date.
        
        Args:
            sport_key: Sport identifier (basketball_nba, basketball_ncaab, etc.)
        
        Returns:
            Schedule dictionary with 'season' and 'games' keys
        """
        from app.services.season_helper import get_schedule_filepath, get_current_season_label
        
        schedule_file = get_schedule_filepath(sport_key, SCHEDULES_DIR)
        current_season = get_current_season_label(sport_key)
        
        if not schedule_file.exists():
            logger.warning(f"No schedule file found for {sport_key} at {schedule_file}")
            return {"season": current_season, "games": []}
        
        try:
            with open(schedule_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading schedule for {sport_key}: {e}")
            return {"season": current_season, "games": []}
    
    def _schedule_game_to_api_format(
        self, 
        game: dict[str, str], 
        sport_key: str,
        today_str: str,
    ) -> dict[str, Any]:
        """
        Convert a schedule game entry to The Odds API format.
        
        Args:
            game: Game dict from schedule JSON
            sport_key: Sport identifier
            today_str: Today's date as ISO string
        
        Returns:
            Game dict matching The Odds API response format
        """
        # Parse game time and convert to UTC
        time_et = game.get("time_et", "19:00")
        hour, minute = map(int, time_et.split(":"))
        
        game_date = datetime.strptime(game["date"], "%Y-%m-%d")
        game_dt = datetime(
            game_date.year, game_date.month, game_date.day,
            hour, minute, tzinfo=EASTERN_TZ
        )
        commence_time = game_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Generate moneyline from power ratings
        home_ml, away_ml = self._generate_moneyline_from_ratings(
            game["home_team"], game["away_team"], sport_key
        )
        
        # Generate game ID
        home_abbr = game.get("home_abbr", game["home_team"][:3].upper())
        away_abbr = game.get("away_abbr", game["away_team"][:3].upper())
        game_id = f"game_{away_abbr.lower()}_{home_abbr.lower()}_{game['date'].replace('-', '')}"
        
        # Sport title
        sport_titles = {
            "basketball_nba": "NBA",
            "basketball_ncaab": "NCAAB",
            "americanfootball_nfl": "NFL",
            "baseball_mlb": "MLB",
            "americanfootball_ncaaf": "NCAAF",
        }
        sport_title = sport_titles.get(sport_key, sport_key.upper())
        
        # Generate bookmakers with slight odds variation per book
        stub_bookmakers = []
        for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
            stub_bookmakers.append({
                "key": book_key,
                "title": book_title,
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": game["home_team"], "price": home_ml + odds_offset},
                        {"name": game["away_team"], "price": away_ml - odds_offset},
                    ]
                }]
            })
        
        return {
            "id": game_id,
            "sport_key": sport_key,
            "sport_title": sport_title,
            "commence_time": commence_time,
            "home_team": game["home_team"],
            "away_team": game["away_team"],
            "bookmakers": stub_bookmakers,
        }
    
    def _generate_moneyline_from_ratings(
        self, 
        home_team: str, 
        away_team: str, 
        sport_key: str,
    ) -> tuple[int, int]:
        """
        Generate realistic moneyline odds from team power ratings.
        
        Uses the spread_to_moneyline conversion with home court advantage.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            sport_key: Sport for selecting correct ratings
        
        Returns:
            Tuple of (home_odds, away_odds) in American format
        """
        # Select appropriate ratings
        if "ncaab" in sport_key:
            ratings = NCAAB_POWER_RATINGS
            home_advantage = 4.0  # College home court is bigger
        else:
            ratings = NBA_POWER_RATINGS
            home_advantage = 3.0  # NBA home court advantage
        
        home_rating = ratings.get(home_team, 0.0)
        away_rating = ratings.get(away_team, 0.0)
        
        # Spread = home_rating - away_rating + home_advantage
        # Positive spread = home is favorite
        spread = home_rating - away_rating + home_advantage
        
        return _spread_to_moneyline(spread)
    
    def _stub_games_response(self, sport_key: str) -> list[dict[str, Any]]:
        """
        Return dynamic stub game data based on season schedule files.
        
        Automatically filters to today's games and generates realistic
        moneylines from team power ratings.
        
        Args:
            sport_key: Sport identifier
        
        Returns:
            List of games in The Odds API format for today's date
        """
        # Get today's date in Eastern time
        today = datetime.now(EASTERN_TZ).date()
        today_str = today.isoformat()
        
        # Handle NFL separately (Super Bowl focus during playoffs)
        # NOTE: Must check exact sport_key to avoid matching NCAAF
        if sport_key == "americanfootball_nfl":
            times = _get_stub_game_times()
            return [
                # SUPER BOWL LX - February 9, 2026 (Chiefs vs Eagles)
                {
                    "id": "nfl_superbowl_lx",
                    "sport_key": sport_key,
                    "sport_title": "NFL",
                    "commence_time": times["night"],
                    "home_team": "Kansas City Chiefs",
                    "away_team": "Philadelphia Eagles",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Kansas City Chiefs", "price": -135},
                                {"name": "Philadelphia Eagles", "price": 115}
                            ]}]
                        }
                    ],
                },
            ]
        
        # Handle NCAAF (off-season: August-January, no games in February)
        if sport_key == "americanfootball_ncaaf":
            logger.info(f"[{sport_key}] College football is off-season (Feb-Aug). No stub games.")
            return []
        
        # Handle MLB (Spring Training preview - season starts March 25)
        if "baseball" in sport_key:
            times = _get_stub_game_times()
            # Classic rivalry matchups for Spring Training preview
            return [
                {
                    "id": f"mlb_nyy_bos_{today_str.replace('-', '')}",
                    "sport_key": sport_key,
                    "sport_title": "MLB",
                    "commence_time": times["afternoon"],
                    "home_team": "Boston Red Sox",
                    "away_team": "New York Yankees",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Boston Red Sox", "price": 105},
                                {"name": "New York Yankees", "price": -125}
                            ]}]
                        }
                    ],
                },
                {
                    "id": f"mlb_lad_sd_{today_str.replace('-', '')}",
                    "sport_key": sport_key,
                    "sport_title": "MLB",
                    "commence_time": times["night"],
                    "home_team": "San Diego Padres",
                    "away_team": "Los Angeles Dodgers",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "San Diego Padres", "price": 120},
                                {"name": "Los Angeles Dodgers", "price": -140}
                            ]}]
                        }
                    ],
                },
                {
                    "id": f"mlb_chc_stl_{today_str.replace('-', '')}",
                    "sport_key": sport_key,
                    "sport_title": "MLB",
                    "commence_time": times["early"],
                    "home_team": "St. Louis Cardinals",
                    "away_team": "Chicago Cubs",
                    "bookmakers": [
                        {
                            "key": "betmgm",
                            "title": "BetMGM",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "St. Louis Cardinals", "price": -110},
                                {"name": "Chicago Cubs", "price": -110}
                            ]}]
                        }
                    ],
                },
                {
                    "id": f"mlb_atl_nym_{today_str.replace('-', '')}",
                    "sport_key": sport_key,
                    "sport_title": "MLB",
                    "commence_time": times["afternoon"],
                    "home_team": "New York Mets",
                    "away_team": "Atlanta Braves",
                    "bookmakers": [
                        {
                            "key": "caesars",
                            "title": "Caesars",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "New York Mets", "price": 100},
                                {"name": "Atlanta Braves", "price": -120}
                            ]}]
                        }
                    ],
                },
                {
                    "id": f"mlb_hou_tex_{today_str.replace('-', '')}",
                    "sport_key": sport_key,
                    "sport_title": "MLB",
                    "commence_time": times["night"],
                    "home_team": "Texas Rangers",
                    "away_team": "Houston Astros",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Texas Rangers", "price": 115},
                                {"name": "Houston Astros", "price": -135}
                            ]}]
                        }
                    ],
                },
                {
                    "id": f"mlb_sf_oak_{today_str.replace('-', '')}",
                    "sport_key": sport_key,
                    "sport_title": "MLB",
                    "commence_time": times["afternoon"],
                    "home_team": "Oakland Athletics",
                    "away_team": "San Francisco Giants",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": "Oakland Athletics", "price": 180},
                                {"name": "San Francisco Giants", "price": -220}
                            ]}]
                        }
                    ],
                },
            ]
        
        # Handle Tennis (ATP and WTA) - generate dynamic matches
        if "tennis" in sport_key:
            times = _get_stub_game_times()
            is_wta = "wta" in sport_key.lower()
            sport_title = "Tennis WTA" if is_wta else "Tennis ATP"
            
            # Current tournaments and players (Feb 2026)
            # ATP: Open Occitanie - Montpellier (Jan 31 - Feb 8, 2026)
            # WTA: Abu Dhabi Open, Ostrava Open, Mumbai Open, Transylvania Open
            if is_wta:
                # Mubadala Abu Dhabi Open (WTA 500) - Jan 30 - Feb 7
                # Mixed with Ostrava Open field
                tournament = "Abu Dhabi Open / Ostrava Open"
                players = [
                    ("Belinda Bencic", -180),          # Abu Dhabi defending champion
                    ("Elena Rybakina", -160),          # Top seed likely
                    ("Daria Kasatkina", +100),         # Strong indoor player
                    ("Beatriz Haddad Maia", +110),     # Brazilian star
                    ("Elina Svitolina", +120),         # Former top 5
                    ("Liudmila Samsonova", +130),      # Russian player
                    ("Anastasia Pavlyuchenkova", +140), # Experienced player
                    ("Donna Vekic", +150),             # Croatian player
                ]
            else:
                # Open Occitanie - Montpellier (ATP 250)
                # Realistic field for indoor hard court 250
                tournament = "Open Occitanie - Montpellier"
                players = [
                    ("Felix Auger-Aliassime", -200),  # Defending champion
                    ("Ugo Humbert", -150),             # French #1, home favorite
                    ("Adrian Mannarino", +110),        # French veteran
                    ("Arthur Fils", +120),             # Rising French star
                    ("Benjamin Bonzi", +140),          # French player
                    ("Giovanni Mpetshi Perricard", +130),  # Big server
                    ("Roman Safiullin", +150),         # Russian player
                    ("Thanasi Kokkinakis", +160),      # Australian
                ]
            
            # Generate 4 matches for today (Quarter-finals)
            matches = []
            for i in range(0, min(len(players), 8), 2):
                p1_name, p1_odds = players[i]
                p2_name, p2_odds = players[i + 1] if i + 1 < len(players) else (players[0][0], players[0][1])
                
                # Adjust odds so they're complementary (proper vig)
                if p1_odds < 0:
                    p2_implied = 100 - abs(p1_odds) + 20  # Add some vig
                    p2_odds = p2_implied if p2_implied > 0 else 100
                
                # Create match ID with tournament context
                p1_last = p1_name.split()[-1].lower().replace("-", "")
                p2_last = p2_name.split()[-1].lower().replace("-", "")
                match_id = f"tennis_{p1_last}_{p2_last}_{today_str.replace('-', '')}"
                match_time = times["early"] if i < 4 else times["afternoon"]
                
                matches.append({
                    "id": match_id,
                    "sport_key": sport_key,
                    "sport_title": f"{sport_title} - {tournament}",
                    "commence_time": match_time,
                    "home_team": p1_name,
                    "away_team": p2_name,
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": p1_name, "price": p1_odds},
                                {"name": p2_name, "price": p2_odds}
                            ]}]
                        },
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": p1_name, "price": p1_odds - 5},
                                {"name": p2_name, "price": p2_odds + 5}
                            ]}]
                        },
                        {
                            "key": "betmgm",
                            "title": "BetMGM",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": p1_name, "price": p1_odds + 3},
                                {"name": p2_name, "price": p2_odds - 3}
                            ]}]
                        },
                    ],
                })
            
            logger.info(f"Generated {len(matches)} stub tennis matches for {sport_key} ({tournament})")
            return matches
        
        # Handle NHL - generate dynamic games
        if sport_key == "icehockey_nhl":
            times = _get_stub_game_times()
            
            # NHL teams with power ratings (2025-26 season)
            # Top teams get negative odds when home, weaker teams get positive
            nhl_matchups = [
                # Game 1: Colorado at Minnesota
                {
                    "home": ("Minnesota Wild", -130),
                    "away": ("Colorado Avalanche", +110),
                    "time": times["early"],
                },
                # Game 2: Boston at Toronto
                {
                    "home": ("Toronto Maple Leafs", -145),
                    "away": ("Boston Bruins", +125),
                    "time": times["early"],
                },
                # Game 3: Vegas at Edmonton
                {
                    "home": ("Edmonton Oilers", -120),
                    "away": ("Vegas Golden Knights", +100),
                    "time": times["night"],
                },
                # Game 4: Rangers at Hurricanes
                {
                    "home": ("Carolina Hurricanes", -135),
                    "away": ("New York Rangers", +115),
                    "time": times["night"],
                },
                # Game 5: Tampa at Florida
                {
                    "home": ("Florida Panthers", -150),
                    "away": ("Tampa Bay Lightning", +130),
                    "time": times["late"],
                },
                # Game 6: Dallas at Winnipeg
                {
                    "home": ("Winnipeg Jets", -140),
                    "away": ("Dallas Stars", +120),
                    "time": times["late"],
                },
            ]
            
            games = []
            for idx, matchup in enumerate(nhl_matchups):
                home_team, home_ml = matchup["home"]
                away_team, away_ml = matchup["away"]
                
                # Create game ID
                home_abbr = home_team.split()[-1][:3].lower()
                away_abbr = away_team.split()[-1][:3].lower()
                game_id = f"nhl_{away_abbr}_{home_abbr}_{today_str.replace('-', '')}"
                
                games.append({
                    "id": game_id,
                    "sport_key": sport_key,
                    "sport_title": "NHL",
                    "commence_time": matchup["time"],
                    "home_team": home_team,
                    "away_team": away_team,
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": home_team, "price": home_ml},
                                {"name": away_team, "price": away_ml}
                            ]}]
                        },
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": home_team, "price": home_ml - 5},
                                {"name": away_team, "price": away_ml + 5}
                            ]}]
                        },
                    ],
                })
            
            logger.info(f"Generated {len(games)} stub NHL games for {sport_key}")
            return games
        
        # Handle Soccer (EPL, UCL, MLS) - generate dynamic matches
        if "soccer" in sport_key:
            times = _get_stub_game_times()
            
            if sport_key == "soccer_epl":
                # English Premier League matchups (2025-26 season)
                soccer_matchups = [
                    {"home": ("Manchester City", -180), "away": ("Arsenal", +145), "time": times["early"]},
                    {"home": ("Liverpool", -150), "away": ("Chelsea", +120), "time": times["afternoon"]},
                    {"home": ("Manchester United", +100), "away": ("Tottenham Hotspur", +105), "time": times["late"]},
                    {"home": ("Newcastle United", -130), "away": ("Aston Villa", +110), "time": times["late"]},
                ]
                sport_title = "English Premier League"
            elif sport_key == "soccer_uefa_champs_league":
                # UEFA Champions League matchups
                soccer_matchups = [
                    {"home": ("Real Madrid", -160), "away": ("Bayern Munich", +130), "time": times["afternoon"]},
                    {"home": ("Manchester City", -140), "away": ("Paris Saint-Germain", +115), "time": times["afternoon"]},
                    {"home": ("Barcelona", -120), "away": ("Inter Milan", +100), "time": times["late"]},
                    {"home": ("Borussia Dortmund", +110), "away": ("Atletico Madrid", +105), "time": times["late"]},
                ]
                sport_title = "UEFA Champions League"
            else:  # MLS
                # Major League Soccer matchups
                soccer_matchups = [
                    {"home": ("Inter Miami CF", -150), "away": ("LA Galaxy", +125), "time": times["afternoon"]},
                    {"home": ("LAFC", -130), "away": ("Atlanta United", +110), "time": times["late"]},
                    {"home": ("Seattle Sounders", -120), "away": ("FC Cincinnati", +100), "time": times["late"]},
                    {"home": ("New York Red Bulls", +100), "away": ("Columbus Crew", +105), "time": times["night"]},
                ]
                sport_title = "MLS"
            
            games = []
            for idx, matchup in enumerate(soccer_matchups):
                home_team, home_ml = matchup["home"]
                away_team, away_ml = matchup["away"]
                
                # Create game ID
                home_abbr = home_team.split()[0][:3].lower()
                away_abbr = away_team.split()[0][:3].lower()
                game_id = f"soccer_{away_abbr}_{home_abbr}_{today_str.replace('-', '')}"
                
                games.append({
                    "id": game_id,
                    "sport_key": sport_key,
                    "sport_title": sport_title,
                    "commence_time": matchup["time"],
                    "home_team": home_team,
                    "away_team": away_team,
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": home_team, "price": home_ml},
                                {"name": away_team, "price": away_ml},
                                {"name": "Draw", "price": 250}  # Soccer has draw option
                            ]}]
                        },
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": home_team, "price": home_ml - 5},
                                {"name": away_team, "price": away_ml + 5},
                                {"name": "Draw", "price": 245}
                            ]}]
                        },
                    ],
                })
            
            logger.info(f"Generated {len(games)} stub soccer matches for {sport_key}")
            return games
        
        # Handle Golf (PGA Tour) - tournament leaderboard style
        if sport_key == "golf_pga_tour":
            times = _get_stub_game_times()
            
            # PGA Tour tournament with outright winner odds
            tournament = "WM Phoenix Open"  # February tournament
            golfers = [
                ("Scottie Scheffler", +600),
                ("Rory McIlroy", +900),
                ("Jon Rahm", +1000),
                ("Viktor Hovland", +1400),
                ("Xander Schauffele", +1600),
                ("Patrick Cantlay", +1800),
                ("Collin Morikawa", +2000),
                ("Tony Finau", +2200),
            ]
            
            # Golf is structured differently - return tournament as single "event"
            games = [{
                "id": f"golf_pga_{today_str.replace('-', '')}",
                "sport_key": sport_key,
                "sport_title": f"PGA Tour - {tournament}",
                "commence_time": times["early"],
                "home_team": tournament,
                "away_team": "Field",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [{"key": "outrights", "outcomes": [
                            {"name": name, "price": odds} for name, odds in golfers
                        ]}]
                    },
                    {
                        "key": "fanduel",
                        "title": "FanDuel",
                        "markets": [{"key": "outrights", "outcomes": [
                            {"name": name, "price": odds + 50} for name, odds in golfers
                        ]}]
                    },
                ],
            }]
            
            logger.info(f"Generated stub PGA tournament for {sport_key} ({tournament})")
            return games
        
        # Handle UFC/MMA - load from schedule or generate fallback
        if sport_key == "mma_mixed_martial_arts":
            times = _get_stub_game_times()
            games = []
            
            # Try to load from UFC schedule file
            schedule = self._load_season_schedule(sport_key)
            
            if schedule.get("events"):
                # Find today's event or nearest upcoming event
                todays_event = None
                upcoming_event = None
                
                for event in schedule["events"]:
                    event_date = event.get("date", "")
                    if event_date == today_str:
                        todays_event = event
                        break
                    elif event_date > today_str and not upcoming_event:
                        upcoming_event = event
                
                # Use today's event, or upcoming event for preview, or last event
                event = todays_event or upcoming_event
                
                if event and event.get("fights"):
                    event_name = event.get("name", "UFC Event")
                    event_type = event.get("event_type", "Fight Night")
                    event_time = event.get("time_et", "22:00")
                    
                    # Parse event time
                    hour, minute = map(int, event_time.split(":"))
                    base_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    for idx, fight in enumerate(event["fights"]):
                        red_fighter = fight.get("red_corner", "Fighter A")
                        blue_fighter = fight.get("blue_corner", "Fighter B")
                        weight_class = fight.get("weight_class", "")
                        is_main = fight.get("is_main_event", False)
                        is_title = fight.get("is_title_fight", False)
                        
                        # Create fight ID
                        red_last = red_fighter.split()[-1].lower()
                        blue_last = blue_fighter.split()[-1].lower()
                        fight_id = f"ufc_{red_last}_{blue_last}_{today_str.replace('-', '')}"
                        
                        # Generate odds based on fight position
                        if is_main:
                            red_ml, blue_ml = -150, +130  # Close main event
                        else:
                            red_ml, blue_ml = -180 + (idx * 20), +155 - (idx * 15)
                        
                        # Calculate fight time (main event last)
                        fight_time = (base_time + timedelta(minutes=30 * (len(event["fights"]) - idx - 1)))
                        fight_time_str = fight_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                        
                        games.append({
                            "id": fight_id,
                            "sport_key": sport_key,
                            "sport_title": "UFC",
                            "commence_time": fight_time_str,
                            "home_team": red_fighter,  # Red corner
                            "away_team": blue_fighter,  # Blue corner
                            "event_name": event_name,
                            "weight_class": weight_class,
                            "is_title_fight": is_title,
                            "bookmakers": [
                                {
                                    "key": "draftkings",
                                    "title": "DraftKings",
                                    "markets": [{"key": "h2h", "outcomes": [
                                        {"name": red_fighter, "price": red_ml},
                                        {"name": blue_fighter, "price": blue_ml}
                                    ]}]
                                },
                                {
                                    "key": "fanduel",
                                    "title": "FanDuel",
                                    "markets": [{"key": "h2h", "outcomes": [
                                        {"name": red_fighter, "price": red_ml - 10},
                                        {"name": blue_fighter, "price": blue_ml + 10}
                                    ]}]
                                },
                                {
                                    "key": "betmgm",
                                    "title": "BetMGM",
                                    "markets": [{"key": "h2h", "outcomes": [
                                        {"name": red_fighter, "price": red_ml + 5},
                                        {"name": blue_fighter, "price": blue_ml - 5}
                                    ]}]
                                },
                            ],
                        })
                    
                    logger.info(f"Loaded {len(games)} UFC fights from schedule ({event_name})")
                    return games
            
            # Fallback: Generate default UFC card
            fallback_fights = [
                {"red": ("Alex Pereira", -200), "blue": ("Jamahal Hill", +170), "time": times["night"]},
                {"red": ("Sean Strickland", -150), "blue": ("Paulo Costa", +130), "time": times["late"]},
                {"red": ("Paddy Pimblett", -180), "blue": ("Tony Ferguson", +155), "time": times["late"]},
                {"red": ("Sean O'Malley", -220), "blue": ("Merab Dvalishvili", +185), "time": times["afternoon"]},
            ]
            
            for idx, fight in enumerate(fallback_fights):
                red_fighter, red_ml = fight["red"]
                blue_fighter, blue_ml = fight["blue"]
                
                # Create fight ID
                red_last = red_fighter.split()[-1].lower()
                blue_last = blue_fighter.split()[-1].lower()
                fight_id = f"ufc_{red_last}_{blue_last}_{today_str.replace('-', '')}"
                
                games.append({
                    "id": fight_id,
                    "sport_key": sport_key,
                    "sport_title": "UFC",
                    "commence_time": fight["time"],
                    "home_team": red_fighter,  # Red corner
                    "away_team": blue_fighter,  # Blue corner
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": red_fighter, "price": red_ml},
                                {"name": blue_fighter, "price": blue_ml}
                            ]}]
                        },
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": red_fighter, "price": red_ml - 10},
                                {"name": blue_fighter, "price": blue_ml + 10}
                            ]}]
                        },
                        {
                            "key": "betmgm",
                            "title": "BetMGM",
                            "markets": [{"key": "h2h", "outcomes": [
                                {"name": red_fighter, "price": red_ml + 5},
                                {"name": blue_fighter, "price": blue_ml - 5}
                            ]}]
                        },
                    ],
                })
            
            logger.info(f"Generated {len(games)} fallback UFC fights for {sport_key}")
            return games
        
        # Load schedule for NBA/NCAAB
        schedule = self._load_season_schedule(sport_key)
        
        if not schedule.get("games"):
            logger.warning(f"No games in schedule for {sport_key}")
            return []
        
        # Filter to today's and tomorrow's games (tomorrow for slate preview)
        tomorrow = (today + timedelta(days=1)).isoformat()
        upcoming_games = [
            g for g in schedule["games"] 
            if g.get("date") in (today_str, tomorrow)
        ]
        
        if not upcoming_games:
            logger.warning(f"No games found for {sport_key} on {today_str} or {tomorrow}")
            # Sanity check: warn if zero games on a weekday
            if today.weekday() < 5:  # Mon-Fri
                logger.error(
                    f"ALERT: Zero games found for {sport_key} on {today_str} (weekday) - "
                    "check schedule file or date range"
                )
        
        today_count = sum(1 for g in upcoming_games if g.get("date") == today_str)
        tmrw_count = sum(1 for g in upcoming_games if g.get("date") == tomorrow)
        logger.info(f"Found {today_count} today + {tmrw_count} tomorrow games for {sport_key}")
        
        # Convert to API format
        return [
            self._schedule_game_to_api_format(g, sport_key, g.get("date", today_str))
            for g in upcoming_games
        ]
    
    def _stub_lines_response(
        self,
        sport_key: str,
        external_game_id: str,
    ) -> dict[str, Any]:
        """Return realistic stub betting lines for testing with dynamic dates.
        
        Dynamically generates lines based on the current schedule.
        Uses lines from the schedule JSON if available, otherwise generates from power ratings.
        """
        # Get today's and tomorrow's dates for matching game IDs
        today = datetime.now(EASTERN_TZ).date()
        today_str = today.isoformat()
        tomorrow_str = (today + timedelta(days=1)).isoformat()
        
        # Load schedule to get games with their lines
        schedule = self._load_season_schedule(sport_key)
        upcoming_games = [
            g for g in schedule.get("games", [])
            if g.get("date") in (today_str, tomorrow_str)
        ]
        
        # Build game_lines dict dynamically from schedule
        game_lines = {}
        for game in upcoming_games:
            home_abbr = game.get("home_abbr", game["home_team"][:3].upper())
            away_abbr = game.get("away_abbr", game["away_team"][:3].upper())
            date_suffix = game.get("date", today_str).replace("-", "")
            game_id = f"game_{away_abbr.lower()}_{home_abbr.lower()}_{date_suffix}"
            
            # Parse spread if available (format: "TEAM -X.X")
            spread_str = game.get("spread", "")
            home_spread = -3.0  # default
            if spread_str:
                parts = spread_str.split()
                if len(parts) >= 2:
                    spread_team = parts[0]
                    spread_val = float(parts[1])
                    # If spread team is home, home_spread is negative (favored)
                    # If spread team is away, home_spread is positive (underdog)
                    if spread_team == home_abbr:
                        home_spread = spread_val
                    else:
                        home_spread = -spread_val
            
            # Parse total
            total = float(game.get("total", 220.0))
            
            # Parse moneylines (convert string like "+150" to int 150)
            def parse_ml(ml_str):
                if not ml_str:
                    return -110
                return int(ml_str.replace("+", ""))
            
            home_ml = parse_ml(game.get("home_ml"))
            away_ml = parse_ml(game.get("away_ml"))
            
            game_lines[game_id] = {
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "home_spread": home_spread,
                "total": total,
                "home_ml": home_ml,
                "away_ml": away_ml,
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
        """Return realistic stub player props dynamically based on current schedule.
        
        Dynamically generates props from team rosters based on the actual games
        in the schedule, rather than using hardcoded game IDs.
        """
        times = _get_stub_game_times()
        
        # NBA team rosters with star players and their typical prop lines
        # Updated: 2025-26 Season Depth Charts
        # Stats: pts, reb, ast, pra, pr, pa, ra, 3pm, stl, blk, to
        NBA_TEAM_ROSTERS = {
            # Atlanta Hawks - D. Daniels, N. Alexander-Walker, Z. Risacher, J. Johnson, O. Okongwu (IL)
            "ATL": [
                {"name": "Dyson Daniels", "pts": 14.5, "reb": 4.5, "ast": 5.5, "pra": 24.5, "pr": 19.0, "pa": 20.0, "ra": 10.0, "3pm": 1.5, "stl": 2.5, "blk": 0.5, "to": 2.5},
                {"name": "Nickeil Alexander-Walker", "pts": 15.5, "reb": 4.5, "ast": 4.5, "pra": 24.5, "pr": 20.0, "pa": 20.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Zac Risacher", "pts": 16.5, "reb": 6.5, "ast": 3.5, "pra": 26.5, "pr": 23.0, "pa": 20.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Jalen Johnson", "pts": 20.5, "reb": 9.5, "ast": 5.5, "pra": 35.5, "pr": 30.0, "pa": 26.0, "ra": 15.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Onyeka Okongwu", "pts": 12.5, "reb": 8.5, "ast": 2.5, "pra": 23.5, "pr": 21.0, "pa": 15.0, "ra": 11.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
            ],
            # Boston Celtics - J. Tatum, J. Brown, D. White, P. Pritchard, K. Porzingis
            "BOS": [
                {"name": "Jayson Tatum", "pts": 27.5, "reb": 8.5, "ast": 4.5, "pra": 40.5, "pr": 36.0, "pa": 32.0, "ra": 13.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Jaylen Brown", "pts": 26.5, "reb": 6.5, "ast": 4.5, "pra": 37.5, "pr": 33.0, "pa": 31.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Derrick White", "pts": 18.5, "reb": 4.5, "ast": 5.5, "pra": 28.5, "pr": 23.0, "pa": 24.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
                {"name": "Payton Pritchard", "pts": 15.5, "reb": 3.5, "ast": 4.5, "pra": 23.5, "pr": 19.0, "pa": 20.0, "ra": 8.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Kristaps Porzingis", "pts": 19.5, "reb": 7.5, "ast": 2.5, "pra": 29.5, "pr": 27.0, "pa": 22.0, "ra": 10.0, "3pm": 1.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
            ],
            # Brooklyn Nets - E. Demin, T. Mann, M. Porter Jr., N. Clowney, N. Claxton
            "BKN": [
                {"name": "Nic Claxton", "pts": 12.5, "reb": 9.5, "ast": 2.5, "pra": 24.5, "pr": 22.0, "pa": 15.0, "ra": 12.0, "3pm": 0.5, "stl": 1.5, "blk": 2.5, "to": 1.5},
                {"name": "Terrence Mann", "pts": 14.5, "reb": 4.5, "ast": 3.5, "pra": 22.5, "pr": 19.0, "pa": 18.0, "ra": 8.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Michael Porter Jr.", "pts": 18.5, "reb": 6.5, "ast": 2.5, "pra": 27.5, "pr": 25.0, "pa": 21.0, "ra": 9.0, "3pm": 2.5, "stl": 0.5, "blk": 0.5, "to": 1.5},
            ],
            # Charlotte Hornets - L. Ball, K. Knueppel, B. Miller, M. Bridges, M. Diabate
            "CHA": [
                {"name": "LaMelo Ball", "pts": 28.5, "reb": 6.5, "ast": 9.5, "pra": 44.5, "pr": 35.0, "pa": 38.0, "ra": 16.0, "3pm": 4.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Brandon Miller", "pts": 22.5, "reb": 5.5, "ast": 4.5, "pra": 32.5, "pr": 28.0, "pa": 27.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Miles Bridges", "pts": 19.5, "reb": 7.5, "ast": 4.5, "pra": 31.5, "pr": 27.0, "pa": 24.0, "ra": 12.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # Chicago Bulls - J. Giddey, C. White, I. Okoro, M. Buzelis, N. Vucevic
            "CHI": [
                {"name": "Josh Giddey", "pts": 16.5, "reb": 7.5, "ast": 7.5, "pra": 31.5, "pr": 24.0, "pa": 24.0, "ra": 15.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Coby White", "pts": 20.5, "reb": 4.5, "ast": 5.5, "pra": 30.5, "pr": 25.0, "pa": 26.0, "ra": 10.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Nikola Vucevic", "pts": 18.5, "reb": 10.5, "ast": 3.5, "pra": 32.5, "pr": 29.0, "pa": 22.0, "ra": 14.0, "3pm": 1.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
            ],
            # Cleveland Cavaliers - D. Garland, D. Mitchell, D. Wade, E. Mobley, J. Allen
            "CLE": [
                {"name": "Donovan Mitchell", "pts": 26.5, "reb": 4.5, "ast": 5.5, "pra": 36.5, "pr": 31.0, "pa": 32.0, "ra": 10.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Darius Garland", "pts": 20.5, "reb": 3.5, "ast": 7.5, "pra": 31.5, "pr": 24.0, "pa": 28.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Jarrett Allen", "pts": 14.5, "reb": 10.5, "ast": 2.5, "pra": 27.5, "pr": 25.0, "pa": 17.0, "ra": 13.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
            ],
            # Dallas Mavericks - C. Flagg, M. Christie, N. Marshall, P. Washington, D. Gafford
            "DAL": [
                {"name": "Cooper Flagg", "pts": 16.5, "reb": 6.5, "ast": 3.5, "pra": 26.5, "pr": 23.0, "pa": 20.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 1.5, "to": 2.5},
                {"name": "PJ Washington", "pts": 14.5, "reb": 7.5, "ast": 2.5, "pra": 24.5, "pr": 22.0, "pa": 17.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Daniel Gafford", "pts": 11.5, "reb": 7.5, "ast": 1.5, "pra": 20.5, "pr": 19.0, "pa": 13.0, "ra": 9.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
            ],
            # Denver Nuggets - J. Murray, C. Braun, P. Watson, S. Jones, N. Jokic
            "DEN": [
                {"name": "Nikola Jokic", "pts": 26.5, "reb": 12.5, "ast": 9.5, "pra": 48.5, "pr": 39.0, "pa": 36.0, "ra": 22.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Jamal Murray", "pts": 21.5, "reb": 4.5, "ast": 6.5, "pra": 32.5, "pr": 26.0, "pa": 28.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Christian Braun", "pts": 16.5, "reb": 5.5, "ast": 3.5, "pra": 25.5, "pr": 22.0, "pa": 20.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
            ],
            # Detroit Pistons - C. Cunningham, D. Robinson, A. Thompson, T. Harris (IL), J. Duren
            "DET": [
                {"name": "Cade Cunningham", "pts": 24.5, "reb": 5.5, "ast": 9.5, "pra": 39.5, "pr": 30.0, "pa": 34.0, "ra": 15.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Jalen Duren", "pts": 13.5, "reb": 11.5, "ast": 2.5, "pra": 27.5, "pr": 25.0, "pa": 16.0, "ra": 14.0, "3pm": 0.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
                {"name": "Dyson Robinson", "pts": 12.5, "reb": 4.5, "ast": 3.5, "pra": 20.5, "pr": 17.0, "pa": 16.0, "ra": 8.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Ausar Thompson", "pts": 10.5, "reb": 6.5, "ast": 2.5, "pra": 19.5, "pr": 17.0, "pa": 13.0, "ra": 9.0, "3pm": 0.5, "stl": 1.5, "blk": 1.5, "to": 1.5},
            ],
            # Golden State Warriors - S. Curry, B. Podziemski, M. Moody, D. Green, A. Horford
            "GSW": [
                {"name": "Stephen Curry", "pts": 26.5, "reb": 4.5, "ast": 6.5, "pra": 37.5, "pr": 31.0, "pa": 33.0, "ra": 11.0, "3pm": 5.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Draymond Green", "pts": 9.5, "reb": 6.5, "ast": 6.5, "pra": 22.5, "pr": 16.0, "pa": 16.0, "ra": 13.0, "3pm": 1.5, "stl": 1.5, "blk": 1.5, "to": 2.5},
                {"name": "Brandin Podziemski", "pts": 12.5, "reb": 5.5, "ast": 4.5, "pra": 22.5, "pr": 18.0, "pa": 17.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # Houston Rockets - A. Thompson, T. Eason, K. Durant, J. Smith Jr., A. Sengun
            "HOU": [
                {"name": "Kevin Durant", "pts": 28.5, "reb": 6.5, "ast": 5.5, "pra": 40.5, "pr": 35.0, "pa": 34.0, "ra": 12.0, "3pm": 2.5, "stl": 0.5, "blk": 1.5, "to": 2.5},
                {"name": "Alperen Sengun", "pts": 19.5, "reb": 10.5, "ast": 5.5, "pra": 35.5, "pr": 30.0, "pa": 25.0, "ra": 16.0, "3pm": 0.5, "stl": 1.5, "blk": 1.5, "to": 3.5},
                {"name": "Amen Thompson", "pts": 14.5, "reb": 7.5, "ast": 4.5, "pra": 26.5, "pr": 22.0, "pa": 19.0, "ra": 12.0, "3pm": 0.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # Indiana Pacers - A. Nembhard, B. Mathurin, A. Nesmith, J. Walker, P. Siakam
            "IND": [
                {"name": "Pascal Siakam", "pts": 21.5, "reb": 7.5, "ast": 4.5, "pra": 33.5, "pr": 29.0, "pa": 26.0, "ra": 12.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Bennedict Mathurin", "pts": 18.5, "reb": 4.5, "ast": 3.5, "pra": 26.5, "pr": 23.0, "pa": 22.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Andrew Nembhard", "pts": 13.5, "reb": 3.5, "ast": 6.5, "pra": 23.5, "pr": 17.0, "pa": 20.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
            ],
            # LA Clippers - J. Harden, K. Dunn, K. Leonard, J. Collins, I. Zubac
            "LAC": [
                {"name": "Kawhi Leonard", "pts": 24.5, "reb": 6.5, "ast": 4.5, "pra": 35.5, "pr": 31.0, "pa": 29.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "James Harden", "pts": 18.5, "reb": 5.5, "ast": 9.5, "pra": 33.5, "pr": 24.0, "pa": 28.0, "ra": 15.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Ivica Zubac", "pts": 12.5, "reb": 10.5, "ast": 2.5, "pra": 25.5, "pr": 23.0, "pa": 15.0, "ra": 13.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
            ],
            # LA Lakers - L. Doncic, L. James, D. Ayton, A. Reaves, R. Hachimura (2026 Post-AD Trade)
            "LAL": [
                {"name": "Luka Doncic", "pts": 33.5, "reb": 9.5, "ast": 9.5, "pra": 52.5, "pr": 43.0, "pa": 43.0, "ra": 19.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 4.5},
                {"name": "LeBron James", "pts": 25.5, "reb": 7.5, "ast": 8.5, "pra": 41.5, "pr": 33.0, "pa": 34.0, "ra": 16.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Deandre Ayton", "pts": 18.5, "reb": 12.5, "ast": 2.5, "pra": 33.5, "pr": 31.0, "pa": 21.0, "ra": 15.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                {"name": "Austin Reaves", "pts": 16.5, "reb": 4.5, "ast": 5.5, "pra": 26.5, "pr": 21.0, "pa": 22.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Rui Hachimura", "pts": 13.5, "reb": 5.5, "ast": 2.5, "pra": 21.5, "pr": 19.0, "pa": 16.0, "ra": 8.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
            ],
            # Memphis Grizzlies - C. Spencer, C. Coward, J. Wells, S. Aldama, J. Jackson Jr.
            "MEM": [
                {"name": "Jaren Jackson Jr.", "pts": 22.5, "reb": 6.5, "ast": 2.5, "pra": 31.5, "pr": 29.0, "pa": 25.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 2.5, "to": 2.5},
                {"name": "Santi Aldama", "pts": 14.5, "reb": 7.5, "ast": 3.5, "pra": 25.5, "pr": 22.0, "pa": 18.0, "ra": 11.0, "3pm": 2.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
                {"name": "Cam Spencer", "pts": 12.5, "reb": 3.5, "ast": 4.5, "pra": 20.5, "pr": 16.0, "pa": 17.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
            ],
            # Miami Heat - D. Mitchell, T. Herro, N. Powell, A. Wiggins, B. Adebayo
            "MIA": [
                {"name": "Bam Adebayo", "pts": 21.5, "reb": 11.5, "ast": 5.5, "pra": 38.5, "pr": 33.0, "pa": 27.0, "ra": 17.0, "3pm": 0.5, "stl": 1.5, "blk": 1.5, "to": 2.5},
                {"name": "Tyler Herro", "pts": 23.5, "reb": 5.5, "ast": 6.5, "pra": 35.5, "pr": 29.0, "pa": 30.0, "ra": 12.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Andrew Wiggins", "pts": 17.5, "reb": 4.5, "ast": 2.5, "pra": 24.5, "pr": 22.0, "pa": 20.0, "ra": 7.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
            ],
            # Milwaukee Bucks - R. Rollins, A. Green, G. Harris, K. Kuzma, M. Turner
            "MIL": [
                {"name": "Kyle Kuzma", "pts": 22.5, "reb": 6.5, "ast": 3.5, "pra": 32.5, "pr": 29.0, "pa": 26.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Myles Turner", "pts": 16.5, "reb": 8.5, "ast": 2.5, "pra": 27.5, "pr": 25.0, "pa": 19.0, "ra": 11.0, "3pm": 1.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
                {"name": "Gary Harris", "pts": 10.5, "reb": 2.5, "ast": 2.5, "pra": 15.5, "pr": 13.0, "pa": 13.0, "ra": 5.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
            ],
            # Minnesota Timberwolves - D. DiVincenzo, A. Edwards, J. McDaniels, J. Randle, R. Gobert
            "MIN": [
                {"name": "Anthony Edwards", "pts": 28.5, "reb": 6.5, "ast": 5.5, "pra": 40.5, "pr": 35.0, "pa": 34.0, "ra": 12.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Julius Randle", "pts": 23.5, "reb": 10.5, "ast": 5.5, "pra": 39.5, "pr": 34.0, "pa": 29.0, "ra": 16.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Rudy Gobert", "pts": 12.5, "reb": 12.5, "ast": 1.5, "pra": 26.5, "pr": 25.0, "pa": 14.0, "ra": 14.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
            ],
            # New Orleans Pelicans - T. Murphy III, H. Jones, S. Bey, Z. Williamson, D. Queen
            "NOP": [
                {"name": "Zion Williamson", "pts": 26.5, "reb": 7.5, "ast": 5.5, "pra": 39.5, "pr": 34.0, "pa": 32.0, "ra": 13.0, "3pm": 0.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Trey Murphy III", "pts": 17.5, "reb": 5.5, "ast": 2.5, "pra": 25.5, "pr": 23.0, "pa": 20.0, "ra": 8.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Saddiq Bey", "pts": 14.5, "reb": 5.5, "ast": 2.5, "pra": 22.5, "pr": 20.0, "pa": 17.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
            ],
            # New York Knicks - J. Brunson, J. Hart, M. Bridges, O. Anunoby, K. Towns
            "NYK": [
                {"name": "Jalen Brunson", "pts": 28.5, "reb": 3.5, "ast": 7.5, "pra": 39.5, "pr": 32.0, "pa": 36.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Karl-Anthony Towns", "pts": 24.5, "reb": 11.5, "ast": 3.5, "pra": 39.5, "pr": 36.0, "pa": 28.0, "ra": 15.0, "3pm": 2.5, "stl": 0.5, "blk": 0.5, "to": 2.5},
                {"name": "Mikal Bridges", "pts": 18.5, "reb": 4.5, "ast": 3.5, "pra": 26.5, "pr": 23.0, "pa": 22.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
            ],
            # Oklahoma City Thunder - S. Gilgeous-Alexander, L. Dort, J. Williams, C. Holmgren, I. Hartenstein
            "OKC": [
                {"name": "Shai Gilgeous-Alexander", "pts": 32.5, "reb": 5.5, "ast": 6.5, "pra": 44.5, "pr": 38.0, "pa": 39.0, "ra": 12.0, "3pm": 2.5, "stl": 2.5, "blk": 1.5, "to": 2.5},
                {"name": "Chet Holmgren", "pts": 17.5, "reb": 9.5, "ast": 3.5, "pra": 30.5, "pr": 27.0, "pa": 21.0, "ra": 13.0, "3pm": 1.5, "stl": 1.5, "blk": 2.5, "to": 1.5},
                {"name": "Jalen Williams", "pts": 21.5, "reb": 6.5, "ast": 6.5, "pra": 34.5, "pr": 28.0, "pa": 28.0, "ra": 13.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # Orlando Magic - J. Suggs, D. Bane, F. Wagner, P. Banchero, W. Carter Jr.
            "ORL": [
                {"name": "Paolo Banchero", "pts": 24.5, "reb": 7.5, "ast": 5.5, "pra": 37.5, "pr": 32.0, "pa": 30.0, "ra": 13.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Franz Wagner", "pts": 22.5, "reb": 6.5, "ast": 5.5, "pra": 34.5, "pr": 29.0, "pa": 28.0, "ra": 12.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Desmond Bane", "pts": 21.5, "reb": 4.5, "ast": 5.5, "pra": 31.5, "pr": 26.0, "pa": 27.0, "ra": 10.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # Philadelphia 76ers - T. Maxey, V. Edgecombe, K. Oubre Jr., P. George, J. Embiid
            "PHI": [
                {"name": "Joel Embiid", "pts": 28.5, "reb": 11.5, "ast": 4.5, "pra": 44.5, "pr": 40.0, "pa": 33.0, "ra": 16.0, "3pm": 1.5, "stl": 1.5, "blk": 1.5, "to": 3.5},
                {"name": "Tyrese Maxey", "pts": 27.5, "reb": 4.5, "ast": 7.5, "pra": 39.5, "pr": 32.0, "pa": 35.0, "ra": 12.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Paul George", "pts": 22.5, "reb": 6.5, "ast": 5.5, "pra": 34.5, "pr": 29.0, "pa": 28.0, "ra": 12.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # Phoenix Suns - D. Booker, J. Green, K. Durant, R. O'Neale, D. Ayton (2026 Post-Trades)
            "PHX": [
                {"name": "Devin Booker", "pts": 28.5, "reb": 4.5, "ast": 6.5, "pra": 39.5, "pr": 33.0, "pa": 35.0, "ra": 11.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Jalen Green", "pts": 24.5, "reb": 5.5, "ast": 4.5, "pra": 34.5, "pr": 30.0, "pa": 29.0, "ra": 10.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Kevin Durant", "pts": 26.5, "reb": 6.5, "ast": 5.5, "pra": 38.5, "pr": 33.0, "pa": 32.0, "ra": 12.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Royce O'Neale", "pts": 11.5, "reb": 5.5, "ast": 3.5, "pra": 20.5, "pr": 17.0, "pa": 15.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Deandre Ayton", "pts": 16.5, "reb": 11.5, "ast": 2.5, "pra": 30.5, "pr": 28.0, "pa": 19.0, "ra": 14.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 1.5},
            ],
            # Portland Trail Blazers - J. Holiday, S. Sharpe, T. Camara, D. Avdija, D. Clingan
            "POR": [
                {"name": "Shaedon Sharpe", "pts": 19.5, "reb": 4.5, "ast": 3.5, "pra": 27.5, "pr": 24.0, "pa": 23.0, "ra": 8.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Deni Avdija", "pts": 15.5, "reb": 7.5, "ast": 4.5, "pra": 27.5, "pr": 23.0, "pa": 20.0, "ra": 12.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Donovan Clingan", "pts": 10.5, "reb": 9.5, "ast": 1.5, "pra": 21.5, "pr": 20.0, "pa": 12.0, "ra": 11.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
            ],
            # Sacramento Kings - R. Westbrook, Z. LaVine, D. DeRozan, P. Achiuwa, D. Sabonis
            "SAC": [
                {"name": "Domantas Sabonis", "pts": 19.5, "reb": 13.5, "ast": 7.5, "pra": 40.5, "pr": 33.0, "pa": 27.0, "ra": 21.0, "3pm": 0.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "DeMar DeRozan", "pts": 24.5, "reb": 4.5, "ast": 5.5, "pra": 34.5, "pr": 29.0, "pa": 30.0, "ra": 10.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Zach LaVine", "pts": 22.5, "reb": 4.5, "ast": 4.5, "pra": 31.5, "pr": 27.0, "pa": 27.0, "ra": 9.0, "3pm": 3.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # San Antonio Spurs - D. Fox, S. Castle, D. Vassell, H. Barnes, V. Wembanyama
            "SAS": [
                {"name": "Victor Wembanyama", "pts": 26.5, "reb": 10.5, "ast": 4.5, "pra": 41.5, "pr": 37.0, "pa": 31.0, "ra": 15.0, "3pm": 2.5, "stl": 1.5, "blk": 3.5, "to": 3.5},
                {"name": "De'Aaron Fox", "pts": 27.5, "reb": 4.5, "ast": 6.5, "pra": 38.5, "pr": 32.0, "pa": 34.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Devin Vassell", "pts": 17.5, "reb": 4.5, "ast": 4.5, "pra": 26.5, "pr": 22.0, "pa": 22.0, "ra": 9.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # Toronto Raptors - I. Quickley, B. Ingram, R. Barrett, S. Barnes, C. Murray-Boyles
            "TOR": [
                {"name": "Scottie Barnes", "pts": 22.5, "reb": 8.5, "ast": 6.5, "pra": 37.5, "pr": 31.0, "pa": 29.0, "ra": 15.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 3.5},
                {"name": "Brandon Ingram", "pts": 24.5, "reb": 5.5, "ast": 5.5, "pra": 35.5, "pr": 30.0, "pa": 30.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "RJ Barrett", "pts": 21.5, "reb": 6.5, "ast": 4.5, "pra": 32.5, "pr": 28.0, "pa": 26.0, "ra": 11.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
            ],
            # Utah Jazz - K. George, C. Williams, A. Bailey, L. Markkanen, J. Nurkic
            "UTA": [
                {"name": "Lauri Markkanen", "pts": 24.5, "reb": 8.5, "ast": 2.5, "pra": 35.5, "pr": 33.0, "pa": 27.0, "ra": 11.0, "3pm": 2.5, "stl": 0.5, "blk": 0.5, "to": 2.5},
                {"name": "Keyonte George", "pts": 18.5, "reb": 3.5, "ast": 6.5, "pra": 28.5, "pr": 22.0, "pa": 25.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 2.5},
                {"name": "Jusuf Nurkic", "pts": 11.5, "reb": 10.5, "ast": 3.5, "pra": 25.5, "pr": 22.0, "pa": 15.0, "ra": 14.0, "3pm": 0.5, "stl": 0.5, "blk": 1.5, "to": 2.5},
            ],
            # Washington Wizards - T. Johnson, K. George, B. Coulibaly, J. Champagnie, A. Sarr (Current Starters)
            "WAS": [
                {"name": "Tyus Johnson", "pts": 12.5, "reb": 4.5, "ast": 6.5, "pra": 23.5, "pr": 17.0, "pa": 19.0, "ra": 11.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Kevin George", "pts": 14.5, "reb": 5.5, "ast": 4.5, "pra": 24.5, "pr": 20.0, "pa": 19.0, "ra": 10.0, "3pm": 2.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Bilal Coulibaly", "pts": 15.5, "reb": 6.5, "ast": 5.5, "pra": 27.5, "pr": 22.0, "pa": 21.0, "ra": 12.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Jalen Champagnie", "pts": 13.5, "reb": 6.5, "ast": 4.5, "pra": 24.5, "pr": 20.0, "pa": 18.0, "ra": 11.0, "3pm": 1.5, "stl": 1.5, "blk": 0.5, "to": 1.5},
                {"name": "Alex Sarr", "pts": 13.5, "reb": 9.5, "ast": 3.5, "pra": 26.5, "pr": 23.0, "pa": 17.0, "ra": 13.0, "3pm": 0.5, "stl": 0.5, "blk": 2.5, "to": 1.5},
            ],
        }
        
        # Parse the game ID to get teams
        # Format: game_{away_abbr}_{home_abbr}_{date}
        parts = external_game_id.split("_")
        if len(parts) >= 3 and parts[0] == "game":
            away_abbr = parts[1].upper()
            home_abbr = parts[2].upper()
        else:
            # Fallback for unexpected format
            away_abbr = "LAL"
            home_abbr = "BOS"
        
        # Get players for each team
        home_players = NBA_TEAM_ROSTERS.get(home_abbr, NBA_TEAM_ROSTERS.get("BOS", []))
        away_players = NBA_TEAM_ROSTERS.get(away_abbr, NBA_TEAM_ROSTERS.get("LAL", []))
        
        # Map abbreviation to full team name
        TEAM_NAMES = {
            "CHA": "Charlotte Hornets", "SAS": "San Antonio Spurs", "IND": "Indiana Pacers",
            "ATL": "Atlanta Hawks", "PHI": "Philadelphia 76ers", "NOP": "New Orleans Pelicans",
            "MIA": "Miami Heat", "CHI": "Chicago Bulls", "MEM": "Memphis Grizzlies",
            "MIN": "Minnesota Timberwolves", "HOU": "Houston Rockets", "DAL": "Dallas Mavericks",
            "OKC": "Oklahoma City Thunder", "DEN": "Denver Nuggets", "BOS": "Boston Celtics",
            "MIL": "Milwaukee Bucks", "LAL": "Los Angeles Lakers", "NYK": "New York Knicks",
            "CLE": "Cleveland Cavaliers", "PHX": "Phoenix Suns", "GSW": "Golden State Warriors",
            "LAC": "Los Angeles Clippers", "SAC": "Sacramento Kings", "POR": "Portland Trail Blazers",
            "WAS": "Washington Wizards", "DET": "Detroit Pistons", "BKN": "Brooklyn Nets",
            "ORL": "Orlando Magic", "TOR": "Toronto Raptors", "UTA": "Utah Jazz",
        }
        
        home_team = TEAM_NAMES.get(home_abbr, "Home Team")
        away_team = TEAM_NAMES.get(away_abbr, "Away Team")
        
        # Build dynamic game_props
        game_props = {
            external_game_id: {
                "home_team": home_team,
                "away_team": away_team,
                "commence_time": times["early"],
                "players": home_players + away_players,
            }
        }
        
        # Also maintain backward compatibility with NCAAB and NFL props
        # (keeping the original static definitions for non-NBA sports)
        game_props.update({
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
                    # Seattle Seahawks (DK Metcalf traded to Steelers)
                    {"name": "Geno Smith", "pass_yds": 265.5, "pass_tds": 2.5, "pass_att": 34.5, "pass_comp": 23.5, "int": 0.5, "rush_yds": 18.5, "rush_att": 4.5},
                    {"name": "Kenneth Walker III", "rush_yds": 78.5, "rush_att": 17.5, "rush_tds": 0.5, "rec": 3.5, "rec_yds": 22.5},
                    {"name": "Tyler Lockett", "rec": 5.5, "rec_yds": 65.5, "rec_tds": 0.5, "targets": 8.5},
                    {"name": "Jaxon Smith-Njigba", "rec": 6.5, "rec_yds": 72.5, "rec_tds": 0.5, "targets": 9.5},
                    {"name": "Noah Fant", "rec": 4.5, "rec_yds": 42.5, "rec_tds": 0.5, "targets": 6.5},
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
        })
        
        # Check if this game exists in static props
        if external_game_id not in game_props:
            # Generate dynamic props for NBA games using team names from game ID
            # Game IDs format: game_lal_was_20260130 -> LAL vs WAS
            if "basketball_nba" in sport_key:
                return self._generate_dynamic_nba_props(external_game_id, sport_key, times)
            elif "basketball_ncaab" in sport_key:
                return self._generate_dynamic_ncaab_props(external_game_id, sport_key, times)
            elif sport_key == "americanfootball_nfl":
                return self._generate_dynamic_nfl_props(external_game_id, sport_key, times)
            elif sport_key == "americanfootball_ncaaf":
                # NCAAF is off-season (Feb-Aug), return empty props
                logger.info(f"[{sport_key}] College football is off-season. No props.")
                return {
                    "id": external_game_id,
                    "sport_key": sport_key,
                    "home_team": "Off Season",
                    "away_team": "Off Season",
                    "commence_time": times["early"],
                    "bookmakers": [],
                }
            elif "tennis" in sport_key:
                return self._generate_dynamic_tennis_props(external_game_id, sport_key, times)
            elif "baseball" in sport_key:
                return self._generate_dynamic_mlb_props(external_game_id, sport_key, times)
            elif sport_key == "icehockey_nhl":
                return self._generate_dynamic_nhl_props(external_game_id, sport_key, times)
            else:
                # Unknown sport - return empty
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
            
            # Generate multi-bookmaker props with varied odds
            def vary_outcomes_nfl(outcomes: list, odds_offset: int) -> list:
                return [{**o, "price": o["price"] + odds_offset} for o in outcomes]
            
            bookmakers_nfl = []
            for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
                bookmakers_nfl.append({
                    "key": book_key,
                    "title": book_title,
                    "markets": [
                        {"key": "player_pass_yds", "outcomes": vary_outcomes_nfl(pass_yds_outcomes, odds_offset)},
                        {"key": "player_pass_tds", "outcomes": vary_outcomes_nfl(pass_tds_outcomes, odds_offset)},
                        {"key": "player_pass_attempts", "outcomes": vary_outcomes_nfl(pass_att_outcomes, odds_offset)},
                        {"key": "player_rush_yds", "outcomes": vary_outcomes_nfl(rush_yds_outcomes, odds_offset)},
                        {"key": "player_rush_attempts", "outcomes": vary_outcomes_nfl(rush_att_outcomes, odds_offset)},
                        {"key": "player_receptions", "outcomes": vary_outcomes_nfl(rec_outcomes, odds_offset)},
                        {"key": "player_reception_yds", "outcomes": vary_outcomes_nfl(rec_yds_outcomes, odds_offset)},
                    ],
                })
            
            return {
                "id": external_game_id,
                "sport_key": sport_key,
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "commence_time": game["commence_time"],
                "bookmakers": bookmakers_nfl,
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
        
        # Generate multi-bookmaker props with varied odds
        def vary_outcomes(outcomes: list, odds_offset: int) -> list:
            return [{**o, "price": o["price"] + odds_offset} for o in outcomes]
        
        bookmakers = []
        for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
            bookmakers.append({
                "key": book_key,
                "title": book_title,
                "markets": [
                    {"key": "player_points", "outcomes": vary_outcomes(points_outcomes, odds_offset)},
                    {"key": "player_rebounds", "outcomes": vary_outcomes(rebounds_outcomes, odds_offset)},
                    {"key": "player_assists", "outcomes": vary_outcomes(assists_outcomes, odds_offset)},
                    {"key": "player_points_rebounds_assists", "outcomes": vary_outcomes(pra_outcomes, odds_offset)},
                    {"key": "player_points_rebounds", "outcomes": vary_outcomes(pr_outcomes, odds_offset)},
                    {"key": "player_points_assists", "outcomes": vary_outcomes(pa_outcomes, odds_offset)},
                    {"key": "player_rebounds_assists", "outcomes": vary_outcomes(ra_outcomes, odds_offset)},
                    {"key": "player_threes", "outcomes": vary_outcomes(threes_outcomes, odds_offset)},
                    {"key": "player_steals", "outcomes": vary_outcomes(steals_outcomes, odds_offset)},
                    {"key": "player_blocks", "outcomes": vary_outcomes(blocks_outcomes, odds_offset)},
                    {"key": "player_turnovers", "outcomes": vary_outcomes(turnovers_outcomes, odds_offset)},
                ],
            })
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": game["home_team"],
            "away_team": game["away_team"],
            "commence_time": game["commence_time"],
            "bookmakers": bookmakers,
        }

    def _generate_dynamic_nba_props(
        self,
        external_game_id: str,
        sport_key: str,
        times: dict[str, str],
    ) -> dict[str, Any]:
        """Generate dynamic NBA player props for any game using roster data."""
        import random
        
        # Try to extract team abbreviations from game ID
        # Format: game_lal_was_20260130
        parts = external_game_id.split("_")
        home_team = "Unknown"
        away_team = "Unknown"
        
        # Map abbreviations to full team names
        abbr_to_team = {
            "lal": "Los Angeles Lakers", "bos": "Boston Celtics", "gsw": "Golden State Warriors",
            "phi": "Philadelphia 76ers", "mil": "Milwaukee Bucks", "den": "Denver Nuggets",
            "cle": "Cleveland Cavaliers", "phx": "Phoenix Suns", "min": "Minnesota Timberwolves",
            "nyk": "New York Knicks", "mia": "Miami Heat", "dal": "Dallas Mavericks",
            "sac": "Sacramento Kings", "lac": "Los Angeles Clippers", "nop": "New Orleans Pelicans",
            "ind": "Indiana Pacers", "orl": "Orlando Magic", "atl": "Atlanta Hawks",
            "chi": "Chicago Bulls", "hou": "Houston Rockets", "bkn": "Brooklyn Nets",
            "mem": "Memphis Grizzlies", "tor": "Toronto Raptors", "uta": "Utah Jazz",
            "sas": "San Antonio Spurs", "por": "Portland Trail Blazers", "cha": "Charlotte Hornets",
            "was": "Washington Wizards", "det": "Detroit Pistons", "okc": "Oklahoma City Thunder",
        }
        
        if len(parts) >= 3:
            away_abbr = parts[1].lower()
            home_abbr = parts[2].lower()
            away_team = abbr_to_team.get(away_abbr, "Unknown")
            home_team = abbr_to_team.get(home_abbr, "Unknown")
        
        # Get rosters
        home_roster = NBA_ROSTERS.get(home_team, DEFAULT_NBA_ROSTER)
        away_roster = NBA_ROSTERS.get(away_team, DEFAULT_NBA_ROSTER)
        
        # Generate props for all players
        players = []
        
        def gen_nba_stats(position_idx: int, team_rating: int) -> dict:
            """Generate realistic NBA stats based on position."""
            rating_mult = 0.9 + (team_rating / 100) * 0.2
            
            # Position-based stat ranges (PG=0, SG=1, SF=2, PF=3, C=4)
            # Updated ranges based on 2024-25 season averages
            if position_idx <= 1:  # PG/SG - guards
                pts = round(random.uniform(15, 32) * rating_mult * 2) / 2
                reb = round(random.uniform(2.5, 6.5) * 2) / 2
                ast = round(random.uniform(3.5, 9) * rating_mult * 2) / 2
                threes = round(random.uniform(1.5, 4.5) * 2) / 2
            elif position_idx <= 3:  # SF/PF - wings/bigs
                pts = round(random.uniform(12, 28) * rating_mult * 2) / 2
                reb = round(random.uniform(5.5, 11.5) * 2) / 2
                ast = round(random.uniform(2.5, 6.5) * rating_mult * 2) / 2
                threes = round(random.uniform(0.5, 3) * 2) / 2
            else:  # C
                pts = round(random.uniform(8, 22) * rating_mult * 2) / 2
                reb = round(random.uniform(8, 14) * 2) / 2
                ast = round(random.uniform(1, 3.5) * 2) / 2
                threes = round(random.uniform(0, 1) * 2) / 2
            
            # Calculate combo props
            pra = round((pts + reb + ast) * 2) / 2
            pr = round((pts + reb) * 2) / 2
            pa = round((pts + ast) * 2) / 2
            ra = round((reb + ast) * 2) / 2
            
            # Defensive stats (lower variance)
            stl = round(random.uniform(0.5, 2.5) * 2) / 2
            blk = round(random.uniform(0.3, 2.5) * 2) / 2 if position_idx >= 2 else round(random.uniform(0.2, 1.5) * 2) / 2
            to = round(random.uniform(1.5, 4.5) * 2) / 2
            
            return {
                "pts": pts, "reb": reb, "ast": ast,
                "pra": pra, "pr": pr, "pa": pa, "ra": ra,
                "3pm": threes, "stl": stl, "blk": blk, "to": to,
            }
        
        for i, name in enumerate(home_roster):
            stats = gen_nba_stats(i, home_rating)
            players.append({"name": name, **stats})
        
        for i, name in enumerate(away_roster):
            stats = gen_nba_stats(i, away_rating)
            players.append({"name": name, **stats})
        
        # Build outcomes
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
        
        for player in players:
            points_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pts"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pts"]},
            ])
            rebounds_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["reb"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["reb"]},
            ])
            assists_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["ast"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["ast"]},
            ])
            pra_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pra"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pra"]},
            ])
            pr_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pr"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pr"]},
            ])
            pa_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pa"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pa"]},
            ])
            ra_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["ra"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["ra"]},
            ])
            threes_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["3pm"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["3pm"]},
            ])
            steals_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["stl"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["stl"]},
            ])
            blocks_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["blk"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["blk"]},
            ])
            turnovers_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["to"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["to"]},
            ])
        
        # Generate bookmakers with varied odds for realistic multi-book display
        def vary_outcomes(outcomes: list, odds_offset: int) -> list:
            """Create varied odds for different bookmakers."""
            return [
                {**o, "price": o["price"] + odds_offset} 
                for o in outcomes
            ]
        
        bookmakers = []
        for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
            bookmakers.append({
                "key": book_key,
                "title": book_title,
                "markets": [
                    {"key": "player_points", "outcomes": vary_outcomes(points_outcomes, odds_offset)},
                    {"key": "player_rebounds", "outcomes": vary_outcomes(rebounds_outcomes, odds_offset)},
                    {"key": "player_assists", "outcomes": vary_outcomes(assists_outcomes, odds_offset)},
                    {"key": "player_points_rebounds_assists", "outcomes": vary_outcomes(pra_outcomes, odds_offset)},
                    {"key": "player_points_rebounds", "outcomes": vary_outcomes(pr_outcomes, odds_offset)},
                    {"key": "player_points_assists", "outcomes": vary_outcomes(pa_outcomes, odds_offset)},
                    {"key": "player_rebounds_assists", "outcomes": vary_outcomes(ra_outcomes, odds_offset)},
                    {"key": "player_threes", "outcomes": vary_outcomes(threes_outcomes, odds_offset)},
                    {"key": "player_steals", "outcomes": vary_outcomes(steals_outcomes, odds_offset)},
                    {"key": "player_blocks", "outcomes": vary_outcomes(blocks_outcomes, odds_offset)},
                    {"key": "player_turnovers", "outcomes": vary_outcomes(turnovers_outcomes, odds_offset)},
                ],
            })
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": times["early"],
            "bookmakers": bookmakers,
        }

    def _generate_dynamic_ncaab_props(
        self,
        external_game_id: str,
        sport_key: str,
        times: dict[str, str],
    ) -> dict[str, Any]:
        """Generate dynamic NCAAB player props for any game using roster data."""
        import random
        
        # NCAAB abbreviation to team name mapping (matches schedule file abbreviations)
        NCAAB_ABBR_TO_TEAM = {
            "ku": "Kansas Jayhawks", "duke": "Duke Blue Devils", "uk": "Kentucky Wildcats",
            "hou": "Houston Cougars", "gonz": "Gonzaga Bulldogs", "conn": "UConn Huskies",
            "pur": "Purdue Boilermakers", "fla": "Florida Gators", "ucla": "UCLA Bruins",
            "ariz": "Arizona Wildcats", "bama": "Alabama Crimson Tide", "tenn": "Tennessee Volunteers",
            "sju": "St. John's Red Storm", "mich": "Michigan Wolverines", "ark": "Arkansas Razorbacks",
            "ill": "Illinois Fighting Illini", "isu": "Iowa State Cyclones", "byu": "BYU Cougars",
            "ttu": "Texas Tech Red Raiders", "lou": "Louisville Cardinals",
            # Additional teams from schedule
            "unc": "North Carolina Tar Heels", "ksu": "Kansas State Wildcats",
            "nova": "Villanova Wildcats", "gtwn": "Georgetown Hoyas",
            "msu": "Michigan State Spartans", "osu": "Ohio State Buckeyes",
            "tex": "Texas Longhorns", "bay": "Baylor Bears", "smc": "Saint Mary's Gaels",
            "crei": "Creighton Bluejays", "ind": "Indiana Hoosiers", "aub": "Auburn Tigers",
            "cin": "Cincinnati Bearcats", "ore": "Oregon Ducks", "wash": "Washington Huskies",
            "uva": "Virginia Cavaliers", "wake": "Wake Forest Demon Deacons",
            "ou": "Oklahoma Sooners", "van": "Vanderbilt Commodores", "usc": "USC Trojans",
            "marq": "Marquette Golden Eagles", "tcu": "TCU Horned Frogs", "lsu": "LSU Tigers",
            "scar": "South Carolina Gamecocks", "wis": "Wisconsin Badgers", "mem": "Memphis Tigers",
            "okst": "Oklahoma State Cowboys", "ncst": "NC State Wolfpack", "iowa": "Iowa Hawkeyes",
            "minn": "Minnesota Golden Gophers", "stan": "Stanford Cardinal", "orst": "Oregon State Beavers",
            "wvu": "West Virginia Mountaineers", "uga": "Georgia Bulldogs", "msst": "Mississippi State Bulldogs",
            "usf": "San Francisco Dons", "pitt": "Pittsburgh Panthers", "hall": "Seton Hall Pirates",
            "asu": "Arizona State Sun Devils", "rutg": "Rutgers Scarlet Knights", "mia": "Miami Hurricanes",
            "miss": "Ole Miss Rebels", "utah": "Utah Utes", "pepp": "Pepperdine Waves", "xav": "Xavier Musketeers",
            "cal": "California Golden Bears", "fsu": "Florida State Seminoles", "colo": "Colorado Buffaloes",
            "psu": "Penn State Nittany Lions",
        }
        
        # Parse game ID format: game_{away_abbr}_{home_abbr}_{date}
        parts = external_game_id.split("_")
        away_abbr = parts[1].lower() if len(parts) > 1 else ""
        home_abbr = parts[2].lower() if len(parts) > 2 else ""
        
        # Map abbreviations to team names
        home_team = NCAAB_ABBR_TO_TEAM.get(home_abbr, f"{home_abbr.upper()} Team")
        away_team = NCAAB_ABBR_TO_TEAM.get(away_abbr, f"{away_abbr.upper()} Team")
        
        # Get rosters from NCAAB_ROSTERS
        home_roster = NCAAB_ROSTERS.get(home_team, DEFAULT_ROSTER)
        away_roster = NCAAB_ROSTERS.get(away_team, DEFAULT_ROSTER)
        
        players = []
        
        def gen_ncaab_stats(position_idx: int) -> dict:
            """Generate realistic NCAAB stats based on position."""
            if position_idx <= 1:  # Guards
                pts = round(random.uniform(12, 16) * 2) / 2
                reb = round(random.uniform(3, 4.5) * 2) / 2
                ast = round(random.uniform(4, 6) * 2) / 2
                blk = 0.5
            elif position_idx == 2:  # Wing
                pts = round(random.uniform(11, 14) * 2) / 2
                reb = round(random.uniform(4.5, 6) * 2) / 2
                ast = round(random.uniform(2, 3.5) * 2) / 2
                blk = 0.5
            else:  # Forwards/Center
                pts = round(random.uniform(10, 14) * 2) / 2
                reb = round(random.uniform(6.5, 9) * 2) / 2
                ast = round(random.uniform(1.5, 2.5) * 2) / 2
                blk = round(random.uniform(1.5, 2.5) * 2) / 2
            
            return {
                "pts": pts, "reb": reb, "ast": ast,
                "pra": round((pts + reb + ast) * 2) / 2,
                "pr": round((pts + reb) * 2) / 2,
                "pa": round((pts + ast) * 2) / 2,
                "ra": round((reb + ast) * 2) / 2,
                "3pm": round(random.uniform(1, 3) * 2) / 2,
                "stl": round(random.uniform(0.5, 1.5) * 2) / 2,
                "blk": blk,
                "to": round(random.uniform(1.5, 2.5) * 2) / 2,
            }
        
        # Generate props for home team (use real player names)
        for i, name in enumerate(home_roster):
            stats = gen_ncaab_stats(i)
            players.append({"name": name, "team": home_team, **stats})
        
        # Generate props for away team (use real player names)
        for i, name in enumerate(away_roster):
            stats = gen_ncaab_stats(i)
            players.append({"name": name, "team": away_team, **stats})
        
        # Build same outcomes structure as NBA
        points_outcomes = []
        rebounds_outcomes = []
        assists_outcomes = []
        
        for player in players:
            points_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["pts"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["pts"]},
            ])
            rebounds_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["reb"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["reb"]},
            ])
            assists_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["ast"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["ast"]},
            ])
        
        # Generate multi-bookmaker props with varied odds
        def vary_outcomes(outcomes: list, odds_offset: int) -> list:
            return [{**o, "price": o["price"] + odds_offset} for o in outcomes]
        
        bookmakers = []
        for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
            bookmakers.append({
                "key": book_key,
                "title": book_title,
                "markets": [
                    {"key": "player_points", "outcomes": vary_outcomes(points_outcomes, odds_offset)},
                    {"key": "player_rebounds", "outcomes": vary_outcomes(rebounds_outcomes, odds_offset)},
                    {"key": "player_assists", "outcomes": vary_outcomes(assists_outcomes, odds_offset)},
                ],
            })
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": times["early"],
            "bookmakers": bookmakers,
        }

    def _generate_dynamic_nfl_props(
        self,
        external_game_id: str,
        sport_key: str,
        times: dict[str, str],
    ) -> dict[str, Any]:
        """Generate dynamic NFL player props for any game."""
        import random
        
        # Use default roster
        home_roster = DEFAULT_NFL_ROSTER
        away_roster = DEFAULT_NFL_ROSTER
        
        players = []
        
        def gen_nfl_stats(position_idx: int) -> dict:
            """Generate realistic NFL stats based on position."""
            if position_idx == 0:  # QB
                return {
                    "pass_yds": round(random.uniform(220, 280) * 2) / 2,
                    "pass_tds": round(random.uniform(1.5, 2.5) * 2) / 2,
                    "pass_att": round(random.uniform(28, 36) * 2) / 2,
                    "int": round(random.uniform(0.5, 1) * 2) / 2,
                    "rush_yds": round(random.uniform(8, 25) * 2) / 2,
                }
            elif position_idx == 1:  # RB
                return {
                    "rush_yds": round(random.uniform(55, 85) * 2) / 2,
                    "rush_att": round(random.uniform(12, 18) * 2) / 2,
                    "rec": round(random.uniform(2, 4) * 2) / 2,
                    "rec_yds": round(random.uniform(15, 35) * 2) / 2,
                }
            else:  # WR/TE
                return {
                    "rec": round(random.uniform(4, 7) * 2) / 2,
                    "rec_yds": round(random.uniform(50, 85) * 2) / 2,
                    "targets": round(random.uniform(6, 10) * 2) / 2,
                }
        
        for i, name in enumerate(home_roster):
            stats = gen_nfl_stats(i)
            players.append({"name": f"Home {name}", **stats})
        
        for i, name in enumerate(away_roster):
            stats = gen_nfl_stats(i)
            players.append({"name": f"Away {name}", **stats})
        
        pass_yds_outcomes = []
        rush_yds_outcomes = []
        rec_yds_outcomes = []
        
        for player in players:
            if "pass_yds" in player:
                pass_yds_outcomes.extend([
                    {"name": "Over", "description": player["name"], "price": -110, "point": player["pass_yds"]},
                    {"name": "Under", "description": player["name"], "price": -110, "point": player["pass_yds"]},
                ])
            if "rush_yds" in player:
                rush_yds_outcomes.extend([
                    {"name": "Over", "description": player["name"], "price": -110, "point": player["rush_yds"]},
                    {"name": "Under", "description": player["name"], "price": -110, "point": player["rush_yds"]},
                ])
            if "rec_yds" in player:
                rec_yds_outcomes.extend([
                    {"name": "Over", "description": player["name"], "price": -110, "point": player["rec_yds"]},
                    {"name": "Under", "description": player["name"], "price": -110, "point": player["rec_yds"]},
                ])
        
        # Generate multi-bookmaker props with varied odds
        def vary_outcomes(outcomes: list, odds_offset: int) -> list:
            return [{**o, "price": o["price"] + odds_offset} for o in outcomes]
        
        bookmakers = []
        for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
            bookmakers.append({
                "key": book_key,
                "title": book_title,
                "markets": [
                    {"key": "player_pass_yds", "outcomes": vary_outcomes(pass_yds_outcomes, odds_offset)},
                    {"key": "player_rush_yds", "outcomes": vary_outcomes(rush_yds_outcomes, odds_offset)},
                    {"key": "player_reception_yds", "outcomes": vary_outcomes(rec_yds_outcomes, odds_offset)},
                ],
            })
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": "Home Team",
            "away_team": "Away Team",
            "commence_time": times["early"],
            "bookmakers": bookmakers,
        }

    def _generate_dynamic_tennis_props(
        self,
        external_game_id: str,
        sport_key: str,
        times: dict[str, str],
    ) -> dict[str, Any]:
        """Generate dynamic tennis player props for any match."""
        import random
        
        # Tennis match is between 2 players (player1 vs player2)
        # Try to extract player names from game ID
        # Format examples: match_djokovic_alcaraz_20260202, match_player1_player2_20260202
        parts = external_game_id.split("_")
        
        # ATP/WTA top players for realistic stub data
        atp_players = [
            "Novak Djokovic", "Carlos Alcaraz", "Jannik Sinner", "Daniil Medvedev",
            "Andrey Rublev", "Alexander Zverev", "Stefanos Tsitsipas", "Holger Rune",
            "Taylor Fritz", "Casper Ruud", "Hubert Hurkacz", "Alex de Minaur",
            "Tommy Paul", "Frances Tiafoe", "Ben Shelton", "Sebastian Korda",
        ]
        
        wta_players = [
            "Iga Swiatek", "Aryna Sabalenka", "Coco Gauff", "Elena Rybakina",
            "Jessica Pegula", "Ons Jabeur", "Qinwen Zheng", "Jasmine Paolini",
            "Madison Keys", "Emma Navarro", "Danielle Collins", "Mirra Andreeva",
            "Jelena Ostapenko", "Maria Sakkari", "Daria Kasatkina", "Beatriz Haddad Maia",
        ]
        
        # Select player pool based on sport key
        if "wta" in sport_key:
            players = wta_players
        else:
            players = atp_players
        
        # Try to get player names from parts or randomly select
        if len(parts) >= 3:
            player1_name = parts[1].replace("-", " ").title()
            player2_name = parts[2].replace("-", " ").title()
            # If names are generic, replace with random top players
            if player1_name.lower() in ["player1", "home", "unknown"]:
                player1_name = random.choice(players)
            if player2_name.lower() in ["player2", "away", "unknown"]:
                player2_name = random.choice([p for p in players if p != player1_name])
        else:
            player1_name = random.choice(players)
            player2_name = random.choice([p for p in players if p != player1_name])
        
        def gen_tennis_stats(is_favorite: bool) -> dict:
            """Generate realistic tennis prop stats."""
            # Favorites tend to have higher stats in winning scenarios
            mult = 1.1 if is_favorite else 0.9
            
            return {
                "aces": round(random.uniform(5, 15) * mult * 2) / 2,
                "double_faults": round(random.uniform(2, 6) * 2) / 2,
                "games_won": round(random.uniform(10, 18) * mult * 2) / 2,
                "sets_won": round(random.uniform(1.5, 2.5) * mult * 2) / 2,
            }
        
        # Generate stats for both players
        player1_stats = gen_tennis_stats(is_favorite=True)
        player2_stats = gen_tennis_stats(is_favorite=False)
        
        players_data = [
            {"name": player1_name, **player1_stats},
            {"name": player2_name, **player2_stats},
        ]
        
        # Build outcomes for each prop type
        aces_outcomes = []
        double_faults_outcomes = []
        games_won_outcomes = []
        sets_won_outcomes = []
        
        for player in players_data:
            aces_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["aces"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["aces"]},
            ])
            double_faults_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["double_faults"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["double_faults"]},
            ])
            games_won_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["games_won"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["games_won"]},
            ])
            sets_won_outcomes.extend([
                {"name": "Over", "description": player["name"], "price": -110, "point": player["sets_won"]},
                {"name": "Under", "description": player["name"], "price": -110, "point": player["sets_won"]},
            ])
        
        # Total games for the match (both players combined)
        total_games = round((player1_stats["games_won"] + player2_stats["games_won"]) * 2) / 2
        total_games_outcomes = [
            {"name": "Over", "description": "Total Games", "price": -110, "point": total_games},
            {"name": "Under", "description": "Total Games", "price": -110, "point": total_games},
        ]
        
        # Generate multi-bookmaker props with varied odds
        def vary_outcomes(outcomes: list, odds_offset: int) -> list:
            return [{**o, "price": o["price"] + odds_offset} for o in outcomes]
        
        bookmakers = []
        for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
            bookmakers.append({
                "key": book_key,
                "title": book_title,
                "markets": [
                    {"key": "player_aces", "outcomes": vary_outcomes(aces_outcomes, odds_offset)},
                    {"key": "player_double_faults", "outcomes": vary_outcomes(double_faults_outcomes, odds_offset)},
                    {"key": "player_games_won", "outcomes": vary_outcomes(games_won_outcomes, odds_offset)},
                    {"key": "player_sets_won", "outcomes": vary_outcomes(sets_won_outcomes, odds_offset)},
                    {"key": "player_total_games", "outcomes": vary_outcomes(total_games_outcomes, odds_offset)},
                ],
            })
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": player1_name,  # In tennis, home_team is player 1
            "away_team": player2_name,  # away_team is player 2
            "commence_time": times["early"],
            "bookmakers": bookmakers,
        }

    def _generate_dynamic_mlb_props(
        self,
        external_game_id: str,
        sport_key: str,
        times: dict[str, str],
    ) -> dict[str, Any]:
        """Generate dynamic MLB player props for any game."""
        import random
        
        # MLB team rosters with key players (2025-26 season)
        MLB_ROSTERS = {
            "New York Yankees": [
                ("Aaron Judge", "OF", {"hits": 1.5, "total_bases": 2.5, "home_runs": 0.5, "rbis": 1.5, "runs": 1.0}),
                ("Juan Soto", "OF", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.0, "runs": 1.0}),
                ("Gerrit Cole", "SP", {"strikeouts": 7.5, "earned_runs": 2.5, "hits_allowed": 5.5, "outs": 18.5}),
            ],
            "Boston Red Sox": [
                ("Rafael Devers", "3B", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.0, "runs": 0.5}),
                ("Masataka Yoshida", "OF", {"hits": 1.5, "total_bases": 1.5, "home_runs": 0.5, "rbis": 1.0, "runs": 0.5}),
                ("Brayan Bello", "SP", {"strikeouts": 5.5, "earned_runs": 3.0, "hits_allowed": 6.0, "outs": 17.5}),
            ],
            "Los Angeles Dodgers": [
                ("Mookie Betts", "OF", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.0, "runs": 1.0}),
                ("Freddie Freeman", "1B", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.5, "runs": 1.0}),
                ("Tyler Glasnow", "SP", {"strikeouts": 8.5, "earned_runs": 2.5, "hits_allowed": 5.0, "outs": 18.5}),
            ],
            "San Diego Padres": [
                ("Fernando Tatis Jr.", "OF", {"hits": 1.5, "total_bases": 2.5, "home_runs": 0.5, "rbis": 1.0, "runs": 1.0}),
                ("Manny Machado", "3B", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.0, "runs": 0.5}),
                ("Yu Darvish", "SP", {"strikeouts": 6.5, "earned_runs": 3.0, "hits_allowed": 6.0, "outs": 18.5}),
            ],
            "Chicago Cubs": [
                ("Cody Bellinger", "OF", {"hits": 1.0, "total_bases": 1.5, "home_runs": 0.5, "rbis": 1.0, "runs": 0.5}),
                ("Nico Hoerner", "SS", {"hits": 1.5, "total_bases": 1.5, "home_runs": 0.5, "rbis": 0.5, "runs": 0.5}),
                ("Justin Steele", "SP", {"strikeouts": 6.5, "earned_runs": 3.0, "hits_allowed": 6.5, "outs": 17.5}),
            ],
            "St. Louis Cardinals": [
                ("Nolan Arenado", "3B", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.0, "runs": 0.5}),
                ("Paul Goldschmidt", "1B", {"hits": 1.0, "total_bases": 1.5, "home_runs": 0.5, "rbis": 1.0, "runs": 0.5}),
                ("Sonny Gray", "SP", {"strikeouts": 7.5, "earned_runs": 2.5, "hits_allowed": 5.5, "outs": 18.5}),
            ],
            "Atlanta Braves": [
                ("Ronald Acuna Jr.", "OF", {"hits": 1.5, "total_bases": 2.5, "home_runs": 0.5, "rbis": 1.0, "runs": 1.0}),
                ("Matt Olson", "1B", {"hits": 1.0, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.5, "runs": 0.5}),
                ("Spencer Strider", "SP", {"strikeouts": 9.5, "earned_runs": 2.5, "hits_allowed": 5.0, "outs": 18.5}),
            ],
            "New York Mets": [
                ("Francisco Lindor", "SS", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.0, "runs": 1.0}),
                ("Pete Alonso", "1B", {"hits": 1.0, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.5, "runs": 0.5}),
                ("Kodai Senga", "SP", {"strikeouts": 8.5, "earned_runs": 2.5, "hits_allowed": 5.5, "outs": 18.5}),
            ],
            "Houston Astros": [
                ("Jose Altuve", "2B", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.0, "runs": 1.0}),
                ("Yordan Alvarez", "DH", {"hits": 1.5, "total_bases": 2.5, "home_runs": 0.5, "rbis": 1.5, "runs": 0.5}),
                ("Framber Valdez", "SP", {"strikeouts": 6.5, "earned_runs": 3.0, "hits_allowed": 7.0, "outs": 19.5}),
            ],
            "Texas Rangers": [
                ("Corey Seager", "SS", {"hits": 1.5, "total_bases": 2.5, "home_runs": 0.5, "rbis": 1.5, "runs": 1.0}),
                ("Marcus Semien", "2B", {"hits": 1.5, "total_bases": 2.0, "home_runs": 0.5, "rbis": 1.0, "runs": 1.0}),
                ("Jacob deGrom", "SP", {"strikeouts": 9.5, "earned_runs": 2.0, "hits_allowed": 4.5, "outs": 18.5}),
            ],
            "San Francisco Giants": [
                ("Matt Chapman", "3B", {"hits": 1.0, "total_bases": 1.5, "home_runs": 0.5, "rbis": 1.0, "runs": 0.5}),
                ("Jung Hoo Lee", "OF", {"hits": 1.5, "total_bases": 1.5, "home_runs": 0.5, "rbis": 0.5, "runs": 0.5}),
                ("Logan Webb", "SP", {"strikeouts": 6.5, "earned_runs": 3.0, "hits_allowed": 7.0, "outs": 19.5}),
            ],
            "Oakland Athletics": [
                ("Brent Rooker", "DH", {"hits": 1.0, "total_bases": 1.5, "home_runs": 0.5, "rbis": 1.0, "runs": 0.5}),
                ("JJ Bleday", "OF", {"hits": 1.0, "total_bases": 1.5, "home_runs": 0.5, "rbis": 0.5, "runs": 0.5}),
                ("JP Sears", "SP", {"strikeouts": 5.5, "earned_runs": 3.5, "hits_allowed": 7.0, "outs": 17.5}),
            ],
        }
        
        # Parse team names from game ID (format: mlb_nyy_bos_20260201)
        parts = external_game_id.replace("mlb_", "").split("_")
        if len(parts) >= 2:
            # Map abbreviations to team names
            abbr_to_team = {
                "nyy": "New York Yankees", "bos": "Boston Red Sox",
                "lad": "Los Angeles Dodgers", "sd": "San Diego Padres",
                "chc": "Chicago Cubs", "stl": "St. Louis Cardinals",
                "atl": "Atlanta Braves", "nym": "New York Mets",
                "hou": "Houston Astros", "tex": "Texas Rangers",
                "sf": "San Francisco Giants", "oak": "Oakland Athletics",
            }
            away_abbr = parts[0].lower()
            home_abbr = parts[1].lower()
            away_team = abbr_to_team.get(away_abbr, "Away Team")
            home_team = abbr_to_team.get(home_abbr, "Home Team")
        else:
            away_team = "Away Team"
            home_team = "Home Team"
        
        # Get players for both teams
        home_players = MLB_ROSTERS.get(home_team, MLB_ROSTERS["New York Yankees"])
        away_players = MLB_ROSTERS.get(away_team, MLB_ROSTERS["Boston Red Sox"])
        
        # Generate props outcomes
        batter_hits_outcomes = []
        batter_total_bases_outcomes = []
        batter_home_runs_outcomes = []
        batter_rbis_outcomes = []
        pitcher_strikeouts_outcomes = []
        pitcher_outs_outcomes = []
        
        for team_players, team_name in [(home_players, home_team), (away_players, away_team)]:
            for player_name, position, stats in team_players:
                # Add slight randomness to lines
                variance = random.uniform(-0.5, 0.5)
                
                if position == "SP":
                    # Pitcher props
                    ks = stats["strikeouts"] + variance
                    outs = stats["outs"]
                    pitcher_strikeouts_outcomes.extend([
                        {"name": "Over", "description": f"{player_name} Strikeouts", "price": -115, "point": round(ks * 2) / 2},
                        {"name": "Under", "description": f"{player_name} Strikeouts", "price": -105, "point": round(ks * 2) / 2},
                    ])
                    pitcher_outs_outcomes.extend([
                        {"name": "Over", "description": f"{player_name} Outs Recorded", "price": -110, "point": outs},
                        {"name": "Under", "description": f"{player_name} Outs Recorded", "price": -110, "point": outs},
                    ])
                else:
                    # Batter props
                    hits = stats["hits"]
                    tb = stats["total_bases"] + variance * 0.5
                    hr = stats["home_runs"]
                    rbis = stats["rbis"]
                    
                    batter_hits_outcomes.extend([
                        {"name": "Over", "description": f"{player_name} Hits", "price": -120, "point": hits},
                        {"name": "Under", "description": f"{player_name} Hits", "price": 100, "point": hits},
                    ])
                    batter_total_bases_outcomes.extend([
                        {"name": "Over", "description": f"{player_name} Total Bases", "price": -115, "point": round(tb * 2) / 2},
                        {"name": "Under", "description": f"{player_name} Total Bases", "price": -105, "point": round(tb * 2) / 2},
                    ])
                    batter_home_runs_outcomes.extend([
                        {"name": "Over", "description": f"{player_name} Home Runs", "price": 180, "point": hr},
                        {"name": "Under", "description": f"{player_name} Home Runs", "price": -220, "point": hr},
                    ])
                    batter_rbis_outcomes.extend([
                        {"name": "Over", "description": f"{player_name} RBIs", "price": -110, "point": rbis},
                        {"name": "Under", "description": f"{player_name} RBIs", "price": -110, "point": rbis},
                    ])
        
        # Generate multi-bookmaker props with varied odds
        def vary_outcomes(outcomes: list, odds_offset: int) -> list:
            return [{**o, "price": o["price"] + odds_offset} for o in outcomes]
        
        bookmakers = []
        for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
            bookmakers.append({
                "key": book_key,
                "title": book_title,
                "markets": [
                    {"key": "batter_hits", "outcomes": vary_outcomes(batter_hits_outcomes, odds_offset)},
                    {"key": "batter_total_bases", "outcomes": vary_outcomes(batter_total_bases_outcomes, odds_offset)},
                    {"key": "batter_home_runs", "outcomes": vary_outcomes(batter_home_runs_outcomes, odds_offset)},
                    {"key": "batter_rbis", "outcomes": vary_outcomes(batter_rbis_outcomes, odds_offset)},
                    {"key": "pitcher_strikeouts", "outcomes": vary_outcomes(pitcher_strikeouts_outcomes, odds_offset)},
                    {"key": "pitcher_outs", "outcomes": vary_outcomes(pitcher_outs_outcomes, odds_offset)},
                ],
            })
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": times["afternoon"],
            "bookmakers": bookmakers,
        }

    def _generate_dynamic_nhl_props(
        self,
        external_game_id: str,
        sport_key: str,
        times: dict[str, str],
    ) -> dict[str, Any]:
        """Generate dynamic NHL player props for any game."""
        import random
        
        # NHL team rosters (2/6/26 current slate)
        NHL_ROSTERS = {
            "Pittsburgh Penguins": [
                ("Sidney Crosby", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Evgeni Malkin", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Erik Karlsson", "D", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 2.5, "blocked": 1.5}),
                ("Bryan Rust", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 3.5, "blocked": 0.5}),
                ("Yaroslav Chinakhov", "LW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
            ],
            "Buffalo Sabres": [
                ("Tage Thompson", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Jack Quinn", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 3.5, "blocked": 0.5}),
                ("Rasmus Dahlin", "D", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 2.5}),
                ("Jason Zucker", "LW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("Josh Doan", "LD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
            ],
            "New York Islanders": [
                ("Bo Horvat", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Mathew Barzal", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Cal Clutterbuck", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
                ("Mike Schaefer", "LD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 1.5, "blocked": 2.5}),
                ("Simon Holmstrom", "RD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
            ],
            "New Jersey Devils": [
                ("Nico Hischier", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Jesper Bratt", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Dawson Mercer", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("Timo Meier", "LD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 1.5}),
                ("Dougie Hamilton", "RD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 2.5}),
            ],
            "Carolina Hurricanes": [
                ("Sebastian Aho", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Andrei Svechnikov", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Seth Jarvis", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("Shayne Gostisbehere", "LD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 1.5}),
                ("Nikita Ehlers", "RD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
            ],
            "New York Rangers": [
                ("Vincent Trocheck", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("J.T. Miller", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Alexis Lafreniere", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("Vladislav Gavrikov", "LD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 1.5, "blocked": 2.5}),
                ("Mika Zibanejad", "RD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
            ],
            "Ottawa Senators": [
                ("Tim Stutzle", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Brady Tkachuk", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Drake Batherson", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 3.5, "blocked": 0.5}),
                ("Jake Sanderson", "LD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 2.5, "blocked": 1.5}),
                ("Dylan Cozens", "RD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
            ],
            "Philadelphia Flyers": [
                ("Cole Dvorak", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Bobby Brink", "LW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("Travis Konecny", "RW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Tyson Zegras", "LD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Jamie Drysdale", "RD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
            ],
            "Nashville Predators": [
                ("Ryan O'Reilly", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Steven Stamkos", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Jonathan Marchessault", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("Filip Forsberg", "LD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Roman Josi", "RD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 2.5}),
            ],
            "Washington Capitals": [
                ("Dylan Strome", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Alex Ovechkin", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 5.5, "blocked": 0.5}),
                ("Ryan Leonard", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("John Chychrun", "LD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 1.5}),
                ("Tom Wilson", "RD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
            ],
            "Florida Panthers": [
                ("Sam Bennett", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Sam Reinhart", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Matthew Tkachuk", "RW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
                ("Anton Lundell", "LD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
                ("Urho Balinskis", "RD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
            ],
            "Tampa Bay Lightning": [
                ("Jonny Gaudreau", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Brandon Hagel", "LW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Nikita Kucherov", "RW", {"goals": 0.5, "assists": 2.5, "points": 3.5, "shots": 4.5, "blocked": 0.5}),
                ("Oliver Bjorkstrand", "LD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 3.5, "blocked": 0.5}),
                ("Darren Raddysh", "RD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
            ],
            "Los Angeles Kings": [
                ("Adrian Kempe", "RW", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Anze Kopitar", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Quinton Byfield", "LW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("Kevin Fiala", "LD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Brandt Clarke", "RD", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
            ],
            "Vegas Golden Knights": [
                ("Jack Eichel", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Pavel Dorofeyev", "LW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 0.5}),
                ("Mark Stone", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 1.5}),
                ("Mitch Marner", "LD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
                ("Tomas Hertl", "RD", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 3.5, "blocked": 0.5}),
            ],
        }
        
        DEFAULT_NHL_ROSTER = [
            ("Star Forward", "C", {"goals": 0.5, "assists": 1.5, "points": 2.5, "shots": 4.5, "blocked": 0.5}),
            ("Top Winger", "RW", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 3.5, "blocked": 0.5}),
            ("Elite Defenseman", "D", {"goals": 0.5, "assists": 0.5, "points": 1.5, "shots": 2.5, "blocked": 2.5}),
        ]
        
        # Parse game ID to get teams (format: nhl_away_home_date)
        parts = external_game_id.split("_")
        home_team = "Home Team"
        away_team = "Away Team"
        
        # Try to match team abbreviations
        team_abbr_map = {
            # 2/6/26 Slate Teams
            "pit": "Pittsburgh Penguins", "buf": "Buffalo Sabres",
            "nyi": "New York Islanders", "nj": "New Jersey Devils", "njd": "New Jersey Devils",
            "car": "Carolina Hurricanes", "nyr": "New York Rangers",
            "ott": "Ottawa Senators", "phi": "Philadelphia Flyers",
            "nsh": "Nashville Predators", "wsh": "Washington Capitals",
            "fla": "Florida Panthers", "tbl": "Tampa Bay Lightning",
            "lak": "Los Angeles Kings", "vgk": "Vegas Golden Knights",
            # Legacy teams for compatibility
            "ava": "Colorado Avalanche", "wil": "Minnesota Wild", "min": "Minnesota Wild",
            "lea": "Toronto Maple Leafs", "tor": "Toronto Maple Leafs", "bru": "Boston Bruins", "bos": "Boston Bruins",
            "oil": "Edmonton Oilers", "edm": "Edmonton Oilers", "kni": "Vegas Golden Knights",
            "pan": "Florida Panthers", "hur": "Carolina Hurricanes", "ran": "New York Rangers",
            "lig": "Tampa Bay Lightning", "jet": "Winnipeg Jets", "wpg": "Winnipeg Jets",
            "sta": "Dallas Stars", "dal": "Dallas Stars",
        }
        
        if len(parts) >= 3:
            away_abbr = parts[1].lower()
            home_abbr = parts[2].lower()
            away_team = team_abbr_map.get(away_abbr, "Away Team")
            home_team = team_abbr_map.get(home_abbr, "Home Team")
        
        # Get rosters
        home_roster = NHL_ROSTERS.get(home_team, DEFAULT_NHL_ROSTER)
        away_roster = NHL_ROSTERS.get(away_team, DEFAULT_NHL_ROSTER)
        
        # Build outcomes for props
        goals_outcomes = []
        assists_outcomes = []
        points_outcomes = []
        shots_outcomes = []
        blocked_outcomes = []
        
        for team_roster, team_name in [(home_roster, home_team), (away_roster, away_team)]:
            for player_name, position, stats in team_roster:
                # Add some variance
                goals_line = stats.get("goals", 0.5)
                assists_line = stats.get("assists", 0.5)
                points_line = stats.get("points", 1.5)
                shots_line = stats.get("shots", 3.5)
                blocked_line = stats.get("blocked", 0.5)
                
                goals_outcomes.extend([
                    {"name": "Over", "description": player_name, "price": -115, "point": goals_line},
                    {"name": "Under", "description": player_name, "price": -105, "point": goals_line},
                ])
                assists_outcomes.extend([
                    {"name": "Over", "description": player_name, "price": -110, "point": assists_line},
                    {"name": "Under", "description": player_name, "price": -110, "point": assists_line},
                ])
                points_outcomes.extend([
                    {"name": "Over", "description": player_name, "price": -115, "point": points_line},
                    {"name": "Under", "description": player_name, "price": -105, "point": points_line},
                ])
                shots_outcomes.extend([
                    {"name": "Over", "description": player_name, "price": -110, "point": shots_line},
                    {"name": "Under", "description": player_name, "price": -110, "point": shots_line},
                ])
                blocked_outcomes.extend([
                    {"name": "Over", "description": player_name, "price": -110, "point": blocked_line},
                    {"name": "Under", "description": player_name, "price": -110, "point": blocked_line},
                ])
        
        # Generate multi-bookmaker props with varied odds
        def vary_outcomes(outcomes: list, odds_offset: int) -> list:
            return [{**o, "price": o["price"] + odds_offset} for o in outcomes]
        
        bookmakers = []
        for book_key, book_title, odds_offset in STUB_BOOKMAKER_CONFIGS:
            bookmakers.append({
                "key": book_key,
                "title": book_title,
                "markets": [
                    {"key": "player_goals", "outcomes": vary_outcomes(goals_outcomes, odds_offset)},
                    {"key": "player_assists", "outcomes": vary_outcomes(assists_outcomes, odds_offset)},
                    {"key": "player_points", "outcomes": vary_outcomes(points_outcomes, odds_offset)},
                    {"key": "player_shots_on_goal", "outcomes": vary_outcomes(shots_outcomes, odds_offset)},
                    {"key": "player_blocked_shots", "outcomes": vary_outcomes(blocked_outcomes, odds_offset)},
                ],
            })
        
        return {
            "id": external_game_id,
            "sport_key": sport_key,
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": times["early"],
            "bookmakers": bookmakers,
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
        
        # Enforce rate limiting before making request
        await get_betstack_api_limiter().wait()
        
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
    "Seattle Seahawks": ["Geno Smith", "Kenneth Walker III", "Tyler Lockett", "Jaxon Smith-Njigba", "Noah Fant"],
    "Los Angeles Rams": ["Matthew Stafford", "Kyren Williams", "Puka Nacua", "Cooper Kupp", "Tutu Atwell"],
    "Minnesota Vikings": ["Sam Darnold", "Aaron Jones", "Justin Jefferson", "Jordan Addison", "TJ Hockenson"],
    "Houston Texans": ["CJ Stroud", "Joe Mixon", "Nico Collins", "Tank Dell", "Stefon Diggs"],
    "Pittsburgh Steelers": ["Russell Wilson", "Najee Harris", "George Pickens", "DK Metcalf", "Pat Freiermuth"],
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
    # Additional teams from schedule file
    "Villanova Wildcats": ["Mark Armstrong", "Wooga Poplar", "Eric Dixon", "TJ Bamba", "Brendan Hausen"],
    "Georgetown Hoyas": ["Malik Mack", "Jayden Epps", "Micah Peavy", "Thomas Sorber", "Curtis Williams Jr."],
    "Michigan State Spartans": ["Jaden Akins", "AJ Hoggard", "Coen Carr", "Xavier Booker", "Carson Cooper"],
    "Ohio State Buckeyes": ["Bruce Thornton", "Meechie Johnson Jr.", "Roddy Gayle Jr.", "Zed Key", "Evan Mahaffey"],
    "Texas Longhorns": ["Max Abmas", "Tre Johnson", "Jordan Pope", "Arthur Kaluma", "Ze'rik Onyema"],
    "Saint Mary's Gaels": ["Aidan Mahaney", "Paulius Murauskas", "Mitchell Saxen", "Luke Barrett", "Joshua Jefferson"],
    "Creighton Bluejays": ["Ryan Kalkbrenner", "Pop Isaacs", "Steven Ashworth", "Jamiya Neal", "Francisco Farabello"],
    "Indiana Hoosiers": ["Mackenzie Mgbako", "Oumar Ballo", "Myles Rice", "Kanaan Carlyle", "Luke Goode"],
    "Cincinnati Bearcats": ["Dan Skillings Jr.", "Simas Lukosius", "Dillon Mitchell", "Day Day Thomas", "Aziz Bandaogo"],
    "Oregon Ducks": ["TJ Bamba", "Jadrian Tracey", "Nate Bittle", "Jackson Shelstad", "Keeshawn Barthelemy"],
    "Washington Huskies": ["Great Osobor", "DJ Davis", "Zoom Diallo", "Tyler Harris", "Wilhelm Breidenbach"],
    "Virginia Cavaliers": ["Isaac McKneely", "Taine Murray", "Blake Buchanan", "Andrew Rohde", "Jacob Groves"],
    "Wake Forest Demon Deacons": ["Hunter Sallis", "Tre'Von Spillers", "Parker Friedrichsen", "Davion Hannah", "Efton Reid"],
    "Oklahoma Sooners": ["Jeremiah Fears", "Jalon Moore", "Kobe Elvis", "Sam Godwin", "Glenn Taylor Jr."],
    "Vanderbilt Commodores": ["Jason Edwards", "Devin McGlockton", "Tyler Tanner", "Mikaeel Alexander", "JaVon Small"],
    "USC Trojans": ["Isaiah Collier", "Boogie Ellis", "Kobe Johnson", "Arrinten Page", "Joshua Morgan"],
    "Marquette Golden Eagles": ["Kam Jones", "Tyler Kolek", "Chase Ross", "Stevie Mitchell", "Ben Gold"],
    "TCU Horned Frogs": ["Jameer Nelson Jr.", "Trazarien White", "Ernest Udeh Jr.", "Emanuel Miller", "Noah Reynolds"],
    "LSU Tigers": ["Cam Carter", "Jordan Sears", "Derek Fountain", "Daimion Collins", "Vyctorius Miller"],
    "South Carolina Gamecocks": ["Collin Murray-Boyles", "Zachary Davis", "Jamarii Thomas", "Nick Pringle", "Jacobi Wright"],
    "Wisconsin Badgers": ["John Blackwell", "John Tonje", "Kamari McGee", "Steven Crowl", "Nolan Winter"],
    "Memphis Tigers": ["PJ Haggerty", "Tyrese Hunter", "Colby Rogers", "Moussa Cisse", "Jahvon Quinerly"],
    "Oklahoma State Cowboys": ["Javon Small", "Abou Ousmane", "Jamyron Keller", "Brandon Garrison", "Joe Bamisile"],
    "NC State Wolfpack": ["Michael O'Connell", "Marcus Hill", "Brandon Huntley-Hatfield", "Ben Middlebrooks", "Jayden Taylor"],
    "Iowa Hawkeyes": ["Payton Sandfort", "Owen Freeman", "Josh Dix", "Brock Harding", "Seydou Traore"],
    "Minnesota Golden Gophers": ["Dawson Garcia", "Mike Mitchell Jr.", "Lu'Cye Patterson", "Pharrel Payne", "Cam Christie"],
    "Stanford Cardinal": ["Maxime Raynaud", "Jaylen Blakes", "Benny Gealer", "Ryan Agarwal", "Oziyah Sellers"],
    "Oregon State Beavers": ["Michael Rataj", "Nate Kingz", "Jordan Pope", "Parsa Fallah", "Tyler Bey"],
    "West Virginia Mountaineers": ["Tucker DeVries", "Javon Small", "Joseph Yesufu", "Amani Hansberry", "Eduardo Andre"],
    "Georgia Bulldogs": ["Somto Cyril", "Silas Demary Jr.", "Blue Cain", "Asa Newell", "Dylan James"],
    "Mississippi State Bulldogs": ["Josh Hubbard", "KeShawn Murphy", "Claudell Harris Jr.", "Cameron Matthews", "Michael Nwoko"],
    "San Francisco Dons": ["Marcus Williams", "Malik Thomas", "Josh Kunen", "Tyrell Roberts", "Ndewedo Newbury"],
    "Pittsburgh Panthers": ["Ishmael Leggett", "Jaland Lowe", "Zack Austin", "Jorge Diaz Graham", "Cam Corhen"],
    "Seton Hall Pirates": ["Kadary Richmond", "Dylan Addae-Wusu", "Chaunce Jenkins", "Prince Aligbe", "Jahmir Young"],
    "Arizona State Sun Devils": ["Adam Miller", "Joson Sanon", "BJ Freeman", "Basheer Jihad", "Shawn Phillips Jr."],
    "Rutgers Scarlet Knights": ["Dylan Harper", "Ace Bailey", "Emmanuel Ogbole", "Lathan Sommerville", "Zach Martini"],
    "Miami Hurricanes": ["Nijel Pack", "Matthew Cleveland", "Jalen Blackmon", "Brandon Johnson", "Favor Aire"],
    "Ole Miss Rebels": ["Sean Pedulla", "Jaylen Murray", "Malik Dia", "Jaemyn Brakefield", "Davon Barnes"],
    "Utah Utes": ["Gabe Madsen", "Keanu Dawes", "Hunter Erickson", "Lawson Lovering", "Ezra Ausar"],
    "Pepperdine Waves": ["Stefan Todorovic", "Michael Ajayi", "Moe Musa", "Dovydas Butka", "Boubacar Coulibaly"],
    "Xavier Musketeers": ["Zach Freemantle", "Quincy Olivari", "Dayvion McKnight", "Ryan Conwell", "Trey Green"],
    "California Golden Bears": ["Andrej Stojakovic", "Javan Willingham", "Joshua Ola-Joseph", "BJ Omot", "Mady Sissoko"],
    "Florida State Seminoles": ["Daquan Davis", "Jamir Watkins", "Malique Ewin", "Chandler Jackson", "Taylor Bol Bowen"],
    "Colorado Buffaloes": ["Andrej Jakimovski", "Julian Hammond III", "Javon Ruffin", "Elijah Malone", "Cody Williams"],
    "Penn State Nittany Lions": ["Ace Baldwin Jr.", "Nick Kern Jr.", "Zach Hicks", "Yanic Konan Niederhäuser", "Freddie Dilione V"],
    "Kansas State Wildcats": ["Dug McDaniel", "David N'Guessan", "Brendan Hausen", "Achor Achor", "Coleman Hawkins"],
}

# Default roster for teams not in the list
DEFAULT_ROSTER = ["Player One", "Player Two", "Player Three", "Player Four", "Player Five"]

# NBA Team Power Ratings
NBA_TEAM_RATINGS = {
    "Boston Celtics": 95, "Oklahoma City Thunder": 94, "Denver Nuggets": 93,
    "Milwaukee Bucks": 92, "Cleveland Cavaliers": 91, "Phoenix Suns": 90,
    "Minnesota Timberwolves": 89, "New York Knicks": 88, "Philadelphia 76ers": 87,
    "Miami Heat": 86, "Dallas Mavericks": 85, "Los Angeles Lakers": 84,
    "Golden State Warriors": 83, "Sacramento Kings": 82, "Los Angeles Clippers": 81,
    "New Orleans Pelicans": 80, "Indiana Pacers": 79, "Orlando Magic": 78,
    "Atlanta Hawks": 77, "Chicago Bulls": 76, "Houston Rockets": 75,
    "Brooklyn Nets": 74, "Memphis Grizzlies": 73, "Toronto Raptors": 72,
    "Utah Jazz": 71, "San Antonio Spurs": 70, "Portland Trail Blazers": 69,
    "Washington Wizards": 67, "Detroit Pistons": 66,
}

# NBA Rosters (key players for props) - 2026 Season Depth Charts
NBA_ROSTERS = {
    "Boston Celtics": ["Jayson Tatum", "Jaylen Brown", "Derrick White", "Jrue Holiday", "Kristaps Porzingis"],
    "Oklahoma City Thunder": ["Shai Gilgeous-Alexander", "Chet Holmgren", "Jalen Williams", "Josh Giddey", "Luguentz Dort"],
    "Denver Nuggets": ["Nikola Jokic", "Jamal Murray", "Michael Porter Jr.", "Aaron Gordon", "Kentavious Caldwell-Pope"],
    "Milwaukee Bucks": ["Giannis Antetokounmpo", "Damian Lillard", "Khris Middleton", "Brook Lopez", "Bobby Portis"],
    "Cleveland Cavaliers": ["Donovan Mitchell", "Darius Garland", "Evan Mobley", "Jarrett Allen", "Max Strus"],
    "Phoenix Suns": ["Kevin Durant", "Devin Booker", "Bradley Beal", "Jusuf Nurkic", "Grayson Allen"],
    "Minnesota Timberwolves": ["Anthony Edwards", "Karl-Anthony Towns", "Rudy Gobert", "Jaden McDaniels", "Mike Conley"],
    "New York Knicks": ["Jalen Brunson", "Julius Randle", "OG Anunoby", "Donte DiVincenzo", "Isaiah Hartenstein"],
    "Philadelphia 76ers": ["Joel Embiid", "Tyrese Maxey", "Tobias Harris", "Buddy Hield", "Kelly Oubre Jr."],
    "Miami Heat": ["Jimmy Butler", "Bam Adebayo", "Tyler Herro", "Terry Rozier", "Caleb Martin"],
    "Dallas Mavericks": ["Kyrie Irving", "PJ Washington", "Dereck Lively II", "Daniel Gafford", "Klay Thompson"],
    "Los Angeles Lakers": ["LeBron James", "Luka Doncic", "Deandre Ayton", "Austin Reaves", "Rui Hachimura"],
    "Golden State Warriors": ["Stephen Curry", "Klay Thompson", "Andrew Wiggins", "Draymond Green", "Chris Paul"],
    "Sacramento Kings": ["De'Aaron Fox", "Domantas Sabonis", "Keegan Murray", "Malik Monk", "Harrison Barnes"],
    "Los Angeles Clippers": ["Kawhi Leonard", "Paul George", "James Harden", "Ivica Zubac", "Norman Powell"],
    "New Orleans Pelicans": ["Zion Williamson", "Brandon Ingram", "CJ McCollum", "Herb Jones", "Jonas Valanciunas"],
    "Indiana Pacers": ["Tyrese Haliburton", "Pascal Siakam", "Myles Turner", "Buddy Hield", "Aaron Nesmith"],
    "Orlando Magic": ["Paolo Banchero", "Franz Wagner", "Wendell Carter Jr.", "Jalen Suggs", "Cole Anthony"],
    "Atlanta Hawks": ["Trae Young", "Dejounte Murray", "Jalen Johnson", "De'Andre Hunter", "Clint Capela"],
    "Chicago Bulls": ["DeMar DeRozan", "Zach LaVine", "Nikola Vucevic", "Coby White", "Alex Caruso"],
    "Houston Rockets": ["Alperen Sengun", "Fred VanVleet", "Jabari Smith Jr.", "Dillon Brooks", "Amen Thompson"],
    "Brooklyn Nets": ["Mikal Bridges", "Cam Thomas", "Spencer Dinwiddie", "Nic Claxton", "Dorian Finney-Smith"],
    "Memphis Grizzlies": ["Ja Morant", "Desmond Bane", "Jaren Jackson Jr.", "Marcus Smart", "Luke Kennard"],
    "Toronto Raptors": ["Scottie Barnes", "RJ Barrett", "Jakob Poeltl", "Immanuel Quickley", "Gary Trent Jr."],
    "Atlanta Hawks": ["Dyson Daniels", "Nickeil Alexander-Walker", "Zac Risacher", "Jalen Johnson", "Onyeka Okongwu"],
    "Boston Celtics": ["Payton Pritchard", "Derrick White", "Jaylen Brown", "Sam Hauser", "Nikola Vucevic"],
    "Brooklyn Nets": ["Noah Traore", "Eric Demin", "Michael Porter Jr.", "Nic Clowney", "Nic Claxton"],
    "Charlotte Hornets": ["LaMelo Ball", "Kris Knueppel", "Brandon Miller", "Miles Bridges", "Makur Diabate"],
    "Chicago Bulls": ["Josh Giddey", "Jalen Ivey", "Isaac Okoro", "Matas Buzelis", "Jon Smith"],
    "Cleveland Cavaliers": ["James Harden", "Donovan Mitchell", "Darius Wade", "Evan Mobley", "Jarrett Allen"],
    "Dallas Mavericks": ["Cooper Flagg", "Max Christie", "Nickeil Marshall", "PJ Washington", "Daniel Gafford"],
    "Denver Nuggets": ["Jamal Murray", "Christian Braun", "Porter Watson (IL)", "Aaron Jones", "Nikola Jokic"],
    "Detroit Pistons": ["Cade Cunningham", "Dyson Robinson", "Ausar Thompson", "Taj Harris (IL)", "Jalen Duren"],
    "Golden State Warriors": ["Stephen Curry", "Brandin Podziemski", "Moses Moody", "Draymond Green", "Kristaps Porzingis (IL)"],
    "Houston Rockets": ["Amen Thompson", "Tari Eason (IL)", "Kevin Durant", "Jabari Smith Jr.", "Alperen Sengun"],
    "Indiana Pacers": ["Andrew Nembhard", "Bennedict Mathurin", "Aaron Nesmith", "Pascal Siakam", "Isaiah Hartenstein (IL)"],
    "LA Clippers": ["D'Angelo Russell (IL)", "Bennedict Mathurin (IL)", "Kawhi Leonard", "John Collins", "Brook Lopez"],
    "LA Lakers": ["Luka Doncic", "Austin Reaves", "Marcus Smart", "LeBron James", "Deandre Ayton"],
    "Memphis Grizzlies": ["Cam Spencer (IL)", "Cameron Coward", "Jordan Wells", "Gabe Jackson", "Santi Aldama (IL)"],
    "Miami Heat": ["Donovan Mitchell", "Tyler Herro (IL)", "Norman Powell", "Andrew Wiggins", "Bam Adebayo"],
    "Milwaukee Bucks": ["Kyle Kuzma", "Adrian Griffin", "Gary Harris", "Kris Middleton", "Myles Turner"],
    "Minnesota Timberwolves": ["Donte DiVincenzo", "Anthony Edwards", "Jalen McDaniels", "Julius Randle", "Rudy Gobert"],
    "New Orleans Pelicans": ["Trey Murphy III", "Herbert Jones", "Saddiq Bey", "Zion Williamson", "Dereck Queen"],
    "New York Knicks": ["Jalen Brunson", "Josh Hart", "Mikal Bridges", "OG Anunoby", "Karl-Anthony Towns"],
    "Oklahoma City Thunder": ["Shai Gilgeous-Alexander", "Luguentz Dort", "Jalen Williams", "Chet Holmgren", "Isaiah Hartenstein"],
    "Orlando Magic": ["Jalen Suggs", "Desmond Bane", "Franz Wagner", "Paolo Banchero", "Wendell Carter Jr."],
    "Philadelphia 76ers": ["Tyrese Maxey", "Vernon Edgecombe", "Kelly Oubre Jr.", "Dylan Barlow", "Joel Embiid"],
    "Phoenix Suns": ["Devin Booker", "Jalen Green (IL)", "Dillon Brooks", "Royce O'Neale", "Mark Williams"],
    "Portland Trail Blazers": ["Jordan Holiday", "Scoot Sharpe", "Tristan Camara", "Deni Avdija", "Donovan Clingan"],
    "Sacramento Kings": ["Russell Westbrook", "Zach LaVine", "Doug McDermott", "DeMar DeRozan", "Domantas Sabonis"],
    "San Antonio Spurs": ["De'Aaron Fox", "Stephon Castle", "Devin Vassell", "Jalen Champagnie", "Victor Wembanyama"],
    "Toronto Raptors": ["Immanuel Quickley", "Brandon Ingram", "RJ Barrett (IL)", "Scottie Barnes", "Chris Murray-Boyles"],
    "Utah Jazz": ["Keyonte George", "Collin Williams", "Aaron Bailey", "Lauri Markkanen", "Walker Kessler"],
    "Washington Wizards": ["Tyus Johnson", "Kevin George", "Bilal Coulibaly", "Jalen Champagnie", "Alex Sarr"],
    "Detroit Pistons": ["Cade Cunningham", "Dyson Robinson", "Ausar Thompson", "Taj Harris (IL)", "Jalen Duren"],
}

# Default NBA roster
DEFAULT_NBA_ROSTER = ["Guard One", "Guard Two", "Forward One", "Forward Two", "Center"]
class ESPNScheduleProvider:
    """
    Free schedule provider using ESPN's public API.
    
    Supports NBA, NCAAB, NFL, NCAAF, MLB, NHL - fetches real game schedules and generates 
    realistic odds/props based on team power ratings.
    """
    
    # ESPN API base URLs by sport
    ESPN_URLS = {
        "basketball_nba": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba",
        "basketball_ncaab": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball",
        "americanfootball_nfl": "https://site.api.espn.com/apis/site/v2/sports/football/nfl",
        "americanfootball_ncaaf": "https://site.api.espn.com/apis/site/v2/sports/football/college-football",
        "baseball_mlb": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb",
        "icehockey_nhl": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl",
    }
    
    def __init__(self, sport_key: str = "basketball_ncaab"):
        self._client: Optional[httpx.AsyncClient] = None
        self.sport_key = sport_key
        self.base_url = self.ESPN_URLS.get(sport_key)
        if not self.base_url:
            logger.warning(f"No ESPN URL for {sport_key}, defaulting to NCAAB")
            self.base_url = self.ESPN_URLS["basketball_ncaab"]
    
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
            # Enforce rate limiting before making request
            await get_espn_api_limiter().wait()
            
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
        is_nba = self.sport_key == "basketball_nba"
        
        if is_nfl:
            home_roster = NFL_ROSTERS.get(home_team, DEFAULT_NFL_ROSTER)
            away_roster = NFL_ROSTERS.get(away_team, DEFAULT_NFL_ROSTER)
        elif is_nba:
            home_roster = NBA_ROSTERS.get(home_team, DEFAULT_NBA_ROSTER)
            away_roster = NBA_ROSTERS.get(away_team, DEFAULT_NBA_ROSTER)
        else:
            # NCAAB
            home_roster = NCAAB_ROSTERS.get(home_team, DEFAULT_ROSTER)
            away_roster = NCAAB_ROSTERS.get(away_team, DEFAULT_ROSTER)
        
        players = []
        
        # Generate props for home team
        for i, name in enumerate(home_roster):
            if is_nfl:
                players.append(self._generate_nfl_player_props(name, i))
            elif is_nba:
                players.append(self._generate_nba_player_props(name, i, home_team))
            else:
                players.append(self._generate_ncaab_player_props(name, i))
        
        # Generate props for away team
        for i, name in enumerate(away_roster):
            if is_nfl:
                players.append(self._generate_nfl_player_props(name, i))
            elif is_nba:
                players.append(self._generate_nba_player_props(name, i, away_team))
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

    def _generate_nba_player_props(self, name: str, position_idx: int, team: str) -> dict[str, float]:
        """
        Generate realistic NBA player props based on position and team.
        
        NBA stats are higher than college - more minutes, faster pace.
        Position index 0-1 = guards, 2-3 = forwards, 4 = center
        """
        import random
        
        # Get team rating for adjustments (better teams = higher stats)
        team_rating = NBA_TEAM_RATINGS.get(team, 75)
        rating_multiplier = 0.9 + (team_rating / 100) * 0.2  # 0.9 to 1.1
        
        # Base stats vary by position
        if position_idx == 0:  # Point Guard (high assists, moderate points)
            pts = round(random.uniform(18.0, 28.0) * rating_multiplier * 2) / 2
            reb = round(random.uniform(3.0, 5.0) * 2) / 2
            ast = round(random.uniform(6.0, 10.0) * rating_multiplier * 2) / 2
            blk = round(random.uniform(0.5, 1.0) * 2) / 2
            threes = round(random.uniform(2.0, 4.0) * 2) / 2
        elif position_idx == 1:  # Shooting Guard (high points)
            pts = round(random.uniform(20.0, 30.0) * rating_multiplier * 2) / 2
            reb = round(random.uniform(3.5, 5.5) * 2) / 2
            ast = round(random.uniform(3.0, 6.0) * 2) / 2
            blk = round(random.uniform(0.5, 1.0) * 2) / 2
            threes = round(random.uniform(2.5, 4.5) * 2) / 2
        elif position_idx == 2:  # Small Forward (balanced)
            pts = round(random.uniform(16.0, 24.0) * rating_multiplier * 2) / 2
            reb = round(random.uniform(5.0, 7.0) * 2) / 2
            ast = round(random.uniform(2.5, 4.5) * 2) / 2
            blk = round(random.uniform(0.5, 1.5) * 2) / 2
            threes = round(random.uniform(1.5, 3.5) * 2) / 2
        elif position_idx == 3:  # Power Forward (rebounds, moderate points)
            pts = round(random.uniform(14.0, 22.0) * rating_multiplier * 2) / 2
            reb = round(random.uniform(7.0, 10.0) * 2) / 2
            ast = round(random.uniform(2.0, 4.0) * 2) / 2
            blk = round(random.uniform(1.0, 2.0) * 2) / 2
            threes = round(random.uniform(1.0, 2.5) * 2) / 2
        else:  # Center (rebounds, blocks)
            pts = round(random.uniform(12.0, 20.0) * rating_multiplier * 2) / 2
            reb = round(random.uniform(9.0, 13.0) * 2) / 2
            ast = round(random.uniform(1.5, 3.5) * 2) / 2
            blk = round(random.uniform(1.5, 3.0) * 2) / 2
            threes = round(random.uniform(0.5, 1.5) * 2) / 2
        
        # Combo stats
        pra = round((pts + reb + ast) * 2) / 2
        pr = round((pts + reb) * 2) / 2
        pa = round((pts + ast) * 2) / 2
        ra = round((reb + ast) * 2) / 2
        
        return {
            "name": name,
            "team": team,
            "pts": pts,
            "reb": reb,
            "ast": ast,
            "pra": pra,
            "pr": pr,
            "pa": pa,
            "ra": ra,
            "3pm": threes,
            "stl": round(random.uniform(0.5, 2.0) * 2) / 2,
            "blk": blk,
            "to": round(random.uniform(2.0, 4.0) * 2) / 2,
        }
