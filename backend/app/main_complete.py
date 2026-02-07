"""
Complete Main Application - All brain services and enhanced APIs
"""

import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.database import db_lifespan, get_db
from app.core.logging import (
    configure_logging,
    get_logger,
    get_correlation_id,
    set_correlation_id,
    request_metrics,
)
from app.models import Sport
from app.scheduler import (
    start_background_tasks,
    stop_background_tasks,
    get_scheduler_status,
)

# Import enhanced APIs
from app.api.players_enhanced import router as enhanced_players_router
from app.api.teams_enhanced import router as enhanced_teams_router
from app.api.statistics import router as statistics_router
from app.api.active_monitoring import router as active_monitoring_router
from app.api.sports_intelligence import router as sports_intelligence_router

# Import brain services
from app.services.active_line_brain import active_line_brain
from app.services.sports_intelligence_brain import sports_intelligence_brain
from app.services.cache_service import cache_service

# Import existing routers
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
from app.api.sports import router as sports_router

# Configure structured logging
_env = os.getenv("ENVIRONMENT", "production")
configure_logging(json_logs=(_env != "development"), log_level="INFO")
logger = get_logger(__name__)

settings = get_settings()


# =============================================================================
# Request Logging Middleware
# =============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with correlation IDs and metrics."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())[:8]
        set_correlation_id(correlation_id)
        
        # Record start time
        start_time = time.perf_counter()
        
        # Process request
        response = None
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(
                "request_failed",
                path=request.url.path,
                method=request.method,
                error=str(e)[:200],
            )
            raise
        finally:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Record metrics
            request_metrics.record_request(
                path=request.url.path,
                method=request.method,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            
            # Log request (skip health checks for noise reduction)
            if not request.url.path.startswith(("/health", "/ping")):
                log_level = "warning" if status_code >= 400 else "info"
                getattr(logger, log_level)(
                    "request_completed",
                    path=request.url.path,
                    method=request.method,
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    query_params=str(request.query_params) if request.query_params else None,
                )
        
        # Add correlation ID to response headers
        if response:
            response.headers["X-Correlation-ID"] = correlation_id
        
        return response


# =============================================================================
# Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with all brain services."""
    logger.info("starting_perplex_engine_complete", version="2.0.0")
    
    # Initialize database
    async with db_lifespan(app):
        # Database is now initialized and ready
        
        # Initialize cache service
        await cache_service.initialize()
        logger.info("[STARTUP] Cache service initialized")
        
        # Start all brain services
        try:
            import asyncio
            
            # Start active line monitoring brain
            active_brain_task = asyncio.create_task(active_line_brain.start_monitoring())
            logger.info("[STARTUP] Active line monitoring brain started")
            
            # Start sports intelligence brain
            intelligence_task = asyncio.create_task(sports_intelligence_brain.start_monitoring())
            logger.info("[STARTUP] Sports intelligence brain started")
            
            # Store task references for cleanup
            app.state.active_brain_task = active_brain_task
            app.state.intelligence_task = intelligence_task
            
        except Exception as e:
            logger.error(f"[STARTUP] Failed to start brain services: {e}")
            logger.info("[STARTUP] Continuing without brain services")
        
        # Start background tasks if scheduler is enabled
        background_tasks = []
        if settings.scheduler_enabled:
            try:
                background_tasks = start_background_tasks()
                logger.info(
                    "background_tasks_started",
                    task_count=len(background_tasks),
                )
            except Exception as e:
                logger.error("background_tasks_failed", error=str(e))
        
        logger.info(
            "perplex_engine_complete_ready",
            environment=_env,
            scheduler_enabled=settings.scheduler_enabled,
            brain_services="active",
        )
        
        yield
        
        # Shutdown
        logger.info("perplex_engine_shutting_down")
        
        # Stop brain services
        try:
            await active_line_brain.stop_monitoring()
            await sports_intelligence_brain.stop_monitoring()
            logger.info("[SHUTDOWN] Brain services stopped")
        except Exception as e:
            logger.error(f"[SHUTDOWN] Error stopping brain services: {e}")
        
        # Stop background tasks
        if background_tasks:
            await stop_background_tasks(background_tasks)
            logger.info("background_tasks_stopped")
    
    logger.info("perplex_engine_shutdown_complete")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Perplex Edge - Complete Brain Ecosystem",
    description="Sports betting analytics platform with AI-powered intelligence",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration
ALLOWED_ORIGINS = ["*"]  # Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "Content-Type", "Authorization"],
    max_age=600,
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)


# =============================================================================
# Include Routers
# =============================================================================

# Enhanced APIs (Steps 1-2)
app.include_router(enhanced_players_router, tags=["players"])
app.include_router(enhanced_teams_router, tags=["teams"])
app.include_router(statistics_router, tags=["statistics"])

# Brain Services (Steps 3-4)
app.include_router(active_monitoring_router, tags=["active-monitoring"])
app.include_router(sports_intelligence_router, tags=["sports-intelligence"])

# Existing APIs
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
app.include_router(sports_router, prefix="/api/sports", tags=["sports"])


# =============================================================================
# Health Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Perplex Edge - Complete Brain Ecosystem",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Enhanced Players & Teams APIs",
            "Statistics & Analytics",
            "Active Line Monitoring",
            "Sports Intelligence Brain",
            "Real-time Decision Making",
            "Automatic Code Updates"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/health/complete")
async def health_complete():
    """Complete health check with all brain services."""
    return {
        "status": "ok",
        "cache_service": cache_service.is_available(),
        "active_brain": active_line_brain.is_running,
        "intelligence_brain": sports_intelligence_brain.is_running,
        "features": {
            "enhanced_apis": True,
            "statistics": True,
            "active_monitoring": True,
            "sports_intelligence": True,
            "caching": cache_service.is_available()
        }
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"ping": "pong", "service": "perplex-edge-complete"}


# =============================================================================
# Status Endpoints
# =============================================================================

@app.get("/api/status")
async def get_system_status():
    """Get complete system status."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "services": {
            "cache": {
                "available": cache_service.is_available(),
                "status": "operational" if cache_service.is_available() else "disabled"
            },
            "active_brain": {
                "running": active_line_brain.is_running,
                "cycles": active_line_brain.cycle_count,
                "status": "operational" if active_line_brain.is_running else "stopped"
            },
            "intelligence_brain": {
                "running": sports_intelligence_brain.is_running,
                "cycles": sports_intelligence_brain.cycle_count,
                "status": "operational" if sports_intelligence_brain.is_running else "stopped"
            }
        },
        "features": {
            "enhanced_players_api": True,
            "enhanced_teams_api": True,
            "statistics_api": True,
            "active_monitoring": True,
            "sports_intelligence": True,
            "real_time_caching": cache_service.is_available()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
