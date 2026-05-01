from typing import Optional, List, Dict, Any, Tuple
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone, timedelta
import logging
import os

from db.session import get_db
from routers.schemas.health_contracts import HealthResponse, HealthDepsResponse

logger = logging.getLogger(__name__)

router = APIRouter()


async def compute_health(db: AsyncSession) -> Dict[str, Any]:
    """
    Shared health payload for GET /api/health and GET /api/health/deps.
    Legacy shape preserved for existing clients (strip _internal before return).
    """
    from services.heartbeat_service import HeartbeatService
    
    async def _rollback_quietly() -> None:
        try:
            await db.rollback()
        except Exception:
            pass

    db_error: Optional[str] = None
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        db_error = str(e)
        logger.error(f"Health Check: DB failure: {e}")
        await _rollback_quietly()

    odds_error: Optional[str] = None
    try:
        from core.config import settings

        if not settings.ODDS_API_KEYS:
            odds_status = "error: missing_key"
            odds_error = "missing_key"
        else:
            odds_status = "active"
    except Exception as e:
        odds_status = f"error: {str(e)}"
        odds_error = str(e)

    kalshi_status = "not_configured"
    if os.getenv("KALSHI_API_KEY") or os.getenv("KALSHI_EMAIL"):
        kalshi_status = "configured"

    sportmonks_status = "not_configured"
    if os.getenv("SPORTMONKS_KEY", "").strip():
        sportmonks_status = "configured"

    betstack_key = (os.getenv("BETSTACK_API_KEY") or "").strip()
    betstack_url = (os.getenv("BETSTACK_BASE_URL") or "").strip()
    if betstack_key and betstack_url:
        betstack_status = "configured"
        betstack_error: Optional[str] = None
    elif betstack_key and not betstack_url:
        betstack_status = "degraded"
        betstack_error = "missing BETSTACK_BASE_URL"
    else:
        betstack_status = "not_configured"
        betstack_error = None

    from services.odds_api_client import odds_api_client
    from middleware.auth_circuit_breaker import auth_breaker
    from core.config import settings
    from api_utils.supabase_proxy import role_readiness

    odds_api_all_keys_cooldown = odds_api_client.all_keys_unavailable()
    odds_api_key_health = odds_api_client.key_health() if hasattr(odds_api_client, "key_health") else {}
    auth_reset_at = auth_breaker.reset_at() if hasattr(auth_breaker, "reset_at") else None
    supabase_roles = role_readiness()

    try:
        heartbeats = await HeartbeatService.get_all_heartbeats(db)
        hb_map = {hb.feed_name: hb for hb in heartbeats}
    except Exception as e:
        logger.error(f"Health Check: Heartbeat fetch failure: {e}")
        await _rollback_quietly()
        hb_map = {}

    pipeline_hb = hb_map.get("ingest_basketball_nba")
    inference_hb = hb_map.get("model_inference")

    now = datetime.now(timezone.utc)

    def get_status_label(hb, threshold_min=60):
        if not hb or not hb.last_success_at:
            return "IDLE"

        last_success = hb.last_success_at
        if last_success.tzinfo is None:
            last_success = last_success.replace(tzinfo=timezone.utc)

        if now - last_success > timedelta(minutes=threshold_min):
            return "STALE"
        return "ACTIVE"

    pipeline_status = get_status_label(pipeline_hb)
    inference_status = get_status_label(inference_hb)

    ingest_hb_max = int(os.getenv("READINESS_INGEST_HEARTBEAT_MAX_MINUTES", "120"))
    recent_ingest_heartbeat_ok = False
    for name, hb in hb_map.items():
        if not name.startswith("ingest_"):
            continue
        if not hb or not hb.last_success_at:
            continue
        ls = hb.last_success_at
        if ls.tzinfo is None:
            ls = ls.replace(tzinfo=timezone.utc)
        if now - ls <= timedelta(minutes=ingest_hb_max):
            recent_ingest_heartbeat_ok = True
            break

    try:
        query = text("""
            SELECT 
                COUNT(*) as props_count,
                MAX(last_updated_at) as last_odds,
                MAX(last_updated_at) as last_ev
            FROM props_live
        """)
        result = await db.execute(query)
        row = result.mappings().first()

        props_count = row["props_count"] if row else 0
        last_odds = row["last_odds"].isoformat() if row and row["last_odds"] else None
        last_ev = row["last_ev"].isoformat() if row and row["last_ev"] else None

        is_stale = False
        odds_stream_status = "SYNCED"
        if row and row["last_odds"]:
            lo = row["last_odds"]
            if lo.tzinfo is None:
                lo = lo.replace(tzinfo=timezone.utc)
            if now - lo > timedelta(hours=1):
                odds_stream_status = "DELAYED"
            if now - lo > timedelta(hours=3):
                odds_stream_status = "STALE"
                is_stale = True
        elif props_count == 0:
            odds_stream_status = "EMPTY"
            is_stale = True

    except Exception as e:
        logger.error(f"Health Check: Metrics failure: {e}")
        await _rollback_quietly()
        props_count = 0
        last_odds = None
        last_ev = None
        is_stale = True
        odds_stream_status = "ERROR"

    overall_status = "healthy" if db_status == "connected" and not is_stale else "degraded"
    system_status = "ONLINE" if db_status == "connected" else "OFFLINE"

    sync_state: Dict[str, Any] = {}
    try:
        ss_res = await db.execute(
            text(
                "SELECT last_odds_sync, last_ev_sync, last_grade_sync, updated_at FROM system_sync_state WHERE id = 1"
            )
        )
        ss_row = ss_res.mappings().first()
        if ss_row:
            sync_state = {
                "last_odds_sync": ss_row["last_odds_sync"].isoformat() if ss_row["last_odds_sync"] else None,
                "last_ev_sync": ss_row["last_ev_sync"].isoformat() if ss_row["last_ev_sync"] else None,
                "last_grade_sync": ss_row["last_grade_sync"].isoformat() if ss_row["last_grade_sync"] else None,
            }
    except Exception:
        await _rollback_quietly()
        pass

    odds_quota: Dict[str, Any] = {}
    try:
        from services.odds_quota_store import fetch_usage_summary

        odds_quota = await fetch_usage_summary(db)
    except Exception as e:
        logger.warning("Health: odds quota summary unavailable: %s", e)
        await _rollback_quietly()
        odds_quota = {
            "month": datetime.now(timezone.utc).strftime("%Y-%m"),
            "used": 0,
            "remaining": None,
            "limit": int(os.getenv("ODDS_API_MONTHLY_LIMIT") or os.getenv("THE_ODDS_API_MAX_CALLS_PER_MONTH", "20000")),
            "percent_used": 0.0,
            "is_exhausted": False,
            "is_warning": False,
        }

    quota_exhausted = bool(odds_quota.get("is_exhausted"))
    ingest_quota_blocked = False
    ingest_quota_block_reason: Optional[str] = None
    try:
        from services.odds_quota_store import raise_if_quota_blocked

        ingest_quota_blocked, ingest_quota_block_reason = await raise_if_quota_blocked(db)
        odds_quota = {**odds_quota, "ingest_blocked": ingest_quota_blocked, "ingest_block_reason": ingest_quota_block_reason}
    except Exception as e:
        logger.debug("Health: ingest quota block check: %s", e)
        await _rollback_quietly()

    try:
        from services.api_quota_db import try_fetch_monthly_summary_json

        db_m = await try_fetch_monthly_summary_json(db)
        if db_m:
            odds_quota = {**odds_quota, "db_monthly_summary": db_m}
    except Exception as e:
        logger.debug("Health: db_monthly_summary unavailable: %s", e)
        await _rollback_quietly()

    if quota_exhausted:
        overall_status = "degraded"
        odds_stream_status = "STALE"
        is_stale = True
    elif ingest_quota_blocked and ingest_quota_block_reason == "odds_api_quota_hard_stop_pct":
        overall_status = "degraded"

    dependencies = {
        "database": {
            "status": "ok" if db_status == "connected" else "unavailable",
            **({"error": db_error} if db_error else {}),
        },
        "theoddsapi": {
            "status": "ok" if odds_status == "active" else "degraded",
            **({"error": odds_error} if odds_error else {}),
        },
        "supabase": {
            "status": "ok" if supabase_roles.get("anon_present") and supabase_roles.get("service_present") and not supabase_roles.get("service_key_looks_anon") else "degraded",
            **({"error": "service key appears to be anon key"} if supabase_roles.get("service_key_looks_anon") else {}),
        },
        "betstack": {
            "status": "ok" if betstack_status == "configured" else ("degraded" if betstack_status == "degraded" else "degraded"),
            **({"error": betstack_error} if betstack_error else {}),
        },
    }

    return {
        "status": overall_status,
        "dependencies": dependencies,
        "database": db_status,
        "odds_api_status": odds_status,
        "odds_api": {
            "status": odds_status,
            "keys_alive": odds_api_key_health.get("keys_alive"),
            "keys_dead": odds_api_key_health.get("keys_dead"),
            "cooling_until": odds_api_key_health.get("cooling_until"),
        },
        "auth_bypass_enabled": bool(settings.BYPASS_AUTH),
        "supabase_role_split_ready": bool(settings.SUPABASE_ROLE_SPLIT_READY),
        "supabase_service_key_looks_anon": bool(settings.SUPABASE_SERVICE_KEY_LOOKS_ANON),
        "kalshi": kalshi_status,
        "sportmonks": sportmonks_status,
        "odds_api_all_keys_cooldown": odds_api_all_keys_cooldown,
        "odds_api_key_health": odds_api_key_health,
        "auth_circuit_breaker": {
            "state": getattr(auth_breaker, "state", "unknown"),
            "failure_count": int(getattr(auth_breaker, "failures", 0)),
            "reset_at": datetime.fromtimestamp(auth_reset_at, timezone.utc).isoformat() if auth_reset_at else None,
        },
        "cache": "active",
        "inference_status": inference_status,
        "pipeline_status": pipeline_status,
        "odds_stream": odds_stream_status,
        "system_status": system_status,
        "version": "1.2.8",
        "timestamp": now.isoformat(),
        "last_odds_update": last_odds,
        "last_ev_update": last_ev,
        "props_count": props_count,
        "odds_quota": odds_quota,
        "_internal": {
            "is_stale": is_stale,
            "odds_stream_status": odds_stream_status,
            "now": now,
            "recent_ingest_heartbeat_ok": recent_ingest_heartbeat_ok,
            "odds_api_quota_exhausted": quota_exhausted,
            "odds_api_ingest_blocked_reason": ingest_quota_block_reason if ingest_quota_blocked else None,
            "auth_bypass_enabled": bool(settings.BYPASS_AUTH),
            "supabase_role_split_ready": bool(settings.SUPABASE_ROLE_SPLIT_READY),
            "supabase_service_key_looks_anon": bool(settings.SUPABASE_SERVICE_KEY_LOOKS_ANON),
        },
        **sync_state,
    }


def _build_degradation_payload(base: Dict[str, Any], internal: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """Returns (level, reasons, user_message)."""
    reasons: List[str] = []
    oss = internal.get("odds_stream_status") or base.get("odds_stream")

    if not str(base.get("database", "")).startswith("connected"):
        reasons.append("database_disconnected")
        return "severe", reasons, "Service is reachable; database is not."

    if internal.get("is_stale"):
        reasons.append("stale_or_empty_odds_stream")
    if oss in ("STALE", "ERROR", "EMPTY"):
        reasons.append(f"odds_stream_{str(oss).lower()}")

    if str(base.get("odds_api_status", "")).startswith("error"):
        reasons.append("odds_api_config")

    if internal.get("odds_api_quota_exhausted"):
        reasons.append("odds_api_quota_exhausted")
    _ibr = internal.get("odds_api_ingest_blocked_reason")
    if _ibr == "odds_api_quota_hard_stop_pct":
        reasons.append("odds_api_quota_hard_stop")

    if base.get("pipeline_status") == "STALE":
        reasons.append("ingest_heartbeat_stale")
    if base.get("inference_status") == "STALE":
        reasons.append("inference_heartbeat_stale")

    if "database_disconnected" in reasons:
        level = "severe"
    elif reasons:
        level = (
            "severe"
            if oss in ("STALE", "ERROR", "EMPTY")
            or "odds_api_quota_exhausted" in reasons
            or "odds_api_quota_hard_stop" in reasons
            else "partial"
        )
    else:
        level = "none"

    if "odds_api_quota_exhausted" in reasons:
        msg = (
            "TheOddsAPI monthly quota is exhausted. Market data is frozen until the next billing cycle "
            "or quota reset — do not force sync."
        )
    elif "odds_api_quota_hard_stop" in reasons:
        msg = (
            "TheOddsAPI quota is near its monthly limit (ingest hard-stop). Fetches are paused to preserve "
            "remaining requests; the app uses cached lines where possible."
        )
    elif level == "severe":
        msg = "Service is up — market data may be stale, empty, or degraded. Check freshness timestamps."
    elif level == "partial":
        msg = "Market data is delayed or partially degraded; verify odds and EV timestamps before acting."
    else:
        msg = ""

    return level, reasons, msg


@router.get("")
@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Enhanced Health check endpoint (legacy shape).
    Reports DB, Odds API, Cache, and Kalshi status.
    """
    from services.cache import cache
    cached = await cache.get_json("api_health_check")
    if cached:
        return cached

    base = await compute_health(db)
    base.pop("_internal", None)
    
    await cache.set_json("api_health_check", base, 5)
    return base


@router.get("/deps")
async def health_dependencies(db: AsyncSession = Depends(get_db)) -> HealthDepsResponse:
    """
    Dependency-aware health: explicit degradation level for UI truthfulness.
    Prefer this over inferring health from HTTP 200 alone.
    """
    base = await compute_health(db)
    internal = base.pop("_internal", None) or {}
    level, reasons, user_message = _build_degradation_payload(base, internal)

    return {
        "status": base.get("status"),
        "dependencies": base.get("dependencies"),
        "overall": base.get("status"),
        "system_status": base.get("system_status"),
        "degradation": {
            "level": level,
            "reasons": reasons,
            "user_message": user_message,
        },
        "freshness": {
            "odds": base.get("last_odds_update"),
            "ev": base.get("last_ev_update"),
        },
        "components": {
            "database": base.get("database"),
            "odds_api": base.get("odds_api"),
            "kalshi": base.get("kalshi"),
            "sportmonks": base.get("sportmonks"),
            "odds_api_all_keys_cooldown": base.get("odds_api_all_keys_cooldown"),
            "pipeline_status": base.get("pipeline_status"),
            "inference_status": base.get("inference_status"),
            "odds_stream": internal.get("odds_stream_status") or base.get("odds_stream"),
            "props_count": base.get("props_count"),
            "odds_quota": base.get("odds_quota"),
        },
        "timestamp": base.get("timestamp"),
        "version": base.get("version"),
        "sync": {
            "last_odds_sync": base.get("last_odds_sync"),
            "last_ev_sync": base.get("last_ev_sync"),
            "last_grade_sync": base.get("last_grade_sync"),
        },
    }


@router.get("/ready")
async def health_ready(db: AsyncSession = Depends(get_db)):
    """
    Readiness for schedulers / orchestrators: 200 when DB is up, degradation is none,
    and either props meet READINESS_MIN_PROPS (default 1) or a recent ingest heartbeat exists
    (READINESS_INGEST_HEARTBEAT_MAX_MINUTES, default 120). Otherwise 503 JSON.
    """
    base = await compute_health(db)
    internal = base.pop("_internal", None) or {}
    level, reasons, user_message = _build_degradation_payload(base, internal)
    db_ok = str(base.get("database", "")).startswith("connected")
    min_props = int(os.getenv("READINESS_MIN_PROPS", "1"))
    props_ct = int(base.get("props_count") or 0)
    props_ok = props_ct >= min_props
    recent_ing = bool(internal.get("recent_ingest_heartbeat_ok"))
    quota_ok = not bool(internal.get("odds_api_quota_exhausted")) and internal.get(
        "odds_api_ingest_blocked_reason"
    ) not in ("odds_api_quota_hard_stop_pct", "odds_api_quota_exhausted")
    data_plane = props_ok or recent_ing
    ready = bool(db_ok and level == "none" and data_plane and quota_ok)
    body: Dict[str, Any] = {
        "ready": ready,
        "degradation": {"level": level, "reasons": reasons, "user_message": user_message},
        "props_count": props_ct,
        "readiness": {
            "min_props": min_props,
            "props_ok": props_ok,
            "recent_ingest_heartbeat_ok": recent_ing,
            "odds_api_quota_ok": quota_ok,
        },
        "timestamp": base.get("timestamp"),
    }
    if ready:
        return body
    return JSONResponse(status_code=503, content=body)


@router.get("/odds-api-status")
async def odds_api_status():
    """Check Odds API key health from persisted quota state and gateway metadata."""
    from services.odds_api_client import odds_api_client
    from services.external_api_gateway import external_api_gateway

    if hasattr(odds_api_client, "_dead_until"):
        cooling = list(odds_api_client._dead_until.keys())
    else:
        cooling = []
    quota = await external_api_gateway.quota_status("theoddsapi")
    key_health = odds_api_client.key_health() if hasattr(odds_api_client, "key_health") else {}
    return {
        "keys_checked": key_health.get("keys_alive", 0) + key_health.get("keys_dead", 0),
        "results": [],
        "circuit_breaker_dead_keys": len(cooling),
        "key_health": key_health,
        "budget": quota,
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
            
        # 5d. Sport Specific Checks
        sport_counts = {}
        if "props_live" in all_tables:
            res = await db.execute(text("SELECT sport, COUNT(*) FROM props_live GROUP BY sport"))
            sport_counts = {r[0]: r[1] for r in res.fetchall()}
            
        ev_by_sport = {}
        if "ev_signals" in all_tables:
            res = await db.execute(text("SELECT sport, COUNT(*) FROM ev_signals GROUP BY sport"))
            ev_by_sport = {r[0]: r[1] for r in res.fetchall()}
        
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
            "sport_counts": sport_counts,
            "ev_by_sport": ev_by_sport,
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

@router.get("/db-test-write")
async def db_test_write(db: AsyncSession = Depends(get_db)):
    """Test if we can actually write to the users table via raw SQL."""
    try:
        import secrets
        test_email = f"test_{secrets.token_hex(4)}@example.com"
        test_user = f"test_{secrets.token_hex(4)}"
        
        # Raw SQL insert to be ultra-safe and avoid model dependency issues during boot
        sql = text("""
            INSERT INTO users (username, email, hashed_password, created_at, updated_at, is_active)
            VALUES (:u, :e, :p, NOW(), NOW(), true)
            RETURNING id
        """)
        
        res = await db.execute(sql, {"u": test_user, "e": test_email, "p": "TEST_ONLY"})
        row = res.fetchone()
        await db.commit()
        
        return {
            "status": "success",
            "message": f"Successfully wrote user {test_email} via raw SQL",
            "user_id": row[0] if row else "unknown"
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router.get("/db-inspect")
async def db_inspect(table: str = "users", db: AsyncSession = Depends(get_db)):
    """Inspect a table schema and sample data for debugging."""
    try:
        # Check if it's a table or a view
        type_sql = "SELECT table_type FROM information_schema.tables WHERE table_name = :table AND table_schema = 'public'"
        type_res = await db.execute(text(type_sql), {"table": table})
        table_type_row = type_res.fetchone()
        table_type = table_type_row[0] if table_type_row else "unknown"

        # Get column names
        col_sql = "SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_name = :table AND table_schema = 'public' ORDER BY ordinal_position"
        col_res = await db.execute(text(col_sql), {"table": table})
        columns = [{"name": r[0], "type": r[1], "default": r[2]} for r in col_res.fetchall()]
        
        # Get sample data (redacted for safety)
        data_sql = f"SELECT * FROM {table} LIMIT 5"
        data_res = await db.execute(text(data_sql))
        data_keys = [c["name"] for c in columns]
        
        raw_data = data_res.fetchall()
        sample = []
        for row in raw_data:
            row_dict = {}
            for i, key in enumerate(data_keys):
                val = row[i]
                if key in ["email", "username", "hashed_password", "password_reset_token", "clerk_id", "auth_id"]:
                    row_dict[key] = "[REDACTED]"
                else:
                    row_dict[key] = val
            sample.append(row_dict)
            
        return {
            "table": table,
            "type": table_type,
            "columns": columns,
            "sample_count": len(sample),
            "sample": sample
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/force-migrate")
async def force_migrate(db: AsyncSession = Depends(get_db)):
    """
    Force run schema migrations to add missing columns and ensure nullability.
    Uses 'ADD COLUMN IF NOT EXISTS' for maximum safety.
    """
    # Table -> [(ColumnName, Type)]
    migration_targets = [
        ("users", [
            ("password_reset_token", "VARCHAR"),
            ("password_reset_expires", "TIMESTAMP WITH TIME ZONE"),
            ("stripe_customer_id", "VARCHAR"),
            ("clerk_id", "VARCHAR"),
            ("subscription_tier", "VARCHAR DEFAULT 'free'")
        ]),
        ("props_live", [
            ("player_id", "VARCHAR"),
            ("player_name", "VARCHAR"),
            ("team", "VARCHAR"),
            ("market_label", "VARCHAR"),
            ("line", "NUMERIC"),
            ("odds_over", "NUMERIC"),
            ("odds_under", "NUMERIC"),
            ("implied_over", "NUMERIC"),
            ("implied_under", "NUMERIC"),
            ("home_team", "VARCHAR"),
            ("away_team", "VARCHAR")
        ]),
        ("props_history", [
            ("line", "NUMERIC"),
            ("odds_over", "NUMERIC"),
            ("odds_under", "NUMERIC"),
            ("implied_over", "NUMERIC"),
            ("implied_under", "NUMERIC"),
            ("home_team", "VARCHAR"),
            ("away_team", "VARCHAR")
        ]),
        ("ev_signals", [
            ("edge_percent", "DOUBLE PRECISION"),
            ("true_prob", "DOUBLE PRECISION"),
            ("implied_prob", "DOUBLE PRECISION"),
            ("engine_version", "VARCHAR DEFAULT 'v1'")
        ]),
        ("unified_odds", [
            ("outcome_key", "VARCHAR"),
            ("player_name", "VARCHAR"),
            ("league", "VARCHAR"),
            ("game_time", "TIMESTAMP WITH TIME ZONE"),
            ("home_team", "VARCHAR"),
            ("away_team", "VARCHAR")
        ])
    ]
    
    results = {}
    for table, columns in migration_targets:
        for col, col_type in columns:
            try:
                # 1. Ensure column exists
                add_sql = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type}"
                await db.execute(text(add_sql))
                
                # 2. Ensure column is nullable (except where specific defaults might imply NOT NULL which we'll lift)
                drop_sql = f"ALTER TABLE {table} ALTER COLUMN {col} DROP NOT NULL"
                await db.execute(text(drop_sql))
                
                await db.commit()
                results[f"{table}.{col}"] = "Success"
            except Exception as e:
                await db.rollback()
                results[f"{table}.{col}"] = f"Error: {str(e)}"
    
    return {
        "status": "migration_completed",
        "results": results,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/trigger-ingest")
async def trigger_ingest(sport: str = "basketball_nba"):
    """GET version of manual trigger (legacy)"""
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

@router.post("/ingest/{sport}")
async def manual_ingest_sport(sport: str):
    """
    POST manual trigger as per stabilization plan.
    Logs headers and quota results to the console.
    """
    from services.unified_ingestion import unified_ingestion
    logger.info(f"🚦 [Manual Trigger] Starting ingestion for: {sport}")
    try:
        # We use run() directly to bypass some retries for faster feedback in manual mode
        await unified_ingestion.run(sport)
        return {"status": "success", "sport": sport, "message": "Check server logs for quota headers"}
    except Exception as e:
        logger.error(f"❌ [Manual Trigger] Failed for {sport}: {e}")
        return {"status": "error", "detail": str(e)}

@router.get("/fix-indexes")
async def fix_indexes(db: AsyncSession = Depends(get_db)):
    """Force cleanup of conflicting indexes and apply correct unique constraints."""
    results = {}
    
    async def run_step(name, sql):
        try:
            await db.execute(text(sql))
            await db.commit()
            results[name] = "Success"
            return True
        except Exception as e:
            await db.rollback()
            results[name] = f"Failed: {str(e)}"
            logger.warning(f"Fix Step Failed [{name}]: {e}")
            return False

    # 1. Normalization (Both NULL and empty strings to 'Matchup')
    await run_step("norm_props", "UPDATE props_live SET player_name = 'Matchup' WHERE player_name IS NULL OR player_name = ''")
    await run_step("norm_odds", "UPDATE unified_odds SET player_name = 'Matchup' WHERE player_name IS NULL OR player_name = ''")
    await run_step("norm_ev", "UPDATE ev_signals SET player_name = 'Matchup' WHERE player_name IS NULL OR player_name = ''")

    # 2. Drop competing indexes and constraints (The Nuke Option)
    await run_step("nuke_conflicts", """
        DO $$ 
        DECLARE 
            r RECORD;
            tables TEXT[] := ARRAY['props_live', 'unified_odds', 'ev_signals'];
            t TEXT;
        BEGIN
            FOREACH t IN ARRAY tables LOOP
                -- Drop all indexes except PKEY
                FOR r IN (
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = t AND indexname NOT LIKE '%_pkey'
                ) LOOP
                    EXECUTE 'DROP INDEX IF EXISTS ' || r.indexname || ' CASCADE';
                END LOOP;
                
                -- Drop all unique constraints
                FOR r IN (
                    SELECT conname FROM pg_constraint 
                    WHERE conrelid = t::regclass AND contype = 'u'
                ) LOOP
                    EXECUTE 'ALTER TABLE ' || t || ' DROP CONSTRAINT IF EXISTS ' || r.conname || ' CASCADE';
                END LOOP;
            END LOOP;
        END $$;
    """)

    # 3. Robust Duplicate Deletion
    await run_step("del_dup_props", """
        DELETE FROM props_live a USING props_live b
        WHERE a.id < b.id 
        AND a.sport IS NOT DISTINCT FROM b.sport 
        AND a.game_id IS NOT DISTINCT FROM b.game_id 
        AND a.player_name IS NOT DISTINCT FROM b.player_name 
        AND a.market_key IS NOT DISTINCT FROM b.market_key 
        AND a.book IS NOT DISTINCT FROM b.book
    """)
    await run_step("del_dup_odds", """
        DELETE FROM unified_odds a USING unified_odds b
        WHERE a.id < b.id 
        AND a.sport IS NOT DISTINCT FROM b.sport 
        AND a.event_id IS NOT DISTINCT FROM b.event_id 
        AND a.market_key IS NOT DISTINCT FROM b.market_key 
        AND a.outcome_key IS NOT DISTINCT FROM b.outcome_key 
        AND a.bookmaker IS NOT DISTINCT FROM b.bookmaker
    """)

    # 4. Apply Correct Constraints (PG15+ NULLS NOT DISTINCT for robust NULL handling)
    await run_step("add_const_props", """
        ALTER TABLE props_live 
        ADD CONSTRAINT uix_props_live_unique 
        UNIQUE NULLS NOT DISTINCT (sport, game_id, player_name, market_key, book)
    """)
    await run_step("add_const_odds", """
        ALTER TABLE unified_odds 
        ADD CONSTRAINT uix_unified_odds_unique 
        UNIQUE NULLS NOT DISTINCT (sport, event_id, market_key, outcome_key, bookmaker)
    """)
    await run_step("add_const_ev", """
        ALTER TABLE ev_signals 
        ADD CONSTRAINT uix_ev_signals_unique 
        UNIQUE NULLS NOT DISTINCT (sport, event_id, market_key, outcome_key, bookmaker, engine_version)
    """)
    
    # 5. Drop the trigger that might be causing conflicts
    await run_step("drop_trigger", "DROP TRIGGER IF EXISTS ensure_matchup_stats_trigger ON props_live")

    return {"status": "completed", "results": results}
