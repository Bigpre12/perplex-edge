from fastapi import APIRouter, Query, Depends
from common_deps import require_elite, get_user_tier
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.session import get_async_db
from models.brain import WhaleMove
from schemas.unified import WhaleEventSchema
from services.whale_service import detect_whale_signals
from datetime import datetime, timezone, timedelta

router = APIRouter(tags=["whale"])

@router.get("/live", response_model=Dict[str, Any])
@router.get("", response_model=Dict[str, Any])
async def whale_signals(
    sport: Optional[str] = Query("basketball_nba"), 
    tier: str = Depends(get_user_tier),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns live whale moves from the last 24 hours.
    """
    if tier != "elite":
        return {"status": "limited", "data": [], "message": "Elite subscription required"}
        
    stmt = select(WhaleMove).where(WhaleMove.sport == sport)
    stmt = stmt.where(WhaleMove.created_at >= datetime.now(timezone.utc) - timedelta(hours=24))
    stmt = stmt.order_by(desc(WhaleMove.created_at)).limit(20)
    
    result = await db.execute(stmt)
    moves = result.scalars().all()
    
    return {
        "status": "success",
        "data": [WhaleEventSchema.model_validate(m) for m in moves],
        "total": len(moves),
        "sport": sport
    }

@router.get("/history", response_model=Dict[str, Any])
async def whale_history(
    sport: str = Query("basketball_nba"),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_async_db),
    tier: str = Depends(get_user_tier)
):
    """
    Returns historical whale moves for trend analysis.
    """
    if tier != "elite":
        return {"status": "limited", "data": []}
        
    stmt = select(WhaleMove).where(WhaleMove.sport == sport)
    stmt = stmt.order_by(desc(WhaleMove.created_at)).limit(limit)
    
    result = await db.execute(stmt)
    history = result.scalars().all()
    
    return {
        "status": "success",
        "data": [WhaleEventSchema.model_validate(h) for h in history],
        "total": len(history)
    }

# Legacy endpoint for backward compatibility
@router.get("/active-moves")
async def get_active_moves(sport: str = Query("basketball_nba"), tier: str = Depends(get_user_tier), db: AsyncSession = Depends(get_async_db)):
    return await whale_signals(sport, tier, db)
