"""
SportsGameOdds Period Constants
Centralized registry for all supported period IDs.
Data source: SportsGameOdds API Documentation.
"""

SGO_PERIODS = {
    "game": "Full Event",
    "1h": "1st Half",
    "2h": "2nd Half",
    "1q": "1st Quarter",
    "2q": "2nd Quarter",
    "3q": "3rd Quarter",
    "4q": "4th Quarter",
    "1qx3": "1st 3 Quarters",
    "1p": "1st Period",
    "2p": "2nd Period",
    "3p": "3rd Period",
    "1i": "1st Inning",
    "2i": "2nd Inning",
    "3i": "3rd Inning",
    "4i": "4th Inning",
    "5i": "5th Inning",
    "6i": "6i",
    "7i": "7i",
    "8i": "8i",
    "9i": "9i",
    "1ix3": "1st 3 Innings",
    "1ix5": "1st 5 Innings", # Deprecated in favor of 1h
    "1ix7": "1st 7 Innings",
    "1s": "1st Set",
    "2s": "2nd Set",
    "3s": "3rd Set",
    "4s": "4th Set",
    "5s": "5th Set",
    "1r": "1st Round",
    "2r": "2nd Round",
    "3r": "3rd Round",
    "4r": "4th Round",
    "5r": "5th Round",
    "6r": "6th Round",
    "7r": "7r",
    "8r": "8r",
    "9r": "9r",
    "10r": "10r",
    "11r": "11r",
    "12r": "12r",
    "1rx2": "1st 2 Rounds",
    "1m": "1st Minute",
    "1mx4": "1st 4 Minutes",
    "1mx5": "1st 5 Minutes",
    "1mx8": "1st 8 Minutes",
    "1mx10": "1st 10 Minutes",
    "reg": "Regulation",
    "ot": "Extra Time",
    "so": "Penalty Shootout",
    "dec": "Judges' Decision",
}

DEPRECATED_PERIODS = {
    "1ix5": "1h"
}

def get_sgo_period_display(period_id: str) -> str:
    """Get display name for an SGO period ID."""
    p_id = period_id.lower()
    return SGO_PERIODS.get(p_id, period_id.upper())

def is_deprecated_period(period_id: str) -> bool:
    """Check if the period is deprecated."""
    return period_id.lower() in DEPRECATED_PERIODS

def get_period_replacement(period_id: str) -> str:
    """Get the recommended replacement for a deprecated period."""
    return DEPRECATED_PERIODS.get(period_id.lower(), period_id)
