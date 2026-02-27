from fastapi import APIRouter, Query
from services.weather_service import get_game_weather

router = APIRouter(prefix="/weather", tags=["intelligence"])

@router.get("/game")
async def game_weather(team_abbr: str = Query(..., description="e.g. BUF, CHI, KC")):
    """
    Returns weather impact analysis for outdoor games.
    """
    return await get_game_weather(team_abbr)
