class AsyncSession: pass
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc, func, delete
from database import get_async_db
from routers.auth import get_current_user
from models.bets import BetLog, BetResult
from models.users import User
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/bets", tags=["bets"])

class BetCreate(BaseModel):
    user_id: str
    player_name: str
    prop_type: str
    line: float
    side: str
    odds: int
    stake: float = 1.0
    bookmaker: str
    sport: str
    notes: Optional[str] = None

class BetSettle(BaseModel):
    result: BetResult
    actual_value: Optional[float] = None

@router.post("/")
async def log_bet(body: BetCreate, db: AsyncSession = Depends(get_async_db), user: User = Depends(get_current_user)):
    bet_data = body.model_dump()
    bet_data["user_id"] = str(user.id) # Force user ID from auth
    bet = BetLog(**bet_data)
    db.add(bet)
    await db.commit()
    await db.refresh(bet)
    return bet

@router.get("/")
async def get_bets(db: AsyncSession = Depends(get_async_db), user: User = Depends(get_current_user)):
    stmt = select(BetLog).where(BetLog.user_id == str(user.id)).order_by(desc(BetLog.placed_at))
    result = await db.execute(stmt)
    bets = result.scalars().all()
    
    total = len(bets)
    settled = [b for b in bets if b.result != BetResult.pending]
    wins = sum(1 for b in settled if b.result == BetResult.win)
    pl = sum(b.profit_loss for b in settled)
    roi = (pl / (len(settled) * 1.0) * 100) if settled else 0

    return {
        "bets": bets,
        "stats": {
            "total": total,
            "wins": wins,
            "losses": len(settled) - wins,
            "pending": total - len(settled),
            "profit_loss": round(pl, 2),
            "roi": round(roi, 1),
            "win_rate": round(wins / len(settled) * 100, 1) if settled else 0,
        }
    }

@router.patch("/{bet_id}/settle")
async def settle_bet(bet_id: int, body: BetSettle, db: AsyncSession = Depends(get_async_db)):
    stmt = select(BetLog).where(BetLog.id == bet_id)
    result = await db.execute(stmt)
    bet = result.scalar_one_or_none()
    
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")

    bet.result = body.result
    bet.settled_at = datetime.utcnow()

    if body.result == BetResult.win:
        bet.profit_loss = bet.stake * (100 / abs(bet.odds)) if bet.odds < 0 else bet.stake * (bet.odds / 100)
        bet.profit_loss = round(bet.profit_loss, 2)
    elif body.result == BetResult.loss:
        bet.profit_loss = -bet.stake
    else:
        bet.profit_loss = 0.0

    await db.commit()
    await db.refresh(bet)
    return bet

@router.delete("/{bet_id}")
async def delete_bet(bet_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(BetLog).where(BetLog.id == bet_id)
    result = await db.execute(stmt)
    bet = result.scalar_one_or_none()
    
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
        
    await db.delete(bet)
    await db.commit()
    return {"ok": True}
