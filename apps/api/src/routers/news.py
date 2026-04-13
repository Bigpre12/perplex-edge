from fastapi import APIRouter, Query

from services.news_service import news_service

router = APIRouter()

@router.get("")
@router.get("/")
async def news(sport: str = Query("basketball_nba")):
    articles = await news_service.get_news(sport)
    return {
        "status": "ok",
        "sport": sport,
        "count": len(articles),
        "articles": articles
    }
