from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from db.session import get_db
from models.brain import CLVRecord
from models.prop import PropLine
from common_deps import get_user_tier

router = APIRouter(tags=["clv"])

@router.get("")
@router.get("/")
async def get_clv_tracking(
    sport: Optional[str] = Query(None),
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    tier: str = Depends(get_user_tier)
):
    """
    Returns historical CLV tracking data from both Main Markets (clv_tracking table)
    and Player Props (proplines table).
    """
    results = []
    
    # 1. Fetch from CLVRecord (Main Markets)
    stmt = select(CLVRecord).order_by(desc(CLVRecord.created_at)).limit(limit)
    if sport:
        stmt = stmt.where(CLVRecord.sport == sport)
    
    res = await db.execute(stmt)
    records = res.scalars().all()
    
    for r in records:
        results.append({
            "id": r.id,
            "player": r.selection,
            "sport": r.sport,
            "market": r.market_key,
            "open_line": r.opening_line,
            "close_line": r.closing_line,
            "clv_value": r.clv_percentage,
            "beat": r.clv_beat,
            "timestamp": r.created_at.isoformat()
        })

    # 2. Fetch from PropLine (Player Props)
    # Only return settled or tracked ones
    stmt2 = select(PropLine).where(PropLine.closing_line != None).order_by(desc(PropLine.created_at)).limit(limit)
    if sport:
        stmt2 = stmt2.where(PropLine.sport_key == sport)
        
    res2 = await db.execute(stmt2)
    props = res2.scalars().all()
    
    for p in props:
        results.append({
            "id": f"prop_{p.id}",
            "player": p.player_name,
            "sport": p.sport_key,
            "market": p.stat_type,
            "open_line": p.line,
            "close_line": p.closing_line,
            "clv_value": p.clv_val,
            "beat": p.beat_closing_line,
            "timestamp": p.created_at.isoformat()
        })

    # Sort combined results by timestamp
    results.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "status": "active",
        "data": results[:limit],
        "count": len(results)
    }

@router.get("/summary")
async def get_clv_summary(
    sport: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Provides institutional performance metrics: Beat Rate % and Avg CLV.
    """
    # Summary across all tracked CLV
    stmt = select(
        func.count(CLVRecord.id).label("total"),
        func.sum(func.cast(CLVRecord.clv_beat, func.Integer)).label("beats"),
        func.avg(CLVRecord.clv_percentage).label("avg_clv")
    )
    if sport:
        stmt = stmt.where(CLVRecord.sport == sport)
    
    res = await db.execute(stmt)
    summary = res.fetchone()
    
    total = summary.total or 0
    beats = summary.beats or 0
    avg_clv = float(summary.avg_clv or 0.0)
    
    beat_rate = (beats / total * 100) if total > 0 else 0.0
    
    return {
        "status": "active",
        "metrics": {
            "total_tracked": total,
            "beat_rate_pct": round(beat_rate, 2),
            "avg_clv_pct": round(avg_clv, 2),
            "edge_proven": avg_clv > 2.0 # Institutional benchmark
        }
    }
