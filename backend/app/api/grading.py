"""
Pick Grading API - Automated grading and performance tracking
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.tasks.grade_picks import pick_grader
from app.scripts.backtest_model import ModelBacktester

router = APIRouter(prefix="/api/grading", tags=["grading"])

@router.post("/grade-picks")
async def grade_completed_picks(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Grade all completed picks (background task)."""
    try:
        # Run grading in background
        background_tasks.add_task(pick_grader.grade_completed_picks, db)
        
        return {
            "status": "started",
            "message": "Grading pipeline started in background",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/statistics")
async def get_grading_statistics(
    days_back: int = Query(default=30, description="Days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Get grading statistics for recent picks."""
    try:
        stats = await pick_grader.get_grading_statistics(db, days_back)
        return stats
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/backtest/{year}/{month}")
async def backtest_month(
    year: int,
    month: int,
    sport_id: int = Query(default=30, description="Sport ID"),
    db: AsyncSession = Depends(get_db)
):
    """Backtest model performance for a specific month."""
    try:
        backtester = ModelBacktester()
        results = await backtester.backtest_month(year, month, sport_id)
        return results
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "period": f"{year}-{month:02d}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/model-status")
async def get_model_status(db: AsyncSession = Depends(get_db)):
    """Get comprehensive model status with grading data."""
    try:
        # Get recent grading statistics
        grading_stats = await pick_grader.get_grading_statistics(db, 30)
        
        # Get backtest for recent month
        backtester = ModelBacktester()
        current_date = datetime.now(timezone.utc)
        last_month = current_date.replace(day=1) - timedelta(days=1)
        backtest_results = await backtester.backtest_month(
            last_month.year, last_month.month
        )
        
        # Determine model status
        model_status = "BETA"
        confidence_level = "LOW"
        
        if grading_stats.get("total_graded", 0) >= 100:
            win_rate = grading_stats.get("win_rate", 0)
            if win_rate >= 54:
                model_status = "ADVANCED_BETA"
                confidence_level = "MEDIUM"
            if win_rate >= 56:
                model_status = "PRODUCTION"
                confidence_level = "HIGH"
        
        return {
            "status": "success",
            "model_status": model_status,
            "confidence_level": confidence_level,
            "grading_statistics": grading_stats,
            "backtest_results": backtest_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "disclaimer": "Model performance based on historical data. Past results do not guarantee future performance.",
            "recommendations": get_model_recommendations(model_status, grading_stats, backtest_results)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def get_model_recommendations(status: str, grading_stats: dict, backtest_results: dict) -> list:
    """Get recommendations based on model status."""
    recommendations = []
    
    # Always include responsible gambling
    recommendations.append("Always bet responsibly and within your means.")
    recommendations.append("Use small stakes while model is in beta testing.")
    
    if status == "BETA":
        recommendations.append("Model needs more data before production use.")
        recommendations.append("Monitor performance closely before increasing stakes.")
    
    if grading_stats.get("total_graded", 0) < 100:
        recommendations.append("Need more graded picks for reliable statistics.")
    
    win_rate = grading_stats.get("win_rate", 0)
    if win_rate < 52:
        recommendations.append("Model performance below expectations - review calibration.")
    elif win_rate > 60:
        recommendations.append("Unusually high win rate - verify data integrity.")
    
    if backtest_results.get("status") == "success":
        perf = backtest_results.get("performance", {})
        if perf.get("actual_ev", 0) < 0:
            recommendations.append("Negative actual EV detected - model improvements needed.")
    
    return recommendations
