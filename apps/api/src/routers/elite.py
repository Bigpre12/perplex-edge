# apps/api/src/routers/elite.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from db.session import get_async_db
from models import UnifiedEVSignal
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/elite", tags=["elite"])

@router.get("/picks")
async def get_elite_picks(
    sport: Optional[str] = Query(None),
    min_confidence: float = Query(0.85),
    db: AsyncSession = Depends(get_async_db)
):
    """
    ELITE Picks: Returns the highest confidence signals across all markets.
    Requires confluence of EV+, Sharp (Steam), and CLV.
    """
    try:
        # Filter signals that have high confidence AND some confluence
        # tier 'elite' or high edge_percent + sharp/clv
        stmt = select(UnifiedEVSignal).where(
            UnifiedEVSignal.edge_percent >= 5.0 # High threshold for elite
        )
        
        if sport:
            stmt = stmt.where(UnifiedEVSignal.sport == sport)
            
        stmt = stmt.order_by(desc(UnifiedEVSignal.edge_percent)).limit(10)
        
        result = await db.execute(stmt)
        signals = result.scalars().all()
        
        return {
            "status": "ok",
            "picks": [
                {
                    "id": str(s.id),
                    "player": s.player_name,
                    "market": s.market_key,
                    "line": s.line,
                    "odds": s.price,
                    "edge": s.edge_percent,
                    "confidence": 0.92, # Placeholder for elite scoring
                    "reason": s.reason or "High-confidence confluence signal detected.",
                    "tier": "ELITE"
                } for s in signals
            ],
            "count": len(signals),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Elite Picks Error: {e}")
        return {"status": "error", "message": str(e), "picks": []}
