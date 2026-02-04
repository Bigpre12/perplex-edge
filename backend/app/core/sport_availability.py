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
        # Note: Olympic break Feb 6-22, 2026 (Milano Cortina) - NHL pauses
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
    "basketball_wnba": {
        "regular_season": (5, 9),   # May to September
        "playoffs": (9, 10),        # September to October
        "offseason": (11, 4),       # November to April
    },
    "golf_pga_tour": {
        # Golf is year-round with majors spread throughout
        "season_start": (1, 1),     # Sentry Tournament of Champions
        "masters": (4, 4),          # Masters in April
        "pga_championship": (5, 5), # PGA Championship in May
        "us_open": (6, 6),          # US Open in June
        "open_championship": (7, 7), # The Open in July
        "fedex_cup": (8, 9),        # FedEx Cup playoffs Aug-Sept
        "offseason": (12, 12),      # Brief offseason
    },
    "soccer_epl": {
        "regular_season": (8, 5),   # August to May
        "offseason": (6, 7),        # June to July
    },
    "soccer_uefa_champs_league": {
        "league_phase": (9, 1),     # September to January (new format)
        "knockout": (2, 5),         # February to May
        "offseason": (6, 8),        # Summer break (World Cup 2026 in June-July)
    },
    "soccer_uefa_europa": {
        "league_phase": (9, 1),     # September to January
        "knockout": (2, 5),         # February to May
        "offseason": (6, 8),        # Summer break
    },
    "soccer_uefa_conference": {
        "league_phase": (9, 1),     # September to January
        "knockout": (2, 5),         # February to May
        "offseason": (6, 8),        # Summer break
    },
    "soccer_usa_mls": {
        "regular_season": (2, 10),  # February to October
        "playoffs": (10, 12),       # October to December
        "offseason": (12, 2),       # Brief winter break
    },
    "mma_mixed_martial_arts": {
        # UFC has events year-round, no true offseason
        "active": (1, 12),          # Year-round events
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
        "tennis_atp_indian_wells",
        "tennis_atp_miami",
        "tennis_atp_monte_carlo",
        "tennis_atp_madrid",
        "tennis_atp_rome",
        "tennis_atp_canadian_open",
        "tennis_atp_cincinnati",
        "tennis_atp_shanghai",
        "tennis_atp_paris",
        "tennis_atp_finals",
    ],
    "tennis_wta": [
        # Grand Slams
        "tennis_wta_australian_open",
        "tennis_wta_french_open",
        "tennis_wta_wimbledon",
        "tennis_wta_us_open",
        # WTA 1000
        "tennis_wta_doha",
        "tennis_wta_dubai",
        "tennis_wta_indian_wells",
        "tennis_wta_miami",
        "tennis_wta_madrid",
        "tennis_wta_rome",
        "tennis_wta_canadian_open",
        "tennis_wta_cincinnati",
        "tennis_wta_guadalajara",
        "tennis_wta_beijing",
        "tennis_wta_wuhan",
        # WTA 500
        "tennis_wta_brisbane",
        "tennis_wta_adelaide",
        "tennis_wta_abu_dhabi",
        "tennis_wta_charleston",
        "tennis_wta_stuttgart",
        "tennis_wta_linz",
        "tennis_wta_berlin",
        "tennis_wta_eastbourne",
        "tennis_wta_washington",
        "tennis_wta_san_diego",
        "tennis_wta_tokyo",
        "tennis_wta_ningbo",
        "tennis_wta_zhuhai",
        # WTA 250
        "tennis_wta_auckland",
        "tennis_wta_hobart",
        "tennis_wta_cluj",
        "tennis_wta_merida",
        "tennis_wta_austin",
        "tennis_wta_strasbourg",
        "tennis_wta_rabat",
        "tennis_wta_s_hertogenbosch",
        "tennis_wta_nottingham",
        "tennis_wta_birmingham",
        "tennis_wta_bad_homburg",
        "tennis_wta_hamburg",
        "tennis_wta_prague",
        "tennis_wta_iasi",
        "tennis_wta_warsaw",
        "tennis_wta_cleveland",
        "tennis_wta_seoul",
        "tennis_wta_guangzhou",
        "tennis_wta_hong_kong",
        "tennis_wta_jiangxi",
        # WTA Finals
        "tennis_wta_finals",
    ],
}


def get_current_tennis_tournaments(month: Optional[int] = None) -> dict[str, list[str]]:
    """
    Get active tennis tournaments for the current or given month.
    
    Tennis has year-round events. This returns tournament-specific API keys
    that The Odds API uses for tennis.
    
    Returns:
        Dict mapping generic key to list of active tournament keys
    """
    if month is None:
        month = datetime.now(EASTERN_TZ).month
    
    # Tournament windows (month ranges) - expanded to cover more of the year
    # Grand Slams plus major ATP/WTA tour events
    tournament_windows = {
        # =================================================================
        # ATP Grand Slams and Masters
        # =================================================================
        "tennis_atp_australian_open": (1, 2),    # Mid-Jan to late Jan
        "tennis_atp_indian_wells": (3, 3),       # March (Indian Wells/BNP Paribas)
        "tennis_atp_miami": (3, 4),              # Late March to early April
        "tennis_atp_monte_carlo": (4, 4),        # April (Monte Carlo Masters)
        "tennis_atp_madrid": (4, 5),             # Late April to early May
        "tennis_atp_rome": (5, 5),               # May (Italian Open)
        "tennis_atp_french_open": (5, 6),        # Late May to early June
        "tennis_atp_wimbledon": (6, 7),          # Late June to mid-July
        "tennis_atp_canadian_open": (8, 8),      # August
        "tennis_atp_cincinnati": (8, 8),         # August
        "tennis_atp_us_open": (8, 9),            # Late Aug to early Sept
        "tennis_atp_shanghai": (10, 10),         # October (Shanghai Masters)
        "tennis_atp_paris": (10, 11),            # Late Oct to early Nov (Paris Masters)
        "tennis_atp_finals": (11, 11),           # November (ATP Finals)
        
        # =================================================================
        # WTA Grand Slams
        # =================================================================
        "tennis_wta_australian_open": (1, 2),
        "tennis_wta_french_open": (5, 6),
        "tennis_wta_wimbledon": (6, 7),
        "tennis_wta_us_open": (8, 9),
        
        # =================================================================
        # WTA 1000 Events
        # =================================================================
        "tennis_wta_doha": (2, 2),               # February (Qatar Open)
        "tennis_wta_dubai": (2, 2),              # February
        "tennis_wta_indian_wells": (3, 3),       # March
        "tennis_wta_miami": (3, 4),              # Late March to early April
        "tennis_wta_madrid": (4, 5),             # Late April to early May
        "tennis_wta_rome": (5, 5),               # May
        "tennis_wta_canadian_open": (8, 8),      # August
        "tennis_wta_cincinnati": (8, 8),         # August
        "tennis_wta_guadalajara": (9, 9),        # September
        "tennis_wta_beijing": (9, 10),           # Late Sept to early Oct
        "tennis_wta_wuhan": (10, 10),            # October
        
        # =================================================================
        # WTA 500 Events
        # =================================================================
        "tennis_wta_brisbane": (1, 1),           # January
        "tennis_wta_adelaide": (1, 1),           # January
        "tennis_wta_abu_dhabi": (2, 2),          # February
        "tennis_wta_charleston": (4, 4),         # April (clay)
        "tennis_wta_stuttgart": (4, 4),          # April (clay)
        "tennis_wta_linz": (4, 4),               # April (clay)
        "tennis_wta_berlin": (6, 6),             # June (grass)
        "tennis_wta_eastbourne": (6, 6),         # June (grass)
        "tennis_wta_washington": (7, 8),         # Late July to early Aug
        "tennis_wta_san_diego": (8, 8),          # August
        "tennis_wta_tokyo": (9, 9),              # September
        "tennis_wta_ningbo": (10, 10),           # October
        "tennis_wta_zhuhai": (10, 10),           # October
        
        # =================================================================
        # WTA 250 Events (by month)
        # =================================================================
        "tennis_wta_auckland": (1, 1),           # January
        "tennis_wta_hobart": (1, 1),             # January
        "tennis_wta_cluj": (2, 2),               # February
        "tennis_wta_merida": (2, 3),             # Late Feb to early Mar
        "tennis_wta_austin": (2, 3),             # Late Feb to early Mar
        "tennis_wta_strasbourg": (5, 5),         # May (clay)
        "tennis_wta_rabat": (5, 5),              # May (clay)
        "tennis_wta_s_hertogenbosch": (6, 6),    # June (grass)
        "tennis_wta_nottingham": (6, 6),         # June (grass)
        "tennis_wta_birmingham": (6, 6),         # June (grass)
        "tennis_wta_bad_homburg": (6, 6),        # June (grass)
        "tennis_wta_hamburg": (7, 7),            # July (clay)
        "tennis_wta_prague": (7, 7),             # July (clay)
        "tennis_wta_iasi": (7, 7),               # July (clay)
        "tennis_wta_warsaw": (7, 7),             # July (clay)
        "tennis_wta_cleveland": (8, 8),          # August
        "tennis_wta_seoul": (9, 9),              # September
        "tennis_wta_guangzhou": (10, 10),        # October
        "tennis_wta_hong_kong": (10, 11),        # Late Oct to early Nov
        "tennis_wta_jiangxi": (10, 11),          # Late Oct to early Nov
        
        # WTA Finals
        "tennis_wta_finals": (11, 11),           # November (Riyadh)
    }
    
    active = {"tennis_atp": [], "tennis_wta": []}
    
    for tournament, (start_month, end_month) in tournament_windows.items():
        if start_month <= month <= end_month:
            if "atp" in tournament:
                active["tennis_atp"].append(tournament)
            else:
                active["tennis_wta"].append(tournament)
    
    # If no specific tournaments active, try generic keys as fallback
    # (The Odds API might aggregate active events under generic key)
    if not active["tennis_atp"]:
        active["tennis_atp"] = ["tennis_atp"]
    if not active["tennis_wta"]:
        active["tennis_wta"] = ["tennis_wta"]
    
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
        "basketball_wnba": "WNBA",
        "americanfootball_nfl": "NFL",
        "americanfootball_ncaaf": "College Football",
        "baseball_mlb": "MLB",
        "icehockey_nhl": "NHL",
        "tennis_atp": "ATP Tennis",
        "tennis_wta": "WTA Tennis",
        "golf_pga_tour": "PGA Tour",
        "soccer_epl": "English Premier League",
        "soccer_uefa_champs_league": "UEFA Champions League",
        "soccer_uefa_europa": "UEFA Europa League",
        "soccer_uefa_conference": "UEFA Conference League",
        "soccer_usa_mls": "MLS",
        "mma_mixed_martial_arts": "UFC",
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
        "masters": f"{sport_name} Masters week",
        "pga_championship": f"{sport_name} PGA Championship",
        "open_championship": f"{sport_name} The Open Championship",
        "fedex_cup": f"{sport_name} FedEx Cup playoffs",
        "group_stage": f"{sport_name} group stage",
        "knockout": f"{sport_name} knockout rounds",
        "active": f"{sport_name} events ongoing",
    }
    
    return messages.get(phase, f"{sport_name} {phase}")


def _get_next_action(sport_key: str, phase: str, current_month: int) -> str:
    """Get message about when sport will resume."""
    resumption = {
        "basketball_nba": "NBA season resumes in October",
        "basketball_ncaab": "College basketball resumes in November",
        "basketball_wnba": "WNBA season begins in May",
        "americanfootball_nfl": "NFL preseason begins in August",
        "americanfootball_ncaaf": "College football resumes in August",
        "baseball_mlb": "MLB spring training begins in February",
        "icehockey_nhl": "NHL season resumes in October",
        "tennis_atp": "Check for upcoming tournaments",
        "tennis_wta": "Check for upcoming tournaments",
        "golf_pga_tour": "PGA Tour events resume in January",
        "soccer_epl": "EPL season begins in August",
        "soccer_uefa_champs_league": "UCL league phase begins in September",
        "soccer_uefa_europa": "UEL league phase begins in September",
        "soccer_uefa_conference": "UECL league phase begins in September",
        "soccer_usa_mls": "MLS season begins in February",
        "mma_mixed_martial_arts": "UFC events happen year-round",
    }
    
    return resumption.get(sport_key, "Check back later for updates")


def is_sport_active(sport_key: str) -> bool:
    """Quick check if a sport is currently active."""
    return get_sport_status(sport_key)["is_active"]


def get_all_sport_statuses() -> dict[str, dict]:
    """Get status for all supported sports."""
    sports = [
        # Basketball
        "basketball_nba",
        "basketball_ncaab",
        "basketball_wnba",
        # Football
        "americanfootball_nfl",
        "americanfootball_ncaaf",
        # Baseball
        "baseball_mlb",
        # Hockey
        "icehockey_nhl",
        # Tennis
        "tennis_atp",
        "tennis_wta",
        # Golf
        "golf_pga_tour",
        # Soccer
        "soccer_epl",
        "soccer_uefa_champs_league",
        "soccer_uefa_europa",
        "soccer_uefa_conference",
        "soccer_usa_mls",
        # MMA
        "mma_mixed_martial_arts",
    ]
    
    return {sport: get_sport_status(sport) for sport in sports}
