"""
Active Monitoring API - Real-time line and stat monitoring endpoints.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.active_line_brain import active_line_brain
from app.services.cache_service import cache_service

router = APIRouter(prefix="/api/active", tags=["active-monitoring"])

@router.get("/status")
async def get_active_brain_status():
    """Get current active brain status and metrics."""
    try:
        status = active_line_brain.get_status()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "brain_status": status,
            "message": "Active line monitoring brain operational" if status["is_running"] else "Brain stopped"
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "brain_status": {"is_running": False, "error": str(e)}
        }

@router.get("/line-movements")
async def get_line_movements(
    limit: int = Query(default=20, le=100),
    sportsbook: str = Query(None, description="Filter by sportsbook"),
    min_movement: float = Query(default=0.5, description="Minimum line movement"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent line movements across all sportsbooks."""
    try:
        # Try cache first
        cached_data = await cache_service.get("line_movements")
        if cached_data:
            movements = cached_data
        else:
            # Fallback to brain data
            movements = [
                {
                    "player_id": lm.player_id,
                    "stat_type": lm.stat_type,
                    "current_line": lm.line_value,
                    "previous_line": lm.previous_line,
                    "movement": lm.movement_amount,
                    "movement_pct": lm.movement_pct,
                    "sportsbook": lm.sportsbook,
                    "direction": lm.direction,
                    "timestamp": lm.timestamp.isoformat()
                }
                for lm in list(active_line_brain.line_movements)[-50:]
            ]
        
        # Apply filters
        if sportsbook:
            movements = [m for m in movements if m.get("sportsbook") == sportsbook]
        
        movements = [m for m in movements if abs(m.get("movement", 0)) >= min_movement]
        
        # Sort by timestamp and limit
        movements.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_movements": len(movements),
            "filters": {
                "sportsbook": sportsbook,
                "min_movement": min_movement,
                "limit": limit
            },
            "movements": movements[:limit]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "movements": []
        }

@router.get("/opportunities")
async def get_over_under_opportunities(
    min_edge: float = Query(default=5.0, description="Minimum edge percentage"),
    recommendation: str = Query(None, description="Filter by recommendation: over, under, pass"),
    limit: int = Query(default=15, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get current over/under opportunities with model projections."""
    try:
        # Try cache first
        cached_data = await cache_service.get("over_under_opportunities")
        if cached_data:
            opportunities = cached_data
        else:
            # Fallback to brain data
            opportunities = [
                {
                    "player_id": opp.player_id,
                    "player_name": opp.player_name,
                    "stat_type": opp.stat_type,
                    "current_line": opp.current_line,
                    "model_projection": opp.model_projection,
                    "recommendation": opp.recommendation,
                    "over_edge": opp.over_edge,
                    "under_edge": opp.under_edge,
                    "edge": max(opp.over_edge, opp.under_edge),
                    "confidence": opp.confidence,
                    "sportsbooks": opp.sportsbooks,
                    "timestamp": opp.timestamp.isoformat()
                }
                for opp in list(active_line_brain.over_under_opportunities.values())
            ]
        
        # Apply filters
        if recommendation:
            opportunities = [o for o in opportunities if o.get("recommendation") == recommendation]
        
        opportunities = [o for o in opportunities if o.get("edge", 0) >= min_edge]
        
        # Sort by edge and limit
        opportunities.sort(key=lambda x: x.get("edge", 0), reverse=True)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_opportunities": len(opportunities),
            "filters": {
                "min_edge": min_edge,
                "recommendation": recommendation,
                "limit": limit
            },
            "opportunities": opportunities[:limit]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "opportunities": []
        }

@router.get("/ruled-out-players")
async def get_ruled_out_players(db: AsyncSession = Depends(get_db)):
    """Get list of currently ruled out players (injured/out/doubtful)."""
    try:
        # Try cache first
        cached_data = await cache_service.get("ruled_out_players")
        if cached_data:
            ruled_out = cached_data
        else:
            # Fallback to brain data
            ruled_out = {
                "players": list(active_line_brain.ruled_out_players),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "count": len(active_line_brain.ruled_out_players)
            }
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ruled_out_players": ruled_out
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "ruled_out_players": {"players": [], "count": 0}
        }

@router.get("/realtime-data")
async def get_realtime_data():
    """Get comprehensive real-time monitoring data."""
    try:
        # Try cache first
        cached_data = await cache_service.get("active_brain_realtime_data")
        if cached_data:
            return cached_data
        
        # Fallback to brain status
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Real-time data not available, check brain status",
            "brain_status": active_line_brain.get_status()
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

@router.post("/start-monitoring")
async def start_monitoring():
    """Start the active line monitoring brain."""
    try:
        if active_line_brain.is_running:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Active brain already running",
                "status": active_line_brain.get_status()
            }
        
        # Start monitoring in background
        import asyncio
        asyncio.create_task(active_line_brain.start_monitoring())
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Active line monitoring started",
            "status": active_line_brain.get_status()
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "message": "Failed to start monitoring"
        }

@router.post("/stop-monitoring")
async def stop_monitoring():
    """Stop the active line monitoring brain."""
    try:
        await active_line_brain.stop_monitoring()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Active line monitoring stopped",
            "status": active_line_brain.get_status()
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "message": "Failed to stop monitoring"
        }
