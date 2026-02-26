from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from routers.auth_router import get_current_user
from models.users import User
from services.ledger_service import ledger_service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/ledger", tags=["ledger"])

class BetLegCreate(BaseModel):
    prop_id: int
    side: str
    odds_taken: int
    line_taken: float

class BetSlipCreate(BaseModel):
    slip_type: str = "straight"
    sportsbook: str
    total_odds: int
    legs: List[BetLegCreate]

@router.post("/track", status_code=status.HTTP_201_CREATED)
async def track_bet(
    bet_data: BetSlipCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        slip = await ledger_service.track_bet(
            db=db,
            user_id=current_user.id,
            slip_data=bet_data.model_dump(),
            legs=[leg.model_dump() for leg in bet_data.legs]
        )
        return {"status": "success", "slip_id": slip.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-bets")
async def get_my_bets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    slips = await ledger_service.get_user_ledger(db, current_user.id)
    return slips

@router.get("/stats")
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    stats = await ledger_service.get_user_stats(db, current_user.id)
    return stats
