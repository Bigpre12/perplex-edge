from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.prop import Prop
from schemas.prop import PropOut, PropsScoredResponse
from datetime import datetime, timedelta
from sqlalchemy import select, desc, or_, and_
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
@router.get("/")
async def list_props(
    sport: str = "basketball_nba",
    market: Optional[str] = None,
    min_ev: float = 0.0,
    search: Optional[str] = None,
    limit: int = 50,
):
    """Returns top props for a sport using the enhanced PropsService (Market + EV)."""
    from services.props_service import get_all_props
    try:
        # Get all props for the sport with EV data
        items = await get_all_props(sport_filter=sport)
        
        # 1. Market Filter
        if market:
            items = [p for p in items if p.get("market_key") == market]
            
        # 2. EV Filter
        if min_ev > 0:
            items = [p for p in items if (p.get("recommendation") or {}).get("ev", 0.0) >= min_ev]
            
        # 3. Search Filter
        if search:
            search_low = search.lower()
            items = [p for p in items if 
                search_low in (p.get("player_name") or "").lower() or 
                search_low in (p.get("market_key") or "").lower()]
                
        # 4. Limit
        items = items[:limit]
        
        if not items:
            return {
                "data": [],
                "results": [],
                "status": "awaiting_ingest",
                "message": "No live props match these filters right now."
            }
            
        return {"data": items, "results": items, "status": "ok", "count": len(items)}
    except Exception as e:
        logger.error(f"Error listing props for {sport}: {e}")
        return {
            "data": [],
            "results": [],
            "status": "error",
            "message": str(e)
        }

@router.get("/scored")
async def scored_props(db: AsyncSession = Depends(get_db)):
    """Returns recently completed props for the ledger/history (last 72h)."""
    try:
        now = datetime.utcnow()
        stmt = select(Prop).where(
            Prop.is_scored == True,
            Prop.created_at >= now - timedelta(hours=72)
        ).order_by(desc(Prop.created_at)).limit(50)
        
        result = await db.execute(stmt)
        items = result.scalars().all()
        return {"data": items, "results": items}
    except Exception as e:
        logger.error(f"Error listing scored props: {e}")
        return {"data": [], "results": []}
