"""
External API Providers.

These are thin API clients - they only fetch data from external APIs.
They do NOT:
- Write to the database
- Cache data (that's the service/cache layer's job)
- Handle fallback logic (that's the service layer's job)

Each provider:
- Extends BaseProvider
- Implements health_check()
- Uses consistent error handling
- Tracks rate limits where applicable
"""

from app.data.providers.odds_api import OddsAPIProvider
from app.data.providers.betstack import BetStackProvider
from app.data.providers.espn import ESPNProvider
from app.data.providers.oddspapi import OddsPapiProvider

__all__ = [
    "OddsAPIProvider",
    "BetStackProvider",
    "ESPNProvider",
    "OddsPapiProvider",
]
