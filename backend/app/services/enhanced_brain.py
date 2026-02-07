"""
Enhanced brain service with Texas sportsbook integration.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.database import get_db
from app.services.brain import BrainState, HealthCheck, brain_loop
from app.services.sportsbook_service import texas_sportsbook_service
from app.services.brain_persistence import log_decision, log_health_check, log_business_metrics

logger = get_logger(__name__)

@dataclass
class SportsbookIntelligence:
    """Sportsbook intelligence data."""
    market_efficiency: float
    arbitrage_opportunities: int
    best_sportsbook: str
    pricing_anomalies: List[str]
    timestamp: datetime

@dataclass
class TradingDecision:
    """Trading decision based on sportsbook intelligence."""
    action: str  # "BET", "PASS", "ARBITRAGE"
    player_name: str
    market_type: str
    sportsbook: str
    odds: int
    our_edge: float
    market_edge: float
    confidence: float
    reasoning: str

class EnhancedBrain:
    """Enhanced brain with Texas sportsbook integration."""
    
    def __init__(self):
        self.state = BrainState()
        self.sportsbook_intelligence = {}
        self.trading_decisions = []
        self.last_sportsbook_analysis = None
        
    async def analyze_sportsbook_markets(self, db: AsyncSession) -> SportsbookIntelligence:
        """Analyze Texas sportsbook markets for intelligence."""
        try:
            # Get market analysis from sportsbook service
            analysis = await texas_sportsbook_service.analyze_market_efficiency(db, sport_id=30)  # NBA
            
            if analysis["status"] == "success":
                arbitrage_count = len(analysis["arbitrage_opportunities"])
                market_efficiency = 100 - (analysis["market_efficiency"]["average_arbitrage_percentage"] or 0)
                best_sportsbook = analysis["market_efficiency"]["most_efficient_sportsbook"]
                
                # Identify pricing anomalies
                pricing_anomalies = []
                for opp in analysis["arbitrage_opportunities"]:
                    if opp["arbitrage_pct"] > 2.0:  # Significant arbitrage
                        pricing_anomalies.append(
                            f"{opp['player']} {opp['market']} - {opp['arbitrage_pct']}% arbitrage"
                        )
                
                intelligence = SportsbookIntelligence(
                    market_efficiency=market_efficiency,
                    arbitrage_opportunities=arbitrage_count,
                    best_sportsbook=best_sportsbook or "Unknown",
                    pricing_anomalies=pricing_anomalies,
                    timestamp=datetime.now(timezone.utc)
                )
                
                self.sportsbook_intelligence["NBA"] = intelligence
                self.last_sportsbook_analysis = analysis
                
                # Log business metrics
                await log_business_metrics(
                    db=db,
                    metric_name="sportsbook_market_efficiency",
                    metric_value=market_efficiency,
                    sport_id=30,
                    additional_data={
                        "arbitrage_opportunities": arbitrage_count,
                        "best_sportsbook": best_sportsbook,
                        "pricing_anomalies": len(pricing_anomalies)
                    }
                )
                
                logger.info(f"[BRAIN] Sportsbook intelligence updated: {market_efficiency:.1f}% efficiency, {arbitrage_count} arbitrage opportunities")
                
                return intelligence
            else:
                logger.warning(f"[BRAIN] Sportsbook analysis failed: {analysis.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"[BRAIN] Error analyzing sportsbook markets: {e}")
            return None
    
    async def generate_trading_decisions(self, db: AsyncSession) -> List[TradingDecision]:
        """Generate trading decisions based on sportsbook intelligence."""
        try:
            decisions = []
            
            # Get our model picks
            picks_sql = """
                SELECT p.name as player_name, mp.line_value, mp.expected_value,
                       m.stat_type, g.start_time
                FROM model_picks mp
                JOIN players p ON mp.player_id = p.id
                JOIN games g ON mp.game_id = g.id
                JOIN markets m ON mp.market_id = m.id
                WHERE g.sport_id = 30
                AND mp.generated_at > NOW() - INTERVAL '6 hours'
                AND mp.line_value IS NOT NULL
                AND mp.expected_value > 0.03  # Grade B or better
                ORDER BY mp.expected_value DESC
                LIMIT 20
            """
            
            result = await db.execute(picks_sql)
            rows = result.fetchall()
            
            for row in rows:
                player_name, line_value, expected_value, stat_type, game_start = row
                
                # Get sportsbook odds for this player
                markets = await texas_sportsbook_service.get_texas_markets(db, 30)
                player_markets = [m for m in markets if m.player_name == player_name and m.market_type == stat_type]
                
                if player_markets:
                    # Find best odds
                    best_market = max(player_markets, key=lambda x: x.odds)
                    
                    # Calculate our edge vs market
                    our_edge = expected_value
                    market_edge = (best_market.implied_probability - 0.5) * 2  # Convert to edge format
                    
                    # Make trading decision
                    if our_edge > market_edge + 0.02:  # We have significantly better edge
                        action = "BET"
                        confidence = min(0.95, (our_edge - market_edge) * 10)
                        reasoning = f"Our edge ({our_edge:.3f}) significantly better than market ({market_edge:.3f})"
                    elif our_edge < market_edge - 0.02:  # Market has better edge
                        action = "PASS"
                        confidence = min(0.95, (market_edge - our_edge) * 10)
                        reasoning = f"Market edge ({market_edge:.3f}) better than ours ({our_edge:.3f})"
                    else:
                        action = "PASS"
                        confidence = 0.5
                        reasoning = f"Edges similar (ours: {our_edge:.3f}, market: {market_edge:.3f})"
                    
                    decision = TradingDecision(
                        action=action,
                        player_name=player_name,
                        market_type=stat_type,
                        sportsbook=best_market.sportsbook,
                        odds=best_market.odds,
                        our_edge=our_edge,
                        market_edge=market_edge,
                        confidence=confidence,
                        reasoning=reasoning
                    )
                    
                    decisions.append(decision)
                    
                    # Log decision
                    await log_decision(
                        db=db,
                        decision_type="sportsbook_trading",
                        decision_data={
                            "action": action,
                            "player": player_name,
                            "market": stat_type,
                            "sportsbook": best_market.sportsbook,
                            "odds": best_market.odds,
                            "our_edge": our_edge,
                            "market_edge": market_edge,
                            "confidence": confidence,
                            "reasoning": reasoning
                        },
                        context={
                            "sport_id": 30,
                            "line_value": line_value,
                            "expected_value": expected_value
                        }
                    )
            
            # Sort by confidence
            decisions.sort(key=lambda x: x.confidence, reverse=True)
            self.trading_decisions = decisions[:10]  # Keep top 10
            
            logger.info(f"[BRAIN] Generated {len(decisions)} trading decisions")
            return decisions
            
        except Exception as e:
            logger.error(f"[BRAIN] Error generating trading decisions: {e}")
            return []
    
    async def enhanced_health_check(self, db: AsyncSession) -> HealthCheck:
        """Enhanced health check with sportsbook intelligence."""
        try:
            base_health = HealthCheck(
                status="HEALTHY",
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                response_time=0.0,
                error_rate=0.0,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Add sportsbook intelligence to health check
            if self.sportsbook_intelligence:
                nba_intel = self.sportsbook_intelligence.get("NBA")
                if nba_intel:
                    if nba_intel.market_efficiency < 90:
                        base_health.status = "DEGRADED"
                        base_health.details = f"Low market efficiency: {nba_intel.market_efficiency:.1f}%"
                    elif nba_intel.arbitrage_opportunities > 10:
                        base_health.status = "WARNING"
                        base_health.details = f"High arbitrage opportunities: {nba_intel.arbitrage_opportunities}"
            
            # Log enhanced health check
            await log_health_check(
                db=db,
                health_check_data={
                    "status": base_health.status,
                    "cpu_usage": base_health.cpu_usage,
                    "memory_usage": base_health.memory_usage,
                    "disk_usage": base_health.disk_usage,
                    "response_time": base_health.response_time,
                    "error_rate": base_health.error_rate,
                    "sportsbook_intelligence": {
                        "market_efficiency": nba_intel.market_efficiency if nba_intel else None,
                        "arbitrage_opportunities": nba_intel.arbitrage_opportunities if nba_intel else None,
                        "trading_decisions": len(self.trading_decisions)
                    }
                }
            )
            
            return base_health
            
        except Exception as e:
            logger.error(f"[BRAIN] Error in enhanced health check: {e}")
            return HealthCheck(
                status="UNHEALTHY",
                timestamp=datetime.now(timezone.utc),
                details=str(e)
            )
    
    async def enhanced_brain_loop(self, interval_minutes: int = 5, initial_delay: int = 90):
        """Enhanced brain loop with sportsbook integration."""
        logger.info(f"[BRAIN] Enhanced brain starting (sportsbook integration every {interval_minutes}m)")
        
        await asyncio.sleep(initial_delay)
        
        while True:
            try:
                start_time = datetime.now(timezone.utc)
                
                # Get database session
                async with get_db() as db:
                    # Analyze sportsbook markets
                    await self.analyze_sportsbook_markets(db)
                    
                    # Generate trading decisions
                    await self.generate_trading_decisions(db)
                    
                    # Enhanced health check
                    health = await self.enhanced_health_check(db)
                    
                    # Update brain state
                    self.state.last_health_check = health
                    self.state.total_operations += 1
                    
                    # Log brain activity
                    logger.info(f"[BRAIN] Enhanced cycle completed - "
                              f"Market efficiency: {self.sportsbook_intelligence.get('NBA', {}).get('market_efficiency', 'N/A')}%, "
                              f"Trading decisions: {len(self.trading_decisions)}, "
                              f"Health: {health.status}")
                
                # Calculate sleep time
                cycle_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                sleep_time = max(60, interval_minutes * 60 - cycle_time)
                
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"[BRAIN] Error in enhanced brain loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute on error

# Global enhanced brain instance
enhanced_brain = EnhancedBrain()
