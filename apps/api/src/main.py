import sys
import os
import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import APP_NAME, settings
from middleware.request_id import RequestIDMiddleware, get_request_id
from middleware.auth_circuit_breaker import AuthCircuitBreakerMiddleware, auth_breaker # Import new circuit breaker
from db.base import Base
from db.session import engine
from services.unified_ingestion import unified_ingestion
from core.connection_manager import manager
from services.live_data_service import live_data_service
from services.kalshi_ws import kalshi_ws_manager

logger = logging.getLogger(__name__)
logging.getLogger("apscheduler").setLevel(logging.INFO)

def validate_env():
    """Fail fast if critical environment variables are missing, but with descriptive error logs."""
    critical_vars = [
        "DATABASE_URL",
        "THE_ODDS_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    missing = [v for v in critical_vars if not os.getenv(v)]
    if missing:
        msg = f"❌ CONFIGURATION WARNING: Missing environment variables: {', '.join(missing)}"
        logger.warning("**************************************************")
        logger.warning(msg)
        logger.warning("Please ensure these variables are set in the Railway dashboard.")
        logger.warning("**************************************************")
        
        # Only hard crash on DATABASE_URL in production
        if os.getenv("RAILWAY_ENVIRONMENT_NAME") and not os.getenv("DATABASE_URL"):
            raise RuntimeError("CRITICAL: DATABASE_URL is missing. Backend cannot start.")

# Run validation immediately
validate_env()

def safe_import(module_path, alias):
    try:
        mod = __import__(f"routers.{module_path}", fromlist=["router"])
        if hasattr(mod, "router"):
            return mod.router
        return getattr(mod, alias)
    except Exception as e:
        logger.error(f"Error importing router '{module_path}': {e}", exc_info=True)
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
sharp_router         = safe_import("sharp", "router")
parlays_router       = safe_import("parlays", "router")
props_history_router = safe_import("props_history", "router")
alerts_router        = safe_import("alerts", "router")
audit_router         = safe_import("audit", "router")
waterfall_router     = safe_import("waterfall", "router")

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
        logger.info("📡 [Background Init] Running schema migrations...")
        is_sqlite = "sqlite" in str(engine.url)
        
        async def run_migration_step(query: str):
            try:
                async with engine.begin() as conn:
                    await conn.execute(text(query))
            except Exception as e:
                q_snippet = query[:100] if query else "NULL"
                logger.debug("Migration step skipped or failed (continuing): %s... Error: %s", q_snippet, e)

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
    try:
        logger.info("📡 [Background Init] Configuring Scheduler...")
        scheduler = AsyncIOScheduler()
        sports_to_ingest = [
            "americanfootball_nfl", "americanfootball_ncaaf", "basketball_nba",
            "baseball_mlb", "icehockey_nhl", "soccer_usa_mls",
            "soccer_uefa_champs_league", "soccer_epl", "mma_mixed_martial_arts",
            "aussierules_afl", "rugbyleague_nrl",
        ]

        ingest_interval = max(1, int(os.getenv("INGEST_INTERVAL_MINUTES", "5")))
        logger.info(
            "📡 [Scheduler] Unified ingestion interval: %s minutes (INGEST_INTERVAL_MINUTES)",
            ingest_interval,
        )
        # NOTE: Internal scheduler is re-enabled to ensure data freshness.
        for sport in sports_to_ingest:
            job = scheduler.add_job(
                unified_ingestion.run_with_retries,
                'interval',
                minutes=ingest_interval,
                args=[sport],
                id=f"ingest_{sport}",
                replace_existing=True,
                jitter=30,
            )
            logger.debug("📡 [Scheduler] Added unified ingestion job %s", job.id)

        from services.grading_service import grading_service
        from services.kalshi_ingestion import kalshi_ingestion
        from services.whale_service import whale_service
        from services.grader import run_full_grading_pipeline
        
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
                kalshi_ingestion.run,
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
        
        scheduler.start()
        logger.info("📡 [Background Init] Internal scheduler active.")
        logger.info("📡 [Background Init] Scheduler started.")

        # 5. Initial Ingest (bounded concurrency to avoid DB pool exhaustion)
        ingest_semaphore = asyncio.Semaphore(3)

        async def run_parallel_ingest():
            logger.info("📡 [Background Init] Starting parallel initial ingestion phase...")
            async def bounded_ingest(coro):
                async with ingest_semaphore:
                    return await coro

            ingest_tasks = [
                bounded_ingest(unified_ingestion.run_with_retries(sport)) for sport in sports_to_ingest
            ]
            ingest_tasks.append(bounded_ingest(kalshi_ingestion.run("NBA")))
            ingest_tasks.append(bounded_ingest(kalshi_ingestion.run("MLB")))
            
            results = await asyncio.gather(*ingest_tasks, return_exceptions=True)
            for sport, res in zip(sports_to_ingest + ["Kalshi_NBA", "Kalshi_MLB"], results):
                if isinstance(res, Exception):
                    logger.error(f"❌ [Initial Ingest Failed] {sport}: {res}")
                else:
                    logger.info(f"✅ [Initial Ingest Complete] {sport}")
            
            # Post-ingest graders hook
            logger.info("📡 [Background Init] Running post-ingest SQL grading pipeline...")
            try:
                from services.grader import run_full_grading_pipeline
                await run_full_grading_pipeline()
            except Exception as e:
                logger.error(f"❌ [Background Init] Post-ingest grader failed: {e}")

        asyncio.create_task(run_parallel_ingest())

    except Exception as e:
        logger.error(f"❌ [Background Init] Scheduler setup failed: {e}")

    # 6. CLV Tracker
    try:
        from services.brain_clv_tracker_loop import start_clv_tracker
        asyncio.create_task(start_clv_tracker())
        logger.info("📡 [Background Init] CLV Tracker started.")
    except Exception as e:
        logger.error(f"❌ [Background Init] CLV Tracker failed: {e}")

    # 7. High-Frequency Live Data Polling
    try:
        logger.info("📡 [Background Init] Starting Live Data Polling Service...")
        asyncio.create_task(live_data_service.run_loop())
    except Exception as e:
        logger.error(f"❌ [Background Init] Live Data Polling failed: {e}")

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

    # Run heavy tasks in the background so they don't block /health
    init_task = asyncio.create_task(initialize_backend_services())
    yield
    # Clean up tasks if necessary on shutdown
    init_task.cancel()

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

@app.post("/admin/reset-circuit-breaker", tags=["admin"])
async def reset_circuit_breaker():
    """Manual reset for Odds API circuit breaker"""
    from services.odds_api_client import odds_api_client

    if hasattr(odds_api_client, "_dead_until"):
        odds_api_client._dead_until.clear()
    elif hasattr(odds_api_client, "_dead_keys"):
        odds_api_client._dead_keys.clear()
    return {"status": "ok", "message": "Circuit breaker reset. Keys will retry immediately."}

# --- Router Registration (all guarded) ---
if health_router:        app.include_router(health_router, prefix="/api/health", tags=["health"])
if intel_router:         app.include_router(intel_router, prefix="/api/intel", tags=["intel"])
if pick_intel_router:    app.include_router(pick_intel_router, prefix="/api", tags=["pick-intel"])
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
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"name": APP_NAME, "status": "healthy"}

@app.post("/api/admin/reset-circuit-breaker")
async def reset_circuit_breaker(request: Request):
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
