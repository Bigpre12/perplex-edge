"""
Dynamic season/year calculation helpers.

This module provides functions to dynamically determine the current sports season
based on the current date, avoiding hardcoded year values throughout the codebase.
"""

from datetime import datetime, date
from pathlib import Path
from typing import Tuple

from app.core.constants import SPORT_ID_TO_KEY


# =============================================================================
# NBA Season Helpers
# =============================================================================

def get_nba_season_years() -> Tuple[int, int]:
    """
    Get the current NBA season start and end years.
    
    NBA season typically runs October to June:
    - Oct-Dec: New season (e.g., in Oct 2025, season is 2025-26)
    - Jan-Sep: Previous season (e.g., in Jan 2026, season is still 2025-26)
    
    Returns:
        Tuple of (start_year, end_year) - e.g., (2025, 2026)
    """
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    
    if month >= 10:  # Oct-Dec: new season starts
        return (year, year + 1)
    else:  # Jan-Sep: still in season that started last year
        return (year - 1, year)


def get_nba_season_label() -> str:
    """
    Get the current NBA season label in format "YYYY-YY".
    
    Examples:
        - In October 2025: "2025-26"
        - In January 2026: "2025-26"
        - In October 2026: "2026-27"
    
    Returns:
        Season label string like "2025-26"
    """
    start_year, end_year = get_nba_season_years()
    return f"{start_year}-{end_year % 100:02d}"


def get_nba_season_start() -> datetime:
    """
    Get the approximate NBA season start date for the current season.
    
    NBA regular season typically starts around October 22-24.
    
    Returns:
        datetime of season start (naive UTC)
    """
    start_year, _ = get_nba_season_years()
    # NBA typically starts around October 22
    return datetime(start_year, 10, 22)


# =============================================================================
# NCAAB Season Helpers
# =============================================================================

def get_ncaab_season_years() -> Tuple[int, int]:
    """
    Get the current NCAAB season start and end years.
    
    NCAAB season typically runs November to April:
    - Nov-Dec: New season starts
    - Jan-Oct: Previous season for stats purposes
    
    Returns:
        Tuple of (start_year, end_year) - e.g., (2025, 2026)
    """
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    
    if month >= 11:  # Nov-Dec: new season starts
        return (year, year + 1)
    elif month <= 4:  # Jan-Apr: tournament/end of season
        return (year - 1, year)
    else:  # May-Oct: offseason, use upcoming season
        return (year, year + 1)


def get_ncaab_season_label() -> str:
    """
    Get the current NCAAB season label in format "YYYY-YY".
    
    Examples:
        - In November 2025: "2025-26"
        - In March 2026: "2025-26"
    
    Returns:
        Season label string like "2025-26"
    """
    start_year, end_year = get_ncaab_season_years()
    return f"{start_year}-{end_year % 100:02d}"


def get_ncaab_season_start() -> datetime:
    """
    Get the approximate NCAAB season start date for the current season.
    
    NCAAB regular season typically starts around November 4.
    
    Returns:
        datetime of season start (naive UTC)
    """
    start_year, _ = get_ncaab_season_years()
    # NCAAB typically starts around November 4
    return datetime(start_year, 11, 4)


# =============================================================================
# NFL Season Helpers
# =============================================================================

def get_nfl_season_year() -> int:
    """
    Get the current NFL season year.
    
    NFL season typically runs September to February:
    - Sep-Dec: Current year's season
    - Jan-Feb: Previous year's season (playoffs/Super Bowl)
    - Mar-Aug: Offseason, use upcoming season
    
    Returns:
        Single year integer (e.g., 2025 for the 2025 season)
    """
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    
    if month >= 9:  # Sep-Dec: current season
        return year
    elif month <= 2:  # Jan-Feb: playoffs from previous year's season
        return year - 1
    else:  # Mar-Aug: offseason, use upcoming
        return year


def get_nfl_season_start() -> datetime:
    """
    Get the approximate NFL season start date for the current season.
    
    NFL regular season typically starts first Thursday after Labor Day.
    
    Returns:
        datetime of approximate season start (naive UTC)
    """
    season_year = get_nfl_season_year()
    # NFL typically starts around September 7
    return datetime(season_year, 9, 7)


# =============================================================================
# NCAAF Season Helpers
# =============================================================================

def get_ncaaf_season_year() -> int:
    """
    Get the current NCAAF season year.
    
    NCAAF season typically runs late August to early January:
    - Aug-Dec: Current year's season (regular season + conference championships)
    - Jan: Bowl games and CFP from previous year's season
    - Feb-Jul: Offseason, use upcoming season
    
    Returns:
        Single year integer (e.g., 2025 for the 2025 season)
    """
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    
    if month >= 8:  # Aug-Dec: current season
        return year
    elif month == 1:  # January: bowl games from previous year's season
        return year - 1
    else:  # Feb-Jul: offseason, use upcoming
        return year


def get_ncaaf_season_label() -> str:
    """
    Get the current NCAAF season label.
    
    Examples:
        - In September 2025: "2025"
        - In January 2026: "2025" (bowl games)
        - In February 2026: "2026" (upcoming season)
    
    Returns:
        Year as string (e.g., "2025")
    """
    return str(get_ncaaf_season_year())


def get_ncaaf_season_start() -> datetime:
    """
    Get the approximate NCAAF season start date for the current season.
    
    NCAAF typically starts last weekend of August (Week 0/1).
    
    Returns:
        datetime of approximate season start (naive UTC)
    """
    season_year = get_ncaaf_season_year()
    # NCAAF typically starts around August 24 (Week 0)
    return datetime(season_year, 8, 24)


# =============================================================================
# MLB Season Helpers
# =============================================================================

def get_mlb_season_year() -> int:
    """
    Get the current MLB season year.
    
    MLB season typically runs late March/early April to October/November:
    - Apr-Oct: Current year's season (regular season + playoffs)
    - Nov-Mar: Offseason, use upcoming season
    
    Returns:
        Single year integer (e.g., 2026 for the 2026 season)
    """
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    
    if month >= 4 and month <= 10:  # Apr-Oct: current season
        return year
    elif month >= 11:  # Nov-Dec: offseason, use next year
        return year + 1
    else:  # Jan-Mar: offseason, use current year (upcoming season)
        return year


def get_mlb_season_label() -> str:
    """
    Get the current MLB season label.
    
    Examples:
        - In April 2026: "2026"
        - In January 2026: "2026"
        - In November 2026: "2027"
    
    Returns:
        Year as string (e.g., "2026")
    """
    return str(get_mlb_season_year())


def get_mlb_season_start() -> datetime:
    """
    Get the approximate MLB season start date for the current season.
    
    MLB Opening Day is typically late March or early April.
    
    Returns:
        datetime of approximate season start (naive UTC)
    """
    season_year = get_mlb_season_year()
    # MLB typically starts around March 28 (Opening Day)
    return datetime(season_year, 3, 28)


# =============================================================================
# Tennis Season Helpers
# =============================================================================

def get_tennis_season_year() -> int:
    """
    Get the current tennis season year.
    
    Tennis runs year-round on calendar year (January - December).
    
    Returns:
        Current calendar year
    """
    return datetime.utcnow().year


def get_tennis_season_label() -> str:
    """
    Get the current tennis season label.
    
    Returns:
        Year as string (e.g., "2026")
    """
    return str(get_tennis_season_year())


def get_tennis_season_start() -> datetime:
    """
    Get the tennis season start date for the current season.
    
    Tennis runs year-round, so season starts January 1.
    
    Returns:
        datetime of January 1 of current year (naive UTC)
    """
    season_year = get_tennis_season_year()
    return datetime(season_year, 1, 1)


# =============================================================================
# NHL Season Helpers
# =============================================================================

def get_nhl_season_years() -> Tuple[int, int]:
    """
    Get the current NHL season start and end years.
    
    NHL season typically runs October to June:
    - Oct-Dec: New season (e.g., in Oct 2025, season is 2025-26)
    - Jan-Jun: Previous season (e.g., in Jan 2026, season is still 2025-26)
    - Jul-Sep: Offseason, use upcoming season
    
    Returns:
        Tuple of (start_year, end_year) - e.g., (2025, 2026)
    """
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    
    if month >= 10:  # Oct-Dec: new season starts
        return (year, year + 1)
    elif month <= 6:  # Jan-Jun: still in season that started last year
        return (year - 1, year)
    else:  # Jul-Sep: offseason, use upcoming season
        return (year, year + 1)


def get_nhl_season_label() -> str:
    """
    Get the current NHL season label in format "YYYY-YY".
    
    Examples:
        - In October 2025: "2025-26"
        - In January 2026: "2025-26"
        - In October 2026: "2026-27"
    
    Returns:
        Season label string like "2025-26"
    """
    start_year, end_year = get_nhl_season_years()
    return f"{start_year}-{end_year % 100:02d}"


def get_nhl_season_start() -> datetime:
    """
    Get the approximate NHL season start date for the current season.
    
    NHL regular season typically starts around October 7-10.
    
    Returns:
        datetime of season start (naive UTC)
    """
    start_year, _ = get_nhl_season_years()
    # NHL typically starts around October 7
    return datetime(start_year, 10, 7)


# =============================================================================
# UFC/MMA Season Helpers
# =============================================================================

def get_ufc_season_year() -> int:
    """
    Get the current UFC season year.
    
    UFC runs on calendar year with events throughout the year.
    
    Returns:
        Current calendar year
    """
    return datetime.utcnow().year


def get_ufc_season_label() -> str:
    """
    Get the current UFC season label.
    
    Returns:
        Year as string (e.g., "2026")
    """
    return str(get_ufc_season_year())


def get_ufc_season_start() -> datetime:
    """
    Get the UFC season start date for the current season.
    
    UFC runs year-round, so season starts January 1.
    
    Returns:
        datetime of January 1 of current year (naive UTC)
    """
    season_year = get_ufc_season_year()
    return datetime(season_year, 1, 1)


# =============================================================================
# Soccer/EPL Season Helpers
# =============================================================================

def get_epl_season_years() -> Tuple[int, int]:
    """
    Get the current EPL season start and end years.
    
    EPL season typically runs August to May:
    - Aug-Dec: New season (e.g., in Aug 2025, season is 2025-26)
    - Jan-May: Previous season (e.g., in Jan 2026, season is still 2025-26)
    - Jun-Jul: Offseason, use upcoming season
    
    Returns:
        Tuple of (start_year, end_year) - e.g., (2025, 2026)
    """
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    
    if month >= 8:  # Aug-Dec: new season starts
        return (year, year + 1)
    elif month <= 5:  # Jan-May: still in season that started last year
        return (year - 1, year)
    else:  # Jun-Jul: offseason, use upcoming season
        return (year, year + 1)


def get_epl_season_label() -> str:
    """
    Get the current EPL season label in format "YYYY-YY".
    
    Examples:
        - In August 2025: "2025-26"
        - In January 2026: "2025-26"
        - In August 2026: "2026-27"
    
    Returns:
        Season label string like "2025-26"
    """
    start_year, end_year = get_epl_season_years()
    return f"{start_year}-{end_year % 100:02d}"


def get_epl_season_start() -> datetime:
    """
    Get the approximate EPL season start date for the current season.
    
    EPL season typically starts around mid-August.
    
    Returns:
        datetime of season start (naive UTC)
    """
    start_year, _ = get_epl_season_years()
    # EPL typically starts around August 15
    return datetime(start_year, 8, 15)


# =============================================================================
# Golf/PGA Season Helpers
# =============================================================================

def get_pga_season_year() -> int:
    """
    Get the current PGA Tour season year.
    
    PGA Tour FedEx Cup season runs calendar year (Jan-Aug) with fall events
    continuing through November for next season points.
    
    Returns:
        Current calendar year
    """
    return datetime.utcnow().year


def get_pga_season_label() -> str:
    """
    Get the current PGA Tour season label.
    
    Examples:
        - In January 2026: "2026"
        - In August 2026: "2026"
        - In November 2026: "2026" (fall events count toward 2027 season)
    
    Returns:
        Season label string like "2026"
    """
    return str(get_pga_season_year())


def get_pga_season_start() -> datetime:
    """
    Get the PGA Tour season start date for the current season.
    
    PGA Tour season typically starts in early January (Sony Open in Hawaii).
    
    Returns:
        datetime of season start (naive UTC)
    """
    season_year = get_pga_season_year()
    # PGA Tour typically starts around January 12 (Sony Open)
    return datetime(season_year, 1, 12)


# =============================================================================
# WNBA Season Helpers
# =============================================================================

def get_wnba_season_year() -> int:
    """
    Get the current WNBA season year.
    
    WNBA season runs May to October within a single calendar year.
    
    Returns:
        Current calendar year for the season
    """
    today = datetime.utcnow().date()
    return today.year


def get_wnba_season_label() -> str:
    """
    Get the current WNBA season label.
    
    Returns:
        Season label string like "2026"
    """
    return str(get_wnba_season_year())


def get_wnba_season_start() -> datetime:
    """
    Get the WNBA season start date for the current season.
    
    WNBA season typically starts in mid-May.
    
    Returns:
        datetime of season start (naive UTC)
    """
    season_year = get_wnba_season_year()
    return datetime(season_year, 5, 15)


# =============================================================================
# MLS Season Helpers
# =============================================================================

def get_mls_season_year() -> int:
    """
    Get the current MLS season year.
    
    MLS season runs February to December within a single calendar year.
    
    Returns:
        Current calendar year for the season
    """
    today = datetime.utcnow().date()
    return today.year


def get_mls_season_label() -> str:
    """
    Get the current MLS season label.
    
    Returns:
        Season label string like "2026"
    """
    return str(get_mls_season_year())


def get_mls_season_start() -> datetime:
    """
    Get the MLS season start date for the current season.
    
    MLS season typically starts in late February.
    
    Returns:
        datetime of season start (naive UTC)
    """
    season_year = get_mls_season_year()
    return datetime(season_year, 2, 21)


# =============================================================================
# UEFA Competitions Season Helpers
# =============================================================================

def get_ucl_season_years() -> Tuple[int, int]:
    """
    Get the current UEFA Champions League season start and end years.
    
    UCL season runs July (qualifying) to May across two calendar years:
    - Jul-Dec: First half of season (e.g., in Sep 2025, season is 2025-26)
    - Jan-May: Second half of season (e.g., in Feb 2026, season is still 2025-26)
    - Jun: Brief offseason before qualifying
    
    Returns:
        Tuple of (start_year, end_year) - e.g., (2025, 2026)
    """
    today = datetime.utcnow().date()
    year = today.year
    month = today.month
    
    if month >= 7:  # Jul-Dec: new season
        return (year, year + 1)
    else:  # Jan-Jun: still in season that started last year
        return (year - 1, year)


def get_ucl_season_label() -> str:
    """
    Get the current UEFA Champions League season label in format "YYYY-YY".
    
    Examples:
        - In September 2025: "2025-26"
        - In February 2026: "2025-26"
    
    Returns:
        Season label string like "2025-26"
    """
    start_year, end_year = get_ucl_season_years()
    return f"{start_year}-{end_year % 100:02d}"


def get_ucl_season_start() -> datetime:
    """
    Get the UCL season start date (league phase start in September).
    
    Returns:
        datetime of season start (naive UTC)
    """
    start_year, _ = get_ucl_season_years()
    # UCL league phase typically starts mid-September
    return datetime(start_year, 9, 15)


def get_uel_season_years() -> Tuple[int, int]:
    """
    Get the current UEFA Europa League season start and end years.
    
    UEL follows same calendar as UCL: July to May.
    
    Returns:
        Tuple of (start_year, end_year) - e.g., (2025, 2026)
    """
    return get_ucl_season_years()


def get_uel_season_label() -> str:
    """
    Get the current UEFA Europa League season label.
    
    Returns:
        Season label string like "2025-26"
    """
    start_year, end_year = get_uel_season_years()
    return f"{start_year}-{end_year % 100:02d}"


def get_uel_season_start() -> datetime:
    """
    Get the UEL season start date (league phase start in September).
    
    Returns:
        datetime of season start (naive UTC)
    """
    start_year, _ = get_uel_season_years()
    return datetime(start_year, 9, 15)


def get_uecl_season_years() -> Tuple[int, int]:
    """
    Get the current UEFA Conference League season start and end years.
    
    UECL follows same calendar as UCL/UEL: July to May.
    
    Returns:
        Tuple of (start_year, end_year) - e.g., (2025, 2026)
    """
    return get_ucl_season_years()


def get_uecl_season_label() -> str:
    """
    Get the current UEFA Conference League season label.
    
    Returns:
        Season label string like "2025-26"
    """
    start_year, end_year = get_uecl_season_years()
    return f"{start_year}-{end_year % 100:02d}"


def get_uecl_season_start() -> datetime:
    """
    Get the UECL season start date (league phase start in September).
    
    Returns:
        datetime of season start (naive UTC)
    """
    start_year, _ = get_uecl_season_years()
    return datetime(start_year, 9, 15)


# =============================================================================
# Schedule File Helpers
# =============================================================================

def get_schedule_filename(sport_key: str) -> str:
    """
    Get the dynamic schedule filename for a sport based on current season.
    
    Args:
        sport_key: Sport identifier (e.g., "basketball_nba", "basketball_ncaab")
    
    Returns:
        Filename string like "nba_2025_26.json"
    """
    if sport_key == "basketball_nba":
        start_year, end_year = get_nba_season_years()
        return f"nba_{start_year}_{end_year % 100:02d}.json"
    elif sport_key == "basketball_ncaab":
        start_year, end_year = get_ncaab_season_years()
        return f"ncaab_{start_year}_{end_year % 100:02d}.json"
    elif sport_key == "americanfootball_nfl":
        season_year = get_nfl_season_year()
        return f"nfl_{season_year}.json"
    elif sport_key == "baseball_mlb":
        season_year = get_mlb_season_year()
        return f"mlb_{season_year}.json"
    elif sport_key == "americanfootball_ncaaf":
        season_year = get_ncaaf_season_year()
        return f"ncaaf_{season_year}.json"
    elif sport_key == "tennis_atp":
        season_year = get_tennis_season_year()
        return f"tennis_atp_{season_year}.json"
    elif sport_key == "tennis_wta":
        season_year = get_tennis_season_year()
        return f"tennis_wta_{season_year}.json"
    elif sport_key == "icehockey_nhl":
        start_year, end_year = get_nhl_season_years()
        return f"nhl_{start_year}_{end_year % 100:02d}.json"
    elif sport_key == "mma_mixed_martial_arts":
        season_year = get_ufc_season_year()
        return f"ufc_{season_year}.json"
    elif sport_key == "soccer_epl":
        start_year, end_year = get_epl_season_years()
        return f"epl_{start_year}_{end_year % 100:02d}.json"
    elif sport_key == "golf_pga_tour":
        season_year = get_pga_season_year()
        return f"pga_{season_year}.json"
    elif sport_key == "soccer_uefa_champs_league":
        start_year, end_year = get_ucl_season_years()
        return f"ucl_{start_year}_{end_year % 100:02d}.json"
    elif sport_key == "soccer_uefa_europa":
        start_year, end_year = get_uel_season_years()
        return f"uel_{start_year}_{end_year % 100:02d}.json"
    elif sport_key == "soccer_uefa_conference":
        start_year, end_year = get_uecl_season_years()
        return f"uecl_{start_year}_{end_year % 100:02d}.json"
    elif sport_key == "basketball_wnba":
        season_year = get_wnba_season_year()
        return f"wnba_{season_year}.json"
    elif sport_key == "soccer_usa_mls":
        season_year = get_mls_season_year()
        return f"mls_{season_year}.json"
    else:
        # Default to NBA format for unknown sports
        start_year, end_year = get_nba_season_years()
        return f"{sport_key}_{start_year}_{end_year % 100:02d}.json"


def get_schedule_filepath(sport_key: str, schedules_dir: Path) -> Path:
    """
    Get the full path to the schedule file for a sport.
    
    Args:
        sport_key: Sport identifier
        schedules_dir: Base directory for schedule files
    
    Returns:
        Path to the schedule file
    """
    filename = get_schedule_filename(sport_key)
    return schedules_dir / filename


# =============================================================================
# Generic Season Start Helper
# =============================================================================

def get_current_season_start(sport_key: str = "basketball_nba") -> datetime:
    """
    Get the season start date for any sport.
    
    Args:
        sport_key: Sport identifier
    
    Returns:
        datetime of season start (naive UTC)
    """
    if sport_key == "basketball_nba":
        return get_nba_season_start()
    elif sport_key == "basketball_ncaab":
        return get_ncaab_season_start()
    elif sport_key == "americanfootball_nfl":
        return get_nfl_season_start()
    elif sport_key == "baseball_mlb":
        return get_mlb_season_start()
    elif sport_key == "americanfootball_ncaaf":
        return get_ncaaf_season_start()
    elif sport_key in ("tennis_atp", "tennis_wta"):
        return get_tennis_season_start()
    elif sport_key == "icehockey_nhl":
        return get_nhl_season_start()
    elif sport_key == "mma_mixed_martial_arts":
        return get_ufc_season_start()
    elif sport_key == "soccer_epl":
        return get_epl_season_start()
    elif sport_key == "golf_pga_tour":
        return get_pga_season_start()
    elif sport_key == "soccer_uefa_champs_league":
        return get_ucl_season_start()
    elif sport_key == "soccer_uefa_europa":
        return get_uel_season_start()
    elif sport_key == "soccer_uefa_conference":
        return get_uecl_season_start()
    elif sport_key == "basketball_wnba":
        return get_wnba_season_start()
    elif sport_key == "soccer_usa_mls":
        return get_mls_season_start()
    else:
        # Default to NBA for unknown
        return get_nba_season_start()


def get_current_season_label(sport_key: str = "basketball_nba") -> str:
    """
    Get the season label for any sport.
    
    Args:
        sport_key: Sport identifier
    
    Returns:
        Season label string
    """
    if sport_key == "basketball_nba":
        return get_nba_season_label()
    elif sport_key == "basketball_ncaab":
        return get_ncaab_season_label()
    elif sport_key == "americanfootball_nfl":
        return str(get_nfl_season_year())
    elif sport_key == "baseball_mlb":
        return get_mlb_season_label()
    elif sport_key == "americanfootball_ncaaf":
        return get_ncaaf_season_label()
    elif sport_key in ("tennis_atp", "tennis_wta"):
        return get_tennis_season_label()
    elif sport_key == "icehockey_nhl":
        return get_nhl_season_label()
    elif sport_key == "mma_mixed_martial_arts":
        return get_ufc_season_label()
    elif sport_key == "soccer_epl":
        return get_epl_season_label()
    elif sport_key == "golf_pga_tour":
        return get_pga_season_label()
    elif sport_key == "soccer_uefa_champs_league":
        return get_ucl_season_label()
    elif sport_key == "soccer_uefa_europa":
        return get_uel_season_label()
    elif sport_key == "soccer_uefa_conference":
        return get_uecl_season_label()
    elif sport_key == "basketball_wnba":
        return get_wnba_season_label()
    elif sport_key == "soccer_usa_mls":
        return get_mls_season_label()
    else:
        return get_nba_season_label()


# =============================================================================
# Sport ID to Season Mapping (for database sport_id values)
# =============================================================================

# SPORT_ID_TO_KEY is imported from app.core.constants


def get_sport_key_from_id(sport_id: int) -> str:
    """
    Convert database sport_id to sport_key string.
    
    Args:
        sport_id: Database sport ID (30=NBA, 31=NFL, 32=NCAAB, 40=MLB, 41=NCAAF)
    
    Returns:
        Sport key string like "basketball_nba"
    """
    return SPORT_ID_TO_KEY.get(sport_id, "basketball_nba")


def get_season_start_for_sport_id(sport_id: int) -> datetime:
    """
    Get the season start date for a sport based on its database ID.
    
    This is the main function to use when you have a sport_id from the database
    and need the correct season start date for that sport.
    
    Args:
        sport_id: Database sport ID (30=NBA, 31=NFL, 32=NCAAB, 40=MLB, 41=NCAAF)
    
    Returns:
        datetime of season start (naive UTC)
        
    Examples:
        >>> get_season_start_for_sport_id(30)  # NBA
        datetime(2025, 10, 22, 0, 0)
        >>> get_season_start_for_sport_id(32)  # NCAAB
        datetime(2025, 11, 4, 0, 0)
        >>> get_season_start_for_sport_id(31)  # NFL
        datetime(2025, 9, 7, 0, 0)
        >>> get_season_start_for_sport_id(40)  # MLB
        datetime(2026, 3, 28, 0, 0)
        >>> get_season_start_for_sport_id(41)  # NCAAF
        datetime(2026, 8, 24, 0, 0)
    """
    sport_key = get_sport_key_from_id(sport_id)
    return get_current_season_start(sport_key)


def get_season_label_for_sport_id(sport_id: int) -> str:
    """
    Get the season label for a sport based on its database ID.
    
    Args:
        sport_id: Database sport ID (30=NBA, 31=NFL, 32=NCAAB, 40=MLB, 41=NCAAF)
    
    Returns:
        Season label string (e.g., "2025-26" for NBA/NCAAB, "2025" for NFL/NCAAF, "2026" for MLB)
    """
    sport_key = get_sport_key_from_id(sport_id)
    return get_current_season_label(sport_key)
