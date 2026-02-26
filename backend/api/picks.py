from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Dict, Any
from services.picks_service import picks_service, Pick

router = APIRouter()

@router.get("/stats")
async def get_picks_stats(
    hours: int = Query(24, description="Lookback period in hours")
):
    """Get statistics for picks including CLV and EV metrics"""
    return await picks_service.get_picks_statistics(hours)

@router.get("/high-ev")
async def get_high_ev_picks(
    min_ev: float = Query(5.0, description="Minimum EV percentage"),
    hours: int = Query(24, description="Lookback period in hours")
):
    """Get picks with high Expected Value"""
    return await picks_service.get_high_ev_picks(min_ev, hours)

@router.get("/search")
async def search_picks(
    query: str = Query(..., description="Search query (player name, team, etc)"),
    hours: int = Query(24, description="Lookback period in hours"),
    limit: int = Query(50, description="Max results")
):
    """Search for picks"""
    return await picks_service.search_picks(query, hours, limit)

@router.get("/by-game/{game_id}")
async def get_picks_by_game(game_id: int):
    """Get all picks for a specific game"""
    return await picks_service.get_picks_by_game(game_id)
