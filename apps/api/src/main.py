import os, logging, multiprocessing
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import engine, Base
from services.cache import cache

# New Standardized Routers
from app.api.immediateworking import router as immediate_router
from app.api.validationendpoints import router as validation_router
from app.api.trackrecordendpoints import router as trackrecord_router
from app.api.modelstatusendpoints import router as modelstatus_router
from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.sync import router as sync_router
from routers.meta import router as meta_router
from routers.ws_ev import router as ws_ev_router
from routers.unified_ev import router as unified_ev_router

# Legacy Routers (to be consolidated over time)
from routers import props, live, hit_rate, line_movement, sharp_money, arbitrage, whale, steam, clv, oracle, slate, stripe_router, search, injuries, ev_calculator, brain_router, parlay_suggestions, news, user_router, auth, billing, kalshi

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Standardized lifespan for Perplex Edge."""
    # 1. Connect Cache
    logging.info("Lifespan: Initializing cache...")
    try:
        await cache.connect()
        logging.info(f"Lifespan: Cache initialized (status: {cache.status})")
    except Exception as e:
        logging.error(f"Lifespan: Cache connection failed: {e}")

    # 2. Database tables (Dev)
    if settings.DEBUG:
        logging.info("Lifespan: Initializing database tables...")
        try:
            # Using a simplified check or timeout for DB
            Base.metadata.create_all(bind=engine)
            logging.info("Lifespan: Database tables initialized.")
        except Exception as e:
            logging.error(f"Lifespan: DB init failed: {e}")

    logging.info("Lifespan: Startup complete, yielding.")
    yield
    logging.info("Lifespan: Shutting down...")

app = FastAPI(
    title="Perplex Edge — Sports Betting Intelligence API",
    version="1.1.0",
    lifespan=lifespan,
)

# FIX #14: Restricted CORS for production safety (no wildcards with credentials)
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# New Canonical API v1 Routes
app.include_router(immediate_router,    prefix="/api/immediate",    tags=["immediate"])
app.include_router(validation_router,   prefix="/api/validation",   tags=["validation"])
app.include_router(trackrecord_router,  prefix="/api/track-record", tags=["track-record"])
app.include_router(modelstatus_router,  prefix="/api/status",       tags=["status"])
app.include_router(analysis_router,     prefix="/api/analysis",     tags=["analysis"])
app.include_router(auth_router,         prefix="/api/auth",         tags=["auth"])
app.include_router(sync_router,         prefix="/api/sync",         tags=["sync"])
app.include_router(unified_ev_router,   prefix="/api/ev/unified",   tags=["Unified EV"])
app.include_router(meta_router,         prefix="/api/meta",         tags=["Metadata"])
app.include_router(ws_ev_router)

# Standard Legacy/Expanded Routes
app.include_router(props.router, prefix="/api/props", tags=["Props"])
app.include_router(live.router, prefix="/api/live", tags=["Live"])
app.include_router(ev_calculator.router, prefix="/api/ev", tags=["EV+"])
app.include_router(sharp_money.router, prefix="/api/signals", tags=["Signals"])
app.include_router(brain_router.router, prefix="/api/brain", tags=["Intelligence"])
app.include_router(hit_rate.router, prefix="/api/hit-rate", tags=["Historical"])
app.include_router(line_movement.router, prefix="/api/line-movement", tags=["Signals"])
app.include_router(whale.router, prefix="/api/whale", tags=["Whale"])
app.include_router(clv.router, prefix="/api/clv", tags=["Analytics"])
app.include_router(slate.router, prefix="/api/props/slate", tags=["Props"])
app.include_router(arbitrage.router, prefix="/api/arbitrage", tags=["Arbitrage"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(kalshi.router, prefix="/api/kalshi", tags=["Kalshi"])

# FIX #1: Canonical Health Check
@app.get("/api/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.1.0",
    }

@app.get("/", tags=["system"])
async def root():
    return {"message": "Perplex Edge API", "status": "running", "docs": "/docs"}

@app.exception_handler(Exception)
async def universal_exception_handler(request, exc):
    logging.error(f"Unhandled Exception: {exc}", exc_info=True)
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
        headers=headers,
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT") or 8000) # FIX #16: guard empty string
    uvicorn.run(app, host="0.0.0.0", port=port)
