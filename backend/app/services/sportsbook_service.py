"""
Sportsbook integration service for Texas sportsbooks.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class SportsbookMarket:
    """Sportsbook market data."""
    sportsbook: str
    market_type: str
    player_name: str
    line_value: float
    odds: int
    implied_probability: float
    timestamp: datetime

@dataclass
class SportsbookArbitrage:
    """Arbitrage opportunity between sportsbooks."""
    player_name: str
    market_type: str
    line_value: float
    sportsbook_1: str
    odds_1: int
    sportsbook_2: str
    odds_2: int
    arbitrage_percentage: float

class TexasSportsbookService:
    """Texas sportsbook integration and analysis service."""
    
    def __init__(self):
        self.sportsbooks = [
            "DraftKings Texas",
            "FanDuel Texas", 
            "BetMGM Texas",
            "Caesars Texas",
            "Barstool Texas"
        ]
        self.markets_cache = {}
        self.last_update = None
        
    async def get_texas_markets(self, db: AsyncSession, sport_id: int = 30) -> List[SportsbookMarket]:
        """Get current Texas sportsbook markets."""
        try:
            # Simulate fetching from Texas sportsbooks APIs
            # In production, this would integrate with real sportsbook APIs
            
            markets = []
            
            # Get our model picks for comparison
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
                ORDER BY mp.expected_value DESC
                LIMIT 50
            """)
            
            result = await db.execute(picks_sql)
            rows = result.fetchall()
            
            for row in rows:
                player_name, line_value, expected_value, stat_type, game_start = row
                
                # Simulate sportsbook odds (would be real API calls)
                for sportsbook in self.sportsbooks[:3]:  # Use top 3 for demo
                    # Simulate odds variation between sportsbooks
                    odds_variation = 0.95 + (hash(sportsbook + player_name) % 10) / 100
                    base_odds = -110
                    adjusted_odds = int(base_odds * odds_variation)
                    
                    implied_prob = self._calculate_implied_probability(adjusted_odds)
                    
                    market = SportsbookMarket(
                        sportsbook=sportsbook,
                        market_type=stat_type,
                        player_name=player_name,
                        line_value=line_value,
                        odds=adjusted_odds,
                        implied_probability=implied_prob,
                        timestamp=datetime.now(timezone.utc)
                    )
                    markets.append(market)
            
            self.markets_cache[sport_id] = markets
            self.last_update = datetime.now(timezone.utc)
            
            logger.info(f"[SPORTSBOOK] Fetched {len(markets)} Texas markets for sport {sport_id}")
            return markets
            
        except Exception as e:
            logger.error(f"[SPORTSBOOK] Error fetching Texas markets: {e}")
            return []
    
    def _calculate_implied_probability(self, odds: int) -> float:
        """Calculate implied probability from American odds."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    async def find_arbitrage_opportunities(self, markets: List[SportsbookMarket]) -> List[SportsbookArbitrage]:
        """Find arbitrage opportunities between sportsbooks."""
        try:
            arbitrage_opportunities = []
            
            # Group markets by player and line
            market_groups = {}
            for market in markets:
                key = f"{market.player_name}_{market.market_type}_{market.line_value}"
                if key not in market_groups:
                    market_groups[key] = []
                market_groups[key].append(market)
            
            # Find arbitrage opportunities
            for key, group_markets in market_groups.items():
                if len(group_markets) >= 2:
                    # Sort by odds (best for betting)
                    group_markets.sort(key=lambda x: x.odds, reverse=True)
                    
                    best_market = group_markets[0]
                    second_best = group_markets[1]
                    
                    # Calculate arbitrage opportunity
                    combined_prob = best_market.implied_probability + second_best.implied_probability
                    
                    if combined_prob < 1.0:  # Arbitrage opportunity
                        arbitrage_pct = (1.0 - combined_prob) * 100
                        
                        arbitrage = SportsbookArbitrage(
                            player_name=best_market.player_name,
                            market_type=best_market.market_type,
                            line_value=best_market.line_value,
                            sportsbook_1=best_market.sportsbook,
                            odds_1=best_market.odds,
                            sportsbook_2=second_best.sportsbook,
                            odds_2=second_best.odds,
                            arbitrage_percentage=arbitrage_pct
                        )
                        arbitrage_opportunities.append(arbitrage)
            
            # Sort by arbitrage percentage
            arbitrage_opportunities.sort(key=lambda x: x.arbitrage_percentage, reverse=True)
            
            logger.info(f"[SPORTSBOOK] Found {len(arbitrage_opportunities)} arbitrage opportunities")
            return arbitrage_opportunities[:10]  # Top 10 opportunities
            
        except Exception as e:
            logger.error(f"[SPORTSBOOK] Error finding arbitrage: {e}")
            return []
    
    async def analyze_market_efficiency(self, db: AsyncSession, sport_id: int = 30) -> Dict[str, Any]:
        """Analyze market efficiency and pricing."""
        try:
            markets = await self.get_texas_markets(db, sport_id)
            
            if not markets:
                return {"status": "no_data", "markets": []}
            
            # Analyze pricing across sportsbooks
            sportsbook_analysis = {}
            for sportsbook in self.sportsbooks:
                sportsbook_markets = [m for m in markets if m.sportsbook == sportsbook]
                
                if sportsbook_markets:
                    avg_odds = sum(m.odds for m in sportsbook_markets) / len(sportsbook_markets)
                    avg_implied_prob = sum(m.implied_probability for m in sportsbook_markets) / len(sportsbook_markets)
                    
                    sportsbook_analysis[sportsbook] = {
                        "market_count": len(sportsbook_markets),
                        "average_odds": avg_odds,
                        "average_implied_probability": avg_implied_prob,
                        "best_odds_count": len([m for m in sportsbook_markets if m.odds > -108])
                    }
            
            # Find arbitrage opportunities
            arbitrage_opps = await self.find_arbitrage_opportunities(markets)
            
            return {
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_markets": len(markets),
                "sportsbook_analysis": sportsbook_analysis,
                "arbitrage_opportunities": [
                    {
                        "player": arb.player_name,
                        "market": arb.market_type,
                        "line": arb.line_value,
                        "sportsbook_1": arb.sportsbook_1,
                        "odds_1": arb.odds_1,
                        "sportsbook_2": arb.sportsbook_2,
                        "odds_2": arb.odds_2,
                        "arbitrage_pct": round(arb.arbitrage_percentage, 2)
                    }
                    for arb in arbitrage_opps
                ],
                "market_efficiency": {
                    "total_arbitrage_opportunities": len(arbitrage_opps),
                    "average_arbitrage_percentage": round(sum(a.arbitrage_percentage for a in arbitrage_opps) / len(arbitrage_opps), 2) if arbitrage_opps else 0,
                    "most_efficient_sportsbook": min(sportsbook_analysis.keys(), key=lambda x: sportsbook_analysis[x].get("average_odds", 0)) if sportsbook_analysis else None
                }
            }
            
        except Exception as e:
            logger.error(f"[SPORTSBOOK] Error analyzing market efficiency: {e}")
            return {"status": "error", "error": str(e)}

# Global instance
texas_sportsbook_service = TexasSportsbookService()
