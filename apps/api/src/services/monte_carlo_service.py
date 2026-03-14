"""
Monte Carlo Simulation Service for Sports Betting Analytics

Provides statistically rigorous simulation of:
- Individual prop outcomes (hit probability, percentile distributions)
- Multi-leg parlay outcomes (combined probability, correlated legs)
- Bankroll trajectory over N picks (drawdown, ruin probability)
- Kelly criterion stake sizing

Uses stdlib random for Railway compatibility; numpy optional for speed.
"""
import math
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Try numpy for performance; fall back to stdlib
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.info("numpy not available, using stdlib random for Monte Carlo sims")


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
    Monte Carlo simulation for a single player prop.

    Generates n_sims random outcomes from the player's statistical
    distribution, then checks how many clear the line.

    Args:
        mean: Expected stat value (e.g., 25.3 points)
        std_dev: Standard deviation of the stat
        line: The prop line (e.g., 24.5)
        side: "over" or "under"
        n_sims: Number of simulations to run
        distribution: "normal" or "poisson" (for counting stats like TDs)

    Returns:
        Dict with hit_rate, percentiles, distribution_stats, raw summary
    """
    if n_sims < 100:
        n_sims = 100
    if n_sims > 100000:
        n_sims = 100000

    # Generate simulated outcomes
    if HAS_NUMPY:
        if distribution == "poisson" and mean > 0:
            outcomes = np.random.poisson(mean, n_sims).astype(float)
        else:
            outcomes = np.random.normal(mean, max(std_dev, 0.01), n_sims)
    else:
        if distribution == "poisson" and mean > 0:
            outcomes = [_poisson_sample(mean) for _ in range(n_sims)]
        else:
            outcomes = [random.gauss(mean, max(std_dev, 0.01)) for _ in range(n_sims)]

    # Count hits
    if side.lower() == "over":
        hits = sum(1 for o in outcomes if o > line)
    else:
        hits = sum(1 for o in outcomes if o < line)

    hit_rate = hits / n_sims

    # Distribution statistics
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
    Monte Carlo simulation for a multi-leg parlay.

    Each leg needs: mean, std_dev, line, side, odds.
    Optionally accepts a correlation matrix for correlated legs
    (e.g., same-game props).

    Args:
        legs: List of dicts, each with mean, std_dev, line, side, odds
        n_sims: Number of simulations
        correlation_matrix: NxN correlation matrix (None = independent)

    Returns:
        Dict with combined hit rate, individual leg rates, EV, risk metrics
    """
    n_legs = len(legs)
    if n_legs == 0:
        return {"error": "No legs provided"}
    if n_sims < 100:
        n_sims = 100
    if n_sims > 100000:
        n_sims = 100000

    # Generate correlated or independent outcomes
    if correlation_matrix and HAS_NUMPY and len(correlation_matrix) == n_legs:
        # Correlated simulation using Cholesky decomposition
        outcomes_matrix = _generate_correlated_outcomes(legs, n_sims, correlation_matrix)
    else:
        # Independent simulation
        outcomes_matrix = []
        for leg in legs:
            mean = leg.get("mean", 0)
            std = leg.get("std_dev", 1)
            dist = leg.get("distribution", "normal")

            if HAS_NUMPY:
                if dist == "poisson" and mean > 0:
                    sims = np.random.poisson(mean, n_sims).astype(float)
                else:
                    sims = np.random.normal(mean, max(std, 0.01), n_sims)
            else:
                if dist == "poisson" and mean > 0:
                    sims = [_poisson_sample(mean) for _ in range(n_sims)]
                else:
                    sims = [random.gauss(mean, max(std, 0.01)) for _ in range(n_sims)]

            outcomes_matrix.append(sims)

    # Evaluate each simulation
    parlay_hits = 0
    leg_hits = [0] * n_legs

    for sim_idx in range(n_sims):
        all_hit = True
        for leg_idx, leg in enumerate(legs):
            outcome = outcomes_matrix[leg_idx][sim_idx] if HAS_NUMPY else outcomes_matrix[leg_idx][sim_idx]
            line = leg.get("line", 0)
            side = leg.get("side", "over").lower()

            hit = (outcome > line) if side == "over" else (outcome < line)
            if hit:
                leg_hits[leg_idx] += 1
            else:
                all_hit = False

        if all_hit:
            parlay_hits += 1

    # Calculate combined odds and EV
    combined_decimal = 1.0
    for leg in legs:
        odds = leg.get("odds", -110)
        combined_decimal *= american_to_decimal(odds)

    parlay_hit_rate = parlay_hits / n_sims
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
    Simulate bankroll trajectory over a sequence of picks.

    Each pick needs: win_probability, odds (American).
    Uses fractional Kelly for stake sizing.

    Args:
        picks: List of dicts with win_probability and odds
        kelly_fraction: Fraction of full Kelly to use (0.25 = quarter Kelly)
        initial_bankroll: Starting bankroll
        n_sims: Number of full-trajectory simulations

    Returns:
        Dict with final bankroll stats, max drawdown, ruin probability
    """
    if not picks:
        return {"error": "No picks provided"}
    if n_sims > 10000:
        n_sims = 10000

    final_bankrolls = []
    max_drawdowns = []
    ruin_count = 0
    ruin_threshold = initial_bankroll * 0.05  # 5% of initial = "ruin"

    for _ in range(n_sims):
        bankroll = initial_bankroll
        peak = bankroll
        max_dd = 0.0

        for pick in picks:
            if bankroll <= ruin_threshold:
                ruin_count += 1
                break

            win_prob = pick.get("win_probability", 0.5)
            odds = pick.get("odds", -110)

            # Kelly stake
            kelly = calculate_kelly_stake(win_prob, odds)
            stake_pct = max(kelly * kelly_fraction, 0)
            stake_pct = min(stake_pct, 0.25)  # Cap at 25% of bankroll
            stake = bankroll * stake_pct

            # Simulate outcome
            if random.random() < win_prob:
                payout = stake * (american_to_decimal(odds) - 1)
                bankroll += payout
            else:
                bankroll -= stake

            # Track drawdown
            if bankroll > peak:
                peak = bankroll
            dd = (peak - bankroll) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        final_bankrolls.append(bankroll)
        max_drawdowns.append(max_dd)

    # Compute summary statistics
    final_stats = _compute_distribution_stats(final_bankrolls)
    dd_stats = _compute_distribution_stats(max_drawdowns)

    return {
        "initial_bankroll": initial_bankroll,
        "kelly_fraction": kelly_fraction,
        "num_picks": len(picks),
        "simulations": n_sims,
        "final_bankroll": {
            **final_stats,
            "profit_probability": round(
                sum(1 for b in final_bankrolls if b > initial_bankroll) / n_sims, 4
            ),
        },
        "max_drawdown": {
            "mean": dd_stats["mean"],
            "median": dd_stats["median"],
            "worst_case_90th": dd_stats["percentiles"]["90"],
        },
        "ruin_probability": round(ruin_count / n_sims, 4),
    }


def calculate_kelly_stake(win_prob: float, odds: float) -> float:
    """
    Calculate the Kelly criterion optimal stake fraction.

    Kelly% = (bp - q) / b
    where b = decimal odds - 1, p = win probability, q = 1 - p

    Args:
        win_prob: Probability of winning (0-1)
        odds: American odds

    Returns:
        Optimal stake as a fraction of bankroll (can be negative = no bet)
    """
    if win_prob <= 0 or win_prob >= 1:
        return 0.0

    b = american_to_decimal(odds) - 1  # Net decimal odds
    if b <= 0:
        return 0.0

    p = win_prob
    q = 1 - p

    kelly = (b * p - q) / b
    return round(max(kelly, 0), 6)  # Floor at 0 (don't bet if negative edge)


# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _compute_distribution_stats(values) -> Dict[str, Any]:
    """Compute mean, median, std_dev, percentiles from a list of values."""
    if HAS_NUMPY:
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
    else:
        sorted_v = sorted(values)
        n = len(sorted_v)
        if n == 0:
            return {"mean": 0, "median": 0, "std_dev": 0, "min": 0, "max": 0, "percentiles": {}}

        mean_val = sum(sorted_v) / n
        variance = sum((x - mean_val) ** 2 for x in sorted_v) / n
        std_dev = math.sqrt(variance)

        def percentile(pct):
            idx = (pct / 100) * (n - 1)
            lower = int(math.floor(idx))
            upper = min(lower + 1, n - 1)
            frac = idx - lower
            return sorted_v[lower] * (1 - frac) + sorted_v[upper] * frac

        return {
            "mean": round(mean_val, 4),
            "median": round(percentile(50), 4),
            "std_dev": round(std_dev, 4),
            "min": round(sorted_v[0], 4),
            "max": round(sorted_v[-1], 4),
            "percentiles": {
                "10": round(percentile(10), 4),
                "25": round(percentile(25), 4),
                "50": round(percentile(50), 4),
                "75": round(percentile(75), 4),
                "90": round(percentile(90), 4),
            },
        }


def _generate_correlated_outcomes(
    legs: List[Dict], n_sims: int, corr_matrix: List[List[float]]
) -> List:
    """Generate correlated normal outcomes using Cholesky decomposition."""
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


def _poisson_sample(lam: float) -> float:
    """Stdlib Poisson sampling using inverse transform."""
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= random.random()
        if p < L:
            break
    return float(k - 1)


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
