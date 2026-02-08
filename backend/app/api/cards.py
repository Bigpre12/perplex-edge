"""Shared cards API endpoints for public shareable parlay cards."""

import logging
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import SharedCard

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cards", tags=["Cards"])


# =============================================================================
# Pydantic Schemas
# =============================================================================

class CardLeg(BaseModel):
    """A single leg in a shared card."""
    player_name: str
    team_abbr: Optional[str]
    stat_type: str
    line: float
    side: str
    odds: int
    grade: str
    win_prob: float
    edge: float


class CreateCardRequest(BaseModel):
    """Request to create a shareable card."""
    platform: str
    sport_id: Optional[int]
    legs: List[CardLeg]
    total_odds: int
    decimal_odds: float
    parlay_probability: float
    parlay_ev: float
    overall_grade: str
    label: str
    kelly_suggested_units: Optional[float]
    kelly_risk_level: Optional[str]


class CardResponse(BaseModel):
    """Response for a shared card."""
    id: str
    url: str
    platform: str
    sport_id: Optional[int]
    legs: List[dict]
    leg_count: int
    total_odds: int
    decimal_odds: float
    parlay_probability: float
    parlay_ev: float
    overall_grade: str
    label: str
    kelly_suggested_units: Optional[float]
    kelly_risk_level: Optional[str]
    view_count: int
    created_at: str
    settled: bool
    won: Optional[bool]


# =============================================================================
# Helper Functions
# =============================================================================

def generate_card_id() -> str:
    """Generate a short, URL-safe card ID."""
    return secrets.token_urlsafe(8)[:10]


# =============================================================================
# Endpoints
# =============================================================================

@router.post("", response_model=CardResponse)
async def create_card(
    data: CreateCardRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a shareable card from a parlay.
    
    Returns a short URL that can be shared on social media.
    The card is publicly accessible - no auth required to view.
    """
    # Generate unique ID
    card_id = generate_card_id()
    
    # Ensure uniqueness (unlikely collision but check anyway)
    existing = await db.get(SharedCard, card_id)
    while existing:
        card_id = generate_card_id()
        existing = await db.get(SharedCard, card_id)
    
    # Serialize legs
    legs_data = [leg.model_dump() for leg in data.legs]
    
    card = SharedCard(
        id=card_id,
        platform=data.platform,
        sport_id=data.sport_id,
        legs=legs_data,
        leg_count=len(data.legs),
        total_odds=data.total_odds,
        decimal_odds=data.decimal_odds,
        parlay_probability=data.parlay_probability,
        parlay_ev=data.parlay_ev,
        overall_grade=data.overall_grade,
        label=data.label,
        kelly_suggested_units=data.kelly_suggested_units,
        kelly_risk_level=data.kelly_risk_level,
    )
    
    db.add(card)
    await db.commit()
    await db.refresh(card)
    
    logger.info(f"Created shared card {card_id}: {card.leg_count}-leg {card.platform}")
    
    return CardResponse(
        id=card.id,
        url=f"/cards/{card.id}",
        platform=card.platform,
        sport_id=card.sport_id,
        legs=card.legs,
        leg_count=card.leg_count,
        total_odds=card.total_odds,
        decimal_odds=card.decimal_odds,
        parlay_probability=card.parlay_probability,
        parlay_ev=card.parlay_ev,
        overall_grade=card.overall_grade,
        label=card.label,
        kelly_suggested_units=card.kelly_suggested_units,
        kelly_risk_level=card.kelly_risk_level,
        view_count=card.view_count,
        created_at=card.created_at.isoformat() if card.created_at else "",
        settled=card.settled,
        won=card.won,
    )


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a shared card by ID.
    
    This is a public endpoint - no auth required.
    Increments the view count each time.
    """
    card = await db.get(SharedCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found")
    
    # Increment view count
    card.view_count += 1
    await db.commit()
    
    return CardResponse(
        id=card.id,
        url=f"/cards/{card.id}",
        platform=card.platform,
        sport_id=card.sport_id,
        legs=card.legs,
        leg_count=card.leg_count,
        total_odds=card.total_odds,
        decimal_odds=card.decimal_odds,
        parlay_probability=card.parlay_probability,
        parlay_ev=card.parlay_ev,
        overall_grade=card.overall_grade,
        label=card.label,
        kelly_suggested_units=card.kelly_suggested_units,
        kelly_risk_level=card.kelly_risk_level,
        view_count=card.view_count,
        created_at=card.created_at.isoformat() if card.created_at else "",
        settled=card.settled,
        won=card.won,
    )
