from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.session import get_db
from models.bet import BetLog, BetResult
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/summary")
async def performance_summary(
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Wealth Metrics Summary (Fix #8: BetLog Query)"""
    try:
        # UserID is string in BetLog (Fix #10 context)
        result = await db.execute(
            select(BetLog)
            .where(BetLog.user_id == str(user_id), BetLog.result != BetResult.pending)
            .order_by(BetLog.placed_at.asc())
        )
        logs = result.scalars().all()
        
        return {
            "count": len(logs),
            "performance": "analyzed",
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error in performance summary: {e}")
        return {"error": str(e)}
