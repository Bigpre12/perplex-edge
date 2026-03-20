from fastapi import APIRouter, Query
from services.hit_rate_service import hit_rate_service

router = APIRouter(tags=["Performance & Hit Rate"])

@router.get("")
@router.get("/summary")
async def hit_rate_summary(sport: str = Query("all")):
    """Return overall hit rate summary for the given sport."""
    return await hit_rate_service.get_summary(sport)

@router.get("/players")
@router.get("/by-player")
async def hit_rate_players(
    sport: str = Query("all"),
    slate_only: bool = Query(False),
):
    """Return per-player hit rate breakdown."""
    return await hit_rate_service.get_player_breakdown(sport, slate_only)

@router.get("/trends")
async def hit_rate_trends(sport: str = Query("all")):
    """Return performance trend data for charts."""
    return await hit_rate_service.get_trend_data(sport)

@router.get("/outliers")
async def hit_rate_outliers(
    sport: str = Query("all"),
    min_hit_rate: float = Query(0.70),
    window: int = Query(10),
    market: str = Query(None),
    limit: int = Query(50)
):
    """Return premium player prop outliers (70%+ hit rate)."""
    return await hit_rate_service.get_outliers(sport, min_hit_rate, window, market, limit)
