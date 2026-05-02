from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, cast, Integer
from db.session import get_db, get_async_db
from models.brain import CLVRecord
from schemas.unified import ClvTradeSchema
from models.prop import PropLine
from common_deps import get_user_tier
from datetime import datetime, timezone, timedelta
from itertools import islice

router = APIRouter(tags=["clv"])

@router.get("/live", response_model=Dict[str, Any])
@router.get("", response_model=Dict[str, Any])
async def get_clv_live(
    sport: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns fresh CLV beats from the last 24h.
    """
    stmt = select(CLVRecord).where(CLVRecord.created_at >= datetime.now(timezone.utc) - timedelta(hours=24))
    if sport:
        stmt = stmt.where(CLVRecord.sport == sport)
    stmt = stmt.order_by(desc(CLVRecord.created_at)).limit(20)
    
    res = await db.execute(stmt)
    records = res.scalars().all()
    
    return {
        "status": "success",
        "data": [ClvTradeSchema.model_validate({
            "id": r.id,
            "player": r.selection,
            "sport": r.sport,
            "market": r.market_key,
            "open_line": float(r.opening_line),
            "close_line": float(r.closing_line),
            "clv_value": float(r.clv_percentage),
            "beat": r.clv_beat,
            "timestamp": r.created_at
        }) for r in records],
        "total": len(records)
    }

@router.get("/history", response_model=Dict[str, Any])
async def get_clv_history(
    sport: Optional[str] = Query(None),
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db),
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
            "open_line": float(r.opening_line),
            "close_line": float(r.closing_line),
            "clv_value": float(r.clv_percentage),
            "beat": r.clv_beat,
            "timestamp": r.created_at
        })

    # 2. Fetch from PropLine (Player Props)
    stmt2 = select(PropLine).where(PropLine.closing_line != None).order_by(desc(PropLine.created_at)).limit(limit)
    if sport:
        stmt2 = stmt2.where(PropLine.sport_key == sport)
        
    res2 = await db.execute(stmt2)
    props = res2.scalars().all()
    
    for p in props:
        results.append({
            "id": p.id,
            "player": p.player_name,
            "sport": p.sport_key,
            "market": p.stat_type,
            "open_line": float(p.line),
            "close_line": float(p.closing_line),
            "clv_value": float(p.clv_val),
            "beat": p.beat_closing_line,
            "timestamp": p.created_at
        })

    # Sort combined results by timestamp
    results.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "status": "active",
        "data": [ClvTradeSchema.model_validate(r) for r in list(islice(results, limit))],
        "count": len(results)
    }

@router.get("/summary")
async def get_clv_summary(
    sport: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Provides institutional performance metrics: Beat Rate % and Avg CLV.
    Includes recent results for the analytics table.
    """
    # 1. Metrics
    stmt = select(
        func.count(CLVRecord.id).label("total"),
        func.sum(cast(CLVRecord.clv_beat, Integer)).label("beats"),
        func.avg(CLVRecord.clv_percentage).label("avg_clv")
    )
    if sport:
        stmt = stmt.where(CLVRecord.sport == sport)
    
    res = await db.execute(stmt)
    summary = res.fetchone()
    
    total = summary.total if summary and summary.total else 0
    beats = summary.beats if summary and summary.beats else 0
    avg_clv = float(summary.avg_clv) if summary and summary.avg_clv else 0.0
    beat_rate = (beats / total * 100) if total > 0 else 0.0

    # 2. Recent Results (Merge Main Markets and Props for the UI table)
    results = []
    
    # Recent CLVRecords
    stmt_rec = select(CLVRecord).order_by(desc(CLVRecord.created_at)).limit(10)
    if sport:
        stmt_rec = stmt_rec.where(CLVRecord.sport == sport)
    res_rec = await db.execute(stmt_rec)
    records = res_rec.scalars().all()
    for r in records:
        results.append({
            "player_name": r.selection,
            "market": r.market_key,
            "open_line": float(r.opening_line),
            "close_line": float(r.closing_line),
            "clv_edge": float(r.clv_percentage),
            "status": "WIN" if r.clv_beat else "PENDING",
            "timestamp": r.created_at.isoformat()
        })

    # Recent PropLines with CLV
    stmt_prop = select(PropLine).where(PropLine.closing_line != None).order_by(desc(PropLine.created_at)).limit(10)
    if sport:
        stmt_prop = stmt_prop.where(PropLine.sport_key == sport)
    res_prop = await db.execute(stmt_prop)
    props = res_prop.scalars().all()
    for p in props:
        results.append({
            "player_name": p.player_name,
            "market": p.stat_type,
            "open_line": float(p.line),
            "close_line": float(p.closing_line),
            "clv_edge": float(p.clv_val),
            "status": "WIN" if p.beat_closing_line else "LOSS",
            "timestamp": p.created_at.isoformat()
        })
    
    results.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "status": "active",
        "avg_clv_edge": float(f"{float(avg_clv):.2f}"),
        "win_rate_vs_clv": float(f"{float(beat_rate):.2f}"),
        "results": results[:15],
        "meta": {
            "total_tracked": total,
            "avg_edge": float(f"{float(avg_clv):.2f}"),
            "win_rate": float(f"{float(beat_rate):.2f}")
        }
    }
