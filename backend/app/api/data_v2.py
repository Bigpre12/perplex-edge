"""
Data Layer V2 API Endpoints.

These endpoints use the new unified data layer with:
- Proper caching (live vs historical)
- Automatic fallback
- Response envelopes (source, last_updated, season)

Eventually these will replace the legacy endpoints.
"""

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from app.data.services.odds import get_odds_service
from app.data.services.schedules import get_schedule_service
from app.data.services.stats import get_stats_service
from app.data.services.injuries import get_injury_service
from app.data.cache import get_cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2", tags=["Data Layer V2"])


# =============================================================================
# Odds Endpoints
# =============================================================================

@router.get("/odds/{sport_key}")
async def get_odds(
    sport_key: str,
    include_props: bool = Query(False, description="Include player props"),
    force_refresh: bool = Query(False, description="Skip cache"),
):
    """
    Get live odds for a sport.
    
    Response includes provenance:
    - source: Where data came from (oddsapi, betstack, espn, stub)
    - last_updated: When data was fetched
    - season: Current season label
    - stale: True if from cache after provider failure
    """
    service = get_odds_service()
    response = await service.get_live_odds(
        sport_key,
        include_props=include_props,
        force_refresh=force_refresh,
    )
    
    return {
        "data": response.data,
        "meta": {
            "source": response.source,
            "last_updated": response.last_updated.isoformat(),
            "season": response.season,
            "stale": response.stale,
            "cache_type": response.cache_type.value,
        },
        "count": len(response.data) if isinstance(response.data, list) else 1,
    }


@router.get("/props/{sport_key}")
async def get_player_props(
    sport_key: str,
    game_id: Optional[str] = Query(None, description="Specific game ID"),
    force_refresh: bool = Query(False, description="Skip cache"),
):
    """
    Get player props for a sport or specific game.
    
    Note: Fetching all props uses more API credits.
    """
    service = get_odds_service()
    response = await service.get_player_props(
        sport_key,
        game_id=game_id,
        force_refresh=force_refresh,
    )
    
    return {
        "data": response.data,
        "meta": {
            "source": response.source,
            "last_updated": response.last_updated.isoformat(),
            "season": response.season,
        },
        "count": len(response.data) if isinstance(response.data, list) else 1,
    }


# =============================================================================
# Schedule Endpoints
# =============================================================================

@router.get("/schedule/{sport_key}")
async def get_schedule(
    sport_key: str,
    game_date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), default today"),
    force_refresh: bool = Query(False, description="Skip cache"),
):
    """
    Get games for a sport on a specific date.
    
    Primary source: ESPN (free)
    Fallback: TheOddsAPI
    """
    service = get_schedule_service()
    
    if game_date:
        try:
            parsed_date = date.fromisoformat(game_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        parsed_date = date.today()
    
    response = await service.get_games(
        sport_key,
        game_date=parsed_date,
        force_refresh=force_refresh,
    )
    
    return {
        "data": response.data,
        "meta": {
            "source": response.source,
            "last_updated": response.last_updated.isoformat(),
            "season": response.season,
            "date": parsed_date.isoformat(),
        },
        "count": len(response.data),
    }


@router.get("/schedule/{sport_key}/today")
async def get_today_schedule(
    sport_key: str,
    force_refresh: bool = Query(False, description="Skip cache"),
):
    """Get today's games for a sport."""
    service = get_schedule_service()
    response = await service.get_today_games(sport_key, force_refresh=force_refresh)
    
    return {
        "data": response.data,
        "meta": {
            "source": response.source,
            "last_updated": response.last_updated.isoformat(),
            "season": response.season,
            "date": date.today().isoformat(),
        },
        "count": len(response.data),
    }


# =============================================================================
# Injury Endpoints
# =============================================================================

@router.get("/injuries/{sport_key}")
async def get_injuries(
    sport_key: str,
    force_refresh: bool = Query(False, description="Skip cache"),
):
    """
    Get injury report for a sport.
    
    Source: ESPN (free)
    """
    service = get_injury_service()
    response = await service.get_injuries(sport_key, force_refresh=force_refresh)
    
    return {
        "data": response.data,
        "meta": {
            "source": response.source,
            "last_updated": response.last_updated.isoformat(),
            "season": response.season,
        },
        "count": len(response.data),
    }


@router.get("/injuries/{sport_key}/player-ids")
async def get_injured_player_ids(
    sport_key: str,
):
    """
    Get set of injured player IDs (OUT, IR, DOUBTFUL).
    
    Useful for filtering props.
    """
    service = get_injury_service()
    injured_ids = await service.get_injured_player_ids(sport_key)
    
    return {
        "player_ids": list(injured_ids),
        "count": len(injured_ids),
    }


# =============================================================================
# Cache Management
# =============================================================================

@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    cache = get_cache_manager()
    return cache.get_stats()


@router.post("/cache/clear")
async def clear_cache(
    live_only: bool = Query(False, description="Only clear live cache"),
):
    """
    Clear cache.
    
    Use after season changes or data fixes.
    """
    cache = get_cache_manager()
    
    if live_only:
        count = cache.clear_live()
        return {"cleared": "live", "count": count}
    else:
        count = cache.clear_all()
        return {"cleared": "all", "count": count}


# =============================================================================
# Health & Quota
# =============================================================================

@router.get("/quota")
async def get_quota_status():
    """Get API quota status for all providers."""
    service = get_odds_service()
    return service.get_quota_status()
