# apps/api/src/routers/unified_ev.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy import select, desc
from database import get_async_db, DummyAsyncSession
from models.unified import UnifiedEVSignal

router = APIRouter(tags=["Unified EV"])

@router.get("/top")
async def get_top_ev(
    sport: str = Query(..., description="e.g. basketball_nba"),
    min_ev: float = Query(2.0, description="Minimum edge percentage"),
    limit: int = Query(50, description="Max results")
):
    """
    Returns top EV signals from the pre-computed signals table.
    This route NEVER calls external APIs.
    """
    async with get_async_db() as session:
        # Use simple select from unified signal table
        stmt = select(UnifiedEVSignal).where(
            UnifiedEVSignal.sport == sport,
            UnifiedEVSignal.edge_percent >= min_ev
        ).order_by(desc(UnifiedEVSignal.edge_percent)).limit(limit)
        
        result = await session.execute(stmt)
        signals = result.scalars().all()
        
        return {
            "sport": sport,
            "count": len(signals),
            "signals": [
                {
                    "event_id": s.event_id,
                    "market": s.market_key,
                    "selection": s.outcome_key,
                    "book": s.bookmaker,
                    "odds": float(s.price), # Note: we might need to fetch decimal price if not stored
                    "true_prob": float(s.true_prob),
                    "edge": float(s.edge_percent),
                    "updated_at": s.updated_at.isoformat()
                } for s in signals
            ]
        }
