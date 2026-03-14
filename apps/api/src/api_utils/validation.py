from fastapi import HTTPException
from typing import Optional, List
from config.sports_config import ALL_SPORTS

def validate_sport(sport: Optional[str]) -> Optional[str]:
    """Ensures the sport key is valid according to our configuration."""
    if not sport:
        return None
    if sport not in ALL_SPORTS:
        # Check if it's in the display name map too (fallback)
        from config.sports_config import SPORT_DISPLAY
        if sport in SPORT_DISPLAY.values():
            # Find the key for this display name
            for k, v in SPORT_DISPLAY.items():
                if v == sport:
                    return k
        
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid sport key: '{sport}'. Must be one of {ALL_SPORTS}"
        )
    return sport

def validate_limit(limit: int, max_limit: int = 1000) -> int:
    """Caps the limit to prevent resource exhaustion."""
    if limit < 1:
        return 1
    if limit > max_limit:
        return max_limit
    return limit
