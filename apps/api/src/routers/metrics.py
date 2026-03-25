from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db as get_async_db # standardizing on get_db but keeping name for compatibility
from services.dashboard import get_dashboard_metrics
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("")
async def metrics(db: AsyncSession = Depends(get_async_db)):
    """Returns core system metrics and health diagnostics."""
    try:
        from sqlalchemy import select, func, text
        from models import UnifiedOdds, UnifiedEVSignal
        from datetime import datetime, timezone
        
        # 1. Basic Health Check
        health_check = await db.execute(text("SELECT 1"))
        db_connected = health_check.scalar() == 1
        
        # 2. Last Ingest Time
        last_ingest_stmt = select(func.max(UnifiedOdds.created_at))
        last_ingest = (await db.execute(last_ingest_stmt)).scalar()
        
        # 3. Row Counts
        odds_count_stmt = select(func.count(UnifiedOdds.id))
        odds_count = (await db.execute(odds_count_stmt)).scalar() or 0
        
        ev_count_stmt = select(func.count(UnifiedEVSignal.id))
        ev_count = (await db.execute(ev_count_stmt)).scalar() or 0

        # Current Dashboard Metrics (Fallback to placeholders if empty)
        metrics_data = await get_dashboard_metrics(db)
        
        return {
            **metrics_data,
            "db_connected": db_connected,
            "last_odds_ingest_at": last_ingest.isoformat() if last_ingest else "Never",
            "counts": {
                **metrics_data.get("counts", {}),
                "odds_rows": odds_count,
                "ev_signals": ev_count,
            },
            "status": "healthy" if odds_count > 0 else "awaiting_ingest",
            "inference_status": "ACTIVE" if ev_count > 0 else "IDLE",
            "pipeline_status": "ACTIVE",
            "stream_status": "SYNCED"
        }
    except Exception as e:
        import traceback
        return {
            "status": "degraded",
            "error": str(e),
            "db_connected": False,
            "last_odds_ingest_at": "Error"
        }

@router.get("/picks-stats")
async def picks_stats():
    """Returns pick statistics (model performance) for the leaderboard page."""
    from services.hit_rate_service import hit_rate_service
    
    summary = await hit_rate_service.get_summary("all")
    
    return {
        "models": [
            {
                "name": "Lucrix Alpha Engine", 
                "sport": "ALL MARKET", 
                "hit_rate": summary.get("overall_hit_rate", 0.0), 
                "profit": summary.get("roi", 0.0)
            }
        ],
        "top_pickers": [],
        "consensus_picks": [],
        "total_active_picks": summary.get("graded_picks", 0)
    }
