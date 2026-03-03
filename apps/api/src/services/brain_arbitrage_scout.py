# backend/services/brain_arbitrage_scout.py
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ArbitrageScout:
    def __init__(self):
        pass

    def american_to_decimal(self, odds: int) -> float:
        """Convert American odds to Decimal odds."""
        if odds > 0:
            return 1 + (odds / 100)
        else:
            return 1 + (100 / abs(odds))

    def calculate_arbitrage(self, odds_a: int, odds_b: int, total_investment: float = 100.0) -> Optional[Dict[str, Any]]:
        """
        Calculate arbitrage opportunity between two sides.
        Returns profit details if opportunity exists, otherwise None.
        """
        dec_a = self.american_to_decimal(odds_a)
        dec_b = self.american_to_decimal(odds_b)
        
        implied_a = 1 / dec_a
        implied_b = 1 / dec_b
        
        total_implied = implied_a + implied_b
        
        # Arbitrage exists if total implied probability is less than 1.0 (100%)
        if total_implied < 1.0:
            profit_pct = (1 / total_implied) - 1
            
            # Optimal stakes for a guaranteed profit
            stake_a = (total_investment / total_implied) * implied_a
            stake_b = (total_investment / total_implied) * implied_b
            
            guaranteed_return = stake_a * dec_a # Should be same as stake_b * dec_b
            net_profit = guaranteed_return - total_investment
            
            return {
                "profit_percentage": round(profit_pct * 100, 2),
                "total_investment": round(total_investment, 2),
                "stake_a": round(stake_a, 2),
                "stake_b": round(stake_b, 2),
                "guaranteed_return": round(guaranteed_return, 2),
                "net_profit": round(net_profit, 2),
                "is_arbitrage": True
            }
        
        return None

    async def scan_market_for_arbs(self, props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans a list of formatted props for arbitrage opportunities across different bookmakers.
        This expects props grouped by (player, stat, line).
        """
        arbs = []
        
        # Group props by player, stat, and line to find discrepancies
        grouped = {}
        for p in props:
            key = (p.get("player_name"), p.get("stat_type"), p.get("line_value"))
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(p)
            
        for key, book_lines in grouped.items():
            if len(book_lines) < 2:
                continue
                
            # Find the best 'Over' odds and best 'Under' odds across all books
            # Note: The 'side' in the prop object might be fixed to 'over'.
            # Real scanning would need both sides from the API.
            # Assuming our data structure might need adjustment to track both sides per book.
            
            # Placeholder for cross-book logic:
            # For each pair of books, check Over(Book A) vs Under(Book B)
            # This requires the data to have both sides.
            pass
            
        return arbs

arbitrage_scout = ArbitrageScout()
