import logging
from fastapi import APIRouter, Query, Depends
from api_utils.tier_guards import require_tier
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.session import get_async_db
from models.brain import WhaleMove, WhaleSignal
from schemas.unified import WhaleEventSchema
from datetime import datetime, timezone, timedelta
from models.user import User

router = APIRouter(tags=["whale"])

@router.get("/live", response_model=Dict[str, Any])
@router.get("", response_model=Dict[str, Any])
async def whale_signals(
    sport: Optional[str] = Query("basketball_nba"), 
    min_units: int = Query(0, description="Minimum units threshold"),
    current_user: User = Depends(require_tier("elite")),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns live whale moves from the last 24 hours.
    Access restricted to ELITE users.
    """
        
    sig_rows = []
    try:
        sig_stmt = (
            select(WhaleSignal)
            .where(WhaleSignal.sport == sport)
            .order_by(desc(WhaleSignal.detected_at))
            .limit(50)
        )
        sig_res = await db.execute(sig_stmt)
        sig_rows = sig_res.scalars().all()
    except Exception as e:
        logger.debug("whale_signals read skipped: %s", e)

    out: List[WhaleEventSchema] = []
    for w in sig_rows:
        out.append(
            WhaleEventSchema.model_validate(
                {
                    "id": w.id,
                    "sport": w.sport or sport,
                    "event_id": w.event_id,
                    "player_name": w.player,
                    "market_key": w.market,
                    "bookmaker": w.bookmaker,
                    "price_after": float(w.odds) if w.odds is not None else None,
                    "line": w.line,
                    "whale_rating": w.trust_level or 0.0,
                    "move_size": w.signal_type,
                    "created_at": w.detected_at,
                }
            )
        )

    if len(out) < 50:
        try:
            stmt = select(WhaleMove).where(WhaleMove.sport == sport)
            if min_units > 0:
                stmt = stmt.where(WhaleMove.whale_rating >= min_units)
            stmt = stmt.where(WhaleMove.created_at >= datetime.now(timezone.utc) - timedelta(hours=24))
            stmt = stmt.order_by(desc(WhaleMove.created_at)).limit(50 - len(out))
            result = await db.execute(stmt)
            moves = result.scalars().all()
            for m in moves:
                out.append(WhaleEventSchema.model_validate(m))
        except Exception as e:
            logger.warning("whale_moves fallback query skipped due to schema mismatch: %s", e)
            moves = []
    else:
        moves = []

    return {
        "status": "success",
        "data": out[:50],
        "total": len(out[:50]),
        "sport": sport,
        "min_units": min_units,
        "sources": {"whale_signals": len(sig_rows), "whale_moves_fallback": len(moves)},
    }

@router.get("/history", response_model=Dict[str, Any])
async def whale_history(
    sport: str = Query("basketball_nba"),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_tier("elite"))
):
    """
    Returns historical whale moves for trend analysis.
    Access restricted to ELITE users.
    """
    try:
        stmt = select(WhaleMove).where(WhaleMove.sport == sport)
        stmt = stmt.order_by(desc(WhaleMove.created_at)).limit(limit)
        result = await db.execute(stmt)
        history = result.scalars().all()
    except Exception as e:
        logger.warning("whale history query skipped due to schema mismatch: %s", e)
        history = []
    
    return {
        "status": "success",
        "data": [WhaleEventSchema.model_validate(h) for h in history],
        "total": len(history)
    }

# Legacy endpoint for backward compatibility
@router.get("/active-moves")
async def get_active_moves(
    sport: str = Query("basketball_nba"), 
    current_user: User = Depends(require_tier("elite")), 
    db: AsyncSession = Depends(get_async_db)
):
    return await whale_signals(sport, 0, current_user, db)
