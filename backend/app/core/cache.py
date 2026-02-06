"""
Unified caching layer for Perplex Edge.

Supports both Redis (preferred for production) and in-memory caching.
Falls back to in-memory if Redis is not configured or unavailable.
"""
import json
import asyncio
from datetime import timedelta
from typing import Any, Optional, Callable, TypeVar, Generic
from functools import wraps

from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)

T = TypeVar("T")


class CacheBackend:
    """Abstract cache backend interface."""
    
    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError
    
    async def set(self, key: str, value: str, ttl_seconds: int = 300) -> bool:
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        raise NotImplementedError
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern. Returns count of deleted keys."""
        raise NotImplementedError
    
    def stats(self) -> dict[str, Any]:
        raise NotImplementedError
    
    async def health_check(self) -> bool:
        """Check if cache is healthy."""
        raise NotImplementedError


class InMemoryCacheBackend(CacheBackend):
    """
    Simple in-memory cache with TTL support.
    
    Good for development and single-instance deployments.
    Not suitable for multi-instance production deployments.
    """
    
    def __init__(self, max_size: int = 1000):
        self._cache: dict[str, tuple[str, float]] = {}  # key -> (value, expire_time)
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
    
    async def get(self, key: str) -> Optional[str]:
        import time
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        
        value, expire_time = entry
        if time.time() > expire_time:
            # Expired
            del self._cache[key]
            self._misses += 1
            return None
        
        self._hits += 1
        return value
    
    async def set(self, key: str, value: str, ttl_seconds: int = 300) -> bool:
        import time
        
        # Simple eviction if at capacity
        if len(self._cache) >= self._max_size:
            # Remove oldest 10%
            to_remove = list(self._cache.keys())[:self._max_size // 10]
            for k in to_remove:
                del self._cache[k]
        
        expire_time = time.time() + ttl_seconds
        self._cache[key] = (value, expire_time)
        return True
    
    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None
    
    async def clear_pattern(self, pattern: str) -> int:
        import fnmatch
        keys_to_delete = [k for k in self._cache if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)
    
    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "backend": "in_memory",
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total * 100, 2) if total > 0 else 0,
        }
    
    async def health_check(self) -> bool:
        return True


class RedisCacheBackend(CacheBackend):
    """
    Redis-based cache for production deployments.
    
    Supports multiple instances and horizontal scaling.
    """
    
    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis: Optional[Any] = None
        self._connected = False
        self._hits = 0
        self._misses = 0
    
    async def _get_redis(self):
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                self._connected = True
                logger.info("redis_connected", url=self._redis_url[:20] + "...")
            except Exception as e:
                logger.error("redis_connection_failed", error=str(e)[:200])
                raise
        return self._redis
    
    async def get(self, key: str) -> Optional[str]:
        try:
            redis = await self._get_redis()
            value = await redis.get(f"perplex:{key}")
            if value is None:
                self._misses += 1
            else:
                self._hits += 1
            return value
        except Exception as e:
            logger.error("redis_get_error", key=key, error=str(e)[:100])
            self._misses += 1
            return None
    
    async def set(self, key: str, value: str, ttl_seconds: int = 300) -> bool:
        try:
            redis = await self._get_redis()
            await redis.setex(f"perplex:{key}", ttl_seconds, value)
            return True
        except Exception as e:
            logger.error("redis_set_error", key=key, error=str(e)[:100])
            return False
    
    async def delete(self, key: str) -> bool:
        try:
            redis = await self._get_redis()
            result = await redis.delete(f"perplex:{key}")
            return result > 0
        except Exception as e:
            logger.error("redis_delete_error", key=key, error=str(e)[:100])
            return False
    
    async def exists(self, key: str) -> bool:
        try:
            redis = await self._get_redis()
            return await redis.exists(f"perplex:{key}") > 0
        except Exception as e:
            logger.error("redis_exists_error", key=key, error=str(e)[:100])
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        try:
            redis = await self._get_redis()
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=f"perplex:{pattern}")
                if keys:
                    deleted += await redis.delete(*keys)
                if cursor == 0:
                    break
            return deleted
        except Exception as e:
            logger.error("redis_clear_pattern_error", pattern=pattern, error=str(e)[:100])
            return 0
    
    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "backend": "redis",
            "connected": self._connected,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total * 100, 2) if total > 0 else 0,
        }
    
    async def health_check(self) -> bool:
        try:
            redis = await self._get_redis()
            await redis.ping()
            return True
        except Exception:
            return False


class UnifiedCache:
    """
    Unified cache that automatically uses Redis if available, 
    falls back to in-memory otherwise.
    """
    
    def __init__(self):
        self._backend: Optional[CacheBackend] = None
        self._initialized = False
    
    def _get_backend(self) -> CacheBackend:
        if self._backend is None:
            settings = get_settings()
            if settings.redis_url:
                try:
                    self._backend = RedisCacheBackend(settings.redis_url)
                    logger.info("cache_backend_redis")
                except Exception as e:
                    logger.warning("redis_unavailable_fallback_memory", error=str(e)[:100])
                    self._backend = InMemoryCacheBackend()
            else:
                self._backend = InMemoryCacheBackend()
                logger.info("cache_backend_memory", reason="REDIS_URL not configured")
        return self._backend
    
    async def get(self, key: str) -> Optional[str]:
        return await self._get_backend().get(key)
    
    async def set(self, key: str, value: str, ttl_seconds: int = 300) -> bool:
        return await self._get_backend().set(key, value, ttl_seconds)
    
    async def delete(self, key: str) -> bool:
        return await self._get_backend().delete(key)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize JSON value."""
        value = await self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    
    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Serialize and set JSON value."""
        try:
            json_str = json.dumps(value, default=str)
            return await self.set(key, json_str, ttl_seconds)
        except (TypeError, ValueError) as e:
            logger.error("cache_set_json_error", key=key, error=str(e)[:100])
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        return await self._get_backend().clear_pattern(pattern)
    
    def stats(self) -> dict[str, Any]:
        return self._get_backend().stats()
    
    async def health_check(self) -> bool:
        return await self._get_backend().health_check()


# Global cache instance
cache = UnifiedCache()


# =============================================================================
# Caching Decorators
# =============================================================================

def cached(
    key_prefix: str,
    ttl_seconds: int = 300,
    key_builder: Optional[Callable[..., str]] = None,
):
    """
    Decorator to cache function results.
    
    Usage:
        @cached("player_props", ttl_seconds=60)
        async def get_player_props(sport_id: int):
            ...
        
        @cached("parlay", key_builder=lambda sport, min_ev: f"{sport}:{min_ev}")
        async def get_parlays(sport: str, min_ev: float):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Build cache key
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                # Default: use all args
                key_parts = [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
                key_suffix = ":".join(key_parts) if key_parts else "default"
            
            cache_key = f"{key_prefix}:{key_suffix}"
            
            # Try cache first
            cached_value = await cache.get_json(cache_key)
            if cached_value is not None:
                logger.debug("cache_hit", key=cache_key)
                return cached_value
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            if result is not None:
                await cache.set_json(cache_key, result, ttl_seconds)
                logger.debug("cache_set", key=cache_key, ttl=ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


def cache_invalidator(patterns: list[str]):
    """
    Decorator to invalidate cache after function execution.
    
    Usage:
        @cache_invalidator(["player_props:*", "parlay:*"])
        async def refresh_data():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            result = await func(*args, **kwargs)
            
            # Invalidate cache patterns
            for pattern in patterns:
                deleted = await cache.clear_pattern(pattern)
                if deleted > 0:
                    logger.info("cache_invalidated", pattern=pattern, count=deleted)
            
            return result
        
        return wrapper
    return decorator
