import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import APP_NAME, settings
from db.base import Base
from db.session import engine

import logging

# Define safe_import inside main.py for early availability
def safe_import(module_path, alias):
    try:
        # FastAPI routers are typically named 'router' in their respective modules
        mod = __import__(f"routers.{module_path}", fromlist=["router"])
        return mod.router
    except Exception as e:
        logging.warning(f"⚠️ Skipping router '{module_path}': {e}")
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
lines_router        = safe_import("lines", "lines")
metrics_router      = safe_import("metrics", "metrics")
hit_rate_router     = safe_import("hit_rate", "hit_rate")
whale_router        = safe_import("whale", "whale")
parlay_router       = safe_import("parlay_suggestions", "parlay")
steam_router        = safe_import("steam", "steam")
stripe_router       = safe_import("stripe_router", "stripe")
search_router       = safe_import("search", "search")
intel_router        = safe_import("intel", "intel")
oracle_router       = safe_import("oracle", "oracle")
live_router         = safe_import("live", "live")
slate_router        = safe_import("slate", "slate")
ws_ev_router        = safe_import("ws_ev", "ws_ev")
line_movement_router = safe_import("line_movement", "line_movement")
arbitrage_router    = safe_import("arbitrage", "arbitrage")
kalshi_router       = safe_import("kalshi", "kalshi")
kalshi_ws_router    = safe_import("kalshi_ws_proxy", "kalshi_ws")

app = FastAPI(title=APP_NAME, redirect_slashes=False)

@app.on_event("startup")
async def startup():
    """Ensure database tables are created on startup."""
    import logging
    logging.info("Starting up: Ensuring database tables exist...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Startup complete: Database initialized.")
    except Exception as e:
        logging.error(f"Startup error during DB initialization: {e}")
        # We don't crash here so that the health check can still return 'degraded'
        # and provide diagnostics instead of a generic 503.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "https://perplex-edge.vercel.app"),
        "https://perplex-edge-git-main-bigpre12s-projects.vercel.app",
        "https://perplex-edge.vercel.app",
        "http://localhost:3000",
        "http://localhost:1337",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include external health router for more detailed checks
# Guarded Router Inclusion
if health_router:        app.include_router(health_router, prefix="/api/health", tags=["health"])
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
if lines_router:         app.include_router(lines_router, prefix="/api/lines", tags=["lines"])
if metrics_router:       app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])
if hit_rate_router:      app.include_router(hit_rate_router, prefix="/api/hit-rate", tags=["hit-rate"])
if whale_router:         app.include_router(whale_router, prefix="/api/whale", tags=["whale"])
if parlay_router:        app.include_router(parlay_router, prefix="/api/parlay", tags=["parlay"])
if steam_router:         app.include_router(steam_router, prefix="/api/steam", tags=["steam"])
if stripe_router:        app.include_router(stripe_router, prefix="/api/stripe", tags=["stripe"])
if search_router:        app.include_router(search_router, prefix="/api/search", tags=["search"])
if intel_router:         app.include_router(intel_router, prefix="/api/intel", tags=["intel"])
if oracle_router:        app.include_router(oracle_router, prefix="/api/oracle", tags=["oracle"])
if live_router:          app.include_router(live_router, prefix="/api/live", tags=["live"])
if slate_router:         app.include_router(slate_router, prefix="/api/slate", tags=["slate"])
if ws_ev_router:         app.include_router(ws_ev_router, prefix="/api/ws_ev", tags=["ws_ev"])
if line_movement_router: app.include_router(line_movement_router, prefix="/api/line-movement", tags=["line_movement"])
if arbitrage_router:     app.include_router(arbitrage_router, prefix="/api/arbitrage", tags=["arbitrage"])
if kalshi_router:        app.include_router(kalshi_router, prefix="/api/kalshi", tags=["kalshi"])
if kalshi_ws_router:     app.include_router(kalshi_ws_router, prefix="/api/kalshi_ws", tags=["kalshi_ws"])

@app.get("/")
async def root():
    return {"name": APP_NAME, "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
    
