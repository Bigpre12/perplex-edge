"""
Stats Service - Orchestration layer for player statistics.

Sources:
- ESPN box scores (primary - free)
- OddsPapi historical (for baselines)
- Database (for cached stats)

All responses include provenance (source, last_updated, season).
"""

import logging
from datetime import datetime, timezone, date, timedelta
from typing import Any, Optional, List

from app.data.base import DataResponse, CacheType
from app.data.cache import CacheManager, get_cache_manager
from app.data.providers.espn import ESPNProvider
from app.data.providers.oddspapi import OddsPapiProvider
from app.services.season_helper import get_current_season_label, get_season_start_for_sport_id

logger = logging.getLogger(__name__)


class StatsService:
    """
    Orchestrates player stats fetching with caching.
    
    Features:
    - Box scores from ESPN
    - Historical data from OddsPapi
    - Season-aware filtering
    
    Usage:
        service = StatsService()
        response = await service.get_player_game_logs("basketball_nba", "player_123")
    """
    
    def __init__(
        self,
        cache: Optional[CacheManager] = None,
    ):
        self.cache = cache or get_cache_manager()
    
    async def get_box_score(
        self,
        sport_key: str,
        game_id: str,
        force_refresh: bool = False,
    ) -> DataResponse[dict]:
        """
        Get box score for a game.
        
        Args:
            sport_key: Standard sport key
            game_id: ESPN game ID
            force_refresh: Skip cache
        
        Returns:
            DataResponse with box score data
        """
        cache_key = f"boxscore:{sport_key}:{game_id}"
        season = get_current_season_label(sport_key)
        
        # Check historical cache (box scores don't change once final)
        if not force_refresh:
            cached = await self.cache.get_historical(cache_key)
            if cached is not None:
                return DataResponse.from_cache(
                    data=cached["data"],
                    source=cached["source"],
                    season=season,
                    last_updated=datetime.fromisoformat(cached["last_updated"]),
                    cache_type=CacheType.HISTORICAL,
                )
        
        # Fetch from ESPN
        try:
            async with ESPNProvider() as provider:
                boxscore = await provider.fetch_boxscore(sport_key, game_id)
                
                if boxscore:
                    await self._cache_historical(cache_key, boxscore, "espn")
                    return DataResponse.fresh(data=boxscore, source="espn", season=season)
        except Exception as e:
            logger.error(f"[StatsService] Box score fetch error: {e}")
        
        return DataResponse.fresh(data={}, source="none", season=season)
    
    async def get_historical_odds(
        self,
        sport_key: str,
        game_date: date,
        market: str = "spreads",
        force_refresh: bool = False,
    ) -> DataResponse[List[dict]]:
        """
        Get historical odds for backtesting/analysis.
        
        Args:
            sport_key: Standard sport key
            game_date: Date to fetch
            market: Market type
            force_refresh: Skip cache
        
        Returns:
            DataResponse with historical odds
        """
        cache_key = f"historical_odds:{sport_key}:{game_date.isoformat()}:{market}"
        season = get_current_season_label(sport_key)
        
        # Check historical cache
        if not force_refresh:
            cached = await self.cache.get_historical(cache_key)
            if cached is not None:
                return DataResponse.from_cache(
                    data=cached["data"],
                    source=cached["source"],
                    season=season,
                    last_updated=datetime.fromisoformat(cached["last_updated"]),
                    cache_type=CacheType.HISTORICAL,
                )
        
        # Fetch from OddsPapi
        try:
            async with OddsPapiProvider() as provider:
                odds = await provider.fetch_historical_odds(sport_key, game_date, market)
                
                if odds:
                    await self._cache_historical(cache_key, odds, "oddspapi")
                    return DataResponse.fresh(data=odds, source="oddspapi", season=season)
        except Exception as e:
            logger.error(f"[StatsService] Historical odds fetch error: {e}")
        
        return DataResponse.fresh(data=[], source="none", season=season)
    
    async def _cache_historical(self, key: str, data: Any, source: str) -> None:
        """Cache historical data (24 hour TTL)."""
        cache_value = {
            "data": data,
            "source": source,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        await self.cache.set_historical(key, cache_value, source=source)


# Singleton
_stats_service: Optional[StatsService] = None


def get_stats_service() -> StatsService:
    """Get the global StatsService instance."""
    global _stats_service
    if _stats_service is None:
        _stats_service = StatsService()
    return _stats_service
