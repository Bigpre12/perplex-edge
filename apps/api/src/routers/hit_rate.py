from fastapi import APIRouter, Query, Depends
from db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from services.hit_rate_service import hit_rate_service

router = APIRouter(tags=["Performance & Hit Rate"])

@router.get("")
@router.get("/summary")
async def hit_rate_summary(sport: str = Query("all"), db: AsyncSession = Depends(get_async_db)):
    """Return overall hit rate summary for the given sport, with live fallback."""
    try:
        count_res = await db.execute(text("SELECT COUNT(*) FROM player_hit_rates"))
        count = count_res.scalar()
        
        if count > 0:
            query = """
                SELECT 
                    AVG(hit_rate) as overall_hit_rate,
                    AVG(roi) as roi,
                    COUNT(*) as graded_picks,
                    SUM(CASE WHEN hit_rate > 0.55 THEN 1 ELSE 0 END) as streak
                FROM player_hit_rates
            """
            row_res = await db.execute(text(query))
            row = row_res.mappings().one_or_none()
            if row:
                return {**dict(row), "status": "live", 
                        "last_updated": datetime.utcnow().isoformat() + "Z"}
        
        # Fallback: compute from props_live confidence scores
        fallback_query = """
            SELECT 
                ROUND(AVG(confidence)::numeric, 2) as overall_hit_rate,
                ROUND((AVG(confidence) * 0.1)::numeric, 2) as roi,
                COUNT(*) as graded_picks,
                SUM(CASE WHEN confidence > 0.6 THEN 1 ELSE 0 END) as streak
            FROM props_live
            WHERE last_updated_at > NOW() - INTERVAL '24 hours'
        """
        row_res = await db.execute(text(fallback_query))
        row = row_res.mappings().one_or_none()
        if row:
            return {**dict(row), "status": "computed_live",
                    "last_updated": datetime.utcnow().isoformat() + "Z"}
                    
        return {"overall_hit_rate": 0, "roi": 0, "graded_picks": 0, "streak": 0, "status": "awaiting_ingest"}
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Hit rate summary error: {e}")
        return {"overall_hit_rate": 0, "roi": 0, "graded_picks": 0, "streak": 0, "status": "error"}

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
