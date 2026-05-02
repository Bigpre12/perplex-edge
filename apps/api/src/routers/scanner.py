# apps/api/src/routers/scanner.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, text
from db.session import get_async_db
from models import UnifiedEVSignal
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scanner", tags=["scanner"])

@router.get("")
async def get_scanner_feed(
    sport: str = Query("basketball_nba"),
    min_ev: float = Query(2.0),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Scanner Feed: Returns high-confidence confluence signals.
    Combines EV+, Sharp, and CLV metrics.
    """
    try:
        # Query ev_signals for high-EV confluence signals
        stmt = select(UnifiedEVSignal).where(
            UnifiedEVSignal.sport == sport,
            UnifiedEVSignal.edge_percent >= min_ev
        ).order_by(desc(UnifiedEVSignal.edge_percent)).limit(limit)
        
        result = await db.execute(stmt)
        signals = result.scalars().all()
        
        # Map to frontend ScannerRow shape
        rows = []
        for s in signals:
            # Determine signal type label
            signal_label = "EV+"
            if s.steam:
                signal_label = "SHARP"
            elif s.clv and s.clv > 2.0:
                signal_label = "CLV"
            
            rows.append({
                "id": str(s.id),
                "player": s.player_name or "Matchup",
                "market": s.market_key,
                "line": str(s.line),
                "bookOdds": s.price,
                "fairValue": s.true_prob, # or fair odds
                "edgePct": s.edge_percent,
                "signal": signal_label,
                "recommendation": s.recommendation,
                "tier": s.tier or "standard"
            })
            
        return {
            "status": "ok",
            "data": rows,
            "count": len(rows),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Scanner Feed Error: {e}")
        return {"status": "error", "message": str(e), "data": []}
