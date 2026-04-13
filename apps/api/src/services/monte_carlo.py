import random
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SimLeg:
    player_name: str
    market: str
    line: float
    side: str
    over_price: int
    under_price: int
    historical_hit_rate: Optional[float] = None

@dataclass
class SimResult:
    simulations: int
    win_rate: float
    expected_value: float
    roi: float
    max_drawdown: float
    break_even_rate: float
    edge: float
    confidence: str
    historical_hit_rate: Optional[float]
    true_probability: float
    blend_method: str
    legs: int

class MonteCarloEngine:
    """
    Monte Carlo Simulation Engine for Player Props and Parlays.
    Uses real-world vig removal and historical data blending.
    """

    def run_simulation(self, legs: List[SimLeg], stake: float = 100, n: int = 10000) -> SimResult:
        """
        Runs 10,000 trials for a single prop or parlay.
        """
        if not legs:
            raise ValueError("At least one leg is required for simulation.")

        # 1. Calculate combined true probability
        parlay_true_prob = 1.0
        combined_historical = 0.0
        has_historical = False
        
        # We also need the combined decimal odds for the parlay to calculate EV
        combined_decimal_odds = 1.0

        for leg in legs:
            # A. Remove Vig (Sharp Book Method)
            # This returns the raw 'over' probability from the prices
            true_prob_over = self._remove_vig(leg.over_price, leg.under_price)
            
            # B. Apply Side
            leg_true_prob = true_prob_over if leg.side.lower() == "over" else (1.0 - true_prob_over)
            
            # C. Blend with Historical (if available)
            if leg.historical_hit_rate is not None:
                has_historical = True
                leg_true_prob = self._blend_probability(leg_true_prob, leg.historical_hit_rate)
            
            parlay_true_prob *= leg_true_prob
            
            # Calculate decimal odds for this leg based on the side chosen
            price = leg.over_price if leg.side.lower() == "over" else leg.under_price
            combined_decimal_odds *= self._american_to_decimal(price)

        # 2. Run Trials
        trials = self._run_trials(parlay_true_prob, combined_decimal_odds, stake, n)
        
        # 3. Final Metrics
        win_rate = trials['wins'] / n
        ev = trials['total_profit'] / n
        roi = (ev / stake) * 100
        
        # Break-even rate = 1 / decimal_odds
        break_even = 1 / combined_decimal_odds
        edge = parlay_true_prob - break_even
        
        # Determine confidence
        confidence = "low"
        if edge > 0.05:
            confidence = "high"
        elif edge > 0.02:
            confidence = "medium"

        return SimResult(
            simulations=n,
            win_rate=round(win_rate, 4),
            expected_value=round(ev, 2),
            roi=round(roi, 2),
            max_drawdown=round(trials['max_drawdown'], 2),
            break_even_rate=round(break_even, 4),
            edge=round(edge, 4),
            confidence=confidence,
            historical_hit_rate=legs[0].historical_hit_rate if len(legs) == 1 else None, # Simplified for display
            true_probability=round(parlay_true_prob, 4),
            blend_method="blended" if has_historical else "market_only",
            legs=len(legs)
        )

    def _remove_vig(self, over_price: int, under_price: int) -> float:
        """
        Sharp Book Method: Implied Prob / (Sum of Implied Probs)
        """
        p_over = self._american_to_implied(over_price)
        p_under = self._american_to_implied(under_price)
        
        total_market = p_over + p_under
        if total_market == 0:
            return 0.5
            
        return p_over / total_market # We return the probability of the OVER by default? 
        # Actually, the caller handles if they want under prob by calculating 1-true_prob if needed,
        # but here we should probably return the true prob of the specific side if we knew it.
        # Let's assume the first price passed IS the side the user wants.
        # Wait, the SimLeg has side. Let's fix _remove_vig usage.
        
    def _blend_probability(self, market_prob: float, historical_rate: float) -> float:
        """
        Blends market probability with historical hit rate (60/40 blend).
        """
        return (market_prob * 0.6) + (historical_rate * 0.4)

    def _run_trials(self, true_prob: float, decimal_odds: float, stake: float, n: int) -> dict:
        """
        Vectorized-style simulation in pure Python (avoiding complex dependencies if possible, 
        but numpy is usually available).
        """
        wins = 0
        total_profit = 0.0
        current_bankroll = 0.0
        peak_bankroll = 0.0
        max_drawdown = 0.0
        
        profit_per_win = stake * (decimal_odds - 1)
        
        for _ in range(n):
            if random.random() < true_prob:
                wins += 1
                total_profit += profit_per_win
                current_bankroll += profit_per_win
            else:
                total_profit -= stake
                current_bankroll -= stake
            
            # Track max drawdown (in units/stake)
            if current_bankroll > peak_bankroll:
                peak_bankroll = current_bankroll
            
            dd = peak_bankroll - current_bankroll
            if dd > max_drawdown:
                max_drawdown = dd
                
        return {
            "wins": wins,
            "total_profit": total_profit,
            "max_drawdown": max_drawdown / stake # Normalized to units
        }

    def _american_to_implied(self, odds: int) -> float:
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    def _american_to_decimal(self, odds: int) -> float:
        if odds > 0:
            return (odds / 100) + 1
        else:
            return (100 / abs(odds)) + 1

monte_carlo_engine = MonteCarloEngine()
