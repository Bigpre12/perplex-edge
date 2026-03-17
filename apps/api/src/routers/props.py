from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db, get_async_db
from models.prop import Prop
from schemas.prop import PropOut, PropsScoredResponse
from datetime import datetime, timedelta
from sqlalchemy import select, desc, or_, and_
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def list_props(
    sport: str = "basketball_nba",
    limit: int = 40,
    stale: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns top props for a sport with intelligent freshness filtering."""
    try:
        now = datetime.utcnow()
        stmt = select(Prop).where(Prop.sport == sport)
        
        # Freshness filter: only show games that haven't started recently
        if not stale:
            # Prop doesn't have game_start_time, it has created_at
            stmt = stmt.where(Prop.created_at >= now - timedelta(hours=24))

        stmt = stmt.order_by(desc(Prop.created_at)).limit(limit)
        result = await db.execute(stmt)
        items = result.scalars().all()
        return {"data": items, "results": items}
    except Exception as e:
        logger.error(f"Error listing props: {e}")
        return {"data": [], "results": []}

@router.get("/scored")
async def scored_props(db: AsyncSession = Depends(get_async_db)):
    """Returns recently completed props for the ledger/history (last 72h)."""
    try:
        now = datetime.utcnow()
        stmt = select(Prop).where(
            Prop.is_scored == True,
            Prop.created_at >= now - timedelta(hours=72)
        ).order_by(desc(Prop.created_at)).limit(50)
        
        result = await db.execute(stmt)
        items = result.scalars().all()
        return {"data": items, "results": items}
    except Exception as e:
        logger.error(f"Error listing scored props: {e}")
        return {"data": [], "results": []}
