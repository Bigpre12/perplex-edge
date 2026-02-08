"""Watchlist API endpoints for saving and managing filter presets."""

import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Watchlist, ModelPick, Game, Market

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/watchlists", tags=["Watchlists"])

# =============================================================================
# Pydantic Schemas
# =============================================================================

class WatchlistFilters(BaseModel):
    """Filter criteria for a watchlist."""
    sport_id: Optional[int] = None
    stat_type: Optional[str] = None
    side: Optional[str] = None  # "over" or "under"
    min_ev: Optional[float] = None
    min_confidence: Optional[float] = None
    risk_levels: Optional[str] = None  # Comma-separated: "STANDARD,CONFIDENT,STRONG"

class WatchlistCreate(BaseModel):
    """Request body for creating a watchlist."""
    name: str
    filters: WatchlistFilters
    alert_enabled: bool = False
    alert_discord_webhook: Optional[str] = None
    alert_email: Optional[str] = None

class WatchlistUpdate(BaseModel):
    """Request body for updating a watchlist."""
    name: Optional[str] = None
    filters: Optional[WatchlistFilters] = None
    alert_enabled: Optional[bool] = None
    alert_discord_webhook: Optional[str] = None
    alert_email: Optional[str] = None

class WatchlistResponse(BaseModel):
    """Response for a single watchlist."""
    id: int
    name: str
    filters: dict
    alert_enabled: bool
    alert_discord_webhook: Optional[str]
    alert_email: Optional[str]
    sport_id: Optional[int]
    last_check_at: Optional[str]
    last_match_count: int
    created_at: str
    # Computed fields
    current_match_count: int = 0
    new_matches_since_last_check: int = 0

class WatchlistListResponse(BaseModel):
    """Response for listing watchlists."""
    items: List[WatchlistResponse]
    total: int

# =============================================================================
# Helper Functions
# =============================================================================

async def count_matching_picks(
    db: AsyncSession,
    filters: dict,
) -> int:
    """Count how many current picks match the watchlist filters."""
    from sqlalchemy import and_
    
    conditions = [ModelPick.is_active == True]
    
    sport_id = filters.get("sport_id")
    if sport_id:
        conditions.append(ModelPick.sport_id == sport_id)  # Filter on ModelPick to prevent cross-sport bleed
        conditions.append(Game.sport_id == sport_id)
    
    stat_type = filters.get("stat_type")
    if stat_type:
        conditions.append(Market.stat_type == stat_type)
    
    min_ev = filters.get("min_ev")
    if min_ev is not None:
        conditions.append(ModelPick.expected_value >= min_ev)
    
    min_confidence = filters.get("min_confidence")
    if min_confidence is not None:
        conditions.append(ModelPick.confidence_score >= min_confidence)
    
    side = filters.get("side")
    if side:
        conditions.append(ModelPick.side == side)
    
    # Build query
    result = await db.execute(
        select(func.count(ModelPick.id))
        .join(Game, ModelPick.game_id == Game.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(and_(*conditions))
    )
    
    return result.scalar() or 0

# =============================================================================
# CRUD Endpoints
# =============================================================================

@router.post("", response_model=WatchlistResponse)
async def create_watchlist(
    data: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new watchlist (saved filter preset).
    
    The watchlist stores filter criteria that can be applied to the
    player props endpoint. When you load a watchlist, it applies those
    filters automatically.
    
    Optionally enable alerts to get notified when new picks match.
    """
    watchlist = Watchlist(
        name=data.name,
        filters=data.filters.model_dump(exclude_none=True),
        alert_enabled=data.alert_enabled,
        alert_discord_webhook=data.alert_discord_webhook,
        alert_email=data.alert_email,
        sport_id=data.filters.sport_id,
    )
    
    db.add(watchlist)
    await db.commit()
    await db.refresh(watchlist)
    
    # Count current matches
    match_count = await count_matching_picks(db, watchlist.filters)
    
    logger.info(f"Created watchlist {watchlist.id}: {watchlist.name}")
    
    return WatchlistResponse(
        id=watchlist.id,
        name=watchlist.name,
        filters=watchlist.filters,
        alert_enabled=watchlist.alert_enabled,
        alert_discord_webhook=watchlist.alert_discord_webhook,
        alert_email=watchlist.alert_email,
        sport_id=watchlist.sport_id,
        last_check_at=watchlist.last_check_at.isoformat() if watchlist.last_check_at else None,
        last_match_count=watchlist.last_match_count,
        created_at=watchlist.created_at.isoformat() if watchlist.created_at else datetime.now().isoformat(),
        current_match_count=match_count,
        new_matches_since_last_check=max(0, match_count - watchlist.last_match_count),
    )

@router.get("", response_model=WatchlistListResponse)
async def list_watchlists(
    sport_id: Optional[int] = Query(None, description="Filter by sport"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all watchlists with current match counts.
    
    Returns each watchlist with:
    - current_match_count: How many picks currently match the filters
    - new_matches_since_last_check: How many new matches since last time you checked
    """
    conditions = []
    if sport_id:
        conditions.append(Watchlist.sport_id == sport_id)
    
    query = select(Watchlist).order_by(Watchlist.created_at.desc())
    if conditions:
        from sqlalchemy import and_
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    watchlists = result.scalars().all()
    
    items = []
    for w in watchlists:
        match_count = await count_matching_picks(db, w.filters)
        items.append(WatchlistResponse(
            id=w.id,
            name=w.name,
            filters=w.filters,
            alert_enabled=w.alert_enabled,
            alert_discord_webhook=w.alert_discord_webhook,
            alert_email=w.alert_email,
            sport_id=w.sport_id,
            last_check_at=w.last_check_at.isoformat() if w.last_check_at else None,
            last_match_count=w.last_match_count,
            created_at=w.created_at.isoformat() if w.created_at else datetime.now().isoformat(),
            current_match_count=match_count,
            new_matches_since_last_check=max(0, match_count - w.last_match_count),
        ))
    
    return WatchlistListResponse(items=items, total=len(items))

@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single watchlist by ID."""
    watchlist = await db.get(Watchlist, watchlist_id)
    if not watchlist:
        raise HTTPException(status_code=404, detail=f"Watchlist {watchlist_id} not found")
    
    match_count = await count_matching_picks(db, watchlist.filters)
    
    return WatchlistResponse(
        id=watchlist.id,
        name=watchlist.name,
        filters=watchlist.filters,
        alert_enabled=watchlist.alert_enabled,
        alert_discord_webhook=watchlist.alert_discord_webhook,
        alert_email=watchlist.alert_email,
        sport_id=watchlist.sport_id,
        last_check_at=watchlist.last_check_at.isoformat() if watchlist.last_check_at else None,
        last_match_count=watchlist.last_match_count,
        created_at=watchlist.created_at.isoformat() if watchlist.created_at else datetime.now().isoformat(),
        current_match_count=match_count,
        new_matches_since_last_check=max(0, match_count - watchlist.last_match_count),
    )

@router.patch("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: int,
    data: WatchlistUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a watchlist."""
    watchlist = await db.get(Watchlist, watchlist_id)
    if not watchlist:
        raise HTTPException(status_code=404, detail=f"Watchlist {watchlist_id} not found")
    
    if data.name is not None:
        watchlist.name = data.name
    if data.filters is not None:
        watchlist.filters = data.filters.model_dump(exclude_none=True)
        watchlist.sport_id = data.filters.sport_id
    if data.alert_enabled is not None:
        watchlist.alert_enabled = data.alert_enabled
    if data.alert_discord_webhook is not None:
        watchlist.alert_discord_webhook = data.alert_discord_webhook
    if data.alert_email is not None:
        watchlist.alert_email = data.alert_email
    
    await db.commit()
    await db.refresh(watchlist)
    
    match_count = await count_matching_picks(db, watchlist.filters)
    
    logger.info(f"Updated watchlist {watchlist_id}")
    
    return WatchlistResponse(
        id=watchlist.id,
        name=watchlist.name,
        filters=watchlist.filters,
        alert_enabled=watchlist.alert_enabled,
        alert_discord_webhook=watchlist.alert_discord_webhook,
        alert_email=watchlist.alert_email,
        sport_id=watchlist.sport_id,
        last_check_at=watchlist.last_check_at.isoformat() if watchlist.last_check_at else None,
        last_match_count=watchlist.last_match_count,
        created_at=watchlist.created_at.isoformat() if watchlist.created_at else datetime.now().isoformat(),
        current_match_count=match_count,
        new_matches_since_last_check=max(0, match_count - watchlist.last_match_count),
    )

@router.delete("/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a watchlist."""
    watchlist = await db.get(Watchlist, watchlist_id)
    if not watchlist:
        raise HTTPException(status_code=404, detail=f"Watchlist {watchlist_id} not found")
    
    await db.delete(watchlist)
    await db.commit()
    
    logger.info(f"Deleted watchlist {watchlist_id}")
    
    return {"status": "deleted", "watchlist_id": watchlist_id}

@router.post("/{watchlist_id}/mark-checked")
async def mark_watchlist_checked(
    watchlist_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a watchlist as checked (resets new_matches counter).
    
    Call this when the user loads/views a watchlist to clear the
    "new matches" badge.
    """
    watchlist = await db.get(Watchlist, watchlist_id)
    if not watchlist:
        raise HTTPException(status_code=404, detail=f"Watchlist {watchlist_id} not found")
    
    match_count = await count_matching_picks(db, watchlist.filters)
    
    watchlist.last_check_at = datetime.now(timezone.utc).replace(tzinfo=None)
    watchlist.last_match_count = match_count
    
    await db.commit()
    
    return {"status": "checked", "match_count": match_count}
