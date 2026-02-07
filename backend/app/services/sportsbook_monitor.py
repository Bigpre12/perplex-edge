"""
Simplified sportsbook monitoring service.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.logging import get_logger

logger = get_logger(__name__)

class SportsbookMonitor:
    """Simplified sportsbook monitoring service."""
    
    def __init__(self):
        self.texas_sportsbooks = [
            "DraftKings Texas",
            "FanDuel Texas", 
            "BetMGM Texas",
            "Caesars Texas",
            "Barstool Texas"
        ]
        self.last_analysis = None
        self.market_data = {}
        
    async def analyze_market_opportunities(self, db: AsyncSession, sport_id: int = 30) -> Dict[str, Any]:
        """Analyze market opportunities for Texas sportsbooks."""
        try:
            # Get our model picks
            picks_sql = text(f"""
                SELECT p.name as player_name, mp.line_value, mp.expected_value,
                       m.stat_type, g.start_time
                FROM model_picks mp
                JOIN players p ON mp.player_id = p.id
                JOIN games g ON mp.game_id = g.id
                JOIN markets m ON mp.market_id = m.id
                WHERE g.sport_id = {sport_id}
                AND mp.generated_at > NOW() - INTERVAL '6 hours'
                AND mp.line_value IS NOT NULL
                AND mp.expected_value > 0.03
                ORDER BY mp.expected_value DESC
                LIMIT 100
            """)
            
            result = await db.execute(picks_sql)
            rows = result.fetchall()
            
            # Simulate sportsbook market analysis
            opportunities = []
            total_picks = len(rows)
            
            if total_picks > 0:
                # Calculate market metrics
                avg_edge = sum(row[2] for row in rows) / total_picks
                high_edge_picks = len([row for row in rows if row[2] > 0.05])
                
                # Simulate arbitrage opportunities
                arbitrage_count = int(total_picks * 0.02)  # 2% of picks have arbitrage
                
                # Generate sample opportunities
                for i, row in enumerate(rows[:10]):  # Top 10 picks
                    player_name, line_value, expected_value, stat_type, game_start = row
                    
                    # Simulate sportsbook odds variation
                    best_sportsbook = self.texas_sportsbooks[i % len(self.texas_sportsbooks)]
                    market_odds = -110 + (i * 2)  # Slight variation
                    
                    opportunity = {
                        "player": player_name,
                        "market": stat_type,
                        "line": line_value,
                        "our_edge": round(expected_value, 4),
                        "best_sportsbook": best_sportsbook,
                        "market_odds": market_odds,
                        "confidence": "HIGH" if expected_value > 0.05 else "MEDIUM",
                        "recommendation": "BET" if expected_value > 0.04 else "CONSIDER"
                    }
                    opportunities.append(opportunity)
            
            analysis = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sport_id": sport_id,
                "total_picks_analyzed": total_picks,
                "average_edge": round(avg_edge, 4) if total_picks > 0 else 0,
                "high_edge_picks": high_edge_picks,
                "arbitrage_opportunities": arbitrage_count,
                "market_efficiency": round(95 - (avg_edge * 100), 1) if total_picks > 0 else 0,
                "top_opportunities": opportunities,
                "sportsbook_coverage": {
                    "monitored_sportsbooks": self.texas_sportsbooks,
                    "active_markets": len(set(opp["market"] for opp in opportunities)),
                    "best_pricing_sportsbook": max(self.texas_sportsbooks[:3]) if opportunities else None
                }
            }
            
            self.last_analysis = analysis
            self.market_data[sport_id] = analysis
            
            logger.info(f"[SPORTSBOOK] Market analysis complete: {total_picks} picks, {arbitrage_count} arbitrage opportunities")
            return analysis
            
        except Exception as e:
            logger.error(f"[SPORTSBOOK] Error analyzing market opportunities: {e}")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "sport_id": sport_id
            }
    
    async def get_trading_signals(self, db: AsyncSession, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """Get trading signals based on market analysis."""
        try:
            # Get fresh analysis
            analysis = await self.analyze_market_opportunities(db, 30)
            
            if "error" in analysis:
                return []
            
            # Filter for high-confidence signals
            signals = []
            for opp in analysis["top_opportunities"]:
                if opp["our_edge"] > min_confidence:
                    signal = {
                        "action": "BET",
                        "player": opp["player"],
                        "market": opp["market"],
                        "sportsbook": opp["best_sportsbook"],
                        "odds": opp["market_odds"],
                        "edge": opp["our_edge"],
                        "confidence": opp["confidence"],
                        "reasoning": f"Strong edge ({opp['our_edge']}) vs market",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    signals.append(signal)
            
            # Sort by edge
            signals.sort(key=lambda x: x["edge"], reverse=True)
            
            logger.info(f"[SPORTSBOOK] Generated {len(signals)} trading signals")
            return signals[:10]  # Top 10 signals
            
        except Exception as e:
            logger.error(f"[SPORTSBOOK] Error generating trading signals: {e}")
            return []
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get summary of market analysis."""
        if not self.last_analysis:
            return {
                "status": "no_data",
                "message": "No market analysis available"
            }
        
        return {
            "status": "active",
            "last_analysis": self.last_analysis["timestamp"],
            "total_picks": self.last_analysis["total_picks_analyzed"],
            "market_efficiency": self.last_analysis["market_efficiency"],
            "arbitrage_opportunities": self.last_analysis["arbitrage_opportunities"],
            "monitored_sportsbooks": len(self.texas_sportsbooks)
        }

# Global monitor instance
sportsbook_monitor = SportsbookMonitor()
