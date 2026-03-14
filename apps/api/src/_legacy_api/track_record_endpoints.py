from fastapi import APIRouter, Query
from datetime import datetime, timezone
import logging
from services.proof_engine import proof_engine

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/performance")
async def get_performance_metrics(days: int = Query(30, description="Number of days to look back")):
    """Get detailed performance metrics for the track record."""
    metrics = await proof_engine.get_performance_metrics(days=days)
    return {
        "performance": metrics,
        "validation_status": "complete" if not metrics.get("is_mock") else "simulated",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/recent")
async def get_recent_results(limit: int = Query(20, description="Number of recent picks to show")):
    """Get recent picks with their graded results."""
    results = await proof_engine.get_recent_results(limit=limit)
    return {
        "recent_picks": results,
        "total": len(results),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/summary")
async def get_track_record_summary():
    """Get high-level track record summary for dashboard / landing page."""
    # Combine 30d and All-Time (approx 365d)
    m30 = await proof_engine.get_performance_metrics(days=30)
    m365 = await proof_engine.get_performance_metrics(days=365)
    
    return {
        "metrics_30d": m30,
        "metrics_all_time": m365,
        "status": "active",
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
