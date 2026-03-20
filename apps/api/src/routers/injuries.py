from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_async_db
from models.injury import Injury
from models.brain import InjuryImpactEvent
from schemas.injury import InjuryOut, InjuryImpactSchema
from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["injuries"])

@router.get("/live", response_model=List[InjuryOut])
@router.get("", response_model=List[InjuryOut])
async def get_injuries(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Returns live player injuries (current status).
    """
    stmt = select(Injury).filter(Injury.sport == sport).order_by(desc(Injury.created_at)).limit(50)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/history", response_model=List[InjuryImpactSchema])
async def get_injury_history(
    sport: str = Query("basketball_nba"),
    player_name: str = Query(None),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns historical injury impact events.
    """
    stmt = select(InjuryImpactEvent).where(InjuryImpactEvent.sport == sport)
    if player_name:
        stmt = stmt.where(InjuryImpactEvent.player_name == player_name)
    
    stmt = stmt.order_by(desc(InjuryImpactEvent.created_at)).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
