"""
Redis Cache Module — Upstash-compatible (Free: 10k commands/day)

Provides a unified cache interface that:
  1. Uses Upstash Redis when REDIS_URL is set (deployed)
  2. Falls back to in-memory dict when Redis is unavailable (local dev)

This ensures the waterfall cache works both locally and on Render+Upstash.
"""
import os
import time
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import redis — optional dependency
try:
    if os.getenv("DEVELOPMENT_MODE") == "1":
        HAS_REDIS = False
        logger.info("redis disabled locally to prevent import-time hang — using in-memory cache")
    else:
        import redis.asyncio as aioredis
        HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logger.info("redis package not installed — using in-memory cache")


from config import settings

class CacheManager:
    """Dual-mode cache: Redis (production) or in-memory dict (local dev)."""

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._redis = None
        self._memory: dict = {}
        self._connected = False

    async def connect(self):
        """Connect to Redis if URL is configured."""
        if self.redis_url and HAS_REDIS:
            try:
                logger.info(f"Attempting to connect to Redis at {self.redis_url}...")
                self._redis = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=1.0,  # Reduced from 2.0
                    socket_timeout=1.0,          # Added socket timeout
                )
                import asyncio
                try:
                    await asyncio.wait_for(self._redis.ping(), timeout=2.0)
                    self._connected = True
                    logger.info("OK - Redis connected (Upstash)")
                except asyncio.TimeoutError:
                    logger.warning("WARN - Redis ping timed out, using in-memory fallback")
                    self._redis = None
                    self._connected = False
            except Exception as e:
                logger.warning(f"WARN - Redis connection failed, using in-memory: {e}")
                self._redis = None
                self._connected = False
        else:
            logger.info("No REDIS_URL set — using in-memory cache")

    async def get(self, key: str) -> Optional[str]:
        """Get a cached value."""
        if self._connected and self._redis:
            try:
                return await self._redis.get(key)
            except Exception:
                pass

        # In-memory fallback
        entry = self._memory.get(key)
        if entry and time.time() < entry.get("exp", 0):
            return entry["val"]
        return None

    async def set(self, key: str, value: str, ttl: int = 300):
        """Set a cached value with TTL in seconds."""
        if self._connected and self._redis:
            try:
                await self._redis.setex(key, ttl, value)
                return
            except Exception:
                pass

        # In-memory fallback
        self._memory[key] = {"val": value, "exp": time.time() + ttl}

    async def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize a JSON-cached value."""
        raw = await self.get(key)
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        return None

    async def set_json(self, key: str, data: Any, ttl: int = 300):
        """Serialize and cache a JSON value."""
        await self.set(key, json.dumps(data, default=str), ttl)

    async def delete(self, key: str):
        """Delete a cached key."""
        if self._connected and self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                pass
        self._memory.pop(key, None)

    @property
    def is_redis(self) -> bool:
        return self._connected

    @property
    def status(self) -> str:
        return "redis" if self._connected else "memory"


# Singleton
cache = CacheManager()
