"""
Multi-sport parlay API endpoints.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.parlay_service_multisport import build_parlays_multisport, get_supported_sports

router = APIRouter(prefix="/api/multisport", tags=["multisport"])


@router.get("/supported-sports")
async def get_supported_sports_endpoint(
    db: AsyncSession = Depends(get_db)
):
    """Get list of supported sports with available candidates."""
    try:
        sports = await get_supported_sports(db)
        return {
            "supported_sports": sports,
            "total_sports": len(sports),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "supported_sports": []
        }


@router.get("/sports/{sport_id}/parlays/builder")
async def build_multisport_parlay(
    sport_id: int,
    leg_count: int = Query(3, ge=2, le=15, description="Number of legs (2-15)"),
    include_100_pct: bool = Query(False, description="Require at least one 100% hit rate leg"),
    min_leg_grade: str = Query("C", description="Minimum grade per leg (A, B, C, D)"),
    max_results: int = Query(5, ge=1, le=10, description="Number of parlays to return"),
    block_correlated: bool = Query(True, description="Block high-correlation parlays"),
    max_correlation_risk: str = Query("MEDIUM", description="Max allowed: LOW, MEDIUM, HIGH, CRITICAL"),
    db: AsyncSession = Depends(get_db)
):
    """
    Build optimized parlays for any supported sport.
    
    This endpoint supports all sports with proper data integrity.
    """
    try:
        result = await build_parlays_multisport(
            db=db,
            sport_id=sport_id,
            leg_count=leg_count,
            include_100_pct=include_100_pct,
            min_grade=min_grade.upper(),
            max_results=max_results,
            block_correlated=block_correlated,
            max_correlation_risk=max_correlation_risk.upper()
        )
        
        return result
        
    except Exception as e:
        from app.schemas.public import ParlayBuilderResponse
        return ParlayBuilderResponse(
            parlays=[],
            total_candidates=0,
            leg_count=leg_count,
            filters_applied={
                "min_leg_grade": min_grade.upper(),
                "include_100_pct": include_100_pct,
                "sport_id": sport_id,
                "error": str(e)
            }
        )
