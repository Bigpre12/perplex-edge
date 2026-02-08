"""
Line Movement API - Track sharp money and market movements
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.line_movement_tracker import LineMovementTracker

router = APIRouter(prefix="/api/line-movement", tags=["line-movement"])

@router.get("/track/{sport_id}")
async def track_line_movements(
    sport_id: int,
    hours_back: int = Query(default=24, description="Hours to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Track line movements for a sport."""
    try:
        tracker = LineMovementTracker()
        movements_data = await tracker.track_line_movements(db, sport_id, hours_back)
        return movements_data
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/alerts/{sport_id}")
async def get_line_movement_alerts(
    sport_id: int = Query(default=30, description="Sport ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get line movement alerts for sharp money activity."""
    try:
        tracker = LineMovementTracker()
        alerts = await tracker.get_line_movement_alerts(db, sport_id)
        return alerts
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
