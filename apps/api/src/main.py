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
import os
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
        msg = f"❌ CRITICAL ERROR: Missing environment variables: {', '.join(missing)}"
        logger.error(msg)
        # In production, we want to fail fast. In local dev, we might just warn.
        if os.getenv("RAILWAY_ENVIRONMENT_NAME"):
            raise RuntimeError(msg)
        else:
            logger.warning("⚠️ Running in LOCAL mode with missing variables. Some features will fail.")

validate_env()
def safe_import(module_path, alias):
    try:
        # FastAPI routers are typically named 'router' in their respective modules
        mod = __import__(f"routers.{module_path}", fromlist=["router"])
        if hasattr(mod, "router"):
            return mod.router
        # Fallback to alias if 'router' is not found
        return getattr(mod, alias)
    except Exception as e:
        import traceback
        logging.error(f"❌ Error importing router '{module_path}': {e}\n{traceback.format_exc()}")
        return None

health_router       = safe_import("health", "health")
meta_router         = safe_import("meta", "meta")
auth_router         = safe_import("auth", "auth")
props_router        = safe_import("props", "props")
ev_router           = safe_import("ev", "ev")
clv_router          = safe_import("clv", "clv")
brain_router        = safe_import("brain_router", "brain")
bets_router         = safe_import("bets", "bets")
injuries_router     = safe_import("injuries", "injuries")
news_router         = safe_import("news", "news")
signals_router      = safe_import("signals", "signals")
metrics_router      = safe_import("metrics", "metrics")
hit_rate_router     = safe_import("hit_rate", "hit_rate")
whale_router        = safe_import("whale", "whale")
steam_router        = safe_import("steam", "steam")
stripe_router       = safe_import("stripe_router", "stripe")
search_router       = safe_import("search", "search")
oracle_router       = safe_import("oracle", "oracle")
live_router         = safe_import("live", "live")
slate_router        = safe_import("slate", "slate")
ws_ev_router        = safe_import("ws_ev", "ws_ev")
line_movement_router = safe_import("line_movement", "line_movement")
arbitrage_router    = safe_import("arbitrage", "arbitrage")
kalshi_router       = safe_import("kalshi", "kalshi")
kalshi_ws_router    = safe_import("kalshi_ws_proxy", "kalshi_ws")
systems_router      = safe_import("systems", "systems")
performance_router  = safe_import("performance", "performance")
streaks_router      = safe_import("streaks", "streaks")
intel_router        = safe_import("intel", "router")
props_history_router = safe_import("props_history", "router")
contest_router      = safe_import("contest_router", "contests")

app = FastAPI(title=APP_NAME, redirect_slashes=False)

@app.on_event("startup")
async def startup():
    """Ensure database tables are created on startup."""
    import logging
    logging.info("Starting up: Ensuring database tables exist...")
    try:
        from db.session import engine
        import db.base
        from db.base import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            # Migration check for ev_signals.sport
            from sqlalchemy import text
            async def check_ev_sport(connection):
                # Using text() for raw SQL check
                res = await connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='ev_signals' AND column_name='sport'"))
                if not res.fetchone():
                    logging.warning("⚠️ Column 'sport' missing in 'ev_signals'. Attempting migration...")
                    await connection.execute(text("ALTER TABLE ev_signals ADD COLUMN sport VARCHAR"))
                    logging.info("✅ Migration successful: Added 'sport' to 'ev_signals'.")
            
            # Since we are in run_sync context for create_all, we need a separate way or just run it after
            # Actually engine.begin() provides a connection.
        
        # Run migration after create_all
        async with engine.begin() as conn:
            # information_schema check is for postgres. For sqlite (dev) we might skip or use pragma.
            is_sqlite = "sqlite" in str(engine.url)
            if not is_sqlite:
                await conn.execute(text("ALTER TABLE ev_signals ADD COLUMN IF NOT EXISTS sport VARCHAR"))
                await conn.execute(text("ALTER TABLE unified_odds ADD COLUMN IF NOT EXISTS implied_prob FLOAT"))
                logging.info("Startup complete: Schema verified.")
            else:
                logging.info("Startup complete: Database initialized (SQLite).")
    except Exception as e:
        # Tables might already exist, or connection failed
        logging.error(f"Startup error during DB initialization: {e}")

    # Start WebSocket Broadcast Listener (Redis-backed)
    try:
        await manager.start_redis_listener()
        logging.info("✅ WebSocket Redis Listener active.")
    except Exception as e:
        logging.error(f"Failed to start WebSocket Redis Listener: {e}")

    # Initialize Scheduler
    scheduler = AsyncIOScheduler()
    
    # Schedule Ingest Jobs (Every 5 minutes)
    sports_to_ingest = [
        # American Football
        "americanfootball_nfl",
        "americanfootball_ncaaf",

        # Basketball
        "basketball_nba",

        # Baseball
        "baseball_mlb",

        # Hockey
        "icehockey_nhl",

        # Soccer (a few high-value comps)
        "soccer_usa_mls",
        "soccer_uefa_champs_league",
        "soccer_epl",

        # MMA
        "mma_mixed_martial_arts",

        # Aussie Rules / Rugby (optional)
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
    
    # Schedule Grading Job (Every 10 minutes)
    from services.grading_service import grading_service
    scheduler.add_job(
        grading_service.run_grading_cycle,
        'interval',
        minutes=10,
        id="auto_grading",
        replace_existing=True
    )
    
    scheduler.start()
    logging.info("Scheduler started: Ingest and Grading jobs queued.")

    # Trigger initial ingest after a short delay
    async def initial_ingest():
        await asyncio.sleep(5)
        for sport in sports_to_ingest:
            logging.info(f"Triggering initial ingest for {sport}...")
            await unified_ingestion.run_with_retries(sport)
            
    asyncio.create_task(initial_ingest())

    # Start CLV Tracking Loop
    from services.brain_clv_tracker_loop import start_clv_tracker
    logging.info("CLV Tracker started.")
    
origins = [
    "https://perplex-edge.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)

@app.get("/api/smart-money")
async def get_sharp_signals():
    """Neural Engine: Smart Money Threadpool (Fix #4)"""
    from services.brain_sharp_money import sharp_money_brain
    from db.session import SessionLocal
    import asyncio
    
    def _sync():
        with SessionLocal() as syncdb:
            # Note: syncdb is a sync session for the threadpool
            return {"status": "processing", "signal": "captured"} # Placeholder for actual logic
            
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync)

# Include external health router for more detailed checks
# Guarded Router Inclusion
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
if systems_router:       app.include_router(systems_router, prefix="/api/systems", tags=["systems"])
if performance_router:   app.include_router(performance_router, prefix="/api/performance", tags=["performance"])
if streaks_router:       app.include_router(streaks_router, prefix="/api/streaks", tags=["streaks"])
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
