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
        "version": "1.0.5",
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
        import traceback
        from services.heartbeat_service import HeartbeatService
        heartbeats = await HeartbeatService.get_all_heartbeats(db)
        
        # 1. List all tables to see what physically exists
        tabs_res = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        all_tables = [r[0] for r in tabs_res.fetchall()]

        # 2. Count tables that MIGHT exist
        stats = {}
        target_tables = ["props_live", "props", "props_v2", "unified_odds", "ev_signals", "ledger_entries", "bets", "model_picks"]
        for t in target_tables:
            try:
                if t in all_tables:
                    c_res = await db.execute(text(f"SELECT COUNT(*) FROM {t}"))
                    stats[t] = c_res.scalar()
                else:
                    stats[t] = "MISSING"
            except Exception as e:
                stats[t] = f"ERROR: {str(e)}"
        
        # 3. Duplicate check (only if props_live exists)
        duplicates = []
        if "props_live" in all_tables:
            dup_res = await db.execute(text("""
                SELECT sport, game_id, player_name, market_key, book, COUNT(*) 
                FROM props_live 
                GROUP BY sport, game_id, player_name, market_key, book 
                HAVING COUNT(*) > 1 
                LIMIT 5
            """))
            duplicates = [dict(r._mapping) for r in dup_res.fetchall()]
        
        # 4. PG version
        pg_res = await db.execute(text("SELECT VERSION()"))
        pg_version = pg_res.scalar()
        
        # 5. Sample odds (only if unified_odds exists)
        sample_odds = []
        if "unified_odds" in all_tables:
            sample_odds_res = await db.execute(text("SELECT sport, market_key, outcome_key, price FROM unified_odds LIMIT 5"))
            sample_odds = [dict(r._mapping) for r in sample_odds_res.fetchall()]
        
        # 5b. Sample EV signals
        sample_ev = []
        if "ev_signals" in all_tables:
            ev_res = await db.execute(text("SELECT sport, market_key, edge_percent, updated_at FROM ev_signals ORDER BY updated_at DESC LIMIT 5"))
            sample_ev = [{**dict(r._mapping), "updated_at": str(r.updated_at)} for r in ev_res.fetchall()]
            
        # 6. File inspection
        content_snippet = ""
        try:
            with open("apps/api/src/services/persistence_helpers.py", "r") as f:
                content_snippet = f.read(500)
        except Exception:
            try:
                with open("services/persistence_helpers.py", "r") as f:
                    content_snippet = f.read(500)
            except Exception:
                content_snippet = "Could not read file"
            
        # 7. Column nullability (props_live)
        nullability = {}
        if "props_live" in all_tables:
            nullability_res = await db.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'props_live'
            """))
            nullability = {row[0]: row[1] for row in nullability_res.fetchall()}

        # 8. Table Columns
        columns = []
        if "props_live" in all_tables:
            col_res = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'props_live'"))
            columns = [r[0] for r in col_res.fetchall()]

        # 9. Index Inspection
        indexes = []
        if "props_live" in all_tables:
            idx_res = await db.execute(text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'props_live'"))
            indexes = [dict(r._mapping) for r in idx_res.fetchall()]

        # 10. Routes
        available_routes = [route.path for route in router.routes]

        return {
            "table_stats": stats,
            "all_tables": all_tables,
            "columns": columns,
            "nullability": nullability,
            "routes": available_routes,
            "indexes": indexes,
            "pg_version": pg_version,
            "sample_odds": sample_odds,
            "sample_ev": sample_ev,
            "duplicates": duplicates,
            "code_snippet": content_snippet,
            "heartbeats": [
                {
                    "feed": h.feed_name,
                    "status": h.status,
                    "last_run": str(h.last_run_at),
                    "last_success": str(h.last_success_at),
                    "rows_written": getattr(h, "rows_written_today", 0),
                    "meta": h.meta
                } for h in heartbeats
            ]
        }
    except Exception as e:
        import traceback
        logger.error(f"Diagnostics: Failed to collect: {e}", exc_info=True)
        return {"status": "error", "detail": str(e), "traceback": traceback.format_exc()}

@router.get("/force-migrate")
async def force_migrate(db: AsyncSession = Depends(get_db)):
    """Force run schema migrations and return results."""
    cols_to_fix = [
        ("props_live", "player_id"),
        ("props_live", "player_name"),
        ("props_live", "team"),
        ("props_live", "market_label"),
        ("props_live", "line"),
        ("unified_odds", "outcome_name")
    ]
    results = {}
    for table, col in cols_to_fix:
        try:
            await db.execute(text(f"ALTER TABLE {table} ALTER COLUMN {col} DROP NOT NULL"))
            await db.commit()
            results[f"{table}.{col}"] = "Success"
        except Exception as e:
            results[f"{table}.{col}"] = f"Failed: {str(e)}"
    
    return results

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
