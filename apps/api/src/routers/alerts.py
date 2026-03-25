from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from db.session import get_db
from services.alert_writer import run_alert_detection
from services.ev_writer import run_ev_grader

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.post("/trigger")
@router.get("/trigger")
async def trigger_alerts(
    sport: str = Query(default="basketball_nba"),
    db: AsyncSession = Depends(get_db)
):
    """Manually invoke the sharp/steam detection pipeline."""
    alert_count = await run_alert_detection(sport, db)
    ev_count = await run_ev_grader(sport, db)
    return {
        "status": "ok", 
        "alerts_written": alert_count,
        "ev_signals_written": ev_count,
        "sport": sport
    }

@router.get("")
async def get_alerts(
    sport: str = Query(default="basketball_nba"),
    alert_type: Optional[str] = Query(default=None),
    limit: int = Query(default=20),
    db: AsyncSession = Depends(get_db)
):
    try:
        where_sql = "sport = :sport"
        params = {"sport": sport, "limit": limit}
        if alert_type:
            where_sql += " AND alert_type = :alert_type"
            params["alert_type"] = alert_type
            
        result = await db.execute(text(f"""
            SELECT 
                id,
                player_name,
                market_key,
                sport,
                alert_type,
                direction,
                line,
                book,
                confidence,
                created_at
            FROM sharp_alerts
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT :limit
        """), params)
        
        rows = result.mappings().all()
        return {
            "alerts": [dict(r) for r in rows],
            "total": len(rows),
            "sport": sport,
            "status": "ok" if rows else "no_data"
        }
    except Exception as e:
        # Graceful fallback — return empty rather than crash
        return {
            "alerts": [],
            "total": 0,
            "sport": sport,
            "status": "error",
            "detail": str(e)
        }
