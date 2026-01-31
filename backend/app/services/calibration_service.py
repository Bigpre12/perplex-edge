"""
Calibration Service for tracking model accuracy and ROI.

Provides:
- CLV (Closing Line Value) calculation
- Profit/Loss calculation
- Brier score calculation
- Bucketed calibration metrics (predicted vs actual hit rates)
- Reliability plot data
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Sport, ModelPick, PickResult, CalibrationMetrics

logger = logging.getLogger(__name__)


# =============================================================================
# Probability Buckets
# =============================================================================

PROBABILITY_BUCKETS = [
    ("50-55", 0.50, 0.55),
    ("55-60", 0.55, 0.60),
    ("60-65", 0.60, 0.65),
    ("65-70", 0.65, 0.70),
    ("70-75", 0.70, 0.75),
    ("75-80", 0.75, 0.80),
    ("80-85", 0.80, 0.85),
    ("85-90", 0.85, 0.90),
    ("90+", 0.90, 1.00),
]

# Sport key to league code mapping
SPORT_KEY_TO_LEAGUE = {
    "basketball_nba": "NBA",
    "basketball_ncaab": "NCAAB",
    "americanfootball_nfl": "NFL",
}


# =============================================================================
# Core Calculation Functions
# =============================================================================

def calculate_clv(opening_odds: int, closing_odds: int) -> float:
    """
    Calculate Closing Line Value (CLV) in cents.
    
    CLV measures how much value you captured by betting before the line moved.
    Positive CLV = you beat the closing line (good)
    Negative CLV = line moved in your favor after you bet (bad)
    
    Args:
        opening_odds: American odds when you placed the bet
        closing_odds: American odds at game start
    
    Returns:
        CLV in cents (e.g., 5.0 = 5 cents of value captured)
    
    Examples:
        opening=-110, closing=-115 -> +5 cents (beat the close)
        opening=-110, closing=-105 -> -5 cents (got worse line)
    """
    if opening_odds == closing_odds:
        return 0.0
    
    # Convert to implied probabilities
    def odds_to_prob(odds: int) -> float:
        if odds < 0:
            return abs(odds) / (abs(odds) + 100)
        else:
            return 100 / (odds + 100)
    
    opening_prob = odds_to_prob(opening_odds)
    closing_prob = odds_to_prob(closing_odds)
    
    # CLV = (closing_prob - opening_prob) * 100 in percentage points
    # Convert to cents (1 cent = 0.01 probability difference at standard juice)
    clv = (closing_prob - opening_prob) * 100
    
    return round(clv, 2)


def calculate_profit_loss(odds: int, hit: bool, unit: float = 100.0) -> float:
    """
    Calculate profit/loss for a bet.
    
    Args:
        odds: American odds of the bet
        hit: Whether the bet won
        unit: Bet size (default $100)
    
    Returns:
        Profit (positive) or loss (negative)
    
    Examples:
        odds=-110, hit=True, unit=100 -> +90.91 (win $90.91 profit)
        odds=-110, hit=False, unit=100 -> -100.00 (lose $100)
        odds=+150, hit=True, unit=100 -> +150.00 (win $150 profit)
        odds=+150, hit=False, unit=100 -> -100.00 (lose $100)
    """
    if not hit:
        return -unit
    
    if odds < 0:
        # Favorite: profit = unit * (100 / abs(odds))
        profit = unit * (100 / abs(odds))
    else:
        # Underdog: profit = unit * (odds / 100)
        profit = unit * (odds / 100)
    
    return round(profit, 2)


def calculate_brier_score(predictions: list[float], outcomes: list[bool]) -> float:
    """
    Calculate Brier score for a set of predictions.
    
    Brier score = mean((predicted - actual)^2)
    - 0 = perfect calibration
    - 0.25 = random guessing at 50%
    - 1 = perfectly wrong
    
    Args:
        predictions: List of predicted probabilities (0-1)
        outcomes: List of actual outcomes (True = hit, False = miss)
    
    Returns:
        Brier score (lower is better)
    """
    if not predictions or len(predictions) != len(outcomes):
        return 0.0
    
    total = 0.0
    for pred, outcome in zip(predictions, outcomes):
        actual = 1.0 if outcome else 0.0
        total += (pred - actual) ** 2
    
    return round(total / len(predictions), 4)


def get_probability_bucket(prob: float) -> tuple[str, float, float]:
    """
    Get the bucket for a given probability.
    
    Args:
        prob: Probability between 0 and 1
    
    Returns:
        Tuple of (bucket_name, bucket_min, bucket_max)
    """
    for bucket_name, bucket_min, bucket_max in PROBABILITY_BUCKETS:
        if bucket_min <= prob < bucket_max:
            return (bucket_name, bucket_min, bucket_max)
    
    # Edge case: prob == 1.0
    if prob >= 0.90:
        return ("90+", 0.90, 1.00)
    
    # Below 50% (unlikely for +EV picks)
    return ("50-55", 0.50, 0.55)


# =============================================================================
# Database Operations
# =============================================================================

async def compute_calibration_metrics(
    db: AsyncSession,
    sport_key: str,
    start_date: date,
    end_date: date,
) -> list[dict[str, Any]]:
    """
    Compute calibration metrics for a sport over a date range.
    
    Groups settled picks by probability bucket and calculates:
    - Predicted vs actual hit rate
    - Brier score
    - ROI
    - Average CLV
    
    Args:
        db: Database session
        sport_key: Sport to analyze
        start_date: Start of date range
        end_date: End of date range
    
    Returns:
        List of calibration metric dictionaries per bucket
    """
    # Get sport
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        return []
    
    sport_result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = sport_result.scalar_one_or_none()
    if not sport:
        return []
    
    # Get all settled picks in date range (timezone-naive to match DB column)
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    result = await db.execute(
        select(ModelPick, PickResult)
        .join(PickResult, ModelPick.id == PickResult.pick_id)
        .where(
            and_(
                ModelPick.sport_id == sport.id,
                PickResult.settled_at >= start_dt,
                PickResult.settled_at <= end_dt,
            )
        )
    )
    
    picks_with_results = result.all()
    
    if not picks_with_results:
        return []
    
    # Group by bucket
    buckets: dict[str, list[tuple[ModelPick, PickResult]]] = {
        b[0]: [] for b in PROBABILITY_BUCKETS
    }
    
    for pick, pick_result in picks_with_results:
        bucket_name, _, _ = get_probability_bucket(pick.model_probability)
        buckets[bucket_name].append((pick, pick_result))
    
    # Calculate metrics per bucket
    metrics = []
    for bucket_name, bucket_min, bucket_max in PROBABILITY_BUCKETS:
        bucket_picks = buckets[bucket_name]
        
        if not bucket_picks:
            continue
        
        predictions = [p.model_probability for p, _ in bucket_picks]
        outcomes = [r.hit for _, r in bucket_picks]
        profit_losses = [r.profit_loss or 0.0 for _, r in bucket_picks]
        clvs = [r.clv_cents for _, r in bucket_picks if r.clv_cents is not None]
        
        sample_size = len(bucket_picks)
        predicted_prob = sum(predictions) / sample_size
        actual_hit_rate = sum(outcomes) / sample_size
        brier = calculate_brier_score(predictions, outcomes)
        
        total_wagered = sample_size * 100.0  # $100 per pick
        total_profit = sum(profit_losses)
        roi_percent = (total_profit / total_wagered) * 100 if total_wagered > 0 else 0.0
        avg_clv = sum(clvs) / len(clvs) if clvs else None
        
        metrics.append({
            "probability_bucket": bucket_name,
            "bucket_min": bucket_min,
            "bucket_max": bucket_max,
            "predicted_prob": round(predicted_prob, 4),
            "actual_hit_rate": round(actual_hit_rate, 4),
            "sample_size": sample_size,
            "brier_score": brier,
            "total_wagered": total_wagered,
            "total_profit": round(total_profit, 2),
            "roi_percent": round(roi_percent, 2),
            "avg_clv_cents": round(avg_clv, 2) if avg_clv else None,
        })
    
    return metrics


async def store_calibration_metrics(
    db: AsyncSession,
    sport_key: str,
    metrics_date: date,
    metrics: list[dict[str, Any]],
) -> int:
    """
    Store calibration metrics in the database.
    
    Args:
        db: Database session
        sport_key: Sport key
        metrics_date: Date for these metrics
        metrics: List of metric dictionaries from compute_calibration_metrics
    
    Returns:
        Number of records stored
    """
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        return 0
    
    sport_result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = sport_result.scalar_one_or_none()
    if not sport:
        return 0
    
    stored = 0
    for m in metrics:
        cal = CalibrationMetrics(
            date=metrics_date,
            sport_id=sport.id,
            probability_bucket=m["probability_bucket"],
            bucket_min=m["bucket_min"],
            bucket_max=m["bucket_max"],
            predicted_prob=m["predicted_prob"],
            actual_hit_rate=m["actual_hit_rate"],
            sample_size=m["sample_size"],
            brier_score=m["brier_score"],
            total_wagered=m["total_wagered"],
            total_profit=m["total_profit"],
            roi_percent=m["roi_percent"],
            avg_clv_cents=m.get("avg_clv_cents"),
        )
        db.add(cal)
        stored += 1
    
    await db.commit()
    return stored


async def get_reliability_data(
    db: AsyncSession,
    sport_key: str,
    days: int = 30,
) -> dict[str, Any]:
    """
    Get data for a reliability plot (calibration curve).
    
    A reliability plot shows predicted probability vs actual hit rate.
    Perfect calibration = diagonal line from (0,0) to (1,1).
    
    Args:
        db: Database session
        sport_key: Sport to analyze
        days: Number of days to look back
    
    Returns:
        Dictionary with plot data and summary statistics
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    metrics = await compute_calibration_metrics(db, sport_key, start_date, end_date)
    
    if not metrics:
        return {
            "sport": sport_key,
            "days": days,
            "buckets": [],
            "overall_brier": None,
            "calibration_error": None,
        }
    
    # Calculate overall metrics
    total_predictions = []
    total_outcomes = []
    
    # Get all picks for overall Brier score
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    sport_result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = sport_result.scalar_one_or_none()
    
    if sport:
        # Timezone-naive to match DB column
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        result = await db.execute(
            select(ModelPick.model_probability, PickResult.hit)
            .join(PickResult, ModelPick.id == PickResult.pick_id)
            .where(
                and_(
                    ModelPick.sport_id == sport.id,
                    PickResult.settled_at >= start_dt,
                    PickResult.settled_at <= end_dt,
                )
            )
        )
        
        for prob, hit in result.all():
            total_predictions.append(prob)
            total_outcomes.append(hit)
    
    overall_brier = calculate_brier_score(total_predictions, total_outcomes) if total_predictions else None
    
    # Expected Calibration Error (ECE) = weighted average of |predicted - actual| per bucket
    ece = 0.0
    total_samples = sum(m["sample_size"] for m in metrics)
    for m in metrics:
        weight = m["sample_size"] / total_samples
        ece += weight * abs(m["predicted_prob"] - m["actual_hit_rate"])
    
    return {
        "sport": sport_key,
        "days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_picks": total_samples,
        "buckets": metrics,
        "overall_brier": overall_brier,
        "calibration_error": round(ece, 4),
    }


async def get_roi_by_confidence(
    db: AsyncSession,
    sport_key: str,
    days: int = 30,
) -> dict[str, Any]:
    """
    Get ROI breakdown by confidence bucket.
    
    Args:
        db: Database session
        sport_key: Sport to analyze
        days: Number of days to look back
    
    Returns:
        ROI data per confidence bucket
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    metrics = await compute_calibration_metrics(db, sport_key, start_date, end_date)
    
    # Calculate overall ROI
    total_wagered = sum(m["total_wagered"] for m in metrics)
    total_profit = sum(m["total_profit"] for m in metrics)
    overall_roi = (total_profit / total_wagered) * 100 if total_wagered > 0 else 0.0
    
    return {
        "sport": sport_key,
        "days": days,
        "total_wagered": total_wagered,
        "total_profit": round(total_profit, 2),
        "overall_roi_percent": round(overall_roi, 2),
        "by_bucket": [
            {
                "bucket": m["probability_bucket"],
                "sample_size": m["sample_size"],
                "wagered": m["total_wagered"],
                "profit": m["total_profit"],
                "roi_percent": m["roi_percent"],
            }
            for m in metrics
        ],
    }


async def get_clv_analysis(
    db: AsyncSession,
    sport_key: str,
    days: int = 30,
) -> dict[str, Any]:
    """
    Get CLV analysis and distribution.
    
    Args:
        db: Database session
        sport_key: Sport to analyze
        days: Number of days to look back
    
    Returns:
        CLV statistics and distribution
    """
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        return {"error": f"Unknown sport: {sport_key}"}
    
    sport_result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = sport_result.scalar_one_or_none()
    
    if not sport:
        return {"error": f"Sport not found: {sport_key}"}
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    # Timezone-naive to match DB column
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    # Get all CLV values
    result = await db.execute(
        select(PickResult.clv_cents, PickResult.hit)
        .join(ModelPick, PickResult.pick_id == ModelPick.id)
        .where(
            and_(
                ModelPick.sport_id == sport.id,
                PickResult.settled_at >= start_dt,
                PickResult.settled_at <= end_dt,
                PickResult.clv_cents.isnot(None),
            )
        )
    )
    
    clv_data = result.all()
    
    if not clv_data:
        return {
            "sport": sport_key,
            "days": days,
            "total_picks_with_clv": 0,
            "avg_clv": None,
            "positive_clv_rate": None,
        }
    
    clvs = [row[0] for row in clv_data]
    positive_clv = sum(1 for c in clvs if c > 0)
    
    # CLV by outcome
    clv_on_wins = [row[0] for row in clv_data if row[1]]
    clv_on_losses = [row[0] for row in clv_data if not row[1]]
    
    return {
        "sport": sport_key,
        "days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_picks_with_clv": len(clvs),
        "avg_clv_cents": round(sum(clvs) / len(clvs), 2),
        "positive_clv_rate": round(positive_clv / len(clvs), 4),
        "clv_on_wins": round(sum(clv_on_wins) / len(clv_on_wins), 2) if clv_on_wins else None,
        "clv_on_losses": round(sum(clv_on_losses) / len(clv_on_losses), 2) if clv_on_losses else None,
        "distribution": {
            "min": round(min(clvs), 2),
            "max": round(max(clvs), 2),
            "median": round(sorted(clvs)[len(clvs) // 2], 2),
        },
    }
