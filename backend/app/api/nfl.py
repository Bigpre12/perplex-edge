"""NFL API endpoints for live odds, historical data, and hit rates."""

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.nfl_odds_service import (
    sync_nfl_odds,
    get_live_odds,
    get_historical_odds,
    create_daily_snapshot,
    update_game_results,
    calculate_hit_rates,
    ensure_nfl_sport_exists,
)
from app.services.nfl_backup import (
    list_backups,
    backup_exists,
    delete_old_backups,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/nfl", tags=["NFL"])

# =============================================================================
# Live Odds Endpoints
# =============================================================================

@router.get("/odds")
async def get_nfl_live_odds(
    week: Optional[int] = Query(None, ge=1, le=22, description="NFL week (1-18 regular, 19-22 playoffs)"),
    bookmaker: Optional[str] = Query(None, description="Filter by bookmaker"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get live NFL odds.
    
    Returns current odds from the database, updated hourly via scheduled sync.
    """
    try:
        odds = await get_live_odds(db, week=week, bookmaker=bookmaker)
        return {
            "count": len(odds),
            "week": week,
            "bookmaker": bookmaker,
            "odds": odds,
        }
    except Exception as e:
        logger.error(f"Error fetching live NFL odds: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

@router.post("/odds/sync")
async def sync_odds(
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger manual NFL odds sync.
    
    Fetches latest odds using cascade:
    1. OddsAPI (primary)
    2. BetStack (secondary)
    3. JSON backup (fallback)
    """
    try:
        result = await sync_nfl_odds(db)
        return {
            "status": "success",
            "result": result,
        }
    except Exception as e:
        logger.error(f"Error syncing NFL odds: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

@router.post("/games/sync")
async def sync_nfl_games(
    include_props: bool = Query(True, description="Include player props"),
    generate_picks: bool = Query(True, description="Also generate picks after sync"),
    use_stubs: bool = Query(False, description="Use stub data (default: False for real API)"),
    use_espn: bool = Query(False, description="Use ESPN free API for real weekly games"),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync NFL games, lines, and player props.
    
    This uses the main ETL pipeline to fetch:
    - Games and spreads/totals
    - Player props (passing, rushing, receiving, etc.)
    - Creates player records as needed
    - Generates model picks (if generate_picks=True)
    
    Data Sources:
    - use_stubs=False (default): The Odds API (real odds)
    - use_stubs=True: Static stub data
    - use_espn=True: ESPN free API (real weekly schedule)
    """
    from app.services.etl_games_and_lines import sync_games_and_lines
    from app.services.picks_generator import generate_picks as gen_picks
    
    try:
        # Determine provider
        provider = "odds_api"
        if use_espn and not use_stubs:
            provider = "espn"
        
        result = await sync_games_and_lines(
            db, 
            "americanfootball_nfl", 
            include_props=include_props,
            use_stubs=use_stubs,
            provider=provider,
        )
        
        picks_result = None
        if generate_picks:
            picks_result = await gen_picks(
                db,
                sport_key="americanfootball_nfl",
                min_ev=0.0,
                min_confidence=0.5,
                use_stubs=use_stubs,
            )
        
        return {
            "status": "success",
            "sport": "NFL",
            "use_stubs": use_stubs,
            "use_espn": use_espn,
            "data_source": result.get("data_source", "primary"),
            "result": result,
            "picks": picks_result,
        }
    except Exception as e:
        logger.error(f"Error syncing NFL games: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

# =============================================================================
# Historical Odds Endpoints
# =============================================================================

@router.get("/odds/history")
async def get_nfl_historical_odds(
    week: Optional[int] = Query(None, ge=1, le=22, description="NFL week filter"),
    season: Optional[int] = Query(None, ge=2020, le=2030, description="Season year"),
    bookmaker: Optional[str] = Query(None, description="Filter by bookmaker"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get historical NFL odds snapshots.
    
    Returns daily snapshots of odds for tracking line movements
    and calculating hit rates.
    """
    try:
        odds = await get_historical_odds(
            db,
            week=week,
            season=season,
            bookmaker=bookmaker,
            start_date=start_date,
            end_date=end_date,
        )
        return {
            "count": len(odds),
            "filters": {
                "week": week,
                "season": season,
                "bookmaker": bookmaker,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "odds": odds,
        }
    except Exception as e:
        logger.error(f"Error fetching historical NFL odds: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

@router.post("/odds/snapshot")
async def create_snapshot(
    snapshot_date: Optional[date] = Query(None, description="Snapshot date (defaults to today)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a daily snapshot of current live odds.
    
    Copies live_odds_nfl to historical_odds_nfl for the given date.
    """
    try:
        result = await create_daily_snapshot(db, snapshot_date)
        return {
            "status": "success",
            "result": result,
        }
    except Exception as e:
        logger.error(f"Error creating snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

# =============================================================================
# Results & Hit Rates Endpoints
# =============================================================================

@router.post("/results/{game_id}")
async def set_game_result(
    game_id: str,
    result: str = Query(..., pattern="^(home|away|draw)$", description="Game result"),
    db: AsyncSession = Depends(get_db),
):
    """
    Set the result for a completed game.
    
    Updates all historical records for the game with the final result.
    Used for calculating hit rates.
    """
    try:
        update_result = await update_game_results(db, game_id, result)
        return {
            "status": "success",
            "result": update_result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting game result: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

@router.get("/hit-rates")
async def get_hit_rates(
    season: Optional[int] = Query(None, ge=2020, le=2030, description="Season year"),
    bookmaker: Optional[str] = Query(None, description="Filter by bookmaker"),
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate hit rates from historical odds data.
    
    Analyzes how often favorites won based on pre-game odds.
    
    Returns:
    - Overall hit rate
    - Hit rates by bookmaker
    - Total games analyzed
    """
    try:
        result = await calculate_hit_rates(db, season=season, bookmaker=bookmaker)
        return {
            "status": "success",
            "filters": {
                "season": season,
                "bookmaker": bookmaker,
            },
            "stats": result,
        }
    except Exception as e:
        logger.error(f"Error calculating hit rates: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

# =============================================================================
# Backup Management Endpoints
# =============================================================================

@router.get("/backups")
async def get_backups(
    limit: int = Query(30, ge=1, le=100, description="Maximum number of backups to list"),
):
    """
    List available JSON backup files.
    """
    try:
        backups = list_backups(limit=limit)
        return {
            "count": len(backups),
            "backups": backups,
        }
    except Exception as e:
        logger.error(f"Error listing backups: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

@router.get("/backups/check/{backup_date}")
async def check_backup(backup_date: date):
    """
    Check if a backup exists for a specific date.
    """
    exists = backup_exists(backup_date)
    return {
        "date": backup_date.isoformat(),
        "exists": exists,
    }

@router.delete("/backups/cleanup")
async def cleanup_old_backups(
    days_to_keep: int = Query(90, ge=7, le=365, description="Days of backups to retain"),
):
    """
    Delete backup files older than specified days.
    """
    try:
        deleted = delete_old_backups(days_to_keep)
        return {
            "status": "success",
            "days_kept": days_to_keep,
            "files_deleted": deleted,
        }
    except Exception as e:
        logger.error(f"Error cleaning up backups: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])

# =============================================================================
# Setup Endpoint
# =============================================================================

@router.post("/setup")
async def setup_nfl(
    db: AsyncSession = Depends(get_db),
):
    """
    Initialize NFL sport in the database.
    
    Call this once to add NFL to the sports dropdown.
    Safe to call multiple times - will not create duplicates.
    """
    try:
        sport = await ensure_nfl_sport_exists(db)
        return {
            "status": "success",
            "sport": {
                "id": sport.id,
                "name": sport.name,
                "league_code": sport.league_code,
            },
            "message": "NFL sport is now available in the dropdown",
        }
    except Exception as e:
        logger.error(f"Error setting up NFL: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])
