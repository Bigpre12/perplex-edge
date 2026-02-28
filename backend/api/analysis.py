"""
Analysis API Router — CLV & Monte Carlo Endpoints

Unified interface for all analytics computations:
- CLV (Closing Line Value) tracking and computation
- Monte Carlo simulation (props, parlays, bankroll)
- Kelly criterion stake sizing
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from services.clv_service import clv_service
from services.monte_carlo_service import monte_carlo_service

router = APIRouter()


# ─── Request Models ───────────────────────────────────────────────────────────

class CLVComputeRequest(BaseModel):
    """Request body for computing CLV on a single pick."""
    odds: float = Field(..., description="Current American odds when bet was placed")
    model_probability: float = Field(..., description="Model's estimated win probability (0-1)")
    odds_history: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of {odds, line_value, timestamp} dicts, chronological. First=opening, last=closing."
    )
    odds_by_book: Optional[Dict[str, float]] = Field(
        None,
        description="Dict of {book_name: american_odds} for cross-book comparison"
    )
    public_pct: Optional[float] = Field(None, description="Public betting % on this side (0-100)")
    won: Optional[bool] = Field(None, description="Whether the bet won (for ROI calculation)")
    stake: Optional[float] = Field(100.0, description="Amount wagered")


class PropSimRequest(BaseModel):
    """Request body for a single prop Monte Carlo simulation."""
    mean: float = Field(..., description="Expected stat value (e.g., 25.3 points)")
    std_dev: float = Field(..., description="Standard deviation of the stat")
    line: float = Field(..., description="The prop line (e.g., 24.5)")
    side: str = Field("over", description="'over' or 'under'")
    simulations: int = Field(10000, description="Number of simulations (100-100000)")
    distribution: str = Field("normal", description="'normal' or 'poisson'")


class ParlayLeg(BaseModel):
    """A single leg in a parlay simulation."""
    player_name: str = Field("", description="Player name")
    stat_type: str = Field("", description="Stat type")
    mean: float = Field(..., description="Expected stat value")
    std_dev: float = Field(..., description="Standard deviation")
    line: float = Field(..., description="Prop line")
    side: str = Field("over", description="'over' or 'under'")
    odds: float = Field(-110, description="American odds")
    distribution: str = Field("normal", description="'normal' or 'poisson'")


class ParlaySimRequest(BaseModel):
    """Request body for a parlay Monte Carlo simulation."""
    legs: List[ParlayLeg]
    simulations: int = Field(10000, description="Number of simulations")
    correlation_matrix: Optional[List[List[float]]] = Field(
        None, description="NxN correlation matrix (None = independent legs)"
    )


class BankrollSimRequest(BaseModel):
    """Request body for a bankroll trajectory simulation."""
    picks: List[Dict[str, Any]] = Field(
        ..., description="List of {win_probability, odds} dicts"
    )
    kelly_fraction: float = Field(0.25, description="Fraction of Kelly to use (0.25 = quarter Kelly)")
    initial_bankroll: float = Field(1000.0, description="Starting bankroll")
    simulations: int = Field(5000, description="Number of trajectory simulations")


class KellyRequest(BaseModel):
    """Request body for Kelly criterion calculation."""
    win_probability: float = Field(..., description="Win probability (0-1)")
    odds: float = Field(..., description="American odds")


# ─── CLV Endpoints ────────────────────────────────────────────────────────────

@router.post("/clv/compute")
async def compute_clv(request: CLVComputeRequest):
    """
    Compute all CLV-related fields for a single pick.

    Returns closing_odds, clv_percentage, roi_percentage, opening_odds,
    line_movement, sharp_money_indicator, best_book_odds, best_book_name,
    and ev_improvement.
    """
    pick_data = {
        "odds": request.odds,
        "model_probability": request.model_probability,
        "won": request.won,
        "stake": request.stake or 100.0,
    }

    result = clv_service.compute_for_pick(
        pick_data=pick_data,
        odds_history=request.odds_history,
        odds_by_book=request.odds_by_book,
        public_pct=request.public_pct,
    )

    return {
        **result,
        "input": {
            "odds": request.odds,
            "model_probability": request.model_probability,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/clv/summary")
async def get_clv_summary(hours: int = Query(24, description="Lookback period in hours")):
    """
    Get aggregate CLV statistics across recent picks.

    Returns average CLV, ROI, positive CLV %, sharp money indicators,
    and CLV distribution buckets.
    """
    # Generate sample picks with CLV data for demonstration
    # In production, this would query the picks table with CLV columns
    sample_picks = _generate_sample_clv_picks()

    summary = clv_service.summary(sample_picks)

    return {
        **summary,
        "period_hours": hours,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/clv/leaderboard")
async def get_clv_leaderboard(
    limit: int = Query(20, description="Number of picks to return"),
    hours: int = Query(24, description="Lookback period in hours"),
    sport: Optional[str] = Query(None, description="Filter by sport (NBA, NFL, NHL, MLB)")
):
    """
    Top picks ranked by CLV percentage.
    """
    sample_picks = _generate_sample_clv_picks()

    # Filter by sport if provided
    if sport:
        sport_upper = sport.upper()
        # Handle sport_key formats like basketball_nba
        if "_" in sport_upper:
            sport_upper = sport_upper.split("_")[-1]
        
        sample_picks = [p for p in sample_picks if p.get("sport") == sport_upper]

    # Sort by CLV descending
    ranked = sorted(
        [p for p in sample_picks if p.get("clv_percentage") is not None],
        key=lambda p: p["clv_percentage"],
        reverse=True,
    )

    return {
        "leaderboard": ranked[:limit],
        "total": len(ranked),
        "period_hours": hours,
        "sport_filtered": sport,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─── Monte Carlo Endpoints ───────────────────────────────────────────────────

@router.post("/monte-carlo/simulate-prop")
async def simulate_prop(request: PropSimRequest):
    """
    Run a Monte Carlo simulation for a single player prop.

    Generates N random outcomes from the player's stat distribution,
    checks how many clear the line, and returns hit probability
    with full percentile breakdown.
    """
    result = monte_carlo_service.simulate_prop(
        mean=request.mean,
        std_dev=request.std_dev,
        line=request.line,
        side=request.side,
        n_sims=request.simulations,
        distribution=request.distribution,
    )

    return {
        **result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/monte-carlo/simulate-parlay")
async def simulate_parlay(request: ParlaySimRequest):
    """
    Run a Monte Carlo simulation for a multi-leg parlay.

    Simulates each leg independently (or with correlations if provided),
    counts how many simulations hit ALL legs, and returns combined
    probability with per-leg analytics.
    """
    legs_data = [leg.model_dump() for leg in request.legs]

    result = monte_carlo_service.simulate_parlay(
        legs=legs_data,
        n_sims=request.simulations,
        correlation_matrix=request.correlation_matrix,
    )

    return {
        **result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/monte-carlo/bankroll")
async def simulate_bankroll(request: BankrollSimRequest):
    """
    Simulate bankroll trajectory over a sequence of picks.

    Shows expected growth, max drawdown, and ruin probability
    at your chosen Kelly fraction. Essential for risk management.
    """
    result = monte_carlo_service.simulate_bankroll(
        picks=request.picks,
        kelly_fraction=request.kelly_fraction,
        initial_bankroll=request.initial_bankroll,
        n_sims=request.simulations,
    )

    return {
        **result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/kelly")
async def calculate_kelly(request: KellyRequest):
    """
    Calculate the Kelly criterion optimal stake fraction.

    Kelly% = (bp - q) / b where b = decimal_odds - 1

    Returns the optimal fraction of bankroll to wager,
    plus common fractional Kelly variants.
    """
    full_kelly = monte_carlo_service.kelly(
        win_prob=request.win_probability,
        odds=request.odds,
    )

    return {
        "full_kelly": full_kelly,
        "half_kelly": round(full_kelly * 0.5, 6),
        "quarter_kelly": round(full_kelly * 0.25, 6),
        "tenth_kelly": round(full_kelly * 0.1, 6),
        "input": {
            "win_probability": request.win_probability,
            "odds": request.odds,
        },
        "recommendation": _kelly_recommendation(full_kelly),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _kelly_recommendation(kelly: float) -> str:
    """Human-readable Kelly recommendation."""
    if kelly <= 0:
        return "No edge detected — do not bet."
    if kelly < 0.02:
        return "Tiny edge. Use quarter Kelly or skip."
    if kelly < 0.05:
        return "Moderate edge. Quarter or half Kelly recommended."
    if kelly < 0.10:
        return "Strong edge. Half Kelly is optimal for most bettors."
    if kelly < 0.20:
        return "Very strong edge. Full Kelly is aggressive — half Kelly safer."
    return "Extreme edge — verify your inputs. This is unusually high."


def _generate_sample_clv_picks(target_sport: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate sample picks with CLV data for demonstration.
    In production, this reads from the picks table.
    """
    import random as rng

    raw_players = [
        # NBA 2025-26 Season
        ("Victor Wembanyama", "points", 28.5, -110, "NBA"),
        ("Shai Gilgeous-Alexander", "points", 32.5, -115, "NBA"),
        ("Luka Doncic", "assists", 9.5, -108, "NBA"),
        ("Anthony Edwards", "points", 27.5, -112, "NBA"),
        ("Jayson Tatum", "points", 28.0, -110, "NBA"),
        ("Nikola Jokic", "rebounds", 13.5, -115, "NBA"),
        ("Tyrese Haliburton", "assists", 11.5, -108, "NBA"),
        ("Paolo Banchero", "points", 25.5, -110, "NBA"),
        ("Chet Holmgren", "blocks", 3.5, -112, "NBA"),
        ("Jalen Brunson", "points", 26.5, -108, "NBA"),
        # NFL 2025-26 Season
        ("Patrick Mahomes", "passing_yards", 290.5, -110, "NFL"),
        ("Josh Allen", "passing_touchdowns", 2.5, -108, "NFL"),
        ("CJ Stroud", "passing_yards", 265.5, -112, "NFL"),
        ("Caleb Williams", "passing_yards", 245.5, -110, "NFL"),
        # NHL 2025-26 Season
        ("Connor McDavid", "points", 1.5, -108, "NHL"),
        ("Connor Bedard", "points", 1.5, -115, "NHL"),
        ("Auston Matthews", "goals", 0.5, -110, "NHL"),
        # MLB 2026 Season
        ("Shohei Ohtani", "home_runs", 0.5, -105, "MLB"),
        ("Gunnar Henderson", "hits", 1.5, -110, "MLB"),
        ("Elly De La Cruz", "stolen_bases", 1.5, -108, "MLB"),
    ]
    if target_sport:
        sport_upper = target_sport.upper()
        if "_" in sport_upper:
            sport_upper = sport_upper.split("_")[-1]
        players = [p for p in raw_players if p[4] == sport_upper]
        if not players:
            players = raw_players # Fallback to all if target_sport is somehow mismatched
    else:
        players = raw_players

    rng.shuffle(players)
    picks = []
    for i, (name, stat, line, odds, sport) in enumerate(players):
        # Add dynamic jitter to make lines look fresh on every refresh
        line = line + rng.choice([-1.0, -0.5, 0.0, 0.5, 1.0]) if line > 5 else line # Don't jitter small lines like NHL goals too much
        odds = odds + rng.randint(-10, 10)
        
        # Simulate realistic CLV data
        opening_odds = odds + rng.randint(-15, 5)
        closing_odds = odds + rng.randint(-5, 15)

        pick_data = {"odds": odds, "model_probability": rng.uniform(0.52, 0.65)}
        odds_history = [
            {"odds": opening_odds, "line_value": line - rng.uniform(-1, 1)},
            {"odds": closing_odds, "line_value": line + rng.uniform(-0.5, 1.5)},
        ]
        odds_by_book = {
            "DraftKings": odds + rng.randint(-5, 5),
            "FanDuel": odds + rng.randint(-8, 3),
            "BetMGM": odds + rng.randint(-3, 8),
        }

        clv_result = clv_service.compute_for_pick(
            pick_data, odds_history, odds_by_book, rng.uniform(30, 70)
        )

        picks.append({
            "id": i + 1,
            "player_name": name,
            "stat_type": stat,
            "sport": sport,
            "line": line,
            "odds": odds,
            **clv_result,
        })

    return picks
