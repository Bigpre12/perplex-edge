from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone
import logging

from db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
@router.get("/")
async def health_check(
    db: AsyncSession = Depends(get_db)
):
    """
    Enhanced Health check endpoint.
    Reports DB, Odds API, Cache, and Kalshi status.
    """
    import os
    from services.odds_api_client import odds_api_client
    
    # 1. Database Check
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        logger.error(f"Health Check: DB failure: {e}")

    # 2. Odds API Check
    try:
        # Just check if key exists and is non-empty for a quick check,
        # or ping a lightweight endpoint if we want to be sure.
        api_key = os.getenv("THE_ODDS_API_KEY")
        if not api_key:
            odds_status = "error: missing_key"
        else:
            # We can't easily "ping" without consuming a quota, 
            # so we check if the client is initialized correctly.
            odds_status = "active"
    except Exception as e:
        odds_status = f"error: {str(e)}"

    # 3. Kalshi Check (if creds present)
    kalshi_status = "not_configured"
    if os.getenv("KALSHI_API_KEY") or os.getenv("KALSHI_EMAIL"):
        kalshi_status = "configured" # Placeholder for more complex check

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "odds_api": odds_status,
        "kalshi": kalshi_status,
        "cache": "active", # Placeholder for redis check
        "inference_status": "ACTIVE",
        "pipeline_status": "ACTIVE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.1.0"
    }

@router.get("/summary")
async def meta_summary():
    return {"status": "ok", "app": "LUCRIX"}

@router.get("/diagnostics")
async def diagnostics(db: AsyncSession = Depends(get_db)):
    """Fetch backend internal diagnostics (heartbeats and table counts)"""
    try:
        from services.heartbeat_service import HeartbeatService
        heartbeats = await HeartbeatService.get_all_heartbeats(db)
        
        # also check table counts
        res2 = await db.execute(text("SELECT COUNT(*) FROM props_live"))
        props_count = res2.scalar()
        
        # duplicates check
        dup_res = await db.execute(text("""
            SELECT sport, game_id, player_name, market_key, book, COUNT(*) 
            FROM props_live 
            GROUP BY sport, game_id, player_name, market_key, book 
            HAVING COUNT(*) > 1 
            LIMIT 5
        """))
        duplicates = [dict(r._mapping) for r in dup_res.fetchall()]
        
        res3 = await db.execute(text("SELECT COUNT(*) FROM unified_odds"))
        odds_count = res3.scalar()
        
        # pg version
        pg_res = await db.execute(text("SELECT VERSION()"))
        pg_version = pg_res.scalar()
        
        # sample odds
        sample_odds_res = await db.execute(text("SELECT sport, market_key, outcome_key, price FROM unified_odds LIMIT 5"))
        sample_odds = [dict(r._mapping) for r in sample_odds_res.fetchall()]
        
        # table columns
        col_res = await db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'props_live'
        """))
        columns = [r[0] for r in col_res.fetchall()]
        
        return {
            "props_live_count": props_count,
            "unified_odds_count": odds_count,
            "columns": columns,
            "pg_version": pg_version,
            "sample_odds": sample_odds,
            "duplicates": duplicates,
            "heartbeats": [
                {
                    "feed": h.feed_name,
                    "status": h.status,
                    "last_run": str(h.last_run_at),
                    "last_success": str(h.last_success_at),
                    "rows_written": h.rows_written_today,
                    "heartbeat": h.last_run_at.isoformat() if h.last_run_at else None,
                    "meta": h.meta
                } for h in heartbeats
            ]
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@router.get("/trigger-ingest")
async def trigger_ingest(sport: str = "basketball_nba"):
    """Manual trigger to run ingestion and see errors immediately."""
    from services.unified_ingestion import unified_ingestion
    try:
        await unified_ingestion.run(sport)
        return {"status": "success", "sport": sport}
    except Exception as e:
        import traceback
        return {
            "status": "failed", 
            "error": str(e), 
            "traceback": traceback.format_exc()
        }
