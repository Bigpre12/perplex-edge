"""
Sport availability and season detection utilities.

Helps determine which sports have active data based on current date
and API availability.
"""

from datetime import datetime, date
from typing import Optional
from zoneinfo import ZoneInfo

EASTERN_TZ = ZoneInfo("America/New_York")


# =============================================================================
# Season Windows by Sport
# =============================================================================

SEASON_WINDOWS = {
    "basketball_nba": {
        "regular_season": (10, 4),  # October to April
        "playoffs": (4, 6),         # April to June
        "offseason": (7, 9),        # July to September
    },
    "basketball_ncaab": {
        "regular_season": (11, 3),  # November to March
        "tournament": (3, 4),       # March Madness
        "offseason": (4, 10),       # April to October
    },
    "americanfootball_nfl": {
        "regular_season": (9, 1),   # September to January
        "playoffs": (1, 2),         # January to February (Super Bowl)
        "offseason": (2, 8),        # February to August
    },
    "americanfootball_ncaaf": {
        "regular_season": (8, 12),  # August to December
        "bowls": (12, 1),           # Bowl season
        "offseason": (2, 7),        # February to July
    },
    "baseball_mlb": {
        "spring_training": (2, 3),  # February to March
        "regular_season": (3, 9),   # March to September
        "playoffs": (10, 11),       # October to November
        "offseason": (11, 2),       # November to February
    },
    "icehockey_nhl": {
        "regular_season": (10, 4),  # October to April
        "playoffs": (4, 6),         # April to June
        "offseason": (7, 9),        # July to September
    },
    "tennis_atp": {
        # Tennis is year-round with different tournaments
        "australian_open": (1, 1),
        "clay_season": (4, 6),
        "grass_season": (6, 7),
        "us_open": (8, 9),
        "offseason": (11, 12),      # Brief offseason
    },
    "tennis_wta": {
        # Same as ATP
        "australian_open": (1, 1),
        "clay_season": (4, 6),
        "grass_season": (6, 7),
        "us_open": (8, 9),
        "offseason": (11, 12),
    },
}


# =============================================================================
# Tennis Tournament Mappings for The Odds API
# =============================================================================

# The Odds API uses tournament-specific sport keys for tennis
# Format: tennis_{tour}_{tournament}
TENNIS_TOURNAMENTS = {
    "tennis_atp": [
        "tennis_atp_australian_open",
        "tennis_atp_french_open",
        "tennis_atp_wimbledon",
        "tennis_atp_us_open",
        # Add more tournaments as needed
    ],
    "tennis_wta": [
        "tennis_wta_australian_open",
        "tennis_wta_french_open",
        "tennis_wta_wimbledon",
        "tennis_wta_us_open",
        # Add more tournaments as needed
    ],
}


def get_current_tennis_tournaments(month: Optional[int] = None) -> dict[str, list[str]]:
    """
    Get active tennis tournaments for the current or given month.
    
    Returns:
        Dict mapping generic key to list of active tournament keys
    """
    if month is None:
        month = datetime.now(EASTERN_TZ).month
    
    # Tournament windows (month ranges)
    tournament_windows = {
        "tennis_atp_australian_open": (1, 2),   # January
        "tennis_atp_french_open": (5, 6),       # May-June
        "tennis_atp_wimbledon": (6, 7),         # June-July
        "tennis_atp_us_open": (8, 9),           # Aug-Sept
        "tennis_wta_australian_open": (1, 2),
        "tennis_wta_french_open": (5, 6),
        "tennis_wta_wimbledon": (6, 7),
        "tennis_wta_us_open": (8, 9),
    }
    
    active = {"tennis_atp": [], "tennis_wta": []}
    
    for tournament, (start_month, end_month) in tournament_windows.items():
        if start_month <= month <= end_month:
            if "atp" in tournament:
                active["tennis_atp"].append(tournament)
            else:
                active["tennis_wta"].append(tournament)
    
    return active


def get_sport_status(sport_key: str, check_date: Optional[date] = None) -> dict:
    """
    Get the current status of a sport (in-season, off-season, playoffs, etc.)
    
    Args:
        sport_key: Sport identifier
        check_date: Date to check (defaults to today)
    
    Returns:
        Dict with:
        - is_active: bool - whether sport has live games expected
        - status: str - current phase (regular_season, playoffs, offseason, etc.)
        - message: str - human-readable status message
        - next_action: str - when games will resume (if offseason)
    """
    if check_date is None:
        check_date = datetime.now(EASTERN_TZ).date()
    
    month = check_date.month
    
    # Get sport-specific windows
    windows = SEASON_WINDOWS.get(sport_key, {})
    
    if not windows:
        # Unknown sport - assume active
        return {
            "is_active": True,
            "status": "unknown",
            "message": "Status unknown for this sport",
            "next_action": None,
        }
    
    # Check which window we're in
    for phase, (start_month, end_month) in windows.items():
        # Handle year wrap (e.g., NFL regular season Sept-Jan)
        if start_month > end_month:
            # Spans year boundary
            if month >= start_month or month <= end_month:
                is_active = phase != "offseason"
                return {
                    "is_active": is_active,
                    "status": phase,
                    "message": _get_phase_message(sport_key, phase),
                    "next_action": _get_next_action(sport_key, phase, month) if not is_active else None,
                }
        else:
            # Normal range within a year
            if start_month <= month <= end_month:
                is_active = phase != "offseason"
                return {
                    "is_active": is_active,
                    "status": phase,
                    "message": _get_phase_message(sport_key, phase),
                    "next_action": _get_next_action(sport_key, phase, month) if not is_active else None,
                }
    
    # Default to active if no match
    return {
        "is_active": True,
        "status": "active",
        "message": "Sport is active",
        "next_action": None,
    }


def _get_phase_message(sport_key: str, phase: str) -> str:
    """Get human-readable message for a sport phase."""
    sport_names = {
        "basketball_nba": "NBA",
        "basketball_ncaab": "College Basketball",
        "americanfootball_nfl": "NFL",
        "americanfootball_ncaaf": "College Football",
        "baseball_mlb": "MLB",
        "icehockey_nhl": "NHL",
        "tennis_atp": "ATP Tennis",
        "tennis_wta": "WTA Tennis",
    }
    
    sport_name = sport_names.get(sport_key, sport_key)
    
    messages = {
        "regular_season": f"{sport_name} regular season is active",
        "playoffs": f"{sport_name} playoffs are underway",
        "tournament": f"{sport_name} tournament is active",
        "spring_training": f"{sport_name} spring training is underway",
        "bowls": f"{sport_name} bowl season is active",
        "offseason": f"{sport_name} is in the off-season",
        "australian_open": f"{sport_name} Australian Open season",
        "clay_season": f"{sport_name} clay court season",
        "grass_season": f"{sport_name} grass court season",
        "us_open": f"{sport_name} US Open season",
    }
    
    return messages.get(phase, f"{sport_name} {phase}")


def _get_next_action(sport_key: str, phase: str, current_month: int) -> str:
    """Get message about when sport will resume."""
    resumption = {
        "basketball_nba": "NBA season resumes in October",
        "basketball_ncaab": "College basketball resumes in November",
        "americanfootball_nfl": "NFL preseason begins in August",
        "americanfootball_ncaaf": "College football resumes in August",
        "baseball_mlb": "MLB spring training begins in February",
        "icehockey_nhl": "NHL season resumes in October",
        "tennis_atp": "Check for upcoming tournaments",
        "tennis_wta": "Check for upcoming tournaments",
    }
    
    return resumption.get(sport_key, "Check back later for updates")


def is_sport_active(sport_key: str) -> bool:
    """Quick check if a sport is currently active."""
    return get_sport_status(sport_key)["is_active"]


def get_all_sport_statuses() -> dict[str, dict]:
    """Get status for all supported sports."""
    sports = [
        "basketball_nba",
        "basketball_ncaab", 
        "americanfootball_nfl",
        "americanfootball_ncaaf",
        "baseball_mlb",
        "icehockey_nhl",
        "tennis_atp",
        "tennis_wta",
    ]
    
    return {sport: get_sport_status(sport) for sport in sports}
