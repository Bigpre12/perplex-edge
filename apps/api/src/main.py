import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import APP_NAME, settings
from db.base import Base
from db.session import engine

from routers.health import router as health_router
from routers.meta import router as meta_router
from routers.auth import router as auth_router
from routers.props import router as props_router
from routers.ev import router as ev_router
from routers.clv import router as clv_router
from routers.brain_router import router as brain_router
from routers.bets import router as bets_router
from routers.injuries import router as injuries_router
from routers.news import router as news_router
from routers.signals import router as signals_router
from routers.lines import router as lines_router
from routers.metrics import router as metrics_router
from routers.hit_rate import router as hit_rate_router
from routers.whale import router as whale_router
from routers.parlay_suggestions import router as parlay_router
from routers.steam import router as steam_router
from routers.stripe_router import router as stripe_router
from routers.search import router as search_router
from routers.intel import router as intel_router
from routers.oracle import router as oracle_router
from routers.live import router as live_router
from routers.slate import router as slate_router
from routers.ws_ev import router as ws_ev_router
from routers.arbitrage import router as arbitrage_router
from routers.kalshi import router as kalshi_router
from routers.kalshi_ws_proxy import router as kalshi_ws_router

try:
        from routers.arbitrage import router as arbitrage_router
except ImportError:
        arbitrage_router = None

try:
        from routers.kalshi import router as kalshi_router
except ImportError:
        kalshi_router = None

try:
        from routers.kalshi_ws_proxy import router as kalshi_ws_router
except ImportError:
        kalshi_ws_router = None

app = FastAPI(title=APP_NAME, redirect_slashes=False)

app.add_middleware(
<<<<<<< HEAD
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://perplex-edge.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
=======
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
>>>>>>> f64e8d8167c22f2db5be4c20b757dac1a282d2cb
)

app.include_router(health_router, prefix="/api/health", tags=["health"])
app.include_router(meta_router, prefix="/api/meta", tags=["meta"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(props_router, prefix="/api/props", tags=["props"])
app.include_router(ev_router, prefix="/api/ev", tags=["ev"])
app.include_router(clv_router, prefix="/api/clv", tags=["clv"])
app.include_router(brain_router, prefix="/api/brain", tags=["brain"])
app.include_router(bets_router, prefix="/api/bets", tags=["bets"])
app.include_router(injuries_router, prefix="/api/injuries", tags=["injuries"])
app.include_router(news_router, prefix="/api/news", tags=["news"])
app.include_router(signals_router, prefix="/api/signals", tags=["signals"])
app.include_router(lines_router, prefix="/api/lines", tags=["lines"])
app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])
app.include_router(hit_rate_router, prefix="/api/hit_rate", tags=["hit_rate"])
app.include_router(whale_router, prefix="/api/whale", tags=["whale"])
app.include_router(parlay_router, prefix="/api/parlay", tags=["parlay"])
app.include_router(steam_router, prefix="/api/steam", tags=["steam"])
app.include_router(stripe_router, prefix="/api/stripe", tags=["stripe"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(intel_router, prefix="/api/intel", tags=["intel"])
app.include_router(oracle_router, prefix="/api/oracle", tags=["oracle"])
app.include_router(live_router, prefix="/api/live", tags=["live"])
app.include_router(slate_router, prefix="/api/slate", tags=["slate"])
app.include_router(ws_ev_router, prefix="/api/ws_ev", tags=["ws_ev"])

<<<<<<< HEAD
# Optional Routers (Fix 2: Independent registration)
if 'arbitrage_router' in globals():
    app.include_router(arbitrage_router, prefix="/api/arbitrage", tags=["arbitrage"])
if 'kalshi_router' in globals():
    app.include_router(kalshi_router, prefix="/api/kalshi", tags=["kalshi"])
if 'kalshi_ws_router' in globals():
    app.include_router(kalshi_ws_router, prefix="/api/kalshi_ws", tags=["kalshi_ws"])

@app.get("/")
async def root():
    return {"name": APP_NAME, "status": "healthy"}
=======
if arbitrage_router:
        app.include_router(arbitrage_router, prefix="/api/arbitrage", tags=["arbitrage"])
    if kalshi_router:
            app.include_router(kalshi_router, prefix="/api/kalshi", tags=["kalshi"])
        if kalshi_ws_router:
                app.include_router(kalshi_ws_router, prefix="/api/kalshi_ws", tags=["kalshi_ws"])
>>>>>>> f64e8d8167c22f2db5be4c20b757dac1a282d2cb

if __name__ == "__main__":
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)), log_level="info")
    
