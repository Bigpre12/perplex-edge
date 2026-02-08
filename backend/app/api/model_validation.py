"""
Model Validation API - Backtesting and performance validation
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.model_validation import model_validator

router = APIRouter(prefix="/api/validation", tags=["validation"])

@router.get("/calibration/{sport_id}")
async def validate_model_calibration(
    sport_id: int = Path(description="Sport ID to validate"),
    days_back: int = Query(default=30, description="Days of historical data to use"),
    db: AsyncSession = Depends(get_db)
):
    """Validate model calibration on historical data."""
    try:
        result = await model_validator.validate_model_calibration(db, sport_id, days_back)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/clv/{sport_id}")
async def calculate_clv_performance(
    sport_id: int = Path(description="Sport ID to analyze"),
    days_back: int = Query(default=30, description="Days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Calculate CLV (Closing Line Value) performance."""
    try:
        result = await model_validator.calculate_clv_performance(db, sport_id, days_back)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/status/{sport_id}")
async def get_model_status_report(
    sport_id: int = Path(description="Sport ID to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Generate comprehensive model status report."""
    try:
        result = await model_validator.generate_model_status_report(db, sport_id)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
