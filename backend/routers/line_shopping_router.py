from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from models.props import PropLine, PropOdds
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/api/shop", tags=["line_shopping"])

@router.get("/best-line")
async def get_best_line(
    player_name: str, 
    stat_type: str, 
    side: str = Query("over", regex="^(over|under)$"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Finds the absolute best line and price for a player prop across all integrated books.
    """
    # 1. Find the prop line
    stmt = select(PropLine).where(
        PropLine.player_name.ilike(f"%{player_name}%"),
        PropLine.stat_type == stat_type,
        PropLine.is_active == True
    )
    result = await db.execute(stmt)
    prop = result.scalar_one_or_none()
    
    if not prop:
        raise HTTPException(status_code=404, detail="No active prop found for this player/stat.")

    # 2. Get all odds for this prop
    odds_stmt = select(PropOdds).where(PropOdds.prop_line_id == prop.id)
    odds_result = await db.execute(odds_stmt)
    all_odds = odds_result.scalars().all()
    
    if not all_odds:
        raise HTTPException(status_code=404, detail="No market odds found for this prop.")

    # 3. Calculate best price
    # For 'over', we want the highest odds (or lowest negative)
    # Note: This is simpler than full EV logic but catches the best 'price'
    best_option = None
    if side == "over":
        best_option = max(all_odds, key=lambda x: x.over_odds)
    else:
        best_option = max(all_odds, key=lambda x: x.under_odds)

    return {
        "player": prop.player_name,
        "stat": prop.stat_type,
        "line": prop.line,
        "side": side,
        "best_book": best_option.sportsbook,
        "best_price": best_option.over_odds if side == "over" else best_option.under_odds,
        "all_prices": [
            {
                "book": o.sportsbook,
                "price": o.over_odds if side == "over" else o.under_odds,
                "ev": o.ev_percent
            } for o in all_odds
        ]
    }

@router.get("/best-price/{prop_id}")
async def get_best_price_by_id(prop_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Returns the single best book/price for a specific prop ID.
    Used for the 'Best Price' badge on the frontend.
    """
    odds_stmt = select(PropOdds).where(PropOdds.prop_line_id == prop_id)
    odds_result = await db.execute(odds_stmt)
    all_odds = odds_result.scalars().all()
    
    if not all_odds:
        return {"status": "error", "message": "No odds found"}
        
    # Find max over_odds as default 'Best Price'
    best_over = max(all_odds, key=lambda x: x.over_odds)
    
    return {
        "prop_id": prop_id,
        "best_sportsbook": best_over.sportsbook,
        "best_over_odds": best_over.over_odds,
        "ev_yield": best_over.ev_percent
    }
