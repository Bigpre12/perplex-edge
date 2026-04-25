from fastapi import APIRouter, Query, Depends
from db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from services.hit_rate_service import hit_rate_service
from services.props_live_query import props_live_window_params, props_live_window_sql_clause

router = APIRouter(tags=["Performance & Hit Rate"])

@router.get("")
@router.get("/summary")
async def hit_rate_summary(sport: str = Query("all"), db: AsyncSession = Depends(get_async_db)):
    """Return overall hit rate summary for the given sport, with live fallback."""
    import math
    import logging as _log
    _logger = _log.getLogger(__name__)

    def _safe(val, default=0.0, cap=None):
        if val is None:
            return default
        try:
            f = float(val)
            if math.isnan(f) or math.isinf(f):
                return default
            if cap is not None:
                f = min(f, cap)
            return round(f, 2)
        except (TypeError, ValueError):
            return default

    try:
        count_res = await db.execute(text("SELECT COUNT(*) FROM player_hit_rates"))
        count = count_res.scalar()

        if count and count > 0:
            query = """
                SELECT 
                    AVG(CASE WHEN hit_rate <= 1.0 THEN hit_rate ELSE NULL END) as overall_hit_rate,
                    AVG(CASE WHEN roi BETWEEN -1000 AND 1000 THEN roi ELSE NULL END) as roi,
                    COUNT(*) as graded_picks,
                    SUM(CASE WHEN hit_rate > 0.55 AND hit_rate <= 1.0 THEN 1 ELSE 0 END) as streak
                FROM player_hit_rates
            """
            row_res = await db.execute(text(query))
            row = row_res.mappings().one_or_none()
            if row:
                return {
                    "overall_hit_rate": _safe(row["overall_hit_rate"], cap=1.0),
                    "roi": _safe(row["roi"]),
                    "graded_picks": int(row["graded_picks"] or 0),
                    "streak": int(row["streak"] or 0),
                    "status": "live",
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                }

        t_lo, t_hi = props_live_window_params()
        fallback_query = """
            SELECT 
                ROUND(AVG(confidence)::numeric, 2) as overall_hit_rate,
                ROUND(COALESCE(AVG(confidence) * 0.1, 0)::numeric, 2) as roi,
                COUNT(*) as graded_picks,
                SUM(CASE WHEN confidence > 0.6 THEN 1 ELSE 0 END) as streak
            FROM props_live
            WHERE 1=1
        """ + props_live_window_sql_clause("game_start_time")
        row_res = await db.execute(text(fallback_query), {"t_lo": t_lo, "t_hi": t_hi})
        row = row_res.mappings().one_or_none()
        if row:
            return {
                "overall_hit_rate": _safe(row["overall_hit_rate"], cap=1.0),
                "roi": _safe(row["roi"]),
                "graded_picks": int(row["graded_picks"] or 0),
                "streak": int(row["streak"] or 0),
                "status": "computed_live",
                "last_updated": datetime.utcnow().isoformat() + "Z",
            }

        return {"overall_hit_rate": 0, "roi": 0, "graded_picks": 0, "streak": 0, "status": "awaiting_ingest"}
    except Exception as e:
        _logger.error(f"Hit rate summary error: {e}")
        return {"overall_hit_rate": 0, "roi": 0, "graded_picks": 0, "streak": 0, "status": "error"}

@router.get("/players")
@router.get("/by-player")
@router.get("/leaderboard")
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
