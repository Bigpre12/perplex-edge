from fastapi import APIRouter, Query
from typing import Optional
from services.trends_service import trends_service

router = APIRouter(prefix="/api/trends", tags=["trends"])

@router.get("/hit-rates")
async def get_hit_rates(
    sport_key: str = Query("basketball_nba", description="The Odds API sport key"),
    timeframe: str = Query("10g", description="Number of games to look back (5g, 10g, 30g, szn)")
):
    """Get high-hit-rate player props for the Trend Hunter UI."""
    items = await trends_service.get_high_hit_rates(sport_key, timeframe)
    return {
        "items": items,
        "total": len(items),
        "sport_key": sport_key,
        "timeframe": timeframe
    }
