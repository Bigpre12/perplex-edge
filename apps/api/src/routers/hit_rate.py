from fastapi import APIRouter, Query

router = APIRouter()

@router.get("")
@router.get("/summary")
async def hit_rate_summary(sport: str = Query("all")):
    """Return overall hit rate summary for the given sport."""
    return {
        "sport": sport,
        "overall_hit_rate": 0,
        "sample_size": 0,
        "last_updated": None,
    }

@router.get("/players")
async def hit_rate_players(
    sport: str = Query("all"),
    slate_only: bool = Query(False),
):
    """Return per-player hit rate breakdown."""
    return []
