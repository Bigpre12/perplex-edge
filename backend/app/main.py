"""Perplex Engine - Sports Betting Analytics API."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import db_lifespan, get_db
from app.models import Sport, Pick, HistoricalPerformance
from app.services.stats_calculator import (
    get_all_hit_rates,
    get_player_summary,
)
from app.scheduler import (
    start_background_tasks,
    stop_background_tasks,
    get_scheduler_status,
)
from app.api.admin import router as admin_router
from app.api.public import router as public_router
from app.api.sync import router as sync_router
from app.api.stats import router as stats_router
from app.api.games import router as games_router
from app.api.odds import router as odds_router
from app.api.props import router as props_router
from app.api.injuries import router as injuries_router
from app.api.picks import router as picks_router
from app.api.analytics import router as analytics_router
from app.api.nfl import router as nfl_router
from app.api.ncaab import router as ncaab_router
from app.api.bets import router as bets_router
from app.api.data_v2 import router as data_v2_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


# =============================================================================
# Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    logger.info("Starting Perplex Engine...")
    
    # Initialize database
    async with db_lifespan(app):
        # Start background tasks if scheduler is enabled
        background_tasks = []
        if settings.scheduler_enabled:
            try:
                background_tasks = start_background_tasks()
                logger.info(f"Started {len(background_tasks)} background tasks")
            except Exception as e:
                logger.error(f"Failed to start background tasks: {e}")
        else:
            logger.info("Scheduler disabled via SCHEDULER_ENABLED=false")
        
        logger.info("Perplex Engine started successfully")
        
        yield
        
        # Shutdown
        logger.info("Perplex Engine shutting down...")
        
        # Stop background tasks
        if background_tasks:
            await stop_background_tasks(background_tasks)
            logger.info("Background tasks stopped")
    
    logger.info("Perplex Engine shut down")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Perplex Engine",
    description="Sports betting analytics platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware - allow all origins for frontend access
# Note: allow_credentials must be False when allow_origins=["*"] per CORS spec
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(public_router, prefix="/api", tags=["public"])
app.include_router(sync_router, prefix="/api/sync", tags=["sync"])
app.include_router(stats_router, prefix="/api/stats", tags=["stats"])
app.include_router(games_router, prefix="/api/games", tags=["games"])
app.include_router(odds_router, prefix="/api/odds", tags=["odds"])
app.include_router(props_router, prefix="/api/props", tags=["props"])
app.include_router(injuries_router, prefix="/api/injuries", tags=["injuries"])
app.include_router(picks_router, prefix="/api/picks", tags=["picks"])
app.include_router(analytics_router, prefix="/api", tags=["analytics"])
app.include_router(nfl_router, prefix="/api", tags=["nfl"])
app.include_router(ncaab_router, prefix="/api", tags=["ncaab"])
app.include_router(bets_router, prefix="/api", tags=["bets"])
app.include_router(data_v2_router, prefix="/api/data", tags=["data-v2"])


# =============================================================================
# Health Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Perplex Engine API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint - no database access."""
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    """Simple ping endpoint - no database access."""
    return {"ping": "pong"}


@app.get("/health/db")
async def health_db():
    """Database health check endpoint."""
    from sqlalchemy import text
    from app.core.database import get_engine
    
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)[:200]}


@app.get("/api/health")
async def api_health():
    """API health check (for frontend compatibility)."""
    return {"status": "ok", "api": True}


@app.get("/api/scheduler/status")
async def scheduler_status():
    """Get scheduler status and running tasks."""
    return get_scheduler_status()


# =============================================================================
# Sports Endpoints (utility - database query)
# =============================================================================

@app.get("/sports")
async def list_sports_db(db: AsyncSession = Depends(get_db)):
    """List all sports from database (utility endpoint)."""
    try:
        result = await db.execute(select(Sport))
        sports = result.scalars().all()
        return {
            "items": [
                {"id": s.id, "name": s.name, "league_code": s.league_code}
                for s in sports
            ],
            "total": len(sports)
        }
    except Exception as e:
        return {"items": [], "total": 0, "error": str(e)[:200]}


# NOTE: /api/sports is handled by public_router (queries database)
# NOTE: /api/picks is handled by picks_router (uses ModelPick table)
# NOTE: /api/picks/refresh is handled by picks_router


# =============================================================================
# Stats Endpoints (legacy - uses Pick/HistoricalPerformance tables)
# =============================================================================

@app.get("/api/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get overall stats summary."""
    try:
        # Get total picks
        picks_result = await db.execute(select(Pick))
        picks = picks_result.scalars().all()
        
        # Get historical performance
        perf_result = await db.execute(select(HistoricalPerformance))
        performances = perf_result.scalars().all()
        
        # Calculate averages
        total_picks = len(picks)
        avg_hit_rate = 0.0
        avg_ev = 0.0
        
        if performances:
            avg_hit_rate = sum(p.hit_rate_percentage for p in performances) / len(performances)
            avg_ev = sum(p.avg_ev for p in performances) / len(performances)
        
        return {
            "total_picks": total_picks,
            "hit_rate": round(avg_hit_rate, 2),
            "avg_ev": round(avg_ev, 2),
            "players_tracked": len(performances)
        }
    except Exception as e:
        return {"total_picks": 0, "hit_rate": 0, "avg_ev": 0, "error": str(e)[:200]}


@app.get("/api/stats/player/{player_name}")
async def get_player_stats(player_name: str, db: AsyncSession = Depends(get_db)):
    """Get comprehensive stats for a specific player."""
    try:
        summary = await get_player_summary(db, player_name)
        return summary
    except Exception as e:
        logger.error(f"Error getting player stats for {player_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@app.get("/api/stats/hit-rates")
async def get_hit_rates(db: AsyncSession = Depends(get_db)):
    """Get hit rates for all tracked players."""
    try:
        hit_rates = await get_all_hit_rates(db)
        return {
            "items": hit_rates,
            "total": len(hit_rates),
        }
    except Exception as e:
        logger.error(f"Error getting hit rates: {e}")
        return {"items": [], "total": 0, "error": str(e)[:200]}
