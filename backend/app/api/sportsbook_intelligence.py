"""
Sportsbook intelligence API endpoints.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import ModelPick, Player, Team, Market
from app.services.sportsbook_monitor import enhanced_sportsbook_monitor

router = APIRouter(prefix="/api/sportsbook", tags=["sportsbook"])

@router.get("/market-analysis")
async def get_market_analysis(
    sport_id: int = Query(30, description="Sport ID (30=NBA, 32=NCAA, 53=NHL)"),
    db: AsyncSession = Depends(get_db)
):
    """Get current market analysis for Texas sportsbooks."""
    try:
        # Get recent picks for market analysis
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        ).where(
            ModelPick.sport_id == sport_id
        ).order_by(
            desc(ModelPick.expected_value)
        ).limit(20)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        # Analyze market opportunities
        high_ev_picks = [p for p in picks if p.expected_value > 0.1]
        avg_ev = sum(p.expected_value for p in picks) / len(picks) if picks else 0
        
        analysis = {
            "total_picks": len(picks),
            "high_ev_opportunities": len(high_ev_picks),
            "average_ev": round(avg_ev, 4),
            "market_sentiment": "bullish" if avg_ev > 0.05 else "neutral",
            "top_opportunities": [
                {
                    "player": p.player.name if p.player else "Unknown",
                    "team": p.player.team.name if p.player and p.player.team else "Unknown",
                    "stat_type": p.market.stat_type if p.market else "unknown",
                    "expected_value": p.expected_value,
                    "confidence": p.confidence_score
                }
                for p in high_ev_picks[:5]
            ]
        }
        
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
        # Get high confidence picks
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        ).where(
            ModelPick.confidence_score >= min_confidence
        ).order_by(
            desc(ModelPick.confidence_score)
        ).limit(10)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        signals = [
            {
                "player": p.player.name if p.player else "Unknown",
                "team": p.player.team.name if p.player and p.player.team else "Unknown",
                "stat_type": p.market.stat_type if p.market else "unknown",
                "confidence": p.confidence_score,
                "expected_value": p.expected_value,
                "signal_strength": "strong" if p.confidence_score > 0.8 else "moderate"
            }
            for p in picks
        ]
        
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
            "min_confidence": min_confidence
        }

@router.get("/intelligence")
async def get_sportsbook_intelligence(
    sport_id: int = Query(None, description="Sport ID filter"),
    db: AsyncSession = Depends(get_db)
):
    """Main sportsbook intelligence endpoint."""
    try:
        # Get comprehensive market data
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        )
        
        if sport_id:
            query = query.where(ModelPick.sport_id == sport_id)
        
        query = query.order_by(desc(ModelPick.expected_value)).limit(50)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        # Calculate intelligence metrics
        total_picks = len(picks)
        avg_ev = sum(p.expected_value for p in picks) / total_picks if picks else 0
        avg_confidence = sum(p.confidence_score for p in picks) / total_picks if picks else 0
        
        high_ev_picks = [p for p in picks if p.expected_value > 0.1]
        high_confidence_picks = [p for p in picks if p.confidence_score > 0.7]
        
        intelligence = {
            "market_overview": {
                "total_picks": total_picks,
                "average_ev": round(avg_ev, 4),
                "average_confidence": round(avg_confidence, 3),
                "high_ev_opportunities": len(high_ev_picks),
                "high_confidence_picks": len(high_confidence_picks)
            },
            "top_performers": [
                {
                    "player": p.player.name if p.player else "Unknown",
                    "team": p.player.team.name if p.player and p.player.team else "Unknown",
                    "stat_type": p.market.stat_type if p.market else "unknown",
                    "expected_value": p.expected_value,
                    "confidence": p.confidence_score,
                    "odds": p.odds
                }
                for p in picks[:10]
            ],
            "market_signals": {
                "sentiment": "bullish" if avg_ev > 0.05 else "neutral",
                "volatility": "low" if avg_confidence > 0.7 else "moderate",
                "opportunity_score": min(100, int(avg_ev * 1000))
            }
        }
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "intelligence": intelligence,
            "message": f"Sportsbook intelligence for {total_picks} picks"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-summary")
async def get_market_summary(db: AsyncSession = Depends(get_db)):
    """Get summary of market analysis."""
    try:
        # Get basic market summary
        query = select(ModelPick).options(
            selectinload(ModelPick.player).selectinload(Player.team),
            selectinload(ModelPick.market)
        ).limit(100)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        summary = {
            "total_picks": len(picks),
            "average_ev": round(sum(p.expected_value for p in picks) / len(picks), 4) if picks else 0,
            "average_confidence": round(sum(p.confidence_score for p in picks) / len(picks), 3) if picks else 0,
            "high_ev_count": len([p for p in picks if p.expected_value > 0.1]),
            "high_confidence_count": len([p for p in picks if p.confidence_score > 0.7])
        }
        
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
            "texas_sportsbooks": enhanced_sportsbook_monitor.texas_sportsbooks,
            "total_sportsbooks": len(enhanced_sportsbook_monitor.texas_sportsbooks),
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
        analysis = await enhanced_sportsbook_monitor.analyze_market_opportunities(db, sport_id)
        
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
