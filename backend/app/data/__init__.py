"""
Unified Data Layer for Perplex Engine.

This module provides a clean, unified architecture for all external data:
- Providers: API clients only (no DB operations)
- Services: Orchestration with caching and fallback
- Repositories: Database CRUD operations
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

# Repositories
from app.data.repositories import (
    BaseRepository,
    GameRepository,
    LineRepository,
    PlayerRepository,
    PickRepository,
)

# Services
from app.data.services.odds import OddsService, get_odds_service
from app.data.services.schedules import ScheduleService, get_schedule_service
from app.data.services.stats import StatsService, get_stats_service
from app.data.services.injuries import InjuryService, get_injury_service

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
    # Repositories
    "BaseRepository",
    "GameRepository",
    "LineRepository",
    "PlayerRepository",
    "PickRepository",
    # Services
    "OddsService",
    "get_odds_service",
    "ScheduleService",
    "get_schedule_service",
    "StatsService",
    "get_stats_service",
    "InjuryService",
    "get_injury_service",
]
