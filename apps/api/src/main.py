import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import APP_NAME, settings
from middleware.request_id import RequestIDMiddleware
from db.base import Base
from db.session import engine
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.unified_ingestion import unified_ingestion
import logging
from core.connection_manager import manager

logger = logging.getLogger(__name__)


def validate_env():
    """Fail fast if critical environment variables are missing."""
    critical_vars = [
        "DATABASE_URL",
        "THE_ODDS_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    missing = [v for v in critical_vars if not os.getenv(v)]
    if missing:
        msg = f"CRITICAL ERROR: Missing environment variables: {', '.join(missing)}"
        logger.error(msg)
        if os.getenv("RAILWAY_ENVIRONMENT_NAME"):
            raise RuntimeError(msg)
        else:
            logger.warning("Running in LOCAL mode with missing variables. Some features will fail.")


validate_env()


def safe_import(module_path, alias):
    try:
        mod = __import__(f"routers.{module_path}", fromlist=["router"])
        if hasattr(mod, "router"):
            return mod.router
        return getattr(mod, alias)
    except Exception as e:
        import traceback
        logging.error(f"Error importing router '{module_path}': {e}\n{traceback.format_exc()}")
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
search_router        = safe_import("search", "search")
oracle_router        = safe_import("oracle", "oracle")
live_router          = safe_import("live", "live")
slate_router         = safe_import("slate", "slate")
ws_ev_router         = safe_import("ws_ev", "ws_ev")
line_movement_router = safe_import("line_movement", "line_movement")
arbitrage_router     = safe_import("arbitrage", "arbitrage")
kalshi_router        = safe_import("kalshi", "kalshi")
kalshi_ws_router     = safe_import("kalshi_ws_proxy", "kalshi_ws")
intel_router         = safe_import("intel", "router")
props_history_router = safe_import("props_history", "router")


app = FastAPI(title=APP_NAME, redirect_slashes=False)

origins = [
    "https://perplex-edge.vercel.app",
    "https://perplex-edge-1umcu8vby-bigpre12s-projects.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Startup: create DB tables, run migrations, start scheduler.
    Initial ingest runs in background so /health is available immediately."""
    logging.info("Starting up: Ensuring database tables exist...")
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Schema migrations (safe: IF NOT EXISTS)
        async with engine.begin() as conn:
            is_sqlite = "sqlite" in str(engine.url)
            if not is_sqlite:
                await conn.execute(text("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS sport VARCHAR"))
                await conn.execute(text("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS true_prob FLOAT"))
                await conn.execute(text("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS edge_percent FLOAT"))
                await conn.execute(text("ALTER TABLE unified_odds ADD COLUMN IF NOT EXISTS sport VARCHAR"))
                await conn.execute(text("ALTER TABLE unified_odds ADD COLUMN IF NOT EXISTS implied_prob FLOAT"))
                await conn.execute(text("ALTER TABLE props_live ADD COLUMN IF NOT EXISTS sport VARCHAR"))
                await conn.execute(text("ALTER TABLE props_live ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ"))
                logging.info("Startup: Schema migrations complete.")
    except Exception as e:
        logging.error(f"Startup DB error: {e}")

    # WebSocket Redis Listener
    try:
        await manager.start_redis_listener()
        logging.info("WebSocket Redis Listener active.")
    except Exception as e:
        logging.error(f"Failed to start WebSocket Redis Listener: {e}")

    # Scheduler
    scheduler = AsyncIOScheduler()
    sports_to_ingest = [
        "americanfootball_nfl",
        "americanfootball_ncaaf",
        "basketball_nba",
        "baseball_mlb",
        "icehockey_nhl",
        "soccer_usa_mls",
        "soccer_uefa_champs_league",
        "soccer_epl",
        "mma_mixed_martial_arts",
        "aussierules_afl",
        "rugbyleague_nrl",
    ]

    for sport in sports_to_ingest:
        scheduler.add_job(
            unified_ingestion.run_with_retries,
            'interval',
            minutes=5,
            args=[sport],
            id=f"ingest_{sport}",
            replace_existing=True
        )

    from services.grading_service import grading_service
    scheduler.add_job(
        grading_service.run_grading_cycle,
        'interval',
        minutes=10,
        id="auto_grading",
        replace_existing=True
    )
    scheduler.start()
    logging.info("Scheduler started.")

    # Initial ingest runs fully in background — does NOT block /health
    async def initial_ingest():
        await asyncio.sleep(10)  # Give app time to fully boot first
        for sport in sports_to_ingest:
            try:
                logging.info(f"Initial ingest: {sport}")
                await unified_ingestion.run_with_retries(sport)
            except Exception as e:
                logging.error(f"Initial ingest error for {sport}: {e}")

    asyncio.create_task(initial_ingest())

    # CLV Tracker
    from services.brain_clv_tracker_loop import start_clv_tracker
    logging.info("CLV Tracker started.")


@app.get("/api/smart-money")
async def get_sharp_signals():
    """Smart Money endpoint."""
    return {"status": "processing", "signal": "captured"}


# --- Router Registration (all guarded) ---
if health_router:        app.include_router(health_router, prefix="/api/health", tags=["health"])
if intel_router:         app.include_router(intel_router, prefix="/api/intel", tags=["intel"])
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
if search_router:        app.include_router(search_router, prefix="/api/search", tags=["search"])
if oracle_router:        app.include_router(oracle_router, prefix="/api/oracle", tags=["oracle"])
if live_router:          app.include_router(live_router, prefix="/api/live", tags=["live"])
if slate_router:         app.include_router(slate_router, prefix="/api/slate", tags=["slate"])
if ws_ev_router:         app.mount("/api/ws_ev", ws_ev_router)
if line_movement_router: app.include_router(line_movement_router, prefix="/api/line-movement", tags=["line_movement"])
if arbitrage_router:     app.include_router(arbitrage_router, prefix="/api/arbitrage", tags=["arbitrage"])
if kalshi_router:        app.include_router(kalshi_router, prefix="/api/kalshi", tags=["kalshi"])
if kalshi_ws_router:     app.include_router(kalshi_ws_router, prefix="/api/kalshi_ws", tags=["kalshi_ws"])
if props_history_router: app.include_router(props_history_router, prefix="/api", tags=["props-history"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"name": APP_NAME, "status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
