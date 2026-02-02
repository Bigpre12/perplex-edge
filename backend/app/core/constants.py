"""
Centralized constants for sport mappings and configurations.

This module provides the single source of truth for sport-related mappings
used throughout the application.
"""

# =============================================================================
# Sport Key Mappings
# =============================================================================

# Map sport key (The Odds API format) to display league code
SPORT_KEY_TO_LEAGUE = {
    "basketball_nba": "NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "basketball_ncaab": "NCAAB",
    "americanfootball_ncaaf": "NCAAF",
    "tennis_atp": "ATP",
    "tennis_wta": "WTA",
}

# Map sport key to full name and league code tuple
SPORT_KEY_TO_NAME = {
    "basketball_nba": ("NBA", "NBA"),
    "americanfootball_nfl": ("NFL", "NFL"),
    "baseball_mlb": ("MLB", "MLB"),
    "icehockey_nhl": ("NHL", "NHL"),
    "basketball_ncaab": ("NCAA Basketball", "NCAAB"),
    "americanfootball_ncaaf": ("NCAA Football", "NCAAF"),
    "tennis_atp": ("Tennis ATP", "ATP"),
    "tennis_wta": ("Tennis WTA", "WTA"),
}

# Map league code back to sport key
LEAGUE_TO_SPORT_KEY = {v: k for k, v in SPORT_KEY_TO_LEAGUE.items()}

# =============================================================================
# Sport ID Mappings (Database IDs)
# =============================================================================

# Map database sport ID to sport key
# Note: Tennis IDs are 42/43 in the database (not 50/51)
SPORT_ID_TO_KEY = {
    30: "basketball_nba",
    31: "americanfootball_nfl",
    32: "basketball_ncaab",
    40: "baseball_mlb",
    41: "americanfootball_ncaaf",
    42: "tennis_atp",
    43: "tennis_wta",
    44: "icehockey_nhl",
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
