"""
Validation endpoints for model performance
"""
from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import List, Dict, Any
from real_sports_api import build_transparent_track_record

router = APIRouter()

@router.get("/picks")
async def get_validated_picks(
    limit: int = Query(50, description="Number of picks to return")
):
    """Get picks with real data validation"""
    try:
        # Use the same source as track-record/recent for consistency
        data = await build_transparent_track_record()
        picks = data.get("graded_picks", [])
        
        return {
            "picks": picks[:limit],
            "total_picks": len(picks),
            "graded_picks": len(picks),
            "validation_status": "complete",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/performance")
async def get_validation_performance(days: int = Query(30, description="Days of performance data")):
    """Get model validation performance metrics"""
    try:
        # Use the same source as track-record/recent for consistency
        data = await build_transparent_track_record()
        performance = data.get("performance_metrics", {})
        
        if not performance:
            return {
                "performance": {
                    "hit_rate": 0,
                    "avg_ev": 0,
                    "clv": 0,
                    "roi": 0,
                    "total_picks": 0,
                    "graded_picks": 0
                },
                "validation_status": "pending",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        return {
            "performance": performance,
            "validation_status": "complete",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/track-record")
async def get_track_record():
    """Get transparent track record"""
    try:
        data = await build_transparent_track_record()
        return data
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
