"""Stats provider for fetching player game logs and writing to PlayerGameStats."""

import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings, get_rate_limit_delay
from app.core.logging import get_logger
from app.core.resilience import (
    with_retry,
    RetryConfig,
    CircuitBreakerRegistry,
)
from app.models import Player, Game, PlayerGameStats

logger = get_logger(__name__)


# =============================================================================
# Rate Limiter
# =============================================================================

class RateLimiter:
    """
    Async-friendly rate limiter that enforces minimum intervals between API calls.
    
    This prevents hitting rate limits on external APIs (like NBA stats API)
    by ensuring at least `min_interval` seconds between consecutive calls.
    """
    
    def __init__(self, min_interval: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            min_interval: Minimum seconds between API calls (default: 1.0)
        """
        self._last_call = 0.0
        self._min_interval = min_interval
        self._lock = asyncio.Lock()
    
    async def wait(self) -> None:
        """
        Wait if needed to respect rate limit.
        
        Thread-safe via asyncio lock to handle concurrent calls.
        """
        async with self._lock:
            elapsed = time.time() - self._last_call
            if elapsed < self._min_interval:
                wait_time = self._min_interval - elapsed
                logger.debug(f"Rate limiter: waiting {wait_time:.2f}s before next API call")
                await asyncio.sleep(wait_time)
            self._last_call = time.time()
    
    def reset(self) -> None:
        """Reset the rate limiter (useful for testing)."""
        self._last_call = 0.0

# Retry config for Stats API
STATS_API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    min_wait_seconds=1.0,
    max_wait_seconds=15.0,
    jitter=True,
)

# Create circuit breaker for Stats API
_stats_api_breaker = CircuitBreakerRegistry.get_or_create(
    "stats_api",
    fail_max=5,
    reset_timeout=60,
)


# =============================================================================
# Data Classes
# =============================================================================

class GameLog:
    """Normalized game log entry for a player."""
    
    def __init__(
        self,
        external_game_id: str,
        game_date: datetime,
        opponent: str,
        minutes: float,
        stats: dict[str, float],
    ):
        self.external_game_id = external_game_id
        self.game_date = game_date
        self.opponent = opponent
        self.minutes = minutes
        self.stats = stats  # e.g., {"PTS": 28, "REB": 7, "AST": 9, "3PM": 3}
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "external_game_id": self.external_game_id,
            "game_date": self.game_date.isoformat(),
            "opponent": self.opponent,
            "minutes": self.minutes,
            "stats": self.stats,
        }


class PlayerStatsAggregate:
    """Aggregated stats for a player over N games."""
    
    def __init__(
        self,
        player_external_id: str,
        player_name: str,
        n_games: int,
        averages: dict[str, float],
        totals: dict[str, float],
        hit_rates: dict[str, dict[str, float]],  # stat_type -> {line: hit_rate}
    ):
        self.player_external_id = player_external_id
        self.player_name = player_name
        self.n_games = n_games
        self.averages = averages
        self.totals = totals
        self.hit_rates = hit_rates
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "player_external_id": self.player_external_id,
            "player_name": self.player_name,
            "n_games": self.n_games,
            "averages": self.averages,
            "totals": self.totals,
            "hit_rates": self.hit_rates,
        }


# =============================================================================
# Stats Provider
# =============================================================================

class StatsProvider:
    """
    Provider for fetching player statistics from external APIs.
    
    Fetches game logs, computes aggregates, and writes to PlayerGameStats table.
    """
    
    # Common stat types
    STAT_TYPES = [
        "PTS", "REB", "AST", "3PM", "STL", "BLK", "TO", "MIN",
        "FGM", "FGA", "FG_PCT", "FTM", "FTA", "FT_PCT",
        "OREB", "DREB", "PF", "PLUS_MINUS",
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_stubs: bool = False,
        rate_limit_delay: Optional[float] = None,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.stats_api_key
        self.base_url = base_url or settings.stats_api_base_url
        self.use_stubs = use_stubs
        self._client: Optional[httpx.AsyncClient] = None
        
        # Use config-based rate limit delay if not specified
        if rate_limit_delay is None:
            rate_limit_delay = get_rate_limit_delay()
        self._rate_limiter = RateLimiter(min_interval=rate_limit_delay)
    
    async def __aenter__(self) -> "StatsProvider":
        self._client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
    
    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return self._client
    
    @with_retry(config=STATS_API_RETRY_CONFIG, retry_on=(httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError))
    async def _request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make an authenticated request to the stats API with retry logic."""
        if not self.api_key:
            raise ValueError("STATS_API_KEY not configured")
        
        # Enforce rate limiting before making request
        await self._rate_limiter.wait()
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = await self.client.get(url, params=params, headers=headers)
        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
            logger.error(
                "stats_api_connection_error",
                endpoint=endpoint,
                error_type=type(e).__name__,
                error=str(e)[:200],
            )
            raise  # Let retry decorator handle
        
        # Handle HTTP errors gracefully
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            
            if status_code == 422:
                logger.warning(
                    "stats_api_validation_error",
                    endpoint=endpoint,
                    response=e.response.text[:500],
                )
                return []
            elif status_code == 429:
                logger.warning(
                    "stats_api_rate_limited",
                    endpoint=endpoint,
                    retry_after=e.response.headers.get("Retry-After"),
                )
                return []
            elif status_code == 404:
                logger.info("stats_api_not_found", endpoint=endpoint)
                return []
            elif status_code >= 500:
                logger.error(
                    "stats_api_server_error",
                    endpoint=endpoint,
                    status_code=status_code,
                )
                raise  # May be retried
            else:
                logger.error(
                    "stats_api_client_error",
                    endpoint=endpoint,
                    status_code=status_code,
                    response=e.response.text[:500],
                )
                raise
        
        return response.json()
    
    # =========================================================================
    # Public API Methods
    # =========================================================================
    
    async def fetch_player_game_logs(
        self,
        external_player_id: str,
        n_games: int = 10,
        season: Optional[str] = None,
    ) -> list[GameLog]:
        """
        Fetch recent game logs for a player.
        
        Args:
            external_player_id: External API player ID
            n_games: Number of recent games to fetch
            season: Optional season filter (e.g., '2025-26')
        
        Returns:
            List of GameLog objects, most recent first
        """
        if self.use_stubs:
            raw_data = self._stub_game_logs_response(external_player_id, n_games)
        else:
            params = {"limit": n_games}
            if season:
                params["season"] = season
            raw_data = await self._request(
                f"/players/{external_player_id}/games",
                params,
            )
        
        return self._parse_game_logs(raw_data)
    
    async def fetch_season_averages(
        self,
        external_player_id: str,
        season: Optional[str] = None,
    ) -> dict[str, float]:
        """
        Fetch season averages for a player.
        
        Args:
            external_player_id: External API player ID
            season: Optional season (defaults to current)
        
        Returns:
            Dictionary of stat_type -> average value
        """
        if self.use_stubs:
            raw_data = self._stub_season_averages_response(external_player_id)
        else:
            params = {}
            if season:
                params["season"] = season
            raw_data = await self._request(
                f"/players/{external_player_id}/averages",
                params,
            )
        
        return raw_data.get("averages", {})
    
    def aggregate_stats(
        self,
        game_logs: list[GameLog],
        stat_types: Optional[list[str]] = None,
    ) -> dict[str, float]:
        """
        Compute average stats from game logs.
        
        Args:
            game_logs: List of GameLog objects
            stat_types: Optional list of specific stats to compute
        
        Returns:
            Dictionary of stat_type -> average value
        """
        if not game_logs:
            return {}
        
        stat_types = stat_types or self.STAT_TYPES
        averages = {}
        
        for stat_type in stat_types:
            values = [
                log.stats.get(stat_type, 0)
                for log in game_logs
                if stat_type in log.stats
            ]
            if values:
                averages[stat_type] = sum(values) / len(values)
        
        return averages
    
    def calculate_hit_rates(
        self,
        game_logs: list[GameLog],
        lines: dict[str, float],
    ) -> dict[str, float]:
        """
        Calculate hit rates for given stat lines.
        
        Args:
            game_logs: List of GameLog objects
            lines: Dictionary of stat_type -> line value
        
        Returns:
            Dictionary of stat_type -> hit rate (0.0 to 1.0)
        """
        if not game_logs:
            return {}
        
        hit_rates = {}
        
        for stat_type, line in lines.items():
            hits = sum(
                1 for log in game_logs
                if log.stats.get(stat_type, 0) > line
            )
            hit_rates[stat_type] = hits / len(game_logs)
        
        return hit_rates
    
    async def get_player_aggregate(
        self,
        external_player_id: str,
        player_name: str,
        n_games: int = 10,
        lines: Optional[dict[str, float]] = None,
    ) -> PlayerStatsAggregate:
        """
        Get full aggregate stats for a player.
        
        Args:
            external_player_id: External API player ID
            player_name: Player's name
            n_games: Number of games to aggregate
            lines: Optional lines to calculate hit rates for
        
        Returns:
            PlayerStatsAggregate with averages, totals, and hit rates
        """
        game_logs = await self.fetch_player_game_logs(external_player_id, n_games)
        
        averages = self.aggregate_stats(game_logs)
        
        # Calculate totals
        totals = {}
        for stat_type in self.STAT_TYPES:
            values = [log.stats.get(stat_type, 0) for log in game_logs if stat_type in log.stats]
            if values:
                totals[stat_type] = sum(values)
        
        # Calculate hit rates if lines provided
        hit_rates = {}
        if lines:
            for stat_type, line in lines.items():
                hit_rates[stat_type] = {str(line): self.calculate_hit_rates(game_logs, {stat_type: line}).get(stat_type, 0)}
        
        return PlayerStatsAggregate(
            player_external_id=external_player_id,
            player_name=player_name,
            n_games=len(game_logs),
            averages=averages,
            totals=totals,
            hit_rates=hit_rates,
        )
    
    # =========================================================================
    # Database Write Methods
    # =========================================================================
    
    async def sync_player_stats(
        self,
        db: AsyncSession,
        player_id: int,
        game_logs: list[GameLog],
    ) -> int:
        """
        Write game logs to PlayerGameStats table.
        
        Args:
            db: Database session
            player_id: Internal player ID
            game_logs: List of GameLog objects to write
        
        Returns:
            Number of records written
        """
        written = 0
        
        for log in game_logs:
            # Find the game in our database
            result = await db.execute(
                select(Game).where(Game.external_game_id == log.external_game_id)
            )
            game = result.scalar_one_or_none()
            
            if not game:
                logger.warning(f"Game not found: {log.external_game_id}")
                continue
            
            # Write each stat
            for stat_type, value in log.stats.items():
                # Check if already exists
                existing = await db.execute(
                    select(PlayerGameStats).where(
                        PlayerGameStats.player_id == player_id,
                        PlayerGameStats.game_id == game.id,
                        PlayerGameStats.stat_type == stat_type,
                    )
                )
                
                if existing.scalar_one_or_none():
                    continue  # Skip if already exists
                
                stat = PlayerGameStats(
                    player_id=player_id,
                    game_id=game.id,
                    stat_type=stat_type,
                    value=value,
                    minutes=log.minutes,
                )
                db.add(stat)
                written += 1
        
        await db.commit()
        return written
    
    async def sync_player_by_external_id(
        self,
        db: AsyncSession,
        external_player_id: str,
        n_games: int = 10,
    ) -> int:
        """
        Fetch and sync stats for a player by external ID.
        
        Args:
            db: Database session
            external_player_id: External API player ID
            n_games: Number of games to sync
        
        Returns:
            Number of records written
        """
        # Find player in our database
        result = await db.execute(
            select(Player).where(Player.external_player_id == external_player_id)
        )
        player = result.scalar_one_or_none()
        
        if not player:
            logger.warning(f"Player not found: {external_player_id}")
            return 0
        
        # Fetch and sync
        game_logs = await self.fetch_player_game_logs(external_player_id, n_games)
        return await self.sync_player_stats(db, player.id, game_logs)
    
    # =========================================================================
    # Parsing Methods
    # =========================================================================
    
    def _parse_game_logs(self, raw_data: dict[str, Any]) -> list[GameLog]:
        """Parse game logs from API response."""
        logs = []
        
        for game in raw_data.get("games", []):
            logs.append(GameLog(
                external_game_id=game["game_id"],
                game_date=datetime.fromisoformat(game["date"].replace("Z", "+00:00")),
                opponent=game.get("opponent", ""),
                minutes=game.get("MIN", 0),
                stats={
                    "PTS": game.get("PTS", 0),
                    "REB": game.get("REB", 0),
                    "AST": game.get("AST", 0),
                    "3PM": game.get("3PM", 0),
                    "STL": game.get("STL", 0),
                    "BLK": game.get("BLK", 0),
                    "TO": game.get("TO", 0),
                    "FGM": game.get("FGM", 0),
                    "FGA": game.get("FGA", 0),
                    "FTM": game.get("FTM", 0),
                    "FTA": game.get("FTA", 0),
                    "OREB": game.get("OREB", 0),
                    "DREB": game.get("DREB", 0),
                    "PF": game.get("PF", 0),
                    "PLUS_MINUS": game.get("PLUS_MINUS", 0),
                },
            ))
        
        return logs
    
    # =========================================================================
    # Stub Methods for Testing
    # =========================================================================
    
    def _stub_game_logs_response(
        self,
        external_player_id: str,
        n_games: int,
    ) -> dict[str, Any]:
        """Return realistic stub game log data for testing."""
        # Simulate different players
        if "lebron" in external_player_id.lower():
            base_stats = {"PTS": 27, "REB": 8, "AST": 8, "3PM": 2, "MIN": 35}
            player_name = "LeBron James"
        elif "curry" in external_player_id.lower():
            base_stats = {"PTS": 29, "REB": 5, "AST": 6, "3PM": 5, "MIN": 34}
            player_name = "Stephen Curry"
        elif "davis" in external_player_id.lower():
            base_stats = {"PTS": 25, "REB": 12, "AST": 3, "3PM": 1, "MIN": 36}
            player_name = "Anthony Davis"
        elif "jokic" in external_player_id.lower():
            base_stats = {"PTS": 26, "REB": 12, "AST": 9, "3PM": 1, "MIN": 34}
            player_name = "Nikola Jokic"
        else:
            base_stats = {"PTS": 15, "REB": 4, "AST": 3, "3PM": 1, "MIN": 28}
            player_name = "Unknown Player"
        
        games = []
        opponents = ["GSW", "BOS", "MIA", "PHX", "DEN", "MIL", "PHI", "NYK", "LAC", "DAL"]
        
        import random
        random.seed(hash(external_player_id))  # Consistent randomness per player
        
        # Use dynamic dates based on today in US Eastern timezone
        utc_now = datetime.now(timezone.utc)
        eastern_offset = timedelta(hours=-5)  # EST (UTC-5)
        eastern_now = utc_now + eastern_offset
        today = eastern_now.replace(hour=19, minute=0, second=0, microsecond=0)
        
        for i in range(min(n_games, 10)):
            # Games from today going back
            game_date = today - timedelta(days=i)
            
            # Add some variance
            variance = {k: int(v * (0.7 + random.random() * 0.6)) for k, v in base_stats.items()}
            
            # Dynamic game_id based on date
            date_str = game_date.strftime("%Y%m%d")
            games.append({
                "game_id": f"game_{date_str}_{i}",
                "date": game_date.isoformat(),
                "opponent": opponents[i % len(opponents)],
                "home": i % 2 == 0,
                "result": "W" if random.random() > 0.4 else "L",
                "MIN": variance["MIN"],
                "PTS": variance["PTS"],
                "REB": variance["REB"],
                "AST": variance["AST"],
                "3PM": variance["3PM"],
                "STL": random.randint(0, 3),
                "BLK": random.randint(0, 2),
                "TO": random.randint(1, 4),
                "FGM": int(variance["PTS"] * 0.4),
                "FGA": int(variance["PTS"] * 0.8),
                "FTM": random.randint(2, 8),
                "FTA": random.randint(3, 10),
                "OREB": random.randint(0, 3),
                "DREB": variance["REB"] - random.randint(0, 3),
                "PF": random.randint(1, 4),
                "PLUS_MINUS": random.randint(-15, 20),
            })
        
        return {
            "player_id": external_player_id,
            "player_name": player_name,
            "games": games,
        }
    
    def _stub_season_averages_response(
        self,
        external_player_id: str,
    ) -> dict[str, Any]:
        """Return realistic stub season averages for testing."""
        from app.services.season_helper import get_nba_season_label
        current_season = get_nba_season_label()
        
        if "lebron" in external_player_id.lower():
            return {
                "player_id": external_player_id,
                "season": current_season,
                "games_played": 45,
                "averages": {
                    "PTS": 26.8,
                    "REB": 7.9,
                    "AST": 8.2,
                    "3PM": 2.1,
                    "STL": 1.2,
                    "BLK": 0.6,
                    "TO": 3.5,
                    "MIN": 35.2,
                    "FG_PCT": 0.525,
                    "3P_PCT": 0.398,
                    "FT_PCT": 0.752,
                },
            }
        elif "curry" in external_player_id.lower():
            return {
                "player_id": external_player_id,
                "season": current_season,
                "games_played": 42,
                "averages": {
                    "PTS": 28.5,
                    "REB": 4.8,
                    "AST": 5.9,
                    "3PM": 5.2,
                    "STL": 0.9,
                    "BLK": 0.2,
                    "TO": 3.2,
                    "MIN": 33.8,
                    "FG_PCT": 0.478,
                    "3P_PCT": 0.428,
                    "FT_PCT": 0.915,
                },
            }
        else:
            return {
                "player_id": external_player_id,
                "season": current_season,
                "games_played": 40,
                "averages": {
                    "PTS": 14.5,
                    "REB": 4.2,
                    "AST": 2.8,
                    "3PM": 1.2,
                    "STL": 0.7,
                    "BLK": 0.3,
                    "TO": 1.8,
                    "MIN": 26.5,
                },
            }
