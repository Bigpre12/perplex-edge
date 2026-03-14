from fastapi import APIRouter, Query
from services.player_splits_service import get_full_splits

router = APIRouter(prefix="/splits", tags=["splits"])

@router.get("/player")
async def player_splits(
    player_name: str = Query(..., description="Full player name e.g. LeBron James"),
    stat_type:   str = Query("points", description="points, rebounds, assists, pra, threes, steals, blocks"),
    line:        float = Query(..., description="The prop line to calculate hit rate against"),
):
    """
    Returns L5/L10/L20 hit rates for any player + stat + line.
    Powers the traffic light system on the frontend.
    """
    return await get_full_splits(player_name, stat_type, line)
