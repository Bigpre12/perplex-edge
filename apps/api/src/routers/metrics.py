from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.dashboard import get_dashboard_metrics

router = APIRouter()

from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_async_db

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
