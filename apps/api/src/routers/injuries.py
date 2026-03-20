from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from common_deps import get_db
from models.injury import Injury

router = APIRouter()

@router.get("")
@router.get("/")
async def get_injuries(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Injury).filter(Injury.sport == sport).order_by(desc(Injury.created_at))
    result = await db.execute(stmt)
    return result.scalars().all()
