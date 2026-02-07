"""
Enhanced brain API with Texas sportsbook integration.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.enhanced_brain import enhanced_brain
from app.services.sportsbook_service import texas_sportsbook_service

router = APIRouter(prefix="/api/enhanced-brain", tags=["enhanced-brain"])


@router.get("/status")
async def get_enhanced_brain_status(
    db: AsyncSession = Depends(get_db)
):
    """Get enhanced brain status with sportsbook intelligence."""
    try:
        # Get current brain state
        brain_state = enhanced_brain.state
        
        # Get sportsbook intelligence
        nba_intel = enhanced_brain.sportsbook_intelligence.get("NBA")
        
        # Get trading decisions
        trading_decisions = enhanced_brain.trading_decisions[:5]  # Top 5
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "brain_status": {
                "total_operations": brain_state.total_operations,
                "last_health_check": brain_state.last_health_check.status if brain_state.last_health_check else "UNKNOWN",
                "uptime_seconds": (datetime.now(timezone.utc) - brain_state.started_at).total_seconds() if brain_state.started_at else 0
            },
            "sportsbook_intelligence": {
                "market_efficiency": nba_intel.market_efficiency if nba_intel else None,
                "arbitrage_opportunities": nba_intel.arbitrage_opportunities if nba_intel else 0,
                "best_sportsbook": nba_intel.best_sportsbook if nba_intel else None,
                "pricing_anomalies": nba_intel.pricing_anomalies[:3] if nba_intel else [],
                "last_analysis": nba_intel.timestamp.isoformat() if nba_intel else None
            },
            "trading_decisions": [
                {
                    "action": dec.action,
                    "player": dec.player_name,
                    "market": dec.market_type,
                    "sportsbook": dec.sportsbook,
                    "odds": dec.odds,
                    "our_edge": round(dec.our_edge, 4),
                    "market_edge": round(dec.market_edge, 4),
                    "confidence": round(dec.confidence, 3),
                    "reasoning": dec.reasoning
                }
                for dec in trading_decisions
            ],
            "system_health": "HEALTHY"
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "system_health": "ERROR"
        }


@router.get("/sportsbook-analysis")
async def get_sportsbook_analysis(
    sport_id: int = Query(30, description="Sport ID (30=NBA, 32=NCAA, 53=NHL)"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed sportsbook market analysis."""
    try:
        analysis = await texas_sportsbook_service.analyze_market_efficiency(db, sport_id)
        
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


@router.get("/arbitrage-opportunities")
async def get_arbitrage_opportunities(
    min_arbitrage_pct: float = Query(1.0, description="Minimum arbitrage percentage"),
    db: AsyncSession = Depends(get_db)
):
    """Get current arbitrage opportunities."""
    try:
        # Get markets
        markets = await texas_sportsbook_service.get_texas_markets(db, 30)
        
        # Find arbitrage opportunities
        arbitrage_opps = await texas_sportsbook_service.find_arbitrage_opportunities(markets)
        
        # Filter by minimum percentage
        filtered_opps = [
            opp for opp in arbitrage_opps 
            if opp.arbitrage_percentage >= min_arbitrage_pct
        ]
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_opportunities": len(arbitrage_opps),
            "filtered_opportunities": len(filtered_opps),
            "opportunities": [
                {
                    "player": opp.player_name,
                    "market": opp.market_type,
                    "line": opp.line_value,
                    "sportsbook_1": opp.sportsbook_1,
                    "odds_1": opp.odds_1,
                    "sportsbook_2": opp.sportsbook_2,
                    "odds_2": opp.odds_2,
                    "arbitrage_percentage": round(opp.arbitrage_percentage, 2),
                    "profit_potential": f"${opp.arbitrage_percentage * 10:.2f}"  # Per $100 bet
                }
                for opp in filtered_opps[:10]
            ]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


@router.get("/trading-signals")
async def get_trading_signals(
    min_confidence: float = Query(0.7, description="Minimum confidence level"),
    db: AsyncSession = Depends(get_db)
):
    """Get current trading signals."""
    try:
        # Generate fresh trading decisions
        decisions = await enhanced_brain.generate_trading_decisions(db)
        
        # Filter by confidence
        filtered_decisions = [
            dec for dec in decisions 
            if dec.confidence >= min_confidence
        ]
        
        # Separate by action type
        bets = [dec for dec in filtered_decisions if dec.action == "BET"]
        passes = [dec for dec in filtered_decisions if dec.action == "PASS"]
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_decisions": len(decisions),
            "filtered_decisions": len(filtered_decisions),
            "min_confidence": min_confidence,
            "signals": {
                "bet_signals": [
                    {
                        "player": dec.player_name,
                        "market": dec.market_type,
                        "sportsbook": dec.sportsbook,
                        "odds": dec.odds,
                        "our_edge": round(dec.our_edge, 4),
                        "market_edge": round(dec.market_edge, 4),
                        "edge_difference": round(dec.our_edge - dec.market_edge, 4),
                        "confidence": round(dec.confidence, 3),
                        "reasoning": dec.reasoning
                    }
                    for dec in bets[:5]
                ],
                "pass_signals": [
                    {
                        "player": dec.player_name,
                        "market": dec.market_type,
                        "sportsbook": dec.sportsbook,
                        "odds": dec.odds,
                        "our_edge": round(dec.our_edge, 4),
                        "market_edge": round(dec.market_edge, 4),
                        "edge_difference": round(dec.our_edge - dec.market_edge, 4),
                        "confidence": round(dec.confidence, 3),
                        "reasoning": dec.reasoning
                    }
                    for dec in passes[:5]
                ]
            }
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


@router.post("/trigger-analysis")
async def trigger_sportsbook_analysis(
    sport_id: int = Query(30, description="Sport ID to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Trigger immediate sportsbook market analysis."""
    try:
        # Trigger analysis
        intelligence = await enhanced_brain.analyze_sportsbook_markets(db)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "analysis_triggered": True,
            "intelligence": {
                "market_efficiency": intelligence.market_efficiency if intelligence else None,
                "arbitrage_opportunities": intelligence.arbitrage_opportunities if intelligence else 0,
                "best_sportsbook": intelligence.best_sportsbook if intelligence else None,
                "pricing_anomalies_count": len(intelligence.pricing_anomalies) if intelligence else 0
            }
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "analysis_triggered": False
        }
