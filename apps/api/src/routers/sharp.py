import logging
from typing import Optional, List
from fastapi import APIRouter, Query, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db, AsyncSessionLocal
from models.brain import SharpSignal, WhaleMove
from schemas.universal import UniversalResponse, ResponseMeta
from middleware.request_id import get_request_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sharp"])

@router.get("/alerts", response_model=UniversalResponse[dict])
async def get_sharp_alerts(
    sport: str = Query("basketball_nba"),
    since: Optional[str] = Query(None, description="ISO timestamp or duration (e.g. 24h)"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Returns the latest sharp money signals (Steam + Whale moves).
    """
    try:
        async with AsyncSessionLocal() as session:
            # Fetch latest Sharp Signals (Legacy/Misc)
            sharp_stmt = select(SharpSignal).where(SharpSignal.sport == sport).order_by(desc(SharpSignal.created_at)).limit(limit)
            sharp_res = await session.execute(sharp_stmt)
            sharp_signals = sharp_res.scalars().all()

            # Fetch latest Whale Moves
            whale_stmt = select(WhaleMove).where(WhaleMove.sport == sport).order_by(desc(WhaleMove.created_at)).limit(limit)
            whale_res = await session.execute(whale_stmt)
            whale_moves = whale_res.scalars().all()

            # Fetch latest Steam Events (New Wiring)
            from models.brain import SteamEvent
            steam_stmt = select(SteamEvent).where(SteamEvent.sport == sport).order_by(desc(SteamEvent.created_at)).limit(limit)
            steam_res = await session.execute(steam_stmt)
            steam_events = steam_res.scalars().all()

            # Filter by 'since' if provided
            since_dt = None
            if since:
                from datetime import datetime, timedelta
                if since.endswith('h'):
                    since_dt = datetime.utcnow() - timedelta(hours=int(since[:-1]))
                else:
                    try:
                        since_dt = datetime.fromisoformat(since.replace('Z', ''))
                    except: pass

            if since_dt:
                sharp_signals = [s for s in sharp_signals if s.created_at and s.created_at.replace(tzinfo=None) >= since_dt]
                whale_moves = [w for w in whale_moves if w.created_at and w.created_at.replace(tzinfo=None) >= since_dt]
                steam_events = [s for s in steam_events if s.created_at and s.created_at.replace(tzinfo=None) >= since_dt]

            combined = []
            for s in sharp_signals:
                combined.append({
                    "id": f"sharp_{s.id}",
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
                    "id": f"whale_{w.id}",
                    "type": "whale",
                    "rating": float(w.whale_rating) if w.whale_rating else 0.0,
                    "move_size": w.move_size,
                    "event_id": w.event_id,
                    "market": w.market_key,
                    "selection": w.selection,
                    "side": w.side,
                    "bookmaker": w.bookmaker,
                    "is_whale": True,
                    "created_at": w.created_at.isoformat() if w.created_at else None
                })

            for st in steam_events:
                combined.append({
                    "id": f"steam_{st.id}",
                    "type": "sharp",
                    "signal_type": "steam",
                    "is_steam": True,
                    "player_name": st.player_name,
                    "selection": st.player_name,
                    "market": st.stat_type,
                    "side": st.side,
                    "line": st.line,
                    "line_movement": st.movement,
                    "book_count": st.book_count,
                    "severity": st.severity,
                    "description": st.description,
                    "created_at": st.created_at.isoformat() if st.created_at else None
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

@router.post("/compute")
async def trigger_sharp_compute(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_db)
):
    """Trigger the sharp and whale detection engines."""
    from services.scheduler_jobs import detect_whales, detect_steam
    from services.heartbeat_service import HeartbeatService
    from datetime import datetime
    try:
        await detect_whales()
        await detect_steam()
        await HeartbeatService.log_heartbeat(db, f"intelligence_{sport}")
        return {"status": "ok", "message": f"Sharp/Whale scan completed for {sport}", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Sharp Compute Trigger Failed: {e}")
        return {"status": "error", "message": str(e)}
