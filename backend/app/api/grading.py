"""
Pick Grading API - Automated grading and performance tracking
Uses sync connections for reliability
"""

import random
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, text, create_engine

from app.core.database import get_db, get_engine
from app.tasks.grade_picks import pick_grader
from app.scripts.backtest_model import ModelBacktester
from app.models import ModelPick

router = APIRouter(prefix="/api/grading", tags=["grading"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def grading_health():
    """Simple health check that doesn't need database"""
    return {"status": "ok", "router": "grading", "timestamp": datetime.now(timezone.utc).isoformat()}


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


@router.get("/debug/picks-status")
async def debug_picks_status(db: AsyncSession = Depends(get_db)):
    """Check current state of picks in database."""
    try:
        result = await db.execute(
            select(
                func.count(ModelPick.id).label('total'),
                func.count(ModelPick.id).filter(ModelPick.sport_id == 30).label('nba_total'),
                func.count(ModelPick.id).filter(
                    (ModelPick.sport_id == 30) & (ModelPick.is_active == True)
                ).label('nba_active'),
                func.count(ModelPick.id).filter(
                    (ModelPick.sport_id == 30) & (ModelPick.expected_value > 0.15)
                ).label('nba_high_ev'),
                func.avg(ModelPick.expected_value).filter(
                    ModelPick.sport_id == 30
                ).label('nba_avg_ev')
            )
        )
        
        row = result.first()
        
        return {
            "status": "success",
            "total_picks": row.total or 0,
            "nba_total": row.nba_total or 0,
            "nba_active": row.nba_active or 0,
            "nba_hidden_high_ev": row.nba_high_ev or 0,
            "nba_avg_ev_pct": round(float(row.nba_avg_ev or 0) * 100, 2),
            "diagnosis": "All picks hidden" if (row.nba_active or 0) == 0 else "Some picks active",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.post("/admin/activate-test-picks")
async def activate_test_picks(
    count: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Emergency fix: Activate some picks with realistic EV for testing.
    This updates existing picks to have 3% EV instead of 81%.
    """
    try:
        # Get random NBA pick IDs
        result = await db.execute(
            select(ModelPick.id)
            .where(ModelPick.sport_id == 30)
            .limit(count * 3)  # Get extra to select from
        )
        
        all_ids = [row[0] for row in result.all()]
        
        if not all_ids:
            return {
                "status": "error",
                "message": "No NBA picks found in database",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Randomly select the requested count
        random.shuffle(all_ids)
        selected_ids = all_ids[:min(count, len(all_ids))]
        
        # Update them
        await db.execute(
            update(ModelPick)
            .where(ModelPick.id.in_(selected_ids))
            .values(
                expected_value=0.03,  # 3% EV (realistic)
                is_active=True
            )
        )
        
        await db.commit()
        
        return {
            "status": "success",
            "message": f"Activated {len(selected_ids)} picks",
            "count": len(selected_ids),
            "ev_set_to": "3%",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.post("/admin/delete-bad-picks")
async def delete_bad_picks(db: AsyncSession = Depends(get_db)):
    """Delete all picks with EV > 15% (impossible values)."""
    try:
        result = await db.execute(
            select(func.count(ModelPick.id))
            .where(ModelPick.expected_value > 0.15)
        )
        count_before = result.scalar()
        
        # Delete them
        await db.execute(
            text("DELETE FROM model_picks WHERE expected_value > 0.15")
        )
        await db.commit()
        
        return {
            "status": "success",
            "message": f"Deleted {count_before} picks with EV > 15%",
            "deleted_count": count_before,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
