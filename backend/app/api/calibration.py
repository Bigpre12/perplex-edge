"""
Probability Calibration API - Fix overconfident model predictions
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.probability_calibration import ProbabilityCalibrator

router = APIRouter(prefix="/api/calibration", tags=["calibration"])

@router.get("/metrics/{sport_id}")
async def get_calibration_metrics(
    sport_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get current calibration metrics for a sport."""
    try:
        calibrator = ProbabilityCalibrator()
        metrics = await calibrator.get_calibration_metrics(db, sport_id)
        return metrics
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/train/{sport_id}")
async def train_calibration_model(
    sport_id: int,
    days_back: int = Query(default=90, description="Days of historical data for training"),
    db: AsyncSession = Depends(get_db)
):
    """Train isotonic regression calibration model."""
    try:
        calibrator = ProbabilityCalibrator()
        training_result = await calibrator.fit_isotonic_calibration(db, sport_id, days_back)
        return training_result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/calibrate")
async def calibrate_probability(
    model_prob: float = Query(..., description="Model probability (0-1)"),
    implied_prob: float = Query(..., description="Implied probability from odds (0-1)"),
    sample_size: int = Query(default=10, description="Sample size used for prediction"),
    market_type: str = Query(default="player_props", description="Market type"),
):
    """Calibrate a single probability using market efficiency."""
    try:
        calibrator = ProbabilityCalibrator()
        calibrated_prob = calibrator.calibrate_probability(
            model_prob, implied_prob, sample_size, market_type
        )
        
        confidence_interval = calibrator.calculate_confidence_interval(
            calibrated_prob, sample_size
        )
        
        return {
            "status": "success",
            "model_probability": model_prob,
            "implied_probability": implied_prob,
            "calibrated_probability": calibrated_prob,
            "confidence_interval": confidence_interval,
            "sample_size": sample_size,
            "market_type": market_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
