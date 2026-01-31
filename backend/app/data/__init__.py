"""
Unified Data Layer for Perplex Engine.

This module provides a clean, unified architecture for all external data:
- Providers: API clients only (no DB operations)
- Services: Orchestration with caching and fallback
- Storage: Unified cache management

Architecture:
    API Layer → Services → Cache → Providers → External APIs
                    ↓
              Repositories → Database
"""

from app.data.cache import CacheManager, CacheType, get_cache_manager
from app.data.base import (
    BaseProvider,
    ProviderError,
    RateLimitError,
    DataResponse,
)

__all__ = [
    # Cache
    "CacheManager",
    "CacheType",
    "get_cache_manager",
    # Base
    "BaseProvider",
    "ProviderError",
    "RateLimitError",
    "DataResponse",
]
