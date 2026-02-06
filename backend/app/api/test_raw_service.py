"""
Direct test of raw SQL parlay service.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.parlay_service_raw import build_parlays

router = APIRouter(prefix="/api/test-raw-service", tags=["test-raw-service"])


@router.get("/direct-test")
async def test_raw_parlay_service_directly(
    sport_id: int = Query(30),
    db: AsyncSession = Depends(get_db)
):
    """Test raw parlay service directly."""
    try:
        result = await build_parlays(
            db=db,
            sport_id=sport_id,
            leg_count=3,
            include_100_pct=False,
            min_grade="C",
            max_results=5,
            block_correlated=False,
            max_correlation_risk="HIGH"
        )
        
        return {
            "success": True,
            "total_candidates": result.total_candidates,
            "parlays": len(result.parlays),
            "filters_applied": result.filters_applied,
            "sample_parlay": result.parlays[0] if result.parlays else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sport_id": sport_id
        }
