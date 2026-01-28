"""Sync/ETL API endpoints for manual data refresh."""

from typing import Optional

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.etl.sync_service import SyncService
from app.etl.odds_api import SPORT_KEYS

router = APIRouter()


@router.post("/odds/{sport}")
async def sync_odds_for_sport(
    sport: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger odds sync for a specific sport.
    
    Available sports: NBA, NFL, MLB, NHL, NCAAB, NCAAF
    """
    sport_upper = sport.upper()
    if sport_upper not in SPORT_KEYS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {list(SPORT_KEYS.keys())}",
        )

    sync_service = SyncService(db)
    
    try:
        stats = await sync_service.sync_odds_for_sport(sport_upper)
        return {
            "status": "success",
            "sport": sport_upper,
            "stats": stats,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/odds")
async def sync_all_odds(
    db: AsyncSession = Depends(get_db),
):
    """Trigger odds sync for all sports."""
    sync_service = SyncService(db)
    
    try:
        results = await sync_service.sync_all_sports()
        return {
            "status": "success",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/sports")
async def list_available_sports():
    """List available sports for syncing."""
    return {
        "sports": [
            {"code": code, "api_key": key}
            for code, key in SPORT_KEYS.items()
        ]
    }


@router.get("/status")
async def get_sync_status(
    db: AsyncSession = Depends(get_db),
):
    """Get current sync status and data counts."""
    from sqlalchemy import select, func
    from app.models import Sport, Game, Line, Injury, ModelPick

    # Get counts
    sports_count = await db.scalar(select(func.count()).select_from(Sport))
    games_count = await db.scalar(select(func.count()).select_from(Game))
    lines_count = await db.scalar(select(func.count()).select_from(Line))
    current_lines = await db.scalar(
        select(func.count()).select_from(Line).where(Line.is_current == True)
    )
    injuries_count = await db.scalar(select(func.count()).select_from(Injury))
    picks_count = await db.scalar(select(func.count()).select_from(ModelPick))
    active_picks = await db.scalar(
        select(func.count()).select_from(ModelPick).where(ModelPick.is_active == True)
    )

    return {
        "status": "ok",
        "counts": {
            "sports": sports_count or 0,
            "games": games_count or 0,
            "lines": {
                "total": lines_count or 0,
                "current": current_lines or 0,
            },
            "injuries": injuries_count or 0,
            "picks": {
                "total": picks_count or 0,
                "active": active_picks or 0,
            },
        },
    }
