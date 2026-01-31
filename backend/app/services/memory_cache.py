"""
In-memory cache with TTL for frequently accessed data.

Provides fast access to common queries without hitting the database,
with configurable expiry times for different data types.

Usage:
    from app.services.memory_cache import cache, CacheKey
    
    # Get from cache or fetch
    sports = await cache.get_or_set(
        CacheKey.SPORTS_LIST,
        fetch_sports_from_db,
        ttl_seconds=300,
    )
    
    # Invalidate on update
    cache.invalidate(CacheKey.SPORTS_LIST)
"""

import asyncio
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheKey(str, Enum):
    """Standard cache keys for common data."""
    SPORTS_LIST = "sports:list"
    SPORTS_BY_KEY = "sports:by_key"  # Parameterized: sports:by_key:{key}
    GAMES_TODAY = "games:today"  # Parameterized: games:today:{sport_id}
    PICKS_TODAY = "picks:today"  # Parameterized: picks:today:{sport_id}
    PICKS_100PCT = "picks:100pct"  # Parameterized: picks:100pct:{sport_id}
    SYNC_METADATA = "sync:metadata"
    INJURY_STATUS = "injury:status"  # Parameterized: injury:status:{sport_id}
    PLAYER_INFO = "player:info"  # Parameterized: player:info:{player_id}
    PARLAY_CONFIG = "parlay:config"


# Default TTLs for different data types (in seconds)
DEFAULT_TTLS = {
    CacheKey.SPORTS_LIST: 3600,  # 1 hour - sports rarely change
    CacheKey.SPORTS_BY_KEY: 3600,
    CacheKey.GAMES_TODAY: 120,  # 2 minutes - games can start/end
    CacheKey.PICKS_TODAY: 60,  # 1 minute - picks refresh often
    CacheKey.PICKS_100PCT: 300,  # 5 minutes - historical
    CacheKey.SYNC_METADATA: 30,  # 30 seconds - sync status
    CacheKey.INJURY_STATUS: 300,  # 5 minutes - injuries update less frequently
    CacheKey.PLAYER_INFO: 1800,  # 30 minutes - player data is stable
    CacheKey.PARLAY_CONFIG: 3600,  # 1 hour - config rarely changes
}


@dataclass
class CacheEntry:
    """A single cache entry with value and expiry."""
    value: Any
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hits: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()


class MemoryCache:
    """
    Thread-safe in-memory cache with TTL support.
    
    Features:
    - Configurable TTL per key type
    - Async-safe with locks
    - Background cleanup task
    - Hit/miss statistics
    - Parameterized keys (e.g., games:today:30)
    """
    
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0,
            "expirations": 0,
        }
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def _get_lock(self, key: str) -> asyncio.Lock:
        """Get or create a lock for a specific key."""
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]
    
    def _make_key(self, key: CacheKey | str, *params) -> str:
        """Build a cache key with optional parameters."""
        base = key.value if isinstance(key, CacheKey) else key
        if params:
            return f"{base}:{':'.join(str(p) for p in params)}"
        return base
    
    def _get_default_ttl(self, key: CacheKey | str) -> int:
        """Get default TTL for a key type."""
        if isinstance(key, CacheKey):
            return DEFAULT_TTLS.get(key, 300)
        # For string keys, use prefix matching
        for cache_key, ttl in DEFAULT_TTLS.items():
            if key.startswith(cache_key.value):
                return ttl
        return 300  # Default 5 minutes
    
    async def get(
        self,
        key: CacheKey | str,
        *params,
    ) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key (from CacheKey enum or string)
            *params: Optional parameters to append to key
        
        Returns:
            Cached value or None if not found/expired
        """
        full_key = self._make_key(key, *params)
        
        entry = self._cache.get(full_key)
        if entry is None:
            self._stats["misses"] += 1
            return None
        
        if entry.is_expired:
            self._stats["expirations"] += 1
            del self._cache[full_key]
            return None
        
        entry.hits += 1
        self._stats["hits"] += 1
        return entry.value
    
    async def set(
        self,
        key: CacheKey | str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        *params,
    ) -> None:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live (defaults to key type default)
            *params: Optional parameters to append to key
        """
        full_key = self._make_key(key, *params)
        ttl = ttl_seconds if ttl_seconds is not None else self._get_default_ttl(key)
        
        expires_at = datetime.now(timezone.utc) + asyncio.get_event_loop().time_ns() / 1e9 * 0
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        
        self._cache[full_key] = CacheEntry(
            value=value,
            expires_at=expires_at,
        )
        self._stats["sets"] += 1
    
    async def get_or_set(
        self,
        key: CacheKey | str,
        fetch_fn: Callable[[], Coroutine[Any, Any, T]],
        ttl_seconds: Optional[int] = None,
        *params,
    ) -> T:
        """
        Get from cache or fetch and set if missing.
        
        Thread-safe with per-key locking to prevent thundering herd.
        
        Args:
            key: Cache key
            fetch_fn: Async function to fetch value if not cached
            ttl_seconds: Time to live
            *params: Optional parameters to append to key
        
        Returns:
            Cached or freshly fetched value
        """
        full_key = self._make_key(key, *params)
        
        # Fast path: check cache without lock
        cached = await self.get(key, *params)
        if cached is not None:
            return cached
        
        # Slow path: acquire lock and fetch
        lock = self._get_lock(full_key)
        async with lock:
            # Double-check after acquiring lock
            cached = await self.get(key, *params)
            if cached is not None:
                return cached
            
            # Fetch fresh value
            value = await fetch_fn()
            await self.set(key, value, ttl_seconds, *params)
            return value
    
    def invalidate(self, key: CacheKey | str, *params) -> bool:
        """
        Invalidate a cache entry.
        
        Args:
            key: Cache key to invalidate
            *params: Optional parameters
        
        Returns:
            True if entry was removed, False if not found
        """
        full_key = self._make_key(key, *params)
        
        if full_key in self._cache:
            del self._cache[full_key]
            self._stats["invalidations"] += 1
            return True
        return False
    
    def invalidate_prefix(self, prefix: CacheKey | str) -> int:
        """
        Invalidate all entries matching a prefix.
        
        Useful for invalidating all entries of a type
        (e.g., all "games:today:*" entries).
        
        Args:
            prefix: Key prefix to match
        
        Returns:
            Number of entries invalidated
        """
        prefix_str = prefix.value if isinstance(prefix, CacheKey) else prefix
        
        keys_to_delete = [
            k for k in self._cache.keys()
            if k.startswith(prefix_str)
        ]
        
        for key in keys_to_delete:
            del self._cache[key]
        
        self._stats["invalidations"] += len(keys_to_delete)
        return len(keys_to_delete)
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        self._stats["invalidations"] += count
        return count
    
    async def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        async with self._global_lock:
            expired_keys = [
                k for k, v in self._cache.items()
                if v.is_expired
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            self._stats["expirations"] += len(expired_keys)
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0.0
        
        # Calculate total size (rough estimate)
        entry_count = len(self._cache)
        
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "sets": self._stats["sets"],
            "invalidations": self._stats["invalidations"],
            "expirations": self._stats["expirations"],
            "hit_rate_pct": round(hit_rate, 2),
            "entry_count": entry_count,
        }
    
    def get_entries_info(self) -> list[dict[str, Any]]:
        """
        Get info about all cache entries.
        
        Returns:
            List of entry info dicts
        """
        entries = []
        now = datetime.now(timezone.utc)
        
        for key, entry in self._cache.items():
            entries.append({
                "key": key,
                "age_seconds": round(entry.age_seconds, 1),
                "expires_in_seconds": round((entry.expires_at - now).total_seconds(), 1),
                "is_expired": entry.is_expired,
                "hits": entry.hits,
            })
        
        return sorted(entries, key=lambda x: x["hits"], reverse=True)
    
    async def start_cleanup_task(self, interval_seconds: int = 60) -> None:
        """
        Start background cleanup task.
        
        Args:
            interval_seconds: How often to run cleanup
        """
        if self._cleanup_task is not None:
            return
        
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(interval_seconds)
                    await self.cleanup_expired()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info(f"Started cache cleanup task (interval: {interval_seconds}s)")
    
    async def stop_cleanup_task(self) -> None:
        """Stop the background cleanup task."""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Stopped cache cleanup task")


# Global cache instance
cache = MemoryCache()


# =============================================================================
# Convenience Functions for Common Cache Operations
# =============================================================================

async def get_cached_sports(fetch_fn: Callable):
    """Get sports list from cache or fetch."""
    return await cache.get_or_set(CacheKey.SPORTS_LIST, fetch_fn)


async def get_cached_games_today(sport_id: int, fetch_fn: Callable):
    """Get today's games from cache or fetch."""
    return await cache.get_or_set(CacheKey.GAMES_TODAY, fetch_fn, None, sport_id)


async def get_cached_picks_today(sport_id: int, fetch_fn: Callable):
    """Get today's picks from cache or fetch."""
    return await cache.get_or_set(CacheKey.PICKS_TODAY, fetch_fn, None, sport_id)


async def invalidate_sport_data(sport_id: int) -> int:
    """Invalidate all cached data for a sport after sync."""
    count = 0
    count += cache.invalidate(CacheKey.GAMES_TODAY, sport_id) and 1 or 0
    count += cache.invalidate(CacheKey.PICKS_TODAY, sport_id) and 1 or 0
    count += cache.invalidate(CacheKey.PICKS_100PCT, sport_id) and 1 or 0
    count += cache.invalidate(CacheKey.INJURY_STATUS, sport_id) and 1 or 0
    cache.invalidate(CacheKey.SYNC_METADATA)
    return count


async def invalidate_all_picks():
    """Invalidate all picks caches after a picks generation."""
    return cache.invalidate_prefix(CacheKey.PICKS_TODAY) + \
           cache.invalidate_prefix(CacheKey.PICKS_100PCT)
