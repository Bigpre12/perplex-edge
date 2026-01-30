"""
OddsPapi provider for historical odds data and analytics.

Fetches historical odds movements, game results, and settlement data
from OddsPapi API (https://oddspapi.io).
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# OddsPapi sport IDs
SPORT_IDS = {
    "basketball_nba": 10,  # NBA
    "basketball_ncaab": 10,  # College Basketball (same sport category)
    "americanfootball_nfl": 12,  # NFL
    "baseball_mlb": 16,  # MLB
    "icehockey_nhl": 17,  # NHL
}

# Common bookmakers to track
DEFAULT_BOOKMAKERS = ["pinnacle", "draftkings", "fanduel"]


@dataclass
class OddsPapiFixture:
    """Represents a fixture/game from OddsPapi."""
    fixture_id: str
    sport_id: int
    tournament_id: int
    participant1_id: int
    participant2_id: int
    start_time: datetime
    has_odds: bool


@dataclass
class OddsPapiOddsHistory:
    """Represents historical odds for an outcome."""
    created_at: datetime
    price: float
    limit: float
    is_active: bool


@dataclass
class OddsPapiScore:
    """Represents game scores."""
    fixture_id: str
    participant1_score: int
    participant2_score: int
    period_scores: dict[str, dict[str, int]]


class OddsPapiProvider:
    """
    Provider for fetching historical data from OddsPapi.
    
    Used for:
    - Historical odds movements
    - Game settlements/results
    - Final scores
    
    Rate limits:
    - historical-odds: 5000ms cooldown
    - settlements: 2000ms cooldown
    - scores: 1000ms cooldown
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.oddspapi_api_key
        self.base_url = base_url or settings.oddspapi_base_url
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialize HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def __aenter__(self) -> "OddsPapiProvider":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make an authenticated request to OddsPapi API."""
        if not self.api_key:
            raise ValueError("ODDSPAPI_API_KEY not configured")
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key
        
        logger.debug(f"OddsPapi request: {endpoint}")
        response = await self.client.get(url, params=params)
        
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"OddsPapi API error {e.response.status_code}: {e.response.text[:500]}")
            raise
        
        return response.json()
    
    # =========================================================================
    # Tournament & Fixture Methods
    # =========================================================================
    
    async def fetch_tournaments(self, sport_id: int) -> list[dict[str, Any]]:
        """
        Fetch available tournaments for a sport.
        
        Args:
            sport_id: OddsPapi sport ID (e.g., 10 for basketball)
        
        Returns:
            List of tournament objects with tournamentId, name, etc.
        """
        data = await self._request("/tournaments", {"sportId": sport_id})
        return data if isinstance(data, list) else []
    
    async def fetch_fixtures(
        self,
        tournament_ids: list[int],
        days_ahead: int = 7,
    ) -> list[dict[str, Any]]:
        """
        Fetch fixtures for given tournaments.
        
        Args:
            tournament_ids: List of tournament IDs to fetch
            days_ahead: Number of days ahead to fetch
        
        Returns:
            List of fixture objects
        """
        params = {
            "tournamentIds": ",".join(str(t) for t in tournament_ids),
        }
        data = await self._request("/fixtures", params)
        return data if isinstance(data, list) else []
    
    async def fetch_odds_by_tournaments(
        self,
        tournament_ids: list[int],
        bookmaker: str = "pinnacle",
        odds_format: str = "decimal",
    ) -> list[dict[str, Any]]:
        """
        Fetch current odds for tournaments.
        
        Args:
            tournament_ids: List of tournament IDs
            bookmaker: Bookmaker slug (e.g., "pinnacle", "draftkings")
            odds_format: "decimal" or "american"
        
        Returns:
            List of fixtures with odds data
        """
        params = {
            "tournamentIds": ",".join(str(t) for t in tournament_ids),
            "bookmaker": bookmaker,
            "oddsFormat": odds_format,
        }
        data = await self._request("/odds-by-tournaments", params)
        return data if isinstance(data, list) else []
    
    # =========================================================================
    # Historical Odds Methods
    # =========================================================================
    
    async def fetch_historical_odds(
        self,
        fixture_id: str,
        bookmakers: list[str] = None,
    ) -> dict[str, Any]:
        """
        Fetch historical odds movements for a fixture.
        
        Args:
            fixture_id: OddsPapi fixture ID
            bookmakers: List of bookmaker slugs (max 3)
        
        Returns:
            Historical odds data with price movements
        
        Note: 5000ms rate limit between calls
        """
        bookmakers = bookmakers or DEFAULT_BOOKMAKERS[:3]
        params = {
            "fixtureId": fixture_id,
            "bookmakers": ",".join(bookmakers[:3]),  # Max 3 bookmakers
        }
        data = await self._request("/historical-odds", params)
        return data if isinstance(data, dict) else {}
    
    # =========================================================================
    # Settlement & Scores Methods
    # =========================================================================
    
    async def fetch_settlements(self, fixture_id: str) -> dict[str, Any]:
        """
        Fetch settlement results for a fixture.
        
        Args:
            fixture_id: OddsPapi fixture ID
        
        Returns:
            Settlement data with market outcomes (won/lost/push)
        
        Note: 2000ms rate limit between calls
        """
        params = {"fixtureId": fixture_id}
        data = await self._request("/settlements", params)
        return data if isinstance(data, dict) else {}
    
    async def fetch_scores(self, fixture_id: str) -> dict[str, Any]:
        """
        Fetch final scores for a fixture.
        
        Args:
            fixture_id: OddsPapi fixture ID
        
        Returns:
            Score breakdown by period
        
        Note: 1000ms rate limit between calls
        """
        params = {"fixtureId": fixture_id}
        data = await self._request("/scores", params)
        return data if isinstance(data, dict) else {}
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    async def get_nba_tournaments(self) -> list[dict[str, Any]]:
        """Get NBA tournament IDs."""
        return await self.fetch_tournaments(SPORT_IDS["basketball_nba"])
    
    async def get_completed_fixtures(
        self,
        tournament_ids: list[int],
        days_back: int = 7,
    ) -> list[dict[str, Any]]:
        """
        Get recently completed fixtures that need settlement.
        
        Args:
            tournament_ids: Tournament IDs to check
            days_back: How many days back to look
        
        Returns:
            List of fixtures that have ended
        """
        fixtures = await self.fetch_fixtures(tournament_ids)
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        completed = []
        
        for fixture in fixtures:
            start_time = fixture.get("startTime")
            if start_time:
                try:
                    # Parse ISO datetime
                    dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    # If game started more than 4 hours ago, it's likely finished
                    if dt < datetime.utcnow() - timedelta(hours=4):
                        completed.append(fixture)
                except (ValueError, TypeError):
                    pass
        
        return completed


# =============================================================================
# Helper Functions
# =============================================================================

def decimal_to_american(decimal_odds: float) -> int:
    """Convert decimal odds to American format."""
    if decimal_odds >= 2.0:
        return int((decimal_odds - 1) * 100)
    else:
        return int(-100 / (decimal_odds - 1))


def american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal format."""
    if american_odds > 0:
        return 1 + (american_odds / 100)
    else:
        return 1 + (100 / abs(american_odds))


def parse_oddspapi_datetime(dt_string: str) -> datetime:
    """Parse OddsPapi datetime string to Python datetime."""
    # Handle various formats
    if "+" in dt_string:
        # Has timezone: "2025-04-16T21:12:10.506331+00:00"
        return datetime.fromisoformat(dt_string)
    elif dt_string.endswith("Z"):
        # UTC: "2025-04-16T21:12:10.506Z"
        return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
    else:
        # Assume UTC
        return datetime.fromisoformat(dt_string)
