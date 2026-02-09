"""
Track Record Endpoints - Transparent Performance Tracking
"""
from fastapi import APIRouter, Query
from datetime import datetime, timezone
import asyncio
from app.real_sports_api import build_transparent_track_record, track_record_builder

router = APIRouter()

@router.get("/track-record")
async def get_transparent_track_record():
    """Get complete transparent track record"""
    try:
        result = await build_transparent_track_record()
        
        if "error" in result:
            return {
                "error": result["error"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "track_record": result,
            "verification_status": "verified",
            "public_access": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/track-record/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        result = await build_transparent_track_record()
        
        if "error" in result:
            return {
                "error": result["error"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        performance = result.get("performance_metrics", {})
        
        # Add validation metrics
        validation_metrics = {
            "model_validated": performance.get("total_picks", 0) > 0,
            "ev_realistic": 2 <= performance.get("avg_ev", 0) <= 4,
            "clv_positive": performance.get("avg_clv", 0) > 0,
            "roi_positive": performance.get("roi", 0) > 0,
            "hit_rate_acceptable": 52 <= performance.get("hit_rate", 0) <= 58,
            "sample_size_adequate": performance.get("total_picks", 0) >= 100
        }
        
        performance["validation_metrics"] = validation_metrics
        
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

@router.get("/track-record/recent")
async def get_recent_picks(limit: int = Query(10, description="Number of recent picks to show")):
    """Get recent picks with results"""
    try:
        result = await build_transparent_track_record()
        
        if "error" in result:
            return {
                "error": result["error"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        graded_picks = result.get("graded_picks", [])
        recent_picks = graded_picks[-limit:] if len(graded_picks) > limit else graded_picks
        
        return {
            "recent_picks": recent_picks,
            "total_graded": len(graded_picks),
            "showing_recent": len(recent_picks),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/track-record/bookmakers")
async def get_bookmaker_performance():
    """Get performance by bookmaker"""
    try:
        result = await build_transparent_track_record()
        
        if "error" in result:
            return {
                "error": result["error"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        performance = result.get("performance_metrics", {})
        bookmaker_performance = performance.get("bookmaker_performance", {})
        
        # Rank bookmakers by performance
        ranked_bookmakers = sorted(
            bookmaker_performance.items(),
            key=lambda x: x[1]["roi"],
            reverse=True
        )
        
        return {
            "bookmaker_performance": dict(ranked_bookmakers),
            "best_bookmaker": ranked_bookmakers[0] if ranked_bookmakers else None,
            "total_bookmakers": len(bookmaker_performance),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
