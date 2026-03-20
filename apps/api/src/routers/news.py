from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/")
async def news(sport: str = Query("basketball_nba")):
    return {
        "sport": sport,
        "articles": []
    }
