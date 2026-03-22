from fastapi import APIRouter, Query, Depends
from typing import List, Dict, Any
from sqlalchemy import select, desc
from db.session import AsyncSessionLocal
from models.brain import SharpSignal, WhaleMove
from schemas.universal import UniversalResponse, ResponseMeta
from middleware.request_id import get_request_id

router = APIRouter(tags=["sharp"])

@router.get("/alerts", response_model=UniversalResponse[dict])
async def get_sharp_alerts(
    sport: str = Query("basketball_nba"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Returns the latest sharp money signals and whale moves.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Fetch latest Sharp Signals
            sharp_stmt = select(SharpSignal).where(SharpSignal.sport == sport).order_by(desc(SharpSignal.created_at)).limit(limit)
            sharp_res = await session.execute(sharp_stmt)
            sharp_signals = sharp_res.scalars().all()

            # Fetch latest Whale Moves
            whale_stmt = select(WhaleMove).where(WhaleMove.sport == sport).order_by(desc(WhaleMove.created_at)).limit(limit)
            whale_res = await session.execute(whale_stmt)
            whale_moves = whale_res.scalars().all()

            # Combine and sort by created_at
            combined = []
            for s in sharp_signals:
                combined.append({
                    "type": "sharp",
                    "signal_type": s.signal_type,
                    "severity": float(s.severity) if s.severity else 0.0,
                    "event_id": s.event_id,
                    "market": s.market_key,
                    "selection": s.selection,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                })
            
            for w in whale_moves:
                combined.append({
                    "type": "whale",
                    "rating": float(w.whale_rating) if w.whale_rating else 0.0,
                    "move_size": w.move_size,
                    "event_id": w.event_id,
                    "market": w.market_key,
                    "selection": w.selection,
                    "bookmaker": w.bookmaker,
                    "created_at": w.created_at.isoformat() if w.created_at else None
                })

            combined.sort(key=lambda x: x["created_at"] or "", reverse=True)
            results = combined[:limit]

            return UniversalResponse(
                status="ok" if results else "no_data",
                meta=ResponseMeta(
                    source="sharp_brain",
                    db_rows=len(results),
                    request_id=get_request_id()
                ),
                data=results
            )
    except Exception as e:
        import logging
        logging.error(f"Sharp Router Error: {e}")
        return UniversalResponse(
            status="error",
            message=str(e),
            meta=ResponseMeta(request_id=get_request_id()),
            data=[]
        )
