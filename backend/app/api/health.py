"""
Health check API endpoints.

Provides system health status and monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime, timezone
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.models import Sport, Game, Player

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=Dict[str, Any])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {}
        }
        
        # Database health
        try:
            db_result = await db.execute(text("SELECT 1"))
            db_result.scalar()
            health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["checks"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Sports data health
        try:
            sports_count = await db.scalar(select(Sport.id))
            health_status["checks"]["sports_data"] = "healthy" if sports_count else "no_data"
            if sports_count == 0:
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["checks"]["sports_data"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Games data health
        try:
            games_count = await db.scalar(select(Game.id))
            health_status["checks"]["games_data"] = "healthy" if games_count else "no_data"
            if games_count == 0:
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["checks"]["games_data"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Players data health
        try:
            players_count = await db.scalar(select(Player.id))
            health_status["checks"]["players_data"] = "healthy" if players_count else "no_data"
        except Exception as e:
            health_status["checks"]["players_data"] = f"unhealthy: {str(e)}"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with metrics."""
    try:
        health_details = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {},
            "data_counts": {},
            "performance": {}
        }
        
        # Database metrics
        try:
            # Sports count
            sports_count = await db.scalar(select(Sport.id))
            health_details["data_counts"]["sports"] = sports_count or 0
            
            # Games count
            games_count = await db.scalar(select(Game.id))
            health_details["data_counts"]["games"] = games_count or 0
            
            # Players count
            players_count = await db.scalar(select(Player.id))
            health_details["data_counts"]["players"] = players_count or 0
            
            # Recent games (last 24 hours)
            recent_games_query = select(Game).where(
                Game.start_time >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            )
            recent_games_result = await db.execute(recent_games_query)
            recent_games = len(recent_games_result.scalars().all())
            health_details["data_counts"]["recent_games"] = recent_games
            
        except Exception as e:
            health_details["metrics"]["database_error"] = str(e)
            health_details["status"] = "unhealthy"
        
        # Performance metrics (mock for now)
        health_details["performance"] = {
            "api_response_time_ms": 150,
            "database_query_time_ms": 45,
            "memory_usage_percent": 65,
            "cpu_usage_percent": 35
        }
        
        return health_details
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detailed health check failed: {str(e)}")

@router.get("/ping", response_model=Dict[str, str])
async def ping():
    """Simple ping endpoint for load balancers."""
    return {
        "status": "pong",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check for Kubernetes."""
    try:
        # Check if database is ready
        await db.execute(text("SELECT 1"))
        
        # Check if we have basic data
        sports_count = await db.scalar(select(Sport.id))
        
        if sports_count == 0:
            return {
                "ready": False,
                "reason": "No sports data found",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "ready": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "ready": False,
            "reason": f"Database not ready: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
