from fastapi import APIRouter, Query
from services.dvp_service import get_dvp_rating

router = APIRouter(prefix="/matchup", tags=["matchup"])

@router.get("/dvp")
async def fetch_dvp(
    sport: str = Query(..., description="e.g. NBA, NFL"),
    opponent: str = Query(..., description="The opposing team name or full name, e.g. Lakers"),
    position: str = Query(..., description="The player's position, e.g. PG, SG, QB, WR")
):
    """
    Returns Defense vs Position (DvP) matchup ratings.
    Used to display 🟢 Favorable / 🟡 Neutral / 🔴 Tough badges on player props.
    """
    return get_dvp_rating(sport, opponent, position)
