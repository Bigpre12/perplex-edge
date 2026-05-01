import sys
import os
import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import APP_NAME, settings
from core.ingest_scheduler_config import build_unified_ingest_schedule, scheduled_sport_keys
from middleware.request_id import RequestIDMiddleware, get_request_id
from middleware.auth_circuit_breaker import AuthCircuitBreakerMiddleware, auth_breaker # Import new circuit breaker
from db.base import Base
from db.session import engine, get_db, validate_db_connection
from services.unified_ingestion import unified_ingestion
from core.connection_manager import manager
from services.live_data_service import live_data_service
from services.kalshi_ws import kalshi_ws_manager

logger = logging.getLogger(__name__)
logging.getLogger("apscheduler").setLevel(logging.INFO)
RUN_INTERNAL_SCHEDULER = os.getenv("RUN_INTERNAL_SCHEDULER", "true").strip().lower() in {"1", "true", "yes", "on"}
ENABLE_STARTUP_DDL = os.getenv("ENABLE_STARTUP_DDL", "true").strip().lower() in {"1", "true", "yes", "on"}

def validate_env():
    """Fail fast if critical environment variables are missing, but with descriptive error logs."""
    def _strip(v: Optional[str]) -> str:
        return (v or "").strip()

    missing: list[str] = []
    if not _strip(os.getenv("DATABASE_URL")):
        missing.append("DATABASE_URL")

    supabase_url = _strip(os.getenv("SUPABASE_URL")) or _strip(os.getenv("NEXT_PUBLIC_SUPABASE_URL"))
    if not supabase_url:
        missing.append("SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL)")

    supabase_key = _strip(os.getenv("SUPABASE_KEY")) or _strip(os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY"))
    if not supabase_key:
        missing.append("SUPABASE_KEY (or NEXT_PUBLIC_SUPABASE_ANON_KEY)")

    primary = _strip(os.getenv("ODDS_API_KEY")) or _strip(os.getenv("THE_ODDS_API_KEY"))
    backup = _strip(os.getenv("ODDS_API_KEY_BACKUP"))
    raw_list = os.getenv("ODDS_API_KEYS") or ""
    list_keys = [k.strip() for k in raw_list.split(",") if k.strip()]
    if not primary and not backup and not list_keys:
        missing.append(
            "odds API credentials (set ODDS_API_KEY, THE_ODDS_API_KEY, ODDS_API_KEYS, and/or ODDS_API_KEY_BACKUP)"
        )

    if missing:
        msg = f"❌ CONFIGURATION WARNING: Missing or empty: {', '.join(missing)}"
        logger.warning("**************************************************")
        logger.warning(msg)
        logger.warning("Please ensure these variables are set in the Railway dashboard.")
        logger.warning("**************************************************")

        # Only hard crash on DATABASE_URL in production
        if os.getenv("RAILWAY_ENVIRONMENT_NAME") and not _strip(os.getenv("DATABASE_URL")):
            raise RuntimeError("CRITICAL: DATABASE_URL is missing. Backend cannot start.")

    is_prod = bool((os.getenv("RAILWAY_ENVIRONMENT_NAME") or "").strip()) and (
        os.getenv("DEV_MODE", "false").strip().lower() != "true"
    )
    bypass_auth = _strip(os.getenv("BYPASS_AUTH")).lower() in {"1", "true", "yes", "on"}
    if is_prod and bypass_auth:
        raise RuntimeError("CRITICAL: BYPASS_AUTH=true is forbidden in production.")


# Run validation immediately
validate_env()

_failed_router_imports: list[tuple[str, str]] = []


def safe_import(module_path, alias):
    try:
        mod = __import__(f"routers.{module_path}", fromlist=["router"])
        if hasattr(mod, "router"):
            return mod.router
        return getattr(mod, alias)
    except Exception as e:
        _failed_router_imports.append((module_path, str(e)))
        logger.debug("Error importing router '%s': %s", module_path, e, exc_info=True)
        return None

# --- Router Imports (each guarded by safe_import) ---
health_router        = safe_import("health", "health")
meta_router          = safe_import("meta", "meta")
auth_router          = safe_import("auth", "auth")
props_router         = safe_import("props", "props")
ev_router            = safe_import("ev", "ev")
clv_router           = safe_import("clv", "clv")
brain_router         = safe_import("brain_router", "brain")
bets_router          = safe_import("bets", "bets")
injuries_router      = safe_import("injuries", "injuries")
news_router          = safe_import("news", "news")
signals_router       = safe_import("signals", "signals")
metrics_router       = safe_import("metrics", "metrics")
hit_rate_router      = safe_import("hit_rate", "hit_rate")
whale_router         = safe_import("whale", "whale")
steam_router         = safe_import("steam", "steam")
stripe_router        = safe_import("stripe_router", "stripe")
billing_router       = safe_import("billing", "router")
search_router        = safe_import("search", "search")
oracle_router        = safe_import("oracle", "oracle")
live_router          = safe_import("live", "live")
slate_router         = safe_import("slate", "slate")
ws_ev_router         = safe_import("ws_ev", "ws_ev")
line_movement_router = safe_import("line_movement", "line_movement")
arbitrage_router     = safe_import("arbitrage", "arbitrage")
middle_boost_router  = safe_import("middle_boost", "router")
kalshi_router        = safe_import("kalshi", "kalshi")
kalshi_ws_router     = safe_import("kalshi_ws_proxy", "kalshi_ws")
intel_router         = safe_import("intel", "router")
pick_intel_router    = safe_import("pick_intel", "router")
user_settings_router = safe_import("user_settings", "router")
sharp_router         = safe_import("sharp", "router")
parlays_router       = safe_import("parlays", "router")
simulation_router    = safe_import("simulation", "router")
props_history_router = safe_import("props_history", "router")
alerts_router        = safe_import("alerts", "router")
audit_router         = safe_import("audit", "router")
waterfall_router     = safe_import("waterfall", "router")

if _failed_router_imports:
    parts = []
    for name, err in _failed_router_imports:
        short = err if len(err) <= 120 else err[:117] + "..."
        parts.append(f"{name} ({short})")
    logger.warning(
        "Router import summary: %d module(s) not loaded — %s",
        len(_failed_router_imports),
        "; ".join(parts),
    )

async def initialize_backend_services():
    """Background task to initialize heavy services without blocking /health."""
    logger.info("🚀 [Background Init] Starting service initialization...")
    
    try:
        # 1. Database Setup & Tables
        logger.info("📡 [Background Init] Ensuring database tables exist...")
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 2. Schema Migrations (safe: IF NOT EXISTS)
        if not ENABLE_STARTUP_DDL:
            logger.info(
                "📡 [Background Init] Startup DDL disabled (ENABLE_STARTUP_DDL=false). "
                "Expect Alembic-managed schema in this environment."
            )
            is_sqlite = True
        else:
            logger.info("📡 [Background Init] Running schema migrations...")
            is_sqlite = "sqlite" in str(engine.url)
        
        async def run_migration_step(query: str):
            try:
                async with engine.begin() as conn:
                    await conn.execute(text(query))
            except Exception as e:
                q_snippet = query[:100] if query else "NULL"
                logger.debug("Migration step skipped or failed (continuing): %s... Error: %s", q_snippet, e)

        async def run_sql_migration_file(path: str):
            """Execute an idempotent SQL migration file with best-effort semantics."""
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw_sql = f.read()
            except Exception as e:
                logger.warning("Could not read migration file %s: %s", path, e)
                return

            statements = []
            for chunk in raw_sql.split(";"):
                stmt = chunk.strip()
                if not stmt or stmt.startswith("--"):
                    continue
                cleaned = "\n".join(
                    line for line in stmt.splitlines() if not line.strip().startswith("--")
                ).strip()
                if cleaned:
                    statements.append(cleaned)

            for stmt in statements:
                await run_migration_step(stmt)

        if not is_sqlite:
            # Add columns
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS sport VARCHAR")
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS sport_key VARCHAR")
            await run_migration_step("ALTER TABLE ev_signals ALTER COLUMN sport_key DROP NOT NULL")
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS true_prob FLOAT")
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS edge_percent FLOAT")
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS confidence FLOAT")
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS ev_score FLOAT")
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS ev_percentage FLOAT")
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS fair_prob FLOAT")
            await run_migration_step("ALTER TABLE ev_signals ALTER COLUMN prop_type DROP NOT NULL")
            await run_migration_step("ALTER TABLE ev_signals ALTER COLUMN prop_type SET DEFAULT 'unknown'")
            await run_migration_step("ALTER TABLE unified_odds ADD COLUMN IF NOT EXISTS sport VARCHAR")
            await run_migration_step("ALTER TABLE unified_odds ADD COLUMN IF NOT EXISTS implied_prob FLOAT")
            await run_migration_step("ALTER TABLE props_live ADD COLUMN IF NOT EXISTS sport VARCHAR")
            await run_migration_step("""
                DO $migrate_ev_pct$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = 'props_live' AND column_name = 'evpercentage'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = 'props_live' AND column_name = 'ev_percentage'
                    ) THEN
                        ALTER TABLE props_live RENAME COLUMN evpercentage TO ev_percentage;
                    END IF;
                END $migrate_ev_pct$
            """)
            await run_migration_step("ALTER TABLE props_live ADD COLUMN IF NOT EXISTS ev_percentage FLOAT DEFAULT 0")
            await run_migration_step("ALTER TABLE props_live ADD COLUMN IF NOT EXISTS game_start_time TIMESTAMPTZ")
            await run_migration_step("ALTER TABLE props_live ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ")
            await run_migration_step("ALTER TABLE props_live ADD COLUMN IF NOT EXISTS home_team VARCHAR")
            await run_migration_step("ALTER TABLE props_live ADD COLUMN IF NOT EXISTS away_team VARCHAR")
            await run_migration_step(
                "ALTER TABLE props_live ADD COLUMN IF NOT EXISTS steam_signal BOOLEAN DEFAULT FALSE"
            )
            await run_migration_step(
                "ALTER TABLE props_live ADD COLUMN IF NOT EXISTS whale_signal BOOLEAN DEFAULT FALSE"
            )
            await run_migration_step(
                "ALTER TABLE props_live ADD COLUMN IF NOT EXISTS sharp_conflict BOOLEAN DEFAULT FALSE"
            )
            await run_migration_step("ALTER TABLE props_history ADD COLUMN IF NOT EXISTS home_team VARCHAR")
            await run_migration_step("ALTER TABLE props_history ADD COLUMN IF NOT EXISTS away_team VARCHAR")
            await run_migration_step("ALTER TABLE props_history ADD COLUMN IF NOT EXISTS is_best_over BOOLEAN DEFAULT FALSE")
            await run_migration_step("ALTER TABLE props_history ADD COLUMN IF NOT EXISTS is_best_under BOOLEAN DEFAULT FALSE")
            await run_migration_step("ALTER TABLE props_history ADD COLUMN IF NOT EXISTS is_soft_book BOOLEAN DEFAULT FALSE")
            await run_migration_step("ALTER TABLE props_history ADD COLUMN IF NOT EXISTS is_sharp_book BOOLEAN DEFAULT FALSE")
            await run_migration_step("ALTER TABLE props_history ADD COLUMN IF NOT EXISTS confidence FLOAT")
            await run_migration_step("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS engine_version VARCHAR DEFAULT 'v1'")

            # DROP NOT NULL cleanup - Vital for handling missing data gracefully during ingestion
            not_null_cleanup = [
                # props_live
                ("props_live", "player_id"), ("props_live", "player_name"), ("props_live", "team"), 
                ("props_live", "market_label"), ("props_live", "line"), ("props_live", "odds_over"), 
                ("props_live", "odds_under"), ("props_live", "implied_over"), ("props_live", "implied_under"),
                # props_history 
                ("props_history", "player_id"), ("props_history", "player_name"), ("props_history", "team"),
                ("props_history", "market_label"), ("props_history", "line"), ("props_history", "odds_over"), 
                ("props_history", "odds_under"), ("props_history", "implied_over"), ("props_history", "implied_under"),
                # unified_odds
                ("unified_odds", "outcome_key"), ("unified_odds", "player_name"), ("unified_odds", "home_team"), 
                ("unified_odds", "away_team"), ("unified_odds", "league"), ("unified_odds", "game_time"),
                # ev_signals
                ("ev_signals", "player_name"), ("ev_signals", "line"), ("ev_signals", "price"), 
                ("ev_signals", "outcome_key"),
                # edges_ev_history (legacy NOT NULL on team / market_label)
                ("edges_ev_history", "team"),
                ("edges_ev_history", "market_label"),
                # analytics/logging
                ("line_ticks", "player_name"), ("line_ticks", "line"),
                ("ev_signals_history", "player_name"), ("ev_signals_history", "line")
            ]
            
            for table, col in not_null_cleanup:
                await run_migration_step(f"ALTER TABLE {table} ALTER COLUMN {col} DROP NOT NULL")

            # DATA CLEANUP: Handle NULLs and Duplicates
            logger.info("📡 [Background Init] Cleaning up NULLs and duplicate rows for constraints...")
            
            # Step 1: Normalize NULL player_names to 'Matchup' for consistent indexing
            await run_migration_step("UPDATE props_live SET player_name = 'Matchup' WHERE player_name IS NULL")
            await run_migration_step("UPDATE unified_odds SET player_name = 'Matchup' WHERE player_name IS NULL")
            await run_migration_step("UPDATE ev_signals SET player_name = 'Matchup' WHERE player_name IS NULL")

            # props_live cleanup: USE IS NOT DISTINCT FROM to catch NULL duplicates
            await run_migration_step("""
                DELETE FROM props_live a USING props_live b
                WHERE a.id < b.id 
                AND a.sport IS NOT DISTINCT FROM b.sport 
                AND a.game_id IS NOT DISTINCT FROM b.game_id 
                AND a.player_name IS NOT DISTINCT FROM b.player_name 
                AND a.market_key IS NOT DISTINCT FROM b.market_key 
                AND a.book IS NOT DISTINCT FROM b.book
            """)

            # unified_odds cleanup
            await run_migration_step("""
                DELETE FROM unified_odds a USING unified_odds b
                WHERE a.id < b.id 
                AND a.sport IS NOT DISTINCT FROM b.sport 
                AND a.event_id IS NOT DISTINCT FROM b.event_id 
                AND a.market_key IS NOT DISTINCT FROM b.market_key 
                AND a.outcome_key IS NOT DISTINCT FROM b.outcome_key 
                AND a.bookmaker IS NOT DISTINCT FROM b.bookmaker
            """)

            # ev_signals cleanup
            await run_migration_step("""
                DELETE FROM ev_signals a USING ev_signals b
                WHERE a.id < b.id 
                AND a.sport IS NOT DISTINCT FROM b.sport 
                AND a.event_id IS NOT DISTINCT FROM b.event_id 
                AND a.market_key IS NOT DISTINCT FROM b.market_key 
                AND a.outcome_key IS NOT DISTINCT FROM b.outcome_key 
                AND a.bookmaker IS NOT DISTINCT FROM b.bookmaker
                AND a.engine_version IS NOT DISTINCT FROM b.engine_version
            """)

            # Step 2: Add unique constraints with partial indexes for Supabase Postgres 14 compatibility
            
            # Props Live
            await run_migration_step("ALTER TABLE props_live DROP CONSTRAINT IF EXISTS uix_props_live_unique")
            await run_migration_step("DROP INDEX IF EXISTS uix_props_live_unique")
            await run_migration_step("DROP INDEX IF EXISTS uix_props_live_team_unique")
            
            await run_migration_step("""
                CREATE UNIQUE INDEX IF NOT EXISTS uix_props_live_unique 
                ON props_live (sport, game_id, player_name, market_key, book) 
                WHERE player_name IS NOT NULL
            """)
            await run_migration_step("""
                CREATE UNIQUE INDEX IF NOT EXISTS uix_props_live_team_unique 
                ON props_live (sport, game_id, market_key, book) 
                WHERE player_name IS NULL
            """)
            
            # Unified Odds
            await run_migration_step("ALTER TABLE unified_odds DROP CONSTRAINT IF EXISTS uix_unified_odds_unique")
            await run_migration_step("DROP INDEX IF EXISTS uix_unified_odds_unique")
            await run_migration_step("DROP INDEX IF EXISTS uix_unified_odds_team_unique")
            
            await run_migration_step("""
                CREATE UNIQUE INDEX IF NOT EXISTS uix_unified_odds_unique 
                ON unified_odds (sport, event_id, player_name, market_key, outcome_key, bookmaker)
                WHERE player_name IS NOT NULL
            """)
            await run_migration_step("""
                CREATE UNIQUE INDEX IF NOT EXISTS uix_unified_odds_team_unique 
                ON unified_odds (sport, event_id, market_key, outcome_key, bookmaker)
                WHERE player_name IS NULL
            """)

            # EV Signals
            await run_migration_step("ALTER TABLE ev_signals DROP CONSTRAINT IF EXISTS uix_ev_unique")
            await run_migration_step("ALTER TABLE ev_signals DROP CONSTRAINT IF EXISTS uix_ev_signals_unique")
            await run_migration_step("DROP INDEX IF EXISTS uix_ev_unique")
            await run_migration_step("DROP INDEX IF EXISTS uix_ev_team_unique")
            
            await run_migration_step("""
                CREATE UNIQUE INDEX IF NOT EXISTS uix_ev_unique 
                ON ev_signals (sport, event_id, player_name, market_key, outcome_key, bookmaker, engine_version)
                WHERE player_name IS NOT NULL
            """)
            await run_migration_step("""
                CREATE UNIQUE INDEX IF NOT EXISTS uix_ev_team_unique 
                ON ev_signals (sport, event_id, market_key, outcome_key, bookmaker, engine_version)
                WHERE player_name IS NULL
            """)
            
            # Cleanup corrupt hit rate data (>100% rates, NaN values)
            await run_migration_step("""
                DELETE FROM player_hit_rates
                WHERE l5_hit_rate > 1.0 OR l10_hit_rate > 1.0 OR l20_hit_rate > 1.0
                   OR l5_hit_rate != l5_hit_rate OR l10_hit_rate != l10_hit_rate OR l20_hit_rate != l20_hit_rate
            """)

            # Line Movement table for CLV Engine tracking
            await run_migration_step("""
                CREATE TABLE IF NOT EXISTS line_movement (
                    id SERIAL PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    player_name TEXT,
                    market_key TEXT NOT NULL,
                    bookmaker TEXT NOT NULL,
                    price FLOAT NOT NULL,
                    line FLOAT,
                    recorded_at TIMESTAMPTZ DEFAULT NOW(),
                    is_closing BOOLEAN DEFAULT FALSE
                )
            """)
            await run_migration_step("""
                CREATE INDEX IF NOT EXISTS idx_line_movement_event
                ON line_movement (event_id, market_key, bookmaker)
            """)

            # System Sync State table for tracking waterfall pipeline timestamps
            await run_migration_step("""
                CREATE TABLE IF NOT EXISTS system_sync_state (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    last_odds_sync TIMESTAMPTZ,
                    last_ev_sync TIMESTAMPTZ,
                    last_grade_sync TIMESTAMPTZ,
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            await run_migration_step("INSERT INTO system_sync_state (id) VALUES (1) ON CONFLICT DO NOTHING")

            # Runtime hotfix SQL is intentionally idempotent; execute it on startup to
            # remove deploy-order dependency between code and manual DB migration steps.
            await run_sql_migration_file("src/db/migrations/20260426_runtime_hotfix_whale_and_ev_indexes.sql")

            logger.info("📡 [Background Init] Schema migrations and indexes complete.")
    except Exception as e:
        logger.error(f"❌ [Background Init] Startup DB error: {e}\n{traceback.format_exc()}")

    # 3. WebSocket Redis Listener
    try:
        logger.info("📡 [Background Init] Starting WebSocket Redis Listener...")
        await manager.start_redis_listener()
        logger.info("📡 [Background Init] WebSocket Redis Listener active.")
    except Exception as e:
        logger.error(f"❌ [Background Init] Failed to start WebSocket Redis Listener: {e}")

    # 4. Scheduler & Jobs
    if not RUN_INTERNAL_SCHEDULER:
        logger.info("📡 [Background Init] Internal scheduler disabled (RUN_INTERNAL_SCHEDULER=false).")
    else:
        try:
            logger.info("📡 [Background Init] Configuring Scheduler...")
            scheduler = AsyncIOScheduler()
            ingest_job_specs, ingest_meta = build_unified_ingest_schedule()
            sports_to_ingest = scheduled_sport_keys(ingest_job_specs)

            if ingest_meta.get("mode") == "legacy":
                logger.info(
                    "📡 [Scheduler] Unified ingestion (legacy): %s sports every %s min — set INGEST_USE_LEGACY_SCHEDULER=false for tiered polling",
                    ingest_meta.get("sport_count"),
                    ingest_meta.get("interval_minutes"),
                )
            else:
                floor = ingest_meta.get("active_interval_minutes_floor")
                floor_note = f", active floor={floor} min" if floor else ""
                logger.info(
                    "📡 [Scheduler] Tiered ingest: %s jobs — active=%s (per-sport min interval%s), inactive=%s every %s h, disabled=%s",
                    ingest_meta.get("sport_count"),
                    len(ingest_meta.get("active_sports") or []),
                    floor_note,
                    len(ingest_meta.get("inactive_sports") or []),
                    ingest_meta.get("inactive_interval_hours"),
                    ingest_meta.get("disabled") or [],
                )

            from services.grading_service import grading_service
            from services.kalshi_ingestion import kalshi_ingestion
            from services.whale_service import whale_service
            from services.grader import run_full_grading_pipeline
            from services.odds_api_client import odds_api_client

            async def guarded_unified_ingest(sport_key: str):
                if odds_api_client.all_keys_dead():
                    logger.debug("Skipping job — all keys cooling down")
                    return
                await unified_ingestion.run_with_retries(sport_key)

            async def guarded_kalshi_sync(sport_key: str):
                if odds_api_client.all_keys_dead():
                    logger.debug("Skipping job — all keys cooling down")
                    return
                await kalshi_ingestion.run(sport_key)

            for spec in ingest_job_specs:
                job_kw: dict = {
                    "args": [spec.sport_key],
                    "id": f"ingest_{spec.sport_key}",
                    "replace_existing": True,
                    "jitter": 30,
                }
                if spec.minutes is not None:
                    job_kw["minutes"] = spec.minutes
                else:
                    job_kw["hours"] = spec.hours
                job = scheduler.add_job(guarded_unified_ingest, "interval", **job_kw)
                logger.debug("📡 [Scheduler] Added unified ingestion job %s", job.id)
        
            scheduler.add_job(
                grading_service.run_grading_cycle,
                'interval',
                minutes=10,
                id="auto_grading",
                replace_existing=True,
                jitter=30,
            )
        
            scheduler.add_job(
                run_full_grading_pipeline,
                'interval',
                minutes=5,
                id="sql_grading",
                replace_existing=True,
                jitter=30,
            )
        
            # Kalshi Sync (NBA, MLB)
            for k_sport in ["NBA", "MLB"]:
                scheduler.add_job(
                    guarded_kalshi_sync,
                    'interval',
                    minutes=8,
                    args=[k_sport],
                    id=f"kalshi_sync_{k_sport.lower()}",
                    replace_existing=True,
                    jitter=30,
                )
        
            # Periodic Global Whale Check
            scheduler.add_job(
                whale_service.detect_whale_signals,
                'interval',
                minutes=12,
                id="whale_global_check",
                replace_existing=True,
                jitter=30,
            )

            # Live scores → live_scores table (ESPN / waterfall) for instant /api/live reads
            scheduler.add_job(
                live_data_service.poll_scores,
                "interval",
                seconds=max(15, int(settings.LIVE_DATA_POLLING_INTERVAL)),
                id="live_scores_cache_upsert",
                replace_existing=True,
                jitter=10,
            )
        
            # 7. High-Frequency Live Data Polling
            try:
                logger.info("📡 [Background Init] Starting Live Data Polling Service...")
                asyncio.create_task(live_data_service.run_loop())
            except Exception as e:
                logger.error(f"❌ [Background Init] Live Data Polling failed: {e}")

            scheduler.start()
        except Exception as e:
            logger.error(f"❌ [Background Init] Scheduler failed: {e}")

    # 8. Kalshi WebSocket Bridge
    try:
        logger.info("📡 [Background Init] Starting Kalshi WebSocket Bridge...")
        # Start with a few major indices/markets
        asyncio.create_task(kalshi_ws_manager.run(["INX", "BTC", "ETH"]))
    except Exception as e:
        logger.error(f"❌ [Background Init] Kalshi WS Bridge failed: {e}")

    logger.info("✅ [Background Init] All background services synchronized.")


@asynccontextmanager
async def backend_lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler: non-blocking startup."""
    
    commit_sha = os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown")
    env_name = os.getenv("RAILWAY_ENVIRONMENT_NAME", "local")
    db_host = os.getenv("DATABASE_URL", "").split("@")[-1].split("/")[0] if "@" in os.getenv("DATABASE_URL", "") else "unknown"
    
    logger.info("=" * 60)
    logger.info("🚀 [SYSTEM BOOT] Perplex Edge API Process Init")
    logger.info(f"   ► Commit SHA   : {commit_sha}")
    logger.info(f"   ► Environment  : {env_name}")
    logger.info(f"   ► DB Host      : {db_host}")
    logger.info(f"   ► Service Role : API + Ingest Worker + Heartbeat")
    logger.info("=" * 60)

    app.state.db_startup_degraded = False
    app.state.db_startup_last_error = None
    db_ok = False
    for attempt in range(5):
        try:
            await validate_db_connection()
            logger.info("DB connection validated.")
            db_ok = True
            break
        except Exception as e:
            wait_s = 2 ** attempt
            app.state.db_startup_last_error = str(e)
            logger.warning(
                "DB connection attempt %s failed: %s. Retrying in %ss",
                attempt + 1,
                e,
                wait_s,
            )
            await asyncio.sleep(wait_s)
    if not db_ok:
        app.state.db_startup_degraded = True
        logger.critical(
            "DB connection failed after 5 attempts. Starting in degraded mode."
        )

    async def _safe_initialize_backend_services() -> None:
        try:
            await initialize_backend_services()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(
                "Startup services failed (non-fatal; API stays up): %s",
                e,
                exc_info=True,
            )

    # Run heavy tasks in the background so they don't block liveness (/health)
    init_task = asyncio.create_task(_safe_initialize_backend_services())
    yield
    init_task.cancel()
    try:
        await init_task
    except asyncio.CancelledError:
        pass

app = FastAPI(title=APP_NAME, redirect_slashes=False, lifespan=backend_lifespan)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(AuthCircuitBreakerMiddleware) # Register circuit breaker middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://perplex-edge.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _cors_headers_for_request(request: Request) -> dict:
    origin = request.headers.get("Origin") or request.headers.get("origin")
    allow_origin = "https://perplex-edge.vercel.app"
    if origin and (origin.endswith(".vercel.app") or "localhost" in origin):
        allow_origin = origin
    return {
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE, PATCH",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standard JSON error shape for HTTP errors."""
    rid = get_request_id()
    detail = exc.detail
    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("detail") or str(detail)
        code = detail.get("code", "http_error")
    else:
        message = str(detail)
        code = "http_error"
    body = {"error": {"code": code, "message": message, "request_id": rid}}
    headers = _cors_headers_for_request(request)
    return JSONResponse(status_code=exc.status_code, content=body, headers=headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    rid = get_request_id()
    body = {
        "error": {
            "code": "validation_error",
            "message": "Request validation failed",
            "request_id": rid,
            "details": exc.errors(),
        }
    }
    return JSONResponse(status_code=422, content=body, headers=_cors_headers_for_request(request))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fail-safe for production: CORS + standard error envelope."""
    logger.error(f"GLOBAL EXCEPTION CAUGHT: {str(exc)}", exc_info=True)
    rid = get_request_id()
    headers = _cors_headers_for_request(request)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Internal Server Error",
                "request_id": rid,
            }
        },
        headers=headers,
    )

@app.get("/api/smart-money")
async def get_sharp_signals():
    """Smart Money endpoint."""
    return {"status": "processing", "signal": "captured"}

@app.post("/admin/reset-odds-circuit-breaker", tags=["admin"])
@app.post("/api/admin/reset-odds-circuit-breaker", tags=["admin"])
async def reset_odds_circuit_breaker():
    """Manual reset for Odds API key cooldown state."""
    from services.odds_api_client import odds_api_client

    if hasattr(odds_api_client, "_dead_until"):
        odds_api_client._dead_until.clear()
    if hasattr(odds_api_client, "_all_keys_dead_until"):
        odds_api_client._all_keys_dead_until = None
    return {"status": "ok", "message": "Circuit breaker reset. Keys will retry immediately."}

# --- Router Registration (all guarded) ---
if health_router:        app.include_router(health_router, prefix="/api/health", tags=["health"])
if intel_router:         app.include_router(intel_router, prefix="/api/intel", tags=["intel"])
if pick_intel_router:    app.include_router(pick_intel_router, prefix="/api", tags=["pick-intel"])
if user_settings_router: app.include_router(user_settings_router, prefix="/api", tags=["user-settings"])
if meta_router:          app.include_router(meta_router, prefix="/api/meta", tags=["meta"])
if auth_router:          app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
if props_router:         app.include_router(props_router, prefix="/api/props", tags=["props"])
if ev_router:            app.include_router(ev_router, prefix="/api/ev", tags=["ev"])
if clv_router:           app.include_router(clv_router, prefix="/api/clv", tags=["clv"])
if brain_router:         app.include_router(brain_router, prefix="/api/brain", tags=["brain"])
if bets_router:          app.include_router(bets_router, prefix="/api/bets", tags=["bets"])
if injuries_router:      app.include_router(injuries_router, prefix="/api/injuries", tags=["injuries"])
if news_router:          app.include_router(news_router, prefix="/api/news", tags=["news"])
if signals_router:       app.include_router(signals_router, prefix="/api/signals", tags=["signals"])
if metrics_router:       app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])
if hit_rate_router:      app.include_router(hit_rate_router, prefix="/api/hit-rate", tags=["hit-rate"])
if whale_router:         app.include_router(whale_router, prefix="/api/whale", tags=["whale"])
if steam_router:         app.include_router(steam_router, prefix="/api/steam", tags=["steam"])
if stripe_router:        app.include_router(stripe_router, prefix="/api/stripe", tags=["stripe"])
if billing_router:       app.include_router(billing_router, prefix="/api/billing", tags=["billing"])
if search_router:        app.include_router(search_router, prefix="/api/search", tags=["search"])
if oracle_router:        app.include_router(oracle_router, prefix="/api/oracle", tags=["oracle"])
if live_router:          app.include_router(live_router, prefix="/api/live", tags=["live"])
if slate_router:         app.include_router(slate_router, prefix="/api/slate", tags=["slate"])
if ws_ev_router:         app.mount("/api/ws_ev", ws_ev_router)
if line_movement_router: app.include_router(line_movement_router, prefix="/api/line-movement", tags=["line_movement"])
if arbitrage_router:     app.include_router(arbitrage_router, prefix="/api/arbitrage", tags=["arbitrage"])
if middle_boost_router:  app.include_router(middle_boost_router, prefix="/api/middle-boost", tags=["middle-boost"])
if kalshi_router:        app.include_router(kalshi_router, prefix="/api/kalshi", tags=["kalshi"])
if kalshi_ws_router:     app.include_router(kalshi_ws_router, prefix="/api/kalshi_ws", tags=["kalshi_ws"])
if sharp_router:         app.include_router(sharp_router, prefix="/api/sharp", tags=["sharp"])
if parlays_router:       app.include_router(parlays_router, prefix="/api/parlays", tags=["parlays"])
if simulation_router:    app.include_router(simulation_router, prefix="/api/simulation", tags=["simulation"])
if props_history_router: app.include_router(props_history_router, prefix="/api", tags=["props-history"])
if waterfall_router:     app.include_router(waterfall_router, prefix="/api/waterfall", tags=["waterfall"])

# Hero Stats (Analytics Modal)
from routers.hero import router as hero_router
app.include_router(hero_router, prefix="/api/hero", tags=["hero"])

if alerts_router:        app.include_router(alerts_router)
if audit_router:         app.include_router(audit_router)

# Unified Orchestration
from routers.unified import router as unified_router
if unified_router:       app.include_router(unified_router, prefix="/api", tags=["unified"])

@app.get("/health")
async def health():
    """
    Liveness probe for Railway / load balancers: always HTTP 200 if the process is up.
    Database status is included in JSON; strict readiness (including 503 when not ready)
    is GET /api/health/ready.
    """
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "alive",
            "database_connected": True,
            "startup_degraded": bool(getattr(app.state, "db_startup_degraded", False)),
            "startup_db_error": getattr(app.state, "db_startup_last_error", None),
            "auth_bypass_enabled": bool(getattr(settings, "BYPASS_AUTH", False)),
            "supabase_role_split_ready": bool(getattr(settings, "SUPABASE_ROLE_SPLIT_READY", False)),
        }
    except Exception as e:
        logger.warning("Liveness /health: database check failed: %s", e)
        return {
            "status": "alive",
            "database_connected": False,
            "database_error": str(e),
            "startup_degraded": bool(getattr(app.state, "db_startup_degraded", False)),
            "startup_db_error": getattr(app.state, "db_startup_last_error", None),
            "auth_bypass_enabled": bool(getattr(settings, "BYPASS_AUTH", False)),
            "supabase_role_split_ready": bool(getattr(settings, "SUPABASE_ROLE_SPLIT_READY", False)),
        }

@app.get("/")
async def root():
    return {"name": APP_NAME, "status": "healthy"}

@app.get("/api/admin/odds-usage", tags=["admin"])
async def admin_odds_usage(db: AsyncSession = Depends(get_db)):
    """Monthly TheOddsAPI request usage (from DB + last known headers). Same fields as health/deps components.odds_quota."""
    from services.odds_quota_store import fetch_usage_summary

    return await fetch_usage_summary(db)


@app.get("/api/admin/system-health", tags=["admin"])
async def admin_system_health(db: AsyncSession = Depends(get_db)):
    """
    Compact ops snapshot: DB / pipeline / odds stream + quota (no full /api/health/deps degradation object).
    """
    from routers.health import compute_health

    base = await compute_health(db)
    internal = base.pop("_internal", None) or {}
    return {
        "status": base.get("status"),
        "system_status": base.get("system_status"),
        "odds_stream": base.get("odds_stream"),
        "components": {
            "database": base.get("database"),
            "odds_api": base.get("odds_api"),
            "kalshi": base.get("kalshi"),
            "pipeline_status": base.get("pipeline_status"),
            "inference_status": base.get("inference_status"),
            "props_count": base.get("props_count"),
        },
        "odds_quota": base.get("odds_quota"),
        "flags": {
            "is_stale": internal.get("is_stale"),
            "odds_api_quota_exhausted": internal.get("odds_api_quota_exhausted"),
            "odds_api_ingest_blocked_reason": internal.get("odds_api_ingest_blocked_reason"),
            "recent_ingest_heartbeat_ok": internal.get("recent_ingest_heartbeat_ok"),
            "auth_bypass_enabled": internal.get("auth_bypass_enabled"),
            "supabase_role_split_ready": internal.get("supabase_role_split_ready"),
            "supabase_service_key_looks_anon": internal.get("supabase_service_key_looks_anon"),
        },
        "freshness": {
            "last_odds_update": base.get("last_odds_update"),
            "last_ev_update": base.get("last_ev_update"),
        },
        "sync": {
            "last_odds_sync": base.get("last_odds_sync"),
            "last_ev_sync": base.get("last_ev_sync"),
            "last_grade_sync": base.get("last_grade_sync"),
        },
        "timestamp": base.get("timestamp"),
        "version": base.get("version"),
    }


@app.get("/api/admin/quota/status", tags=["admin"])
async def admin_quota_status(request: Request):
    _require_admin_bearer(request)
    from services.external_api_gateway import external_api_gateway
    from services.odds_api_client import odds_api_client

    return {
        "provider": "theoddsapi",
        "budget": await external_api_gateway.quota_status("theoddsapi"),
        "keys": odds_api_client.key_health() if hasattr(odds_api_client, "key_health") else {},
    }


@app.get("/api/admin/quota/logs", tags=["admin"])
async def admin_quota_logs(request: Request, limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    _require_admin_bearer(request)
    rows = await db.execute(
        text(
            """
            SELECT provider, endpoint, sport, markets, regions, status_code,
                   x_requests_remaining, x_requests_used, x_requests_last,
                   cache_hit, started_at, completed_at
            FROM external_api_call_log
            ORDER BY started_at DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    )
    return {"items": [dict(r._mapping) for r in rows.fetchall()], "limit": limit}


@app.get("/api/admin/quota/budgets", tags=["admin"])
async def admin_quota_budgets(request: Request):
    _require_admin_bearer(request)
    import os
    return {
        "hourly_limit": int(os.getenv("EXT_API_HOURLY_BUDGET", "1200")),
        "daily_limit": int(os.getenv("EXT_API_DAILY_BUDGET", "12000")),
        "live_reserve_limit": int(os.getenv("EXT_API_LIVE_RESERVE_BUDGET", "250")),
    }


@app.get("/api/admin/quota/protection-mode", tags=["admin"])
async def admin_quota_protection_mode(request: Request):
    _require_admin_bearer(request)
    from services.external_api_gateway import external_api_gateway
    b = await external_api_gateway.quota_status("theoddsapi")
    return {"provider": "theoddsapi", "protection_mode": b.get("mode"), "budget": b}


@app.post("/api/admin/circuit-breaker/reset")
@app.post("/api/admin/reset-circuit-breaker")
async def reset_auth_circuit_breaker(request: Request):
    """Manually reset the auth circuit breaker."""
    # Simple check for ADMIN_SECRET_KEY
    import os
    admin_key = os.getenv("ADMIN_SECRET_KEY")
    auth_header = request.headers.get("Authorization", "")
    
    if not admin_key or auth_header != f"Bearer {admin_key}":
        raise HTTPException(status_code=403, detail="Unauthorized reset attempt.")
    
    auth_breaker.reset()
    return {"status": "success", "message": "Circuit breaker reset to CLOSED state."}


def _require_admin_bearer(request: Request) -> None:
    admin_key = os.getenv("ADMIN_SECRET_KEY")
    auth_header = request.headers.get("Authorization", "")
    if not admin_key or auth_header != f"Bearer {admin_key}":
        raise HTTPException(status_code=403, detail="Unauthorized admin request.")


@app.post("/api/admin/trigger-ingestion")
@app.post("/admin/trigger-ingestion")
async def admin_trigger_ingestion(
    request: Request,
    sport: Optional[str] = Query(
        None,
        description="Sport key (e.g. basketball_nba). Overrides JSON body if both sent.",
    ),
):
    """
    Ops: run one unified_ingestion cycle for a sport (same as /api/health/ingest/{sport})
    but matches common runbook URL. JSON body may include {"sport": "basketball_nba"}.
    """
    _require_admin_bearer(request)
    resolved = "basketball_nba"
    try:
        body = await request.json()
        if isinstance(body, dict) and body.get("sport"):
            resolved = str(body["sport"]).strip() or resolved
    except Exception:
        pass
    if sport:
        resolved = str(sport).strip() or resolved

    logger.info("🚦 [Admin trigger-ingestion] starting sport=%s", resolved)
    metrics = await unified_ingestion.run(resolved)
    return {"status": "ok", "sport": resolved, "metrics": metrics}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
