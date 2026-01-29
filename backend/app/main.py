"""Perplex Engine - Sports Betting Analytics API."""
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import db_lifespan, get_db
from app.models import Sport, Pick, PlayerStat, HistoricalPerformance
from app.services.stats_calculator import (
    calculate_historical_hit_rate,
    get_recent_performance,
    get_all_hit_rates,
    get_player_summary,
)
from app.services.picks_generator import generate_picks
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


# =============================================================================
# Sport Key Mappings
# =============================================================================

SPORT_KEY_MAP = {
    "nba": "basketball_nba",
    "nfl": "americanfootball_nfl",
    "mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
}

AVAILABLE_SPORTS = [
    {"key": "nba", "name": "NBA", "league_code": "basketball_nba"},
    {"key": "nfl", "name": "NFL", "league_code": "americanfootball_nfl"},
    {"key": "mlb", "name": "MLB", "league_code": "baseball_mlb"},
    {"key": "nhl", "name": "NHL", "league_code": "icehockey_nhl"},
]


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
# Sports Endpoints
# =============================================================================

@app.get("/sports")
async def list_sports_db(db: AsyncSession = Depends(get_db)):
    """List all sports from database."""
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


@app.get("/api/sports")
async def list_sports():
    """List available sports (static list)."""
    return {
        "items": AVAILABLE_SPORTS,
        "total": len(AVAILABLE_SPORTS),
    }


# =============================================================================
# Picks Endpoints
# =============================================================================

@app.get("/api/picks")
async def list_picks(
    sport: Optional[str] = Query(None, description="Sport filter: nba, nfl, mlb, nhl"),
    pick_type: Optional[str] = Query(None, description="Pick type: all, spread, total, prop"),
    min_ev: Optional[float] = Query(None, description="Minimum EV percentage"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List picks with optional filters."""
    try:
        query = select(Pick)
        
        # Apply filters
        filters = []
        
        if pick_type and pick_type != "all":
            if pick_type == "prop":
                filters.append(Pick.pick_type == "player_prop")
            else:
                filters.append(Pick.pick_type == pick_type)
        
        if min_ev is not None:
            filters.append(Pick.ev_percentage >= min_ev)
        
        if min_confidence is not None:
            filters.append(Pick.confidence >= min_confidence)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Order by confidence descending
        query = query.order_by(Pick.confidence.desc())
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        return {
            "items": [
                {
                    "id": p.id,
                    "game_id": p.game_id,
                    "pick_type": p.pick_type,
                    "player_name": p.player_name,
                    "stat_type": p.stat_type,
                    "line": p.line,
                    "odds": p.odds,
                    "model_probability": p.model_probability,
                    "implied_probability": p.implied_probability,
                    "ev_percentage": p.ev_percentage,
                    "confidence": p.confidence,
                    "hit_rate": p.hit_rate,
                }
                for p in picks
            ],
            "total": len(picks),
            "filters": {
                "sport": sport,
                "pick_type": pick_type,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
            }
        }
    except Exception as e:
        logger.error(f"Error listing picks: {e}")
        return {"items": [], "total": 0, "error": str(e)[:200]}


@app.get("/api/picks/{pick_id}")
async def get_pick(pick_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single pick by ID."""
    try:
        result = await db.execute(select(Pick).where(Pick.id == pick_id))
        pick = result.scalar_one_or_none()
        
        if not pick:
            raise HTTPException(status_code=404, detail="Pick not found")
        
        return {
            "id": pick.id,
            "game_id": pick.game_id,
            "pick_type": pick.pick_type,
            "player_name": pick.player_name,
            "stat_type": pick.stat_type,
            "line": pick.line,
            "odds": pick.odds,
            "model_probability": pick.model_probability,
            "implied_probability": pick.implied_probability,
            "ev_percentage": pick.ev_percentage,
            "confidence": pick.confidence,
            "hit_rate": pick.hit_rate,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pick {pick_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@app.post("/api/picks/refresh")
async def refresh_picks(
    sport: str = Query("nba", description="Sport to refresh: nba, nfl"),
    db: AsyncSession = Depends(get_db),
):
    """Trigger manual refresh of picks for a sport."""
    try:
        sport_key = SPORT_KEY_MAP.get(sport.lower())
        if not sport_key:
            raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
        
        result = await generate_picks(
            db,
            sport_key,
            min_ev=0.0,
            min_confidence=0.5,
            use_stubs=True,  # Use stubs for now
        )
        
        return {
            "status": "success",
            "sport": sport,
            "result": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing picks: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


# =============================================================================
# Stats Endpoints
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
