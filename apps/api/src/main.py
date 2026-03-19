import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import APP_NAME, settings

from db.base import Base
import db.session
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

# Initialize database tables
# Base.metadata.create_all(bind=engine) # DEPRECATED: Use Alembic migrations

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized API Routes
app.include_router(health_router,   prefix="/api/health",       tags=["health"])
app.include_router(meta_router,     prefix="/api/meta",         tags=["meta"])
app.include_router(auth_router,     prefix="/api/auth",         tags=["auth"])
app.include_router(props_router,    prefix="/api/props",        tags=["props"])
app.include_router(ev_router,       prefix="/api/ev",           tags=["ev"])
app.include_router(clv_router,      prefix="/api/clv",          tags=["clv"])
app.include_router(brain_router,    prefix="/api/brain",        tags=["brain"])
app.include_router(bets_router,     prefix="/api/bets",         tags=["bets"])
app.include_router(injuries_router, prefix="/api/injuries",     tags=["injuries"])
app.include_router(news_router,     prefix="/api/news",         tags=["news"])
app.include_router(signals_router,  prefix="/api/signals",      tags=["signals"])
app.include_router(lines_router,    prefix="/api/lines",        tags=["lines"])
app.include_router(metrics_router,  prefix="/api/metrics",      tags=["metrics"])
app.include_router(hit_rate_router, prefix="/api/hit-rate",     tags=["hit-rate"])
app.include_router(whale_router,    prefix="/api/whale",        tags=["whale"])
app.include_router(parlay_router,   prefix="/api/parlay",       tags=["parlay"])
app.include_router(steam_router,    prefix="/api/steam",        tags=["steam"])
app.include_router(stripe_router,   prefix="/api/stripe",       tags=["stripe"])
app.include_router(search_router,   prefix="/api/search",       tags=["search"])
app.include_router(intel_router,    prefix="/api/intel",        tags=["intel"])
app.include_router(oracle_router,   prefix="/api/oracle",       tags=["oracle"])
app.include_router(live_router,     prefix="/api/live",         tags=["live"])
app.include_router(slate_router,    prefix="/api/slate",        tags=["slate"])
app.include_router(ws_ev_router,    prefix="/api",              tags=["ws"])

@app.get("/")
async def root():
    return {"name": APP_NAME, "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT") or 8000)
    # Bind to 0.0.0.0 for container/cloud compatibility
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
