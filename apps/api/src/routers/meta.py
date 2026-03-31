from datetime import datetime, timezone
import os
from fastapi import APIRouter

from sqlalchemy import text
from db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from schemas.universal import UniversalResponse, ResponseMeta
from services.heartbeat_service import HeartbeatService
from middleware.request_id import get_request_id

router = APIRouter()

@router.get("/inspect", response_model=UniversalResponse[dict])
async def data_inspector(db: AsyncSession = Depends(get_async_db)):
    """Source verification: inspect row counts in core tables."""
    # Optimized inspector
    ev_count = (await db.execute(text("SELECT count(*) FROM ev_signals"))).scalar() or 0
    pick_count = (await db.execute(text("SELECT count(*) FROM model_picks"))).scalar() or 0
    odds_count = (await db.execute(text("SELECT count(*) FROM unified_odds"))).scalar() or 0
    
    return UniversalResponse(
        status="ok",
        meta=ResponseMeta(
            request_id=get_request_id(),
            db_rows=ev_count + pick_count + odds_count,
            last_sync=datetime.now(timezone.utc)
        ),
        data=[{"ev_signals": ev_count, "model_picks": pick_count, "unified_odds": odds_count}]
    )

@router.get("/logs")
async def get_logs(lines: int = 100):
    """Diagnostic: read last N lines of app log."""
    log_file = "app.log"
    if not os.path.exists(log_file):
        return {"status": "error", "message": f"Log file {log_file} not found"}
    try:
        with open(log_file, "r") as f:
            all_lines = f.readlines()
            return {"status": "ok", "count": len(all_lines), "data": all_lines[-lines:]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/health", response_model=UniversalResponse[dict])
async def meta_health(db: AsyncSession = Depends(get_async_db)):
    heartbeats = await HeartbeatService.get_all_heartbeats(db)
    feeds = [{
        "name": h.feed_name,
        "status": h.status,
        "last_success": h.last_success_at.isoformat() if h.last_success_at else None,
        "rows_today": h.rows_written_today
    } for h in heartbeats]
    
    return UniversalResponse(
        status="ok",
        meta=ResponseMeta(
            request_id=get_request_id(),
            last_sync=datetime.now(timezone.utc)
        ),
        data=[{"service": "meta", "feeds": feeds}]
    )

@router.get("/summary", response_model=UniversalResponse[dict])
async def meta_summary():
    return UniversalResponse(
        status="ok",
        meta=ResponseMeta(request_id=get_request_id()),
        data=[{"app": "Perplex Edge"}]
    )

@router.get("/username")
async def meta_username():
    return {"username": "demo-user"}

@router.get("/force-ev")
async def force_ev_nba(db: AsyncSession = Depends(get_async_db)):
    """Diagnostic endpoint to force EV cycle and show results."""
    from services.ev_service import ev_service
    from sqlalchemy import select
    from models.brain import UnifiedEVSignal

    await ev_service.run_ev_cycle("basketball_nba")
    
    # Also generate picks from these signals
    from services.brain_advanced_service import brain_advanced_service
    await brain_advanced_service.generate_model_picks("basketball_nba", db)

    # Check results
    stmt = select(UnifiedEVSignal).where(UnifiedEVSignal.sport == "basketball_nba")
    res = await db.execute(stmt)
    signals = res.scalars().all()
    
    return {
        "status": "triggered",
        "count": len(signals),
        "debug": "Check /api/meta/inspect for bookmaker names",
        "samples": [
            {
                "player": s.player_name,
                "market": s.market_key,
                "edge": s.edge_percent,
                "book": s.bookmaker
            } for s in signals[:5]
        ]
    }

@router.get("/ingest-nba")
async def ingest_nba_full(db: AsyncSession = Depends(get_async_db)):
    """
    One-click fix for NBA data:
    1. Wipe NBA odds (only basketball_nba)
    2. Run Injest (Normalized)
    3. Run EV Cycle
    4. Run ModelPick promotion
    """
    from services.unified_ingestion import unified_ingestion
    from services.ev_service import ev_service
    from services.brain_advanced_service import brain_advanced_service
    from models import UnifiedOdds
    from sqlalchemy import delete

    # 1. Wipe
    await db.execute(delete(UnifiedOdds).where(UnifiedOdds.sport == "basketball_nba"))
    await db.commit()
    
    # 2. Ingest
    await unified_ingestion.run("basketball_nba")
    
    # 3. EV cycle
    await ev_service.run_ev_cycle("basketball_nba")
    
    # 4. Picks Promotion
    await brain_advanced_service.generate_model_picks("basketball_nba", db)
    
    return {"status": "ok", "message": "NBA Full Cycle Completed"}

@router.get("/seed-dummy-data")
async def seed_dummy_data(db: AsyncSession = Depends(get_async_db)):
    """Seed a dummy EV signal to verify UI pipeline."""
    from models.brain import UnifiedEVSignal
    from datetime import datetime, timezone
    
    dummy = UnifiedEVSignal(
        sport="basketball_nba",
        event_id="dummy_event_123",
        market_key="player_points",
        outcome_key="over",
        player_name="Antigravity Test",
        bookmaker="pinnacle",
        price=1.91,
        line=25.5,
        true_prob=0.55,
        edge_percent=5.5,
        ev_percentage=5.5,
        implied_prob=0.523,
        confidence=0.9,
        engine_version="test-v1",
        recommendation="OVER",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(dummy)
    await db.commit()
    
    # Also promote it to picks
    from services.brain_advanced_service import brain_advanced_service
    await brain_advanced_service.generate_model_picks("basketball_nba", db)
    
    return {"status": "ok", "message": "Dummy signal seeded and promoted"}
