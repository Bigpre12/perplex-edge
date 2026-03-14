import os
print(f"DEBUG: Loading sport_constants from {os.path.abspath(__file__)}")

from typing import Dict, Optional

# Master mapping of Sport ID to The Odds API Key
SPORT_ID_TO_KEY: Dict[int, str] = {
    30: "basketball_nba",
    31: "americanfootball_nfl",
    40: "baseball_mlb",
    22: "icehockey_nhl",
    39: "basketball_ncaab",
    41: "americanfootball_ncaaf",
    42: "tennis_atp",
    43: "tennis_wta",
    53: "basketball_wnba",
    54: "mma_mixed_martial_arts",
    55: "boxing_boxing",
}

# Reverse mapping for lookups
SPORT_KEY_TO_ID: Dict[str, int] = {v: k for k, v in SPORT_ID_TO_KEY.items()}

def get_sport_id(sport_key: str) -> Optional[int]:
    """Get the standard Sport ID for a given key."""
    if not sport_key:
        return None
    return SPORT_KEY_TO_ID.get(sport_key.lower())

def get_sport_key(sport_id: int) -> Optional[str]:
    """Get the standard The Odds API key for a given Sport ID."""
    return SPORT_ID_TO_KEY.get(sport_id)

def get_all_supported_sport_ids() -> list:
    """Returns a list of all sport IDs supported by the system."""
    return list(SPORT_ID_TO_KEY.keys())
