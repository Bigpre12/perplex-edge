from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.session import get_db
from models.bet import Bet
from schemas.bet import BetOut, BetCreate
from routers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=list[BetOut])
async def list_bets(db: AsyncSession = Depends(get_db)):
    """List all bets (Admin/System view)"""
    try:
        stmt = select(Bet).order_by(Bet.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error listing bets: {e}")
        return []

@router.get("/my", response_model=list[BetOut])
async def list_my_bets(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List only the current user's bets"""
    try:
        user_id_raw = getattr(current_user, "id", "")
        try:
            user_id = int(user_id_raw)
        except (ValueError, TypeError):
            # Fallback if id is missing or not a number
            return []
            
        stmt = select(Bet).where(Bet.user_id == user_id).order_by(Bet.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error listing user bets: {e}")
        return []

@router.post("", response_model=BetOut)
async def create_bet(payload: BetCreate, db: AsyncSession = Depends(get_db)):
    bet = Bet(**payload.model_dump(), status="open")
    db.add(bet)
    await db.commit()
    await db.refresh(bet)
    return bet


@router.get("/stats")
async def bet_stats(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Returns betting statistics for the ledger and bankroll pages."""
    try:
        user_id_raw = getattr(current_user, "id", "")
        try:
            user_id = int(user_id_raw)
        except (ValueError, TypeError):
            return {"total_bets": 0, "total_stake": 0, "profit_loss": 0, "win_rate": 0, "clv_avg": 0}
            
        # Simple aggregate stats
        stmt = select(
            func.count(Bet.id).label("total_bets"),
            func.sum(Bet.stake).label("total_stake"),
            func.sum(Bet.profit_loss).label("total_profit_loss")
        ).where(Bet.user_id == user_id)
        result = await db.execute(stmt)
        # Use result.one_or_none() for better mapping
        stats = result.one_or_none()
        
        # Calculate win rate
        win_stmt = select(func.count(Bet.id)).where(Bet.status == "won", Bet.user_id == user_id)
        win_count_res = await db.execute(win_stmt)
        win_count = win_count_res.scalar() or 0
        
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
async def delete_bet(bet_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Bet).where(Bet.id == bet_id)
    result = await db.execute(stmt)
    bet = result.scalar_one_or_none()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    await db.delete(bet)
    await db.commit()
    return {"success": True}
