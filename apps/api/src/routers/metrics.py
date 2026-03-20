from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db as get_async_db # standardizing on get_db but keeping name for compatibility
from services.dashboard import get_dashboard_metrics
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("")
async def metrics(db: AsyncSession = Depends(get_async_db)):
    return await get_dashboard_metrics(db)

@router.get("/picks-stats")
async def picks_stats():
    """Returns pick statistics for the leaderboard page."""
    return {
        "top_pickers": [],
        "consensus_picks": [],
        "total_active_picks": 0
    }
