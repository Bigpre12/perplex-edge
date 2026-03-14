from fastapi import APIRouter, Query
from services.dfs_service import dfs_service

router = APIRouter(prefix="/dfs", tags=["betting-tools"])

@router.get("/implied-odds")
async def dfs_implied_odds(
    platform: str = Query("prizepicks"),
    legs: int = Query(2)
):
    """
    Returns the implied odds for a single leg on a DFS platform.
    """
    odds = dfs_service.get_implied_odds(platform, legs)
    return {"platform": platform, "legs": legs, "implied_odds": odds}

@router.get("/ev")
async def dfs_leg_ev(
    win_prob: float = Query(...),
    platform: str = Query("prizepicks"),
    legs: int = Query(2)
):
    """
    Calculates the expected value (EV) for a DFS pick.
    """
    ev = dfs_service.calculate_dfs_ev(win_prob, platform, legs)
    return {"platform": platform, "legs": legs, "win_prob": win_prob, "ev": ev}
