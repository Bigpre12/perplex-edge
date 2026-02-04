"""
Centralized constants for sport mappings and configurations.

This module provides the single source of truth for sport-related mappings
used throughout the application.

Note: For type-safe enums and stat type validation, use app.config.sports:
    - SportKey enum for sport keys
    - StatType enum for stat types
    - STAT_TYPES_BY_SPORT for sport-specific stat type validation
    - is_valid_stat_for_sport() for validation checks
"""

# Re-export enums and functions from app.config.sports for convenience
from app.config.sports import (
    SportKey,
    StatType,
    STAT_TYPES_BY_SPORT,
    API_MARKET_TO_STAT_TYPE,
    get_stat_types_for_sport,
    is_valid_stat_for_sport,
    get_stat_type_from_api_market,
)

# =============================================================================
# Sport Key Mappings
# =============================================================================

# Map sport key (The Odds API format) to display league code
SPORT_KEY_TO_LEAGUE = {
    # Basketball
    "basketball_nba": "NBA",
    "basketball_ncaab": "NCAAB",
    "basketball_wnba": "WNBA",
    # Football
    "americanfootball_nfl": "NFL",
    "americanfootball_ncaaf": "NCAAF",
    # Baseball
    "baseball_mlb": "MLB",
    # Hockey
    "icehockey_nhl": "NHL",
    # Tennis
    "tennis_atp": "ATP",
    "tennis_wta": "WTA",
    # Golf
    "golf_pga_tour": "PGA",
    # Soccer
    "soccer_epl": "EPL",
    "soccer_uefa_champs_league": "UCL",
    "soccer_uefa_europa": "UEL",
    "soccer_uefa_conference": "UECL",
    "soccer_usa_mls": "MLS",
    # MMA
    "mma_mixed_martial_arts": "UFC",
}

# Map sport key to full name and league code tuple
SPORT_KEY_TO_NAME = {
    # Basketball
    "basketball_nba": ("NBA", "NBA"),
    "basketball_ncaab": ("NCAA Basketball", "NCAAB"),
    "basketball_wnba": ("WNBA", "WNBA"),
    # Football
    "americanfootball_nfl": ("NFL", "NFL"),
    "americanfootball_ncaaf": ("NCAA Football", "NCAAF"),
    # Baseball
    "baseball_mlb": ("MLB", "MLB"),
    # Hockey
    "icehockey_nhl": ("NHL", "NHL"),
    # Tennis
    "tennis_atp": ("Tennis ATP", "ATP"),
    "tennis_wta": ("Tennis WTA", "WTA"),
    # Golf
    "golf_pga_tour": ("PGA Tour", "PGA"),
    # Soccer
    "soccer_epl": ("English Premier League", "EPL"),
    "soccer_uefa_champs_league": ("UEFA Champions League", "UCL"),
    "soccer_uefa_europa": ("UEFA Europa League", "UEL"),
    "soccer_uefa_conference": ("UEFA Conference League", "UECL"),
    "soccer_usa_mls": ("MLS", "MLS"),
    # MMA
    "mma_mixed_martial_arts": ("UFC", "UFC"),
}

# Map league code back to sport key (base mapping)
LEAGUE_TO_SPORT_KEY = {v: k for k, v in SPORT_KEY_TO_LEAGUE.items()}

# Extended mapping that includes alternate league code formats
# Used by providers that may use TENNIS_ATP instead of ATP, etc.
LEAGUE_TO_SPORT_KEY_EXTENDED = {
    **LEAGUE_TO_SPORT_KEY,
    "TENNIS_ATP": "tennis_atp",
    "TENNIS_WTA": "tennis_wta",
}

# =============================================================================
# Sport ID Mappings (Database IDs)
# =============================================================================

# Map database sport ID to sport key
# Sport IDs follow a logical grouping pattern:
# - 30s: Basketball (NBA=30, NCAAB=32, WNBA=34)
# - 40s: MLB=40, NCAAF=41, Tennis ATP=42, Tennis WTA=43
# - 50s: NHL=53
# - 60s: Golf (PGA=60)
# - 70s: Soccer (EPL=70, UCL=71, MLS=72)
# - 80s: Combat sports (UFC=80)
SPORT_ID_TO_KEY = {
    # Basketball
    30: "basketball_nba",
    32: "basketball_ncaab",
    34: "basketball_wnba",
    # Football
    31: "americanfootball_nfl",
    41: "americanfootball_ncaaf",
    # Baseball
    40: "baseball_mlb",
    # Hockey
    44: "icehockey_nhl",  # Legacy mapping (kept for compatibility)
    53: "icehockey_nhl",  # Actual database ID
    # Tennis
    42: "tennis_atp",
    43: "tennis_wta",
    # Golf
    60: "golf_pga_tour",
    # Soccer
    70: "soccer_epl",
    71: "soccer_uefa_champs_league",
    72: "soccer_usa_mls",
    73: "soccer_uefa_europa",
    74: "soccer_uefa_conference",
    # MMA/UFC
    80: "mma_mixed_martial_arts",
}

# Reverse mapping: sport key to database ID
SPORT_KEY_TO_ID = {v: k for k, v in SPORT_ID_TO_KEY.items()}

# =============================================================================
# All Sport Keys (for iteration)
# =============================================================================

ALL_SPORT_KEYS = list(SPORT_KEY_TO_LEAGUE.keys())


# =============================================================================
# Helper Functions
# =============================================================================

def get_league_code(sport_key: str) -> str:
    """Get league code from sport key with fallback."""
    return SPORT_KEY_TO_LEAGUE.get(sport_key, sport_key.upper())


def get_sport_key_from_id(sport_id: int) -> str | None:
    """Get sport key from database ID."""
    return SPORT_ID_TO_KEY.get(sport_id)


def get_sport_id_from_key(sport_key: str) -> int | None:
    """Get database ID from sport key."""
    return SPORT_KEY_TO_ID.get(sport_key)


def get_sport_name(sport_key: str) -> tuple[str, str]:
    """Get (full_name, league_code) tuple for a sport key."""
    return SPORT_KEY_TO_NAME.get(sport_key, (sport_key.upper(), sport_key.upper()))
