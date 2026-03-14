import os, logging, asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import engine, Base
import models # Load all models
from services.cache import cache

# --- INSTITUTIONAL ROUTERS ---
from routers.props import router as props_router
from routers.ev import router as ev_router
from routers.signals import router as signals_router
from routers.live import router as live_router
from routers.meta import router as meta_router
from routers.kalshi import router as kalshi_router
from routers.ws.ws_ev import router as ws_router, start_websocket_broadcast

@asynccontextmanager
async def lifespan(app: FastAPI):
    """LUCRIX Institutional Lifespan"""
    # 1. Cache Initialization
    logging.info("Lifespan: Initializing cache...")
    try:
        await cache.connect()
    except Exception as e:
        logging.error(f"Lifespan: Cache error: {e}")

    # 2. WebSocket Broadcast Hub
    logging.info("Lifespan: Starting WebSocket Broadcast Hub...")
    try:
        await start_websocket_broadcast()
    except Exception as e:
        logging.error(f"Lifespan: WS Hub error: {e}")

    # 3. DB Migrations/Init (Development only)
    if settings.DEBUG:
        logging.info("Lifespan: Checking DB consistency...")

    logging.info("LUCRIX Institutional Backend: Started successfully.")
    yield
    logging.info("LUCRIX Institutional Backend: Shutting down.")

app = FastAPI(
    title="LUCRIX Institutional API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS Policy
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3300,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CANONICAL INSTITUTIONAL ROUTES ---
app.include_router(props_router)
app.include_router(ev_router)
app.include_router(signals_router)
app.include_router(live_router)
app.include_router(meta_router)
app.include_router(kalshi_router)
app.include_router(ws_router)

@app.get("/", tags=["system"])
async def root():
    return {
        "identity": "LUCRIX-Institutional",
        "status": "operational",
        "docs": "/docs",
        "server_time": datetime.utcnow().isoformat()
    }

@app.exception_handler(Exception)
async def universal_exception_handler(request, exc):
    logging.error(f"CRITICAL ERROR: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "LUCRIX Internal Error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT") or 8000)
    uvicorn.run(app, host="0.0.0.0", port=port)
