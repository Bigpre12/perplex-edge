"""
Parlay Forwarding API - Routes to working ultra-simple parlay builder
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.ultra_simple_parlays import router as ultra_simple_parlay_router

router = APIRouter(prefix="/api/parlays", tags=["parlays"])

# Forward all parlay requests to ultra-simple parlay builder
@router.get("/")
async def get_parlays_forward(
    sport_id: int = Query(None, description="Filter by sport ID"),
    min_ev: float = Query(default=0.05, description="Minimum expected value"),
    min_confidence: float = Query(default=0.6, description="Minimum confidence score"),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Forward parlay requests to ultra-simple parlay builder."""
    # Forward to ultra-simple parlay builder
    return await ultra_simple_parlay_router.get_ultra_simple_parlays(
        sport_id=sport_id,
        min_ev=min_ev,
        min_confidence=min_confidence,
        limit=limit,
        db=db
    )

@router.get("/build")
async def build_parlays_forward(
    sport_id: int = Query(None, description="Filter by sport ID"),
    leg_count: int = Query(default=2, ge=2, le=4, description="Number of legs in parlay"),
    min_ev: float = Query(default=0.05, description="Minimum expected value"),
    min_confidence: float = Query(default=0.6, description="Minimum confidence score"),
    limit: int = Query(default=10, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Forward build parlay requests to ultra-simple parlay builder."""
    return await ultra_simple_parlay_router.build_simple_parlays(
        sport_id=sport_id,
        leg_count=leg_count,
        min_ev=min_ev,
        min_confidence=min_confidence,
        limit=limit,
        db=db
    )

@router.get("/sports")
async def get_sports_parlays_forward(
    sport_id: int = Query(..., description="Sport ID (required)"),
    min_ev: float = Query(default=0.05, description="Minimum expected value"),
    min_confidence: float = Query(default=0.6, description="Minimum confidence score"),
    limit: int = Query(default=10, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Forward sports parlay requests to ultra-simple parlay builder."""
    return await ultra_simple_parlay_router.get_sports_parlays(
        sport_id=sport_id,
        min_ev=min_ev,
        min_confidence=min_confidence,
        limit=limit,
        db=db
    )

@router.get("/player-props")
async def get_player_props_parlays_forward(
    player_id: int = Query(None, description="Player ID (optional)"),
    sport_id: int = Query(None, description="Sport ID (optional)"),
    min_ev: float = Query(default=0.05, description="Minimum expected value"),
    min_confidence: float = Query(default=0.6, description="Minimum confidence score"),
    limit: int = Query(default=10, le=20),
    db: AsyncSession = Depends(None)
):
    """Forward player props parlay requests to ultra-simple parlay builder."""
    return await ultra_simple_parlay_router.get_player_props_parlays(
        player_id=player_id,
        sport_id=sport_id,
        min_ev=min_ev,
        min_confidence=min_confidence,
        limit=limit,
        db=db
    )

@router.get("/available-picks")
async def get_available_picks_forward(
    sport_id: int = Query(None, description="Filter by sport ID"),
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(None)
):
    """Forward available picks requests to ultra-simple parlay builder."""
    return await ultra_simple_parlay_router.get_available_picks(
        sport_id=sport_id,
        limit=limit,
        db=db
    )
