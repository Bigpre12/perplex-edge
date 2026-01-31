"""
Unified Cache Manager for the data layer.

Provides explicit separation between:
- Live cache: Short TTL (5-10 min) for odds and real-time data
- Historical cache: Long TTL (24h+) for stats, baselines, hit rates
- Reference cache: Very long TTL (1 week+) for static data (teams, players)

Design principles:
- All cached items include metadata (cached_at, expires_at, source)
- Explicit cache type prevents mixing live vs historical
- Thread-safe with async support
- Simple in-memory implementation (swap for Redis later)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Generic, Dict

logger = logging.getLogger(__name__)


# =============================================================================
# Cache Types and Configuration
# =============================================================================

class CacheType(Enum):
    """Type of cache with different TTLs."""
    LIVE = "live"           # 5 minutes - odds, scores
    HISTORICAL = "historical"  # 24 hours - stats, baselines
    REFERENCE = "reference"    # 7 days - teams, players, static data


# Default TTLs in seconds
DEFAULT_TTLS = {
    CacheType.LIVE: 300,        # 5 minutes
    CacheType.HISTORICAL: 86400,  # 24 hours
    CacheType.REFERENCE: 604800,  # 7 days
}


T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """A cached item with metadata."""
    value: T
    cached_at: datetime
    expires_at: datetime
    source: str
    cache_type: CacheType
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return (datetime.now(timezone.utc) - self.cached_at).total_seconds()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for debugging."""
        return {
            "cached_at": self.cached_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "source": self.source,
            "cache_type": self.cache_type.value,
            "is_expired": self.is_expired,
            "age_seconds": self.age_seconds,
        }


# =============================================================================
# Cache Manager
# =============================================================================

class CacheManager:
    """
    Unified cache manager with explicit live vs historical separation.
    
    Usage:
        cache = CacheManager()
        
        # Store live odds (5 min TTL)
        await cache.set_live("nba:odds", odds_data, source="oddsapi")
        
        # Store historical stats (24h TTL)
        await cache.set_historical("player:123:stats", stats, source="espn")
        
        # Get with fallback
        data = await cache.get_live("nba:odds")
        if data is None:
            data = await fetch_fresh_odds()
            await cache.set_live("nba:odds", data, source="oddsapi")
    """
    
    def __init__(self):
        self._live_cache: Dict[str, CacheEntry] = {}
        self._historical_cache: Dict[str, CacheEntry] = {}
        self._reference_cache: Dict[str, CacheEntry] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def _get_cache(self, cache_type: CacheType) -> Dict[str, CacheEntry]:
        """Get the appropriate cache dict."""
        if cache_type == CacheType.LIVE:
            return self._live_cache
        elif cache_type == CacheType.HISTORICAL:
            return self._historical_cache
        else:
            return self._reference_cache
    
    def _get_lock(self, key: str) -> asyncio.Lock:
        """Get or create a lock for a key."""
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]
    
    # -------------------------------------------------------------------------
    # Live Cache (5 min TTL) - Odds, scores, real-time data
    # -------------------------------------------------------------------------
    
    async def get_live(self, key: str) -> Optional[Any]:
        """
        Get from live cache.
        
        Returns None if not found or expired.
        """
        return await self._get(CacheType.LIVE, key)
    
    async def set_live(
        self,
        key: str,
        value: Any,
        source: str = "unknown",
        ttl: int = None,
    ) -> None:
        """
        Store in live cache (default 5 min TTL).
        """
        ttl = ttl or DEFAULT_TTLS[CacheType.LIVE]
        await self._set(CacheType.LIVE, key, value, source, ttl)
    
    async def get_live_or_fetch(
        self,
        key: str,
        fetch_fn: Callable[[], Any],
        source: str = "unknown",
        ttl: int = None,
    ) -> Any:
        """
        Get from live cache, or fetch and cache if missing/expired.
        """
        ttl = ttl or DEFAULT_TTLS[CacheType.LIVE]
        return await self._get_or_fetch(CacheType.LIVE, key, fetch_fn, source, ttl)
    
    # -------------------------------------------------------------------------
    # Historical Cache (24h TTL) - Stats, baselines, hit rates
    # -------------------------------------------------------------------------
    
    async def get_historical(self, key: str) -> Optional[Any]:
        """
        Get from historical cache.
        
        Returns None if not found or expired.
        """
        return await self._get(CacheType.HISTORICAL, key)
    
    async def set_historical(
        self,
        key: str,
        value: Any,
        source: str = "unknown",
        ttl: int = None,
    ) -> None:
        """
        Store in historical cache (default 24h TTL).
        """
        ttl = ttl or DEFAULT_TTLS[CacheType.HISTORICAL]
        await self._set(CacheType.HISTORICAL, key, value, source, ttl)
    
    async def get_historical_or_fetch(
        self,
        key: str,
        fetch_fn: Callable[[], Any],
        source: str = "unknown",
        ttl: int = None,
    ) -> Any:
        """
        Get from historical cache, or fetch and cache if missing/expired.
        """
        ttl = ttl or DEFAULT_TTLS[CacheType.HISTORICAL]
        return await self._get_or_fetch(CacheType.HISTORICAL, key, fetch_fn, source, ttl)
    
    # -------------------------------------------------------------------------
    # Reference Cache (7 day TTL) - Teams, players, static data
    # -------------------------------------------------------------------------
    
    async def get_reference(self, key: str) -> Optional[Any]:
        """
        Get from reference cache.
        
        Returns None if not found or expired.
        """
        return await self._get(CacheType.REFERENCE, key)
    
    async def set_reference(
        self,
        key: str,
        value: Any,
        source: str = "unknown",
        ttl: int = None,
    ) -> None:
        """
        Store in reference cache (default 7 day TTL).
        """
        ttl = ttl or DEFAULT_TTLS[CacheType.REFERENCE]
        await self._set(CacheType.REFERENCE, key, value, source, ttl)
    
    # -------------------------------------------------------------------------
    # Internal Implementation
    # -------------------------------------------------------------------------
    
    async def _get(self, cache_type: CacheType, key: str) -> Optional[Any]:
        """Get from specified cache."""
        cache = self._get_cache(cache_type)
        entry = cache.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired:
            # Remove expired entry
            cache.pop(key, None)
            logger.debug(f"Cache miss (expired): {cache_type.value}:{key}")
            return None
        
        logger.debug(f"Cache hit: {cache_type.value}:{key} (age: {entry.age_seconds:.1f}s)")
        return entry.value
    
    async def _set(
        self,
        cache_type: CacheType,
        key: str,
        value: Any,
        source: str,
        ttl: int,
    ) -> None:
        """Store in specified cache."""
        cache = self._get_cache(cache_type)
        now = datetime.now(timezone.utc)
        
        entry = CacheEntry(
            value=value,
            cached_at=now,
            expires_at=now + timedelta(seconds=ttl),
            source=source,
            cache_type=cache_type,
        )
        cache[key] = entry
        logger.debug(f"Cache set: {cache_type.value}:{key} (TTL: {ttl}s, source: {source})")
    
    async def _get_or_fetch(
        self,
        cache_type: CacheType,
        key: str,
        fetch_fn: Callable[[], Any],
        source: str,
        ttl: int,
    ) -> Any:
        """Get from cache or fetch if missing."""
        # Check cache first
        value = await self._get(cache_type, key)
        if value is not None:
            return value
        
        # Fetch with lock to prevent thundering herd
        async with self._get_lock(key):
            # Double-check after acquiring lock
            value = await self._get(cache_type, key)
            if value is not None:
                return value
            
            # Fetch fresh data
            value = await fetch_fn() if asyncio.iscoroutinefunction(fetch_fn) else fetch_fn()
            
            # Cache result
            if value is not None:
                await self._set(cache_type, key, value, source, ttl)
            
            return value
    
    # -------------------------------------------------------------------------
    # Cache Management
    # -------------------------------------------------------------------------
    
    def get_entry_metadata(self, cache_type: CacheType, key: str) -> Optional[dict]:
        """Get metadata for a cache entry (for debugging)."""
        cache = self._get_cache(cache_type)
        entry = cache.get(key)
        return entry.to_dict() if entry else None
    
    def invalidate(self, cache_type: CacheType, key: str) -> bool:
        """
        Invalidate a specific cache entry.
        
        Returns True if entry was found and removed.
        """
        cache = self._get_cache(cache_type)
        if key in cache:
            del cache[key]
            logger.debug(f"Cache invalidated: {cache_type.value}:{key}")
            return True
        return False
    
    def invalidate_prefix(self, cache_type: CacheType, prefix: str) -> int:
        """
        Invalidate all entries with a key prefix.
        
        Returns count of invalidated entries.
        """
        cache = self._get_cache(cache_type)
        keys_to_remove = [k for k in cache.keys() if k.startswith(prefix)]
        for key in keys_to_remove:
            del cache[key]
        logger.debug(f"Cache invalidated by prefix: {cache_type.value}:{prefix}* ({len(keys_to_remove)} entries)")
        return len(keys_to_remove)
    
    def clear_live(self) -> int:
        """Clear all live cache entries. Returns count cleared."""
        count = len(self._live_cache)
        self._live_cache.clear()
        logger.info(f"Live cache cleared ({count} entries)")
        return count
    
    def clear_historical(self) -> int:
        """Clear all historical cache entries. Returns count cleared."""
        count = len(self._historical_cache)
        self._historical_cache.clear()
        logger.info(f"Historical cache cleared ({count} entries)")
        return count
    
    def clear_all(self) -> int:
        """Clear all caches. Returns total count cleared."""
        total = len(self._live_cache) + len(self._historical_cache) + len(self._reference_cache)
        self._live_cache.clear()
        self._historical_cache.clear()
        self._reference_cache.clear()
        logger.info(f"All caches cleared ({total} entries)")
        return total
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "live": {
                "count": len(self._live_cache),
                "keys": list(self._live_cache.keys())[:10],  # First 10 for debugging
            },
            "historical": {
                "count": len(self._historical_cache),
                "keys": list(self._historical_cache.keys())[:10],
            },
            "reference": {
                "count": len(self._reference_cache),
                "keys": list(self._reference_cache.keys())[:10],
            },
        }
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries from all caches. Returns count removed."""
        removed = 0
        for cache_type in CacheType:
            cache = self._get_cache(cache_type)
            expired_keys = [k for k, v in cache.items() if v.is_expired]
            for key in expired_keys:
                del cache[key]
            removed += len(expired_keys)
        
        if removed > 0:
            logger.debug(f"Cache cleanup: removed {removed} expired entries")
        return removed
    
    async def start_cleanup_task(self, interval_seconds: int = 60):
        """Start background task to periodically clean expired entries."""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(interval_seconds)
                await self.cleanup_expired()
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    def stop_cleanup_task(self):
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None


# =============================================================================
# Singleton Instance
# =============================================================================

_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def reset_cache_manager():
    """Reset the global cache manager (for testing)."""
    global _cache_manager
    if _cache_manager:
        _cache_manager.clear_all()
    _cache_manager = None
