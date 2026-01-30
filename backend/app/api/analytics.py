"""Analytics API endpoints for historical performance data."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.stats_calculator import (
    calculate_real_hit_rates,
    calculate_ev_performance,
    calculate_odds_trends,
    get_analytics_dashboard,
)
from app.services.etl_historical import (
    sync_historical_odds,
    sync_game_results,
    settle_picks,
    run_full_historical_sync,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


# =============================================================================
# Hit Rate Endpoints
# =============================================================================

@router.get("/hit-rates/{player_id}")
async def get_player_hit_rates(
    player_id: int,
    stat_type: Optional[str] = Query(None, description="Filter by stat type (PTS, REB, AST, etc.)"),
    games: int = Query(10, ge=1, le=100, description="Number of recent games to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get actual hit rates for a player from settled picks.
    
    Calculates hit rates based on real PickResult data.
    """
    try:
        result = await calculate_real_hit_rates(
            db,
            player_id=player_id,
            stat_type=stat_type,
            games=games,
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching hit rates for player {player_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# EV Performance Endpoints
# =============================================================================

@router.get("/ev-performance")
async def get_ev_performance(
    player_id: Optional[int] = Query(None, description="Optional player filter"),
    days: int = Query(30, ge=1, le=365, description="Days of history to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get realized EV performance from settled picks.
    
    Compares predicted EV vs actual returns over time.
    """
    try:
        result = await calculate_ev_performance(
            db,
            player_id=player_id,
            days=days,
        )
        return result
    except Exception as e:
        logger.error(f"Error calculating EV performance: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# Trends Endpoints
# =============================================================================

@router.get("/trends/{player_id}")
async def get_odds_trends(
    player_id: int,
    stat_type: Optional[str] = Query(None, description="Filter by stat type"),
    days: int = Query(7, ge=1, le=30, description="Days of history to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get odds movement trends for a player.
    
    Analyzes historical odds data from OddsSnapshot to identify:
    - Opening vs closing line movements
    - Sharp money indicators
    - Line value opportunities
    """
    try:
        result = await calculate_odds_trends(
            db,
            player_id=player_id,
            stat_type=stat_type,
            days=days,
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching trends for player {player_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# Dashboard Endpoint
# =============================================================================

@router.get("/dashboard")
async def get_dashboard(
    sport: str = Query("nba", description="Sport: nba, nfl, mlb, nhl"),
    days: int = Query(30, ge=1, le=365, description="Days of history"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive analytics dashboard.
    
    Returns:
    - Overall pick performance
    - Top performing players
    - Key metrics summary
    """
    sport_key_map = {
        "nba": "basketball_nba",
        "nfl": "americanfootball_nfl",
        "mlb": "baseball_mlb",
        "nhl": "icehockey_nhl",
    }
    
    sport_key = sport_key_map.get(sport.lower())
    if not sport_key:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        result = await get_analytics_dashboard(
            db,
            sport_key=sport_key,
            days=days,
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# Sync Endpoints (Manual Triggers)
# =============================================================================

@router.post("/sync")
async def trigger_historical_sync(
    sport: str = Query("nba", description="Sport to sync"),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger manual historical data sync from OddsPapi.
    
    Syncs:
    1. Historical odds movements
    2. Game results/scores
    3. Pick settlements
    
    Note: Requires ODDSPAPI_API_KEY to be configured.
    """
    from app.core.config import get_settings
    
    settings = get_settings()
    if not settings.oddspapi_api_key:
        raise HTTPException(
            status_code=400,
            detail="OddsPapi API key not configured. Set ODDSPAPI_API_KEY environment variable."
        )
    
    sport_key_map = {
        "nba": "basketball_nba",
        "nfl": "americanfootball_nfl",
        "mlb": "baseball_mlb",
        "nhl": "icehockey_nhl",
    }
    
    sport_key = sport_key_map.get(sport.lower())
    if not sport_key:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        result = await run_full_historical_sync(db, sport_key)
        return {
            "status": "success",
            "sport": sport,
            "results": result,
        }
    except Exception as e:
        logger.error(f"Error running historical sync: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@router.post("/sync/odds")
async def trigger_historical_odds_sync(
    sport: str = Query("nba", description="Sport to sync"),
    days_back: int = Query(7, ge=1, le=30, description="Days of history to fetch"),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync historical odds only (without results/settlements).
    """
    from app.core.config import get_settings
    
    settings = get_settings()
    if not settings.oddspapi_api_key:
        raise HTTPException(
            status_code=400,
            detail="OddsPapi API key not configured"
        )
    
    sport_key_map = {
        "nba": "basketball_nba",
        "nfl": "americanfootball_nfl",
    }
    
    sport_key = sport_key_map.get(sport.lower())
    if not sport_key:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        result = await sync_historical_odds(db, sport_key, days_back)
        return {
            "status": "success",
            "sport": sport,
            "days_back": days_back,
            "result": result,
        }
    except Exception as e:
        logger.error(f"Error syncing historical odds: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@router.post("/sync/results")
async def trigger_results_sync(
    sport: str = Query("nba", description="Sport to sync"),
    days_back: int = Query(3, ge=1, le=14, description="Days of games to check"),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync game results and settle picks.
    """
    from app.core.config import get_settings
    
    settings = get_settings()
    if not settings.oddspapi_api_key:
        raise HTTPException(
            status_code=400,
            detail="OddsPapi API key not configured"
        )
    
    sport_key_map = {
        "nba": "basketball_nba",
        "nfl": "americanfootball_nfl",
    }
    
    sport_key = sport_key_map.get(sport.lower())
    if not sport_key:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        # Sync results
        results_sync = await sync_game_results(db, sport_key, days_back)
        
        # Settle picks
        settlement = await settle_picks(db, sport_key)
        
        return {
            "status": "success",
            "sport": sport,
            "results_sync": results_sync,
            "settlement": settlement,
        }
    except Exception as e:
        logger.error(f"Error syncing results: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])
