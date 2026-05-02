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
    return {"status": "ok", "app": "PERPLEX-EDGE"}

