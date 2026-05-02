# apps/api/src/routers/history.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, text
from db.session import get_async_db
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("/summary")
async def get_history_summary(
    days: int = Query(30),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns aggregated performance summary for the History tab.
    """
    try:
        # 1. Total profit/loss from settled bets
        # Using 'bets' table for now as it's the primary tracker in bets.py
        stmt = text("""
            SELECT 
                COUNT(*) as total_bets,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as losses,
                SUM(stake) as total_staked
            FROM bets
            WHERE created_at >= NOW() - INTERVAL ':days days'
        """).bindparams(days=days)
        
        result = await db.execute(stmt)
        summary = result.fetchone()
        
        # 2. Recent results list
        recent_stmt = text("""
            SELECT id, player, market, pick, line, odds, stake, status, created_at
            FROM bets
            ORDER BY created_at DESC
            LIMIT 20
        """)
        recent_res = await db.execute(recent_stmt)
        recent_rows = recent_res.mappings().all()
        
        return {
            "status": "ok",
            "summary": {
                "total_bets": summary.total_bets or 0,
                "win_rate": (summary.wins / summary.total_bets * 100) if summary.total_bets and summary.total_bets > 0 else 0,
                "profit": 0.0, # profit/loss calculation requires bookmaker-specific payout logic
                "total_staked": float(summary.total_staked or 0)
            },
            "results": [dict(r) for r in recent_rows],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"History Summary Error: {e}")
        return {"status": "error", "message": str(e), "results": []}

@router.get("/props")
async def get_props_history(
    sport: str = Query("basketball_nba"),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns historical prop snapshots from props_history table.
    """
    try:
        stmt = text("""
            SELECT snapshot_at, sport, player_name, market_key, line, book, odds_over, odds_under
            FROM props_history
            WHERE sport = :sport
            ORDER BY snapshot_at DESC
            LIMIT :limit
        """).bindparams(sport=sport, limit=limit)
        
        result = await db.execute(stmt)
        rows = result.mappings().all()
        
        return {
            "status": "ok",
            "data": [dict(r) for r in rows],
            "count": len(rows)
        }
    except Exception as e:
        logger.error(f"Props History Error: {e}")
        return {"status": "error", "message": str(e)}
