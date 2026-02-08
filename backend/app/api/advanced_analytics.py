"""
Advanced Analytics API - Comprehensive integration of all Phase 2 features
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.advanced_analytics_integration import advanced_analytics_integration

router = APIRouter(prefix="/api/advanced-analytics", tags=["advanced-analytics"])

@router.get("/pick/{pick_id}")
async def analyze_pick_comprehensive(
    pick_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Perform comprehensive analysis of a single pick using all advanced features."""
    try:
        result = await advanced_analytics_integration.analyze_pick_comprehensive(db, pick_id)
        return {
            "status": "success",
            "comprehensive_analysis": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game/{game_id}")
async def analyze_game_comprehensive(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Perform comprehensive analysis of all picks in a game."""
    try:
        result = await advanced_analytics_integration.analyze_game_comprehensive(db, game_id)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/summary/{sport_id}")
async def get_analytics_summary(
    sport_id: int = Query(default=30, description="Sport ID"),
    hours_back: int = Query(default=24, description="Hours to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics summary for recent picks."""
    try:
        summary = await advanced_analytics_integration.get_analytics_summary(db, sport_id, hours_back)
        return summary
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/optimize-parlay/{game_id}")
async def optimize_parlay_with_analytics(
    game_id: int,
    max_legs: int = Query(default=3, description="Maximum number of parlay legs"),
    db: AsyncSession = Depends(get_db)
):
    """Optimize parlay using all advanced analytics features."""
    try:
        result = await advanced_analytics_integration.optimize_parlay_with_analytics(db, game_id, max_legs)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/status")
async def get_advanced_analytics_status():
    """Get status of all advanced analytics features."""
    try:
        return {
            "status": "active",
            "features": {
                "probability_calibration": "active",
                "line_movement_tracking": "active",
                "multi_book_shopping": "active",
                "correlation_analysis": "active",
                "performance_attribution": "active",
                "clv_tracking": "active",
                "comprehensive_integration": "active"
            },
            "capabilities": [
                "Calibrated probability calculations",
                "Sharp money detection",
                "Multi-book odds comparison",
                "Same-game correlation analysis",
                "Performance factor attribution",
                "CLV tracking and ROI calculation",
                "Comprehensive parlay optimization"
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
