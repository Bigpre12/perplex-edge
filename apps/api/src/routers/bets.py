from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.bet import Bet
from schemas.bet import BetOut, BetCreate

router = APIRouter()

@router.get("", response_model=list[BetOut])
async def list_bets(db: Session = Depends(get_db)):
    return db.query(Bet).order_by(Bet.created_at.desc()).all()

@router.post("", response_model=BetOut)
async def create_bet(payload: BetCreate, db: Session = Depends(get_db)):
    bet = Bet(**payload.model_dump(), status="open")
    db.add(bet)
    db.commit()
    db.refresh(bet)
    return bet

@router.get("/stats")
async def bet_stats(db: AsyncSession = Depends(get_async_db)):
    """Returns betting statistics for the ledger and bankroll pages."""
    try:
        # Simple aggregate stats
        stmt = select(
            func.count(Bet.id).label("total_bets"),
            func.sum(Bet.stake).label("total_stake"),
            func.sum(Bet.profit_loss).label("total_profit_loss")
        )
        result = await db.execute(stmt)
        stats = result.fetchone()
        
        # Calculate win rate
        win_stmt = select(func.count(Bet.id)).where(Bet.status == "won")
        win_count = (await db.execute(win_stmt)).scalar() or 0
        
        total = stats.total_bets if stats and stats.total_bets else 0
        win_rate = (win_count / total * 100) if total > 0 else 0
        
        return {
            "total_bets": total,
            "total_stake": float(stats.total_stake or 0),
            "profit_loss": float(stats.total_profit_loss or 0),
            "win_rate": win_rate,
            "clv_avg": 2.4 # Placeholder for now
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in bet_stats: {e}")
        return {"total_bets": 0, "win_rate": 0, "profit_loss": 0}

@router.delete("/{bet_id}")
async def delete_bet(bet_id: int, db: Session = Depends(get_db)):
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    db.delete(bet)
    db.commit()
    return {"success": True}
