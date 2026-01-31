"""
Injury Service - Orchestration layer for injury data.

Features:
- Injury status from ESPN (free)
- Injury filtering for props/parlays
- Caching with reasonable TTL (injuries don't change every second)

All responses include provenance (source, last_updated, season).
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional, List, Set

from app.data.base import DataResponse, CacheType
from app.data.cache import CacheManager, get_cache_manager
from app.data.providers.espn import ESPNProvider
from app.services.season_helper import get_current_season_label

logger = logging.getLogger(__name__)


# Injury statuses that should be filtered from props/parlays
EXCLUDED_STATUSES = {"OUT", "DOUBTFUL", "IR", "SUSPENDED", "DNP"}

# Statuses that should show a warning
WARNING_STATUSES = {"QUESTIONABLE", "GTD", "PROBABLE"}


class InjuryService:
    """
    Orchestrates injury data fetching and provides filtering utilities.
    
    Features:
    - Fetch injury reports by sport
    - Filter props to exclude injured players
    - Provide injury warnings for questionable players
    
    Usage:
        service = InjuryService()
        
        # Get all injuries
        response = await service.get_injuries("basketball_nba")
        
        # Filter props, removing injured players
        filtered_props = await service.filter_injured_props(
            "basketball_nba",
            props_list,
            exclude_out=True,
            warn_questionable=True,
        )
    """
    
    def __init__(
        self,
        cache: Optional[CacheManager] = None,
    ):
        self.cache = cache or get_cache_manager()
    
    async def get_injuries(
        self,
        sport_key: str,
        force_refresh: bool = False,
    ) -> DataResponse[List[dict]]:
        """
        Get injury report for a sport.
        
        Args:
            sport_key: Standard sport key
            force_refresh: Skip cache
        
        Returns:
            DataResponse with injury list
        """
        cache_key = f"injuries:{sport_key}"
        season = get_current_season_label(sport_key)
        
        # Check cache (injuries cached for 30 min)
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
        
        # Fetch from ESPN
        try:
            async with ESPNProvider() as provider:
                injuries = await provider.fetch_injuries(sport_key)
                
                if injuries:
                    await self._cache_injuries(cache_key, injuries, "espn")
                    logger.info(f"[InjuryService] Fetched {len(injuries)} injuries from ESPN for {sport_key}")
                    return DataResponse.fresh(data=injuries, source="espn", season=season)
        except Exception as e:
            logger.error(f"[InjuryService] ESPN injury fetch error: {e}")
        
        # Return empty if no data
        return DataResponse.fresh(data=[], source="none", season=season)
    
    async def get_injured_player_ids(
        self,
        sport_key: str,
        exclude_statuses: Set[str] = None,
    ) -> Set[str]:
        """
        Get set of player IDs that are injured/out.
        
        Args:
            sport_key: Standard sport key
            exclude_statuses: Statuses to consider "injured" (default: EXCLUDED_STATUSES)
        
        Returns:
            Set of player IDs that should be excluded
        """
        if exclude_statuses is None:
            exclude_statuses = EXCLUDED_STATUSES
        
        response = await self.get_injuries(sport_key)
        injured_ids = set()
        
        for injury in response.data:
            status = injury.get("status", "").upper()
            if status in exclude_statuses:
                player_id = injury.get("player_id") or injury.get("id")
                if player_id:
                    injured_ids.add(str(player_id))
        
        return injured_ids
    
    async def filter_injured_props(
        self,
        sport_key: str,
        props: List[dict],
        player_id_key: str = "player_id",
        exclude_out: bool = True,
        warn_questionable: bool = True,
    ) -> List[dict]:
        """
        Filter props list to remove injured players.
        
        Args:
            sport_key: Standard sport key
            props: List of prop dictionaries
            player_id_key: Key for player ID in prop dict
            exclude_out: Remove OUT/IR players entirely
            warn_questionable: Add warning flag for QUESTIONABLE players
        
        Returns:
            Filtered props list with injury info added
        """
        if not props:
            return props
        
        # Get injury data
        response = await self.get_injuries(sport_key)
        
        # Build lookup by player ID
        injury_by_player: dict[str, dict] = {}
        for injury in response.data:
            player_id = injury.get("player_id") or injury.get("id")
            if player_id:
                injury_by_player[str(player_id)] = injury
        
        # Filter props
        filtered = []
        for prop in props:
            player_id = str(prop.get(player_id_key, ""))
            injury = injury_by_player.get(player_id)
            
            if injury:
                status = injury.get("status", "").upper()
                
                # Skip excluded statuses
                if exclude_out and status in EXCLUDED_STATUSES:
                    logger.debug(f"[InjuryService] Excluding prop for injured player {player_id} ({status})")
                    continue
                
                # Add warning for questionable
                if warn_questionable and status in WARNING_STATUSES:
                    prop = {**prop, "injury_warning": True, "injury_status": status}
            
            filtered.append(prop)
        
        excluded_count = len(props) - len(filtered)
        if excluded_count > 0:
            logger.info(f"[InjuryService] Filtered {excluded_count} props due to injuries")
        
        return filtered
    
    async def enrich_with_injuries(
        self,
        sport_key: str,
        items: List[dict],
        player_id_key: str = "player_id",
    ) -> List[dict]:
        """
        Enrich a list of items with injury status info.
        
        Adds injury_status and injury_detail fields to items where applicable.
        
        Args:
            sport_key: Standard sport key
            items: List of dicts to enrich
            player_id_key: Key for player ID in items
        
        Returns:
            Items with injury info added
        """
        response = await self.get_injuries(sport_key)
        
        # Build lookup
        injury_by_player: dict[str, dict] = {}
        for injury in response.data:
            player_id = injury.get("player_id") or injury.get("id")
            if player_id:
                injury_by_player[str(player_id)] = injury
        
        # Enrich items
        enriched = []
        for item in items:
            player_id = str(item.get(player_id_key, ""))
            injury = injury_by_player.get(player_id)
            
            if injury:
                item = {
                    **item,
                    "injury_status": injury.get("status"),
                    "injury_detail": injury.get("injury") or injury.get("description"),
                    "injury_expected_return": injury.get("expected_return"),
                }
            else:
                item = {**item, "injury_status": None}
            
            enriched.append(item)
        
        return enriched
    
    async def _cache_injuries(self, key: str, data: Any, source: str) -> None:
        """Cache injuries with 30 min TTL."""
        cache_value = {
            "data": data,
            "source": source,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        # Injuries cached for 30 minutes
        await self.cache.set_live(key, cache_value, source=source, ttl=1800)


# Singleton
_injury_service: Optional[InjuryService] = None


def get_injury_service() -> InjuryService:
    """Get the global InjuryService instance."""
    global _injury_service
    if _injury_service is None:
        _injury_service = InjuryService()
    return _injury_service
