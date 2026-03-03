import math
from typing import Dict, List

class RiskService:
    @staticmethod
    def calculate_fractional_kelly(win_prob: float, odds: int, fraction: float = 0.5) -> float:
        """
        Calculate the Fractional Kelly Criterion.
        
        :param win_prob: Probability of winning (0.0 to 1.0)
        :param odds: American odds (e.g., -110, +150)
        :param fraction: Kelly fraction (e.g., 0.5 for Half-Kelly)
        :return: Suggested percentage of bankroll to wager
        """
        if odds > 0:
            b = odds / 100.0
        else:
            b = 100.0 / abs(odds)
            
        p = win_prob
        q = 1.0 - p
        
        # Kelly Formula: f* = (bp - q) / b
        kelly_full = (b * p - q) / b
        
        # Apply fraction and floor at 0
        suggestion = max(0, kelly_full * fraction)
        return round(suggestion * 100, 2)

    @staticmethod
    def calculate_cppi(bankroll: float, floor: float, multiplier: float = 2.0) -> float:
        """
        Constant Proportional Insurance (CPPI) model.
        Wager size is proportional to the 'cushion' (Bankroll - Floor).
        
        :param bankroll: Current total bankroll
        :param floor: The absolute minimum acceptable bankroll
        :param multiplier: Aggression factor
        :return: Absolute dollar amount to risk on the next portfolio segment
        """
        cushion = max(0, bankroll - floor)
        return round(cushion * multiplier, 2)

    @staticmethod
    def calculate_risk_of_ruin(win_rate: float, edge: float, bankroll_units: int) -> float:
        """
        Estimate the probability of ruin given a constant win rate and unit size.
        Using the formula: RoR = ((1 - edge) / (1 + edge)) ^ bankroll_units
        Simplified for constant unit size.
        """
        if edge <= 0:
            return 100.0
            
        a = (1 - edge) / (1 + edge)
        # Prevent division by zero or negative bases if edge is somehow > 1
        a = max(0, min(0.99, a))
        
        ror = (a ** bankroll_units) * 100
        return round(ror, 2)

    @staticmethod
    def calculate_max_drawdown(balance_history: List[float]) -> float:
        """
        Calculate the maximum peak-to-trough decline.
        """
        if not balance_history:
            return 0.0
            
        max_so_far = balance_history[0]
        max_drawdown = 0.0
        
        for balance in balance_history:
            if balance > max_so_far:
                max_so_far = balance
            
            drawdown = (max_so_far - balance) / max_so_far if max_so_far > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                
        return round(max_drawdown * 100, 2)

    @staticmethod
    def calculate_expected_growth(edge: float, win_prob: float, fraction: float = 0.5) -> float:
        """
        Calculate expected geometric growth rate per wager.
        G = p*log(1+f*b) + q*log(1-f)
        """
        p = win_prob
        q = 1.0 - p
        
        # Simplified growth estimation for small edges
        # G approx = fraction * (edge^2 / 2)
        growth = fraction * (edge ** 2) / 2.0
        return round(growth * 100, 4)

    @staticmethod
    def standardize_kelly(bankroll: float, edge: float, odds: int, min_unit: float = 10.0, max_pct: float = 0.05) -> float:
        """
        Standardize a Kelly wager into a dollar amount with safety caps.
        """
        if odds > 0:
            b = odds / 100.0
        else:
            b = 100.0 / abs(odds)
            
        # Full Kelly f = edge / b
        raw_f = edge / b
        
        # Apply conservative 0.25 fraction for "Standardized" sizing
        safe_f = max(0, raw_f * 0.25)
        
        # Cap at max_pct of bankroll
        final_f = min(safe_f, max_pct)
        
        amount = bankroll * final_f
        return max(min_unit, round(amount, 2))

risk_service = RiskService()
