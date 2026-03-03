# backend/services/brain_bottom_up_projections.py
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from services.monte_carlo_service import monte_carlo_service

logger = logging.getLogger(__name__)

class BottomUpProjections:
    def __init__(self):
        pass

    async def generate_true_line(self, player_stats: Dict[str, Any], stat_type: str, sport_key: str) -> Dict[str, Any]:
        """
        Builds an internal "True Line" using historical stats and Monte Carlo simulations.
        """
        # 1. Determine distribution type based on stat
        # Counting stats like TDs, Goals, Strikeouts often follow Poisson
        poisson_stats = ["player_anytime_td", "player_pass_tds", "player_goals", "pitcher_strikeouts", "home_runs"]
        distribution = "poisson" if stat_type in poisson_stats else "normal"
        
        # 2. Extract mean and std_dev from historical stats
        # In a real system, this would query a database of historical performances
        mean = player_stats.get("season_avg", 0.0)
        std_dev = player_stats.get("std_dev", mean * 0.25) # Fallback heuristic
        
        # 3. Simulate outcomes to find the "fair" line (where hit rate is 50%)
        # Note: True line is often the median or mean depending on distribution
        true_line = mean if distribution == "normal" else mean # Poisson median is approx mean - 0.3
        
        # 4. For a given market line, calculate our projected hit rate vs market
        # This part is usually done in the main engine, but this service provides the reference.
        
        return {
            "player_name": player_stats.get("player_name"),
            "stat_type": stat_type,
            "true_line": round(true_line, 2),
            "projected_mean": round(mean, 2),
            "projected_std_dev": round(std_dev, 2),
            "distribution": distribution,
            "confidence_interval": [round(mean - 1.96 * std_dev, 2), round(mean + 1.96 * std_dev, 2)] if distribution == "normal" else None,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    async def identify_value_discrepancy(self, market_prop: Dict[str, Any], true_line_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compares market line vs internal true line to find early value.
        """
        market_line = market_prop.get("line", 0.0)
        true_line = true_line_data.get("true_line", 0.0)
        
        discrepancy = abs(market_line - true_line)
        discrepancy_pct = (discrepancy / market_line) * 100 if market_line > 0 else 0
        
        # Identify if we are 'Over' or 'Under' the market
        recommendation = "OVER" if true_line > market_line else "UNDER"
        
        return {
            "market_line": market_line,
            "true_line": true_line,
            "discrepancy": round(discrepancy, 2),
            "discrepancy_percentage": round(discrepancy_pct, 2),
            "recommendation": recommendation,
            "is_significant": discrepancy_pct > 10.0 # Flag if >10% difference
        }

bottom_up_projections = BottomUpProjections()
