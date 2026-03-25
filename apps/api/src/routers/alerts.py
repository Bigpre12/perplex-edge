from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db
from services.alert_writer import run_alert_detection

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/trigger")
async def trigger_alerts(
    background_tasks: BackgroundTasks,
    sport: str = Query(default="basketball_nba")
):
    """Manually invoke the sharp/steam detection pipeline."""
    background_tasks.add_task(run_alert_detection, sport)
    return {"status": "ok", "message": f"Alert detection triggered for {sport}"}

@router.get("")
async def get_alerts(
    sport: str = Query(default="basketball_nba"),
    limit: int = Query(default=20),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(text("""
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
            WHERE sport = :sport
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"sport": sport, "limit": limit})
        
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
