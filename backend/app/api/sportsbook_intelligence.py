"""
Sportsbook intelligence API endpoints.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.sportsbook_monitor import sportsbook_monitor

router = APIRouter(prefix="/api/sportsbook", tags=["sportsbook"])


@router.get("/market-analysis")
async def get_market_analysis(
    sport_id: int = Query(30, description="Sport ID (30=NBA, 32=NCAA, 53=NHL)"),
    db: AsyncSession = Depends(get_db)
):
    """Get current market analysis for Texas sportsbooks."""
    try:
        analysis = await sportsbook_monitor.analyze_market_opportunities(db, sport_id)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "analysis": analysis
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "sport_id": sport_id
        }


@router.get("/trading-signals")
async def get_trading_signals(
    min_confidence: float = Query(0.7, description="Minimum confidence level"),
    db: AsyncSession = Depends(get_db)
):
    """Get current trading signals."""
    try:
        signals = await sportsbook_monitor.get_trading_signals(db, min_confidence)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "min_confidence": min_confidence,
            "total_signals": len(signals),
            "signals": signals
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "total_signals": 0
        }


@router.get("/market-summary")
async def get_market_summary():
    """Get summary of market analysis."""
    try:
        summary = sportsbook_monitor.get_market_summary()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": summary
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


@router.get("/texas-sportsbooks")
async def get_texas_sportsbooks():
    """Get list of monitored Texas sportsbooks."""
    try:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "texas_sportsbooks": sportsbook_monitor.texas_sportsbooks,
            "total_sportsbooks": len(sportsbook_monitor.texas_sportsbooks),
            "monitoring_status": "active"
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


@router.post("/trigger-analysis")
async def trigger_market_analysis(
    sport_id: int = Query(30, description="Sport ID to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Trigger immediate market analysis."""
    try:
        analysis = await sportsbook_monitor.analyze_market_opportunities(db, sport_id)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "analysis_triggered": True,
            "result": analysis
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "analysis_triggered": False
        }
