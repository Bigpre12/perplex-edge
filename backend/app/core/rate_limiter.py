"""
Shared rate limiting utilities for all API providers.

This module provides a reusable RateLimiter class that can be used by any
external API provider to prevent hitting rate limits.
"""

import asyncio
import time
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Async-friendly rate limiter that enforces minimum intervals between API calls.
    
    This prevents hitting rate limits on external APIs by ensuring at least
    `min_interval` seconds between consecutive calls.
    
    Features:
    - Thread-safe via asyncio lock
    - Configurable minimum interval
    - Supports burst allowance for initial requests
    - Tracks call count for monitoring
    
    Example:
        limiter = RateLimiter(min_interval=1.0)
        async with SomeAPIClient() as client:
            for item in items:
                await limiter.wait()
                result = await client.fetch(item)
    """
    
    def __init__(
        self,
        min_interval: float = 1.0,
        burst_allowance: int = 0,
        name: str = "default",
    ):
        """
        Initialize rate limiter.
        
        Args:
            min_interval: Minimum seconds between API calls (default: 1.0)
            burst_allowance: Number of initial requests allowed without delay (default: 0)
            name: Name for logging purposes
        """
        self._last_call = 0.0
        self._min_interval = min_interval
        self._burst_remaining = burst_allowance
        self._lock = asyncio.Lock()
        self._call_count = 0
        self._name = name
    
    async def wait(self) -> None:
        """
        Wait if needed to respect rate limit.
        
        Thread-safe via asyncio lock to handle concurrent calls.
        """
        async with self._lock:
            self._call_count += 1
            
            # Allow burst requests without delay
            if self._burst_remaining > 0:
                self._burst_remaining -= 1
                self._last_call = time.time()
                return
            
            elapsed = time.time() - self._last_call
            if elapsed < self._min_interval:
                wait_time = self._min_interval - elapsed
                logger.debug(
                    f"[{self._name}] Rate limiter: waiting {wait_time:.2f}s "
                    f"before call #{self._call_count}"
                )
                await asyncio.sleep(wait_time)
            
            self._last_call = time.time()
    
    def reset(self) -> None:
        """Reset the rate limiter (useful for testing)."""
        self._last_call = 0.0
        self._call_count = 0
    
    @property
    def call_count(self) -> int:
        """Get total number of calls made through this limiter."""
        return self._call_count
    
    @property
    def min_interval(self) -> float:
        """Get the minimum interval setting."""
        return self._min_interval


# =============================================================================
# Pre-configured Rate Limiters for Different APIs
# =============================================================================

# Odds API (The Odds API) - 500 requests/month on free tier
# Be conservative: 1 second between calls
_odds_api_limiter: Optional[RateLimiter] = None


def get_odds_api_limiter() -> RateLimiter:
    """Get the shared rate limiter for The Odds API."""
    global _odds_api_limiter
    if _odds_api_limiter is None:
        _odds_api_limiter = RateLimiter(
            min_interval=1.0,
            burst_allowance=3,  # Allow 3 quick calls at startup
            name="odds_api",
        )
    return _odds_api_limiter


# Injury API - Usually more lenient
_injury_api_limiter: Optional[RateLimiter] = None


def get_injury_api_limiter() -> RateLimiter:
    """Get the shared rate limiter for Injury API."""
    global _injury_api_limiter
    if _injury_api_limiter is None:
        _injury_api_limiter = RateLimiter(
            min_interval=0.5,
            burst_allowance=5,
            name="injury_api",
        )
    return _injury_api_limiter


# Roster API (balldontlie.io) - Has rate limits
_roster_api_limiter: Optional[RateLimiter] = None


def get_roster_api_limiter() -> RateLimiter:
    """Get the shared rate limiter for Roster API."""
    global _roster_api_limiter
    if _roster_api_limiter is None:
        _roster_api_limiter = RateLimiter(
            min_interval=0.5,
            burst_allowance=5,
            name="roster_api",
        )
    return _roster_api_limiter


# ESPN API - Generally lenient but can block aggressive scraping
_espn_api_limiter: Optional[RateLimiter] = None


def get_espn_api_limiter() -> RateLimiter:
    """Get the shared rate limiter for ESPN API."""
    global _espn_api_limiter
    if _espn_api_limiter is None:
        _espn_api_limiter = RateLimiter(
            min_interval=0.3,
            burst_allowance=10,
            name="espn_api",
        )
    return _espn_api_limiter


# OddsPapi API (historical data)
_oddspapi_limiter: Optional[RateLimiter] = None


def get_oddspapi_limiter() -> RateLimiter:
    """Get the shared rate limiter for OddsPapi API."""
    global _oddspapi_limiter
    if _oddspapi_limiter is None:
        _oddspapi_limiter = RateLimiter(
            min_interval=1.0,
            burst_allowance=3,
            name="oddspapi",
        )
    return _oddspapi_limiter


# BetStack API (fallback odds provider)
_betstack_api_limiter: Optional[RateLimiter] = None


def get_betstack_api_limiter() -> RateLimiter:
    """Get the shared rate limiter for BetStack API."""
    global _betstack_api_limiter
    if _betstack_api_limiter is None:
        _betstack_api_limiter = RateLimiter(
            min_interval=1.0,
            burst_allowance=3,
            name="betstack_api",
        )
    return _betstack_api_limiter


# Stats API (NBA stats, etc.)
_stats_api_limiter: Optional[RateLimiter] = None


def get_stats_api_limiter() -> RateLimiter:
    """Get the shared rate limiter for Stats API."""
    global _stats_api_limiter
    if _stats_api_limiter is None:
        from app.core.config import get_rate_limit_delay
        _stats_api_limiter = RateLimiter(
            min_interval=get_rate_limit_delay(),
            burst_allowance=2,
            name="stats_api",
        )
    return _stats_api_limiter


def reset_all_limiters() -> None:
    """Reset all rate limiters (useful for testing)."""
    global _odds_api_limiter, _injury_api_limiter, _roster_api_limiter
    global _espn_api_limiter, _oddspapi_limiter, _betstack_api_limiter, _stats_api_limiter
    
    for limiter in [
        _odds_api_limiter, _injury_api_limiter, _roster_api_limiter,
        _espn_api_limiter, _oddspapi_limiter, _betstack_api_limiter, _stats_api_limiter
    ]:
        if limiter:
            limiter.reset()
