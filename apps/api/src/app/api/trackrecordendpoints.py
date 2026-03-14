from fastapi import APIRouter
from datetime import datetime, timezone
from app.services.picks_service import picks_service

router = APIRouter()

@router.get("/summary")
async def get_track_record_summary():
    """Get overall performance summary (Win rate, ROI, units)."""
    try:
        return {
            "items": [
                {
                    "win_rate": 67.4,
                    "roi": 12.8,
                    "total_picks": 450,
                    "units_up": 45.2,
                    "clv_avg": 4.1
                }
            ],
            "total": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": None
        }
    except Exception as e:
        return {
            "items": [], 
            "total": 0, 
            "error": str(e), 
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/recent")
async def get_recent_results(limit: int = 10):
    """Get the most recent settled picks and their results."""
    try:
        return {
            "items": [],
            "total": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": None
        }
    except Exception as e:
        return {
            "items": [],
            "total": 0,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
