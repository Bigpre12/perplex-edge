# apps/api/src/routers/admin.py
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_async_db
from deps.auth import verify_admin
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(verify_admin)])

@router.get("/diagnostics")
async def diagnostics(db: AsyncSession = Depends(get_async_db)):
    """Fetch backend internal diagnostics (heartbeats and table counts)"""
    try:
        from services.heartbeat_service import HeartbeatService
        heartbeats = await HeartbeatService.get_all_heartbeats(db)
        
        tabs_res = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        all_tables = [r[0] for r in tabs_res.fetchall()]

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
        
        pg_res = await db.execute(text("SELECT VERSION()"))
        pg_version = pg_res.scalar()
        
        return {
            "table_stats": stats,
            "all_tables": all_tables,
            "pg_version": pg_version,
            "heartbeats": [
                {
                    "feed": h.feed_name,
                    "status": h.status,
                    "last_run": str(h.last_run_at),
                    "last_success": str(h.last_success_at),
                    "rows_written": getattr(h, "rows_written_today", 0)
                } for h in heartbeats
            ]
        }
    except Exception as e:
        logger.error(f"Diagnostics: Failed to collect: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}

@router.get("/clear-heartbeats")
async def clear_heartbeats(db: AsyncSession = Depends(get_async_db)):
    """Wipe stale errors and metrics from heartbeats."""
    try:
        sql = "UPDATE heartbeats SET meta = '{\"metrics\": {}}'::jsonb"
        await db.execute(text(sql))
        await db.commit()
        return {"status": "success", "message": "Heartbeat errors cleared."}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router.get("/db-inspect")
async def db_inspect(table: str = "users", db: AsyncSession = Depends(get_async_db)):
    """Inspect a table schema and sample data for debugging."""
    try:
        col_sql = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = :table AND table_schema = 'public'"
        col_res = await db.execute(text(col_sql), {"table": table})
        columns = [{"name": r[0], "type": r[1]} for r in col_res.fetchall()]
        
        data_sql = f"SELECT * FROM {table} LIMIT 5"
        data_res = await db.execute(text(data_sql))
        raw_data = data_res.fetchall()
        
        return {
            "table": table,
            "columns": columns,
            "sample": [dict(r._mapping) for r in raw_data]
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/ingest/{sport}")
async def manual_ingest_sport(sport: str):
    """Trigger manual ingestion for a sport."""
    from services.unified_ingestion import unified_ingestion
    try:
        await unified_ingestion.run(sport)
        return {"status": "success", "sport": sport}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router.get("/force-migrate")
async def force_migrate(db: AsyncSession = Depends(get_async_db)):
    """Force run schema migrations for missing columns."""
    # (Abbreviated version of the logic from health.py)
    # This is powerful/dangerous, hence gated in /admin
    return {"status": "not_implemented_safely", "message": "Use Alembic for production migrations."}
