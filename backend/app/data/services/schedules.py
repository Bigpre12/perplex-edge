"""
Schedule Service - Orchestration layer for game schedules.

Primary source: ESPN (free, reliable schedules)
Fallback: TheOddsAPI games endpoint

All responses include provenance (source, last_updated, season).
"""

import logging
from datetime import datetime, timezone, date
from typing import Any, Optional, List

from app.data.base import DataResponse, CacheType
from app.data.cache import CacheManager, get_cache_manager
from app.data.providers.espn import ESPNProvider
from app.data.providers.odds_api import OddsAPIProvider
from app.services.season_helper import get_current_season_label

logger = logging.getLogger(__name__)


class ScheduleService:
    """
    Orchestrates schedule fetching with caching.
    
    Primary: ESPN (free, reliable)
    Fallback: TheOddsAPI
    
    Usage:
        service = ScheduleService()
        response = await service.get_today_games("basketball_nba")
    """
    
    def __init__(
        self,
        cache: Optional[CacheManager] = None,
    ):
        self.cache = cache or get_cache_manager()
    
    async def get_today_games(
        self,
        sport_key: str,
        force_refresh: bool = False,
    ) -> DataResponse[List[dict]]:
        """
        Get today's games for a sport.
        
        Args:
            sport_key: Standard sport key
            force_refresh: Skip cache
        
        Returns:
            DataResponse with games list
        """
        return await self.get_games(sport_key, date.today(), force_refresh)
    
    async def get_games(
        self,
        sport_key: str,
        game_date: date,
        force_refresh: bool = False,
    ) -> DataResponse[List[dict]]:
        """
        Get games for a specific date.
        
        Cascade:
        1. Cache (1 hour TTL)
        2. ESPN (primary - free)
        3. TheOddsAPI (fallback)
        
        Args:
            sport_key: Standard sport key
            game_date: Date to fetch
            force_refresh: Skip cache
        
        Returns:
            DataResponse with games list
        """
        cache_key = f"schedule:{sport_key}:{game_date.isoformat()}"
        season = get_current_season_label(sport_key)
        
        # Check cache (longer TTL for schedules - 1 hour)
        if not force_refresh:
            cached = await self.cache.get_live(cache_key)
            if cached is not None:
                return DataResponse.from_cache(
                    data=cached["data"],
                    source=cached["source"],
                    season=season,
                    last_updated=datetime.fromisoformat(cached["last_updated"]),
                    cache_type=CacheType.LIVE,
                )
        
        # Try ESPN (primary - free)
        try:
            async with ESPNProvider() as provider:
                games = await provider.fetch_games(sport_key, game_date)
                
                if games:
                    await self._cache_schedule(cache_key, games, "espn")
                    logger.info(f"[ScheduleService] Fetched {len(games)} games from ESPN for {sport_key}")
                    return DataResponse.fresh(data=games, source="espn", season=season)
        except Exception as e:
            logger.error(f"[ScheduleService] ESPN error: {e}")
        
        # Try OddsAPI (fallback)
        try:
            async with OddsAPIProvider() as provider:
                games = await provider.fetch_games(sport_key)
                
                # Filter to requested date
                games_on_date = [
                    g for g in games
                    if g.get("commence_time", "").startswith(game_date.isoformat())
                ]
                
                if games_on_date:
                    await self._cache_schedule(cache_key, games_on_date, "oddsapi")
                    logger.info(f"[ScheduleService] Fetched {len(games_on_date)} games from OddsAPI for {sport_key}")
                    return DataResponse.fresh(data=games_on_date, source="oddsapi", season=season)
        except Exception as e:
            logger.error(f"[ScheduleService] OddsAPI error: {e}")
        
        # No data
        logger.warning(f"[ScheduleService] No schedule data for {sport_key} on {game_date}")
        return DataResponse.fresh(data=[], source="none", season=season)
    
    async def _cache_schedule(self, key: str, data: Any, source: str) -> None:
        """Cache schedule data with 1 hour TTL."""
        cache_value = {
            "data": data,
            "source": source,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        # Schedules can be cached longer (1 hour)
        await self.cache.set_live(key, cache_value, source=source, ttl=3600)


# Singleton
_schedule_service: Optional[ScheduleService] = None


def get_schedule_service() -> ScheduleService:
    """Get the global ScheduleService instance."""
    global _schedule_service
    if _schedule_service is None:
        _schedule_service = ScheduleService()
    return _schedule_service
