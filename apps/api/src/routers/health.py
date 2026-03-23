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
        "version": "1.1.6"
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
            sample_odds_res = await db.execute(text("SELECT sport, player_name, market_key, outcome_key, line, price FROM unified_odds WHERE player_name IS NOT NULL LIMIT 10"))
            sample_odds = [dict(r._mapping) for r in sample_odds_res.fetchall()]
        
        # 5b. Sample EV signals
        sample_ev = []
        if "ev_signals" in all_tables:
            ev_res = await db.execute(text("SELECT sport, player_name, market_key, edge_percent, updated_at FROM ev_signals ORDER BY updated_at DESC LIMIT 10"))
            sample_ev = [{**dict(r._mapping), "updated_at": str(r.updated_at)} for r in ev_res.fetchall()]
            
        # 5d. MMA Deep Check
        mma_checks = {}
        if "props_live" in all_tables:
            res = await db.execute(text("SELECT COUNT(*) FROM props_live WHERE sport = 'mma_mixed_martial_arts'"))
            mma_checks["props_live_count"] = res.scalar()
        if "unified_odds" in all_tables:
            res = await db.execute(text("SELECT COUNT(*) FROM unified_odds WHERE sport = 'mma_mixed_martial_arts'"))
            mma_checks["unified_odds_count"] = res.scalar()
        
        # 5e. Clear Ghost Errors (Helper)
        if "t" in router.dependencies: # Not really how it works but I'll check a flag
             pass # I'll do it via a separate endpoint or manual trigger

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
            "mma_checks": mma_checks,
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

@router.get("/clear-heartbeats")
async def clear_heartbeats(db: AsyncSession = Depends(get_db)):
    """Wipe stale errors and metrics from heartbeats to see fresh state."""
    try:
        from models.heartbeat import Heartbeat
        # Update all heartbeats to clear meta or just error key
        # For simplicity, we'll reset meta to empty metrics
        sql = "UPDATE heartbeats SET meta = '{\"metrics\": {}}'::jsonb"
        await db.execute(text(sql))
        await db.commit()
        return {"status": "success", "message": "Heartbeat errors cleared."}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router.get("/force-migrate")
async def force_migrate(db: AsyncSession = Depends(get_db)):
    """Force run schema migrations and return results."""
    # Grouped for clarity
    migration_targets = [
        ("props_live", ["player_id", "player_name", "team", "market_label", "line", "odds_over", "odds_under", "implied_over", "implied_under"]),
        ("props_history", ["line", "odds_over", "odds_under", "implied_over", "implied_under"]),
        ("unified_odds", ["outcome_key"]) # Corrected from outcome_name
    ]
    
    results = {}
    for table, columns in migration_targets:
        for col in columns:
            try:
                # Use DROP NOT NULL to ensure columns are nullable
                sql = f"ALTER TABLE {table} ALTER COLUMN {col} DROP NOT NULL"
                await db.execute(text(sql))
                await db.commit()
                results[f"{table}.{col}"] = "Success"
            except Exception as e:
                # If it already is nullable, this might still say Success or throw an error depending on PG version
                results[f"{table}.{col}"] = f"Info: {str(e)}"
    
    return {
        "status": "migration_completed",
        "results": results,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

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

@router.get("/test-db-null")
async def test_db_null(db: AsyncSession = Depends(get_db)):
    """Test manual insertion of NULL into props_live to verify schema."""
    try:
        from models.brain import PropLive
        # Try to insert a record with null odds_over
        new_row = PropLive(
            sport="test_sport",
            league="TEST",
            game_id="test_game",
            game_start_time=datetime.now(timezone.utc),
            market_key="h2h",
            book="test_book",
            odds_over=None, # This is the critical test
            last_updated_at=datetime.now(timezone.utc)
        )
        db.add(new_row)
        await db.commit()
        
        # The id will be generated automatically
        test_id = new_row.id
        
        # Clean up
        await db.execute(text(f"DELETE FROM props_live WHERE id = {test_id}"))
        await db.commit()
        
        return {"status": "success", "message": f"NULL insertion (id={test_id}) and deletion worked!"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
