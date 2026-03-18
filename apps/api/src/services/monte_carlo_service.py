"""
Monte Carlo Simulation Service for Sports Betting Analytics

Provides statistically rigorous simulation of:
- Individual prop outcomes (hit probability, percentile distributions)
- Multi-leg parlay outcomes (combined probability, correlated legs)
- Bankroll trajectory over N picks (drawdown, ruin probability)
- Kelly criterion stake sizing

Uses NumPy for high-performance vectorized simulations.
"""
import math
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ─── Utility ─────────────────────────────────────────────────────────────────

def american_to_decimal(odds: float) -> float:
    """American odds to decimal odds."""
    if odds < 0:
        return 1 + (100 / abs(odds))
    return 1 + (odds / 100)


def american_to_implied(odds: float) -> float:
    """American odds to implied probability."""
    if odds == 0:
        return 0.5
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    return 100 / (odds + 100)


# ─── Core Simulation Functions ────────────────────────────────────────────────

def run_prop_simulation(
    mean: float,
    std_dev: float,
    line: float,
    side: str = "over",
    n_sims: int = 10000,
    distribution: str = "normal",
) -> Dict[str, Any]:
    """
    Monte Carlo simulation for a single player prop using NumPy.
    """
    if n_sims < 100:
        n_sims = 100
    if n_sims > 100000:
        n_sims = 100000

    # Generate simulated outcomes using NumPy
    if distribution == "poisson" and mean > 0:
        outcomes = np.random.poisson(mean, n_sims).astype(float)
    else:
        outcomes = np.random.normal(mean, max(std_dev, 0.01), n_sims)

    # Count hits using NumPy vectorization
    if side.lower() == "over":
        hits = int(np.sum(outcomes > line))
    else:
        hits = int(np.sum(outcomes < line))

    hit_rate = hits / n_sims

    # Distribution statistics using NumPy
    stats = _compute_distribution_stats(outcomes)

    return {
        "hit_rate": round(hit_rate, 4),
        "hit_count": hits,
        "miss_count": n_sims - hits,
        "simulations": n_sims,
        "line": line,
        "side": side,
        "input_mean": mean,
        "input_std_dev": std_dev,
        "distribution": distribution,
        **stats,
    }


def run_parlay_simulation(
    legs: List[Dict[str, Any]],
    n_sims: int = 10000,
    correlation_matrix: Optional[List[List[float]]] = None,
) -> Dict[str, Any]:
    """
    Monte Carlo simulation for a multi-leg parlay using NumPy.
    """
    n_legs = len(legs)
    if n_legs == 0:
        return {"error": "No legs provided"}
    if n_sims < 100:
        n_sims = 100
    if n_sims > 100000:
        n_sims = 100000

    # Generate correlated or independent outcomes using NumPy
    if correlation_matrix and len(correlation_matrix) == n_legs:
        outcomes_matrix = _generate_correlated_outcomes(legs, n_sims, correlation_matrix)
    else:
        outcomes_matrix = []
        for leg in legs:
            mean = leg.get("mean", 0)
            std = leg.get("std_dev", 1)
            dist = leg.get("distribution", "normal")

            if dist == "poisson" and mean > 0:
                sims = np.random.poisson(mean, n_sims).astype(float)
            else:
                sims = np.random.normal(mean, max(std, 0.01), n_sims)

            outcomes_matrix.append(sims)

    # Evaluate parlay hits using NumPy matrix operations for speed
    outcomes_array = np.array(outcomes_matrix)
    hit_mask = np.ones(n_sims, dtype=bool)
    leg_hits = []

    for i, leg in enumerate(legs):
        line = leg.get("line", 0)
        side = leg.get("side", "over").lower()
        
        if side == "over":
            leg_hit = outcomes_array[i] > line
        else:
            leg_hit = outcomes_array[i] < line
            
        leg_hits.append(int(np.sum(leg_hit)))
        hit_mask &= leg_hit

    parlay_hits = int(np.sum(hit_mask))
    parlay_hit_rate = parlay_hits / n_sims

    # Calculate combined odds and EV
    combined_decimal = 1.0
    for leg in legs:
        odds = leg.get("odds", -110)
        combined_decimal *= american_to_decimal(odds)

    parlay_ev = (parlay_hit_rate * (combined_decimal - 1)) - ((1 - parlay_hit_rate) * 1)

    # Individual leg results
    leg_results = []
    for i, leg in enumerate(legs):
        leg_rate = leg_hits[i] / n_sims
        implied = american_to_implied(leg.get("odds", -110))
        leg_results.append({
            "player_name": leg.get("player_name", f"Leg {i + 1}"),
            "stat_type": leg.get("stat_type", "unknown"),
            "line": leg.get("line", 0),
            "side": leg.get("side", "over"),
            "odds": leg.get("odds", -110),
            "simulated_hit_rate": round(leg_rate, 4),
            "implied_probability": round(implied, 4),
            "edge": round(leg_rate - implied, 4),
        })

    return {
        "parlay_hit_rate": round(parlay_hit_rate, 4),
        "parlay_hits": parlay_hits,
        "simulations": n_sims,
        "combined_decimal_odds": round(combined_decimal, 4),
        "parlay_ev": round(parlay_ev, 4),
        "num_legs": n_legs,
        "is_correlated": correlation_matrix is not None,
        "leg_results": leg_results,
    }


def simulate_bankroll(
    picks: List[Dict[str, Any]],
    kelly_fraction: float = 0.25,
    initial_bankroll: float = 1000.0,
    n_sims: int = 5000,
) -> Dict[str, Any]:
    """
    Simulate bankroll trajectory over a sequence of picks using NumPy.
    """
    if not picks:
        return {"error": "No picks provided"}
    if n_sims > 10000:
        n_sims = 10000

    # Pre-generate random outcomes for all simulations at once for speed
    # Shape: (n_picks, n_sims)
    random_outcomes = np.random.random((len(picks), n_sims))
    
    # We'll iterate through picks but vectorise across simulations
    bankrolls = np.full(n_sims, initial_bankroll)
    peaks = np.full(n_sims, initial_bankroll)
    max_dds = np.zeros(n_sims)
    ruined = np.zeros(n_sims, dtype=bool)
    ruin_threshold = initial_bankroll * 0.05

    for i, pick in enumerate(picks):
        win_prob = pick.get("win_probability", 0.5)
        odds = pick.get("odds", -110)
        
        # Kelly stake calculation (already vectorized in thought, but simpler to apply per pick)
        kelly = calculate_kelly_stake(win_prob, odds)
        stake_pct = min(max(kelly * kelly_fraction, 0), 0.25)
        
        # Only bet on non-ruined bankrolls
        active = ~ruined
        stakes = bankrolls[active] * stake_pct
        
        wins = random_outcomes[i, active] < win_prob
        payouts = stakes * (american_to_decimal(odds) - 1)
        
        # Update bankrolls
        bankrolls[active] += np.where(wins, payouts, -stakes)
        
        # Update ruin status
        ruined[active] = bankrolls[active] <= ruin_threshold
        
        # Update peaks and drawdowns
        peaks = np.maximum(peaks, bankrolls)
        current_dds = (peaks - bankrolls) / peaks
        max_dds = np.maximum(max_dds, current_dds)

    # Compute summary statistics using NumPy
    final_stats = _compute_distribution_stats(bankrolls)
    dd_stats = _compute_distribution_stats(max_dds)

    return {
        "initial_bankroll": initial_bankroll,
        "kelly_fraction": kelly_fraction,
        "num_picks": len(picks),
        "simulations": n_sims,
        "final_bankroll": {
            **final_stats,
            "profit_probability": round(float(np.sum(bankrolls > initial_bankroll) / n_sims), 4),
        },
        "max_drawdown": {
            "mean": dd_stats["mean"],
            "median": dd_stats["median"],
            "worst_case_90th": dd_stats["percentiles"]["90"],
        },
        "ruin_probability": round(float(np.sum(ruined) / n_sims), 4),
    }


def calculate_kelly_stake(win_prob: float, odds: float) -> float:
    """
    Calculate the Kelly criterion optimal stake fraction.
    """
    if win_prob <= 0 or win_prob >= 1:
        return 0.0

    b = american_to_decimal(odds) - 1  # Net decimal odds
    if b <= 0:
        return 0.0

    p = win_prob
    q = 1 - p

    kelly = (b * p - q) / b
    return round(float(max(kelly, 0)), 6)


# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _compute_distribution_stats(values) -> Dict[str, Any]:
    """Compute mean, median, std_dev, percentiles using NumPy."""
    arr = np.array(values, dtype=float)
    return {
        "mean": round(float(np.mean(arr)), 4),
        "median": round(float(np.median(arr)), 4),
        "std_dev": round(float(np.std(arr)), 4),
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "percentiles": {
            "10": round(float(np.percentile(arr, 10)), 4),
            "25": round(float(np.percentile(arr, 25)), 4),
            "50": round(float(np.percentile(arr, 50)), 4),
            "75": round(float(np.percentile(arr, 75)), 4),
            "90": round(float(np.percentile(arr, 90)), 4),
        },
    }


def _generate_correlated_outcomes(
    legs: List[Dict], n_sims: int, corr_matrix: List[List[float]]
) -> List:
    """Generate correlated normal outcomes using NumPy multivariate_normal."""
    n = len(legs)
    means = [leg.get("mean", 0) for leg in legs]
    stds = [max(leg.get("std_dev", 1), 0.01) for leg in legs]

    corr = np.array(corr_matrix)
    # Build covariance matrix from correlation + std devs
    cov = np.outer(stds, stds) * corr

    # Generate correlated samples
    samples = np.random.multivariate_normal(means, cov, n_sims)

    # Return as list of arrays (one per leg)
    return [samples[:, i] for i in range(n)]


# ─── Service Wrapper ──────────────────────────────────────────────────────────

class MonteCarloService:
    """Wrapper class for dependency injection compatibility."""

    def simulate_prop(self, mean, std_dev, line, side="over", n_sims=10000, distribution="normal"):
        return run_prop_simulation(mean, std_dev, line, side, n_sims, distribution)

    def simulate_parlay(self, legs, n_sims=10000, correlation_matrix=None):
        return run_parlay_simulation(legs, n_sims, correlation_matrix)

    def simulate_bankroll(self, picks, kelly_fraction=0.25, initial_bankroll=1000.0, n_sims=5000):
        return simulate_bankroll(picks, kelly_fraction, initial_bankroll, n_sims)

    def kelly(self, win_prob, odds):
        return calculate_kelly_stake(win_prob, odds)


monte_carlo_service = MonteCarloService()
simulate_prop = monte_carlo_service.simulate_prop
simulate_parlay = monte_carlo_service.simulate_parlay
simulate_bankroll = monte_carlo_service.simulate_bankroll
kelly = monte_carlo_service.kelly
american_to_decimal = american_to_decimal
american_to_implied = american_to_implied
run_prop_simulation = run_prop_simulation
run_parlay_simulation = run_parlay_simulation
calculate_kelly_stake = calculate_kelly_stake
