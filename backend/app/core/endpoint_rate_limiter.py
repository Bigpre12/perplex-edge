"""
In-memory sliding window rate limiter for FastAPI endpoints.

Usage:
    from app.core.endpoint_rate_limiter import RateLimitDep

    @router.get("/expensive", dependencies=[Depends(RateLimitDep(max_calls=30, window_seconds=60))])
    async def expensive_endpoint(): ...
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException


class RateLimitDep:
    """FastAPI dependency that enforces per-IP sliding window rate limits."""

    def __init__(self, max_calls: int = 30, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _cleanup(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._hits[key] = [t for t in self._hits[key] if t > cutoff]

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        self._cleanup(client_ip, now)

        if len(self._hits[client_ip]) >= self.max_calls:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_calls} requests per {self.window_seconds}s.",
            )

        self._hits[client_ip].append(now)


# Pre-configured limiters for common use cases
picks_rate_limit = RateLimitDep(max_calls=30, window_seconds=60)
parlays_rate_limit = RateLimitDep(max_calls=20, window_seconds=60)
