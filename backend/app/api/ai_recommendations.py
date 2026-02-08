"""API endpoint for AI-powered recommendations."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.ai.models import AIRecommendationsResponse, RiskProfile
from app.ai.service import get_ai_recommendations

logger = logging.getLogger(__name__)

router = APIRouter()

# =============================================================================
# Request / Response Models
# =============================================================================

class AIRecommendationsRequest(BaseModel):
    """Request body for AI recommendations."""
    sport_id: int
    date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD (defaults to today)")
    risk_profile: str = Field("moderate", description="conservative / moderate / aggressive")
    min_ev: float = Field(0.03, ge=0.0, le=1.0, description="Minimum EV threshold")
    books: Optional[list[str]] = Field(None, description="Preferred sportsbooks")
    markets: Optional[list[str]] = Field(None, description="Stat types to include (PTS, REB, AST, etc.)")
    max_props: int = Field(30, ge=1, le=100, description="Max props to analyze")

# =============================================================================
# Endpoints
# =============================================================================

@router.post(
    "/recommendations",
    response_model=AIRecommendationsResponse,
    tags=["ai"],
    summary="Get AI-powered prop recommendations",
)
async def ai_recommendations(
    request: AIRecommendationsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered prop recommendations for a given sport and date.

    Pulls the top props from the database, sends them to the AI analysis
    layer, and returns normalized recommendations with edge percentages,
    confidence labels, and optional parlay suggestions.

    The response clearly distinguishes between model-only and AI-assisted
    signals via the `signal_source` field.
    """
    # Validate risk_profile
    try:
        RiskProfile(request.risk_profile)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid risk_profile '{request.risk_profile}'. Must be one of: conservative, moderate, aggressive",
        )

    result = await get_ai_recommendations(
        db=db,
        sport_id=request.sport_id,
        date=request.date,
        risk_profile=request.risk_profile,
        min_ev=request.min_ev,
        books=request.books,
        markets=request.markets,
        max_props=request.max_props,
    )

    return result
