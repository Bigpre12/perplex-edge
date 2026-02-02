"""Backtest service for simulating historical strategy performance."""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PickResult, ModelPick, Market, Game, Sport

logger = logging.getLogger(__name__)


async def run_backtest(
    db: AsyncSession,
    sport_id: Optional[int] = None,
    stat_type: Optional[str] = None,
    side: Optional[str] = None,
    min_ev: float = 0.0,
    min_confidence: float = 0.0,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    days_back: int = 30,
) -> dict:
    """
    Run a backtest simulation on historical pick data.
    
    Filters PickResult records by the given criteria and calculates:
    - Win/loss record
    - Flat stake ROI
    - Kelly-weighted ROI
    - Hit rate by confidence bucket
    
    Args:
        db: Database session
        sport_id: Optional sport filter
        stat_type: Optional stat type filter (PTS, AST, REB, etc.)
        side: Optional side filter (over/under)
        min_ev: Minimum EV threshold (0.03 = 3%)
        min_confidence: Minimum confidence threshold (0.55 = 55%)
        start_date: Start of backtest period
        end_date: End of backtest period
        days_back: Alternative to start_date - use last N days
    
    Returns:
        Dict with backtest results
    """
    # Determine date range
    if end_date is None:
        end_date = datetime.now(timezone.utc).date()
    
    if start_date is None:
        start_date = end_date - timedelta(days=days_back)
    
    logger.info(
        f"[backtest] Running backtest: sport={sport_id}, stat={stat_type}, "
        f"side={side}, min_ev={min_ev}, min_conf={min_confidence}, "
        f"dates={start_date} to {end_date}"
    )
    
    # Build query to join PickResult with ModelPick
    conditions = [
        PickResult.created_at >= datetime.combine(start_date, datetime.min.time()),
        PickResult.created_at <= datetime.combine(end_date, datetime.max.time()),
    ]
    
    # Sport filter via Game
    if sport_id:
        conditions.append(Game.sport_id == sport_id)
    
    # Stat type filter via Market
    if stat_type:
        conditions.append(Market.stat_type == stat_type)
    
    # Side filter
    if side:
        conditions.append(PickResult.side == side)
    
    # Query pick results with related data
    query = (
        select(
            PickResult,
            ModelPick.expected_value,
            ModelPick.confidence_score,
            ModelPick.model_probability,
            ModelPick.odds,
        )
        .join(ModelPick, PickResult.pick_id == ModelPick.id)
        .join(Game, PickResult.game_id == Game.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(and_(*conditions))
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    logger.info(f"[backtest] Found {len(rows)} total pick results")
    
    # Filter by EV and confidence thresholds
    qualifying_picks = []
    for pick_result, ev, confidence, model_prob, odds in rows:
        if ev is not None and ev >= min_ev and confidence is not None and confidence >= min_confidence:
            qualifying_picks.append({
                "hit": pick_result.hit,
                "ev": ev,
                "confidence": confidence,
                "model_prob": model_prob or 0.5,
                "odds": odds or -110,
                "clv_cents": pick_result.clv_cents,
                "profit_loss": pick_result.profit_loss or 0,
                "actual_value": pick_result.actual_value,
                "line_value": pick_result.line_value,
                "side": pick_result.side,
            })
    
    logger.info(f"[backtest] {len(qualifying_picks)} picks pass filters")
    
    if not qualifying_picks:
        return {
            "qualifying_bets": 0,
            "wins": 0,
            "losses": 0,
            "hit_rate": 0.0,
            "flat_stake_units": 0.0,
            "flat_stake_roi": 0.0,
            "kelly_stake_units": 0.0,
            "kelly_stake_roi": 0.0,
            "avg_ev": 0.0,
            "avg_clv_cents": 0.0,
            "date_range": {"start": str(start_date), "end": str(end_date)},
            "filters": {
                "sport_id": sport_id,
                "stat_type": stat_type,
                "side": side,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
            },
            "confidence_buckets": [],
            "sample_quality": "insufficient",
        }
    
    # Calculate results
    wins = sum(1 for p in qualifying_picks if p["hit"])
    losses = len(qualifying_picks) - wins
    hit_rate = wins / len(qualifying_picks) if qualifying_picks else 0
    
    # Flat stake P/L (1 unit per bet)
    flat_pl = 0.0
    for p in qualifying_picks:
        if p["hit"]:
            # Calculate profit based on odds
            if p["odds"] >= 100:
                flat_pl += p["odds"] / 100
            else:
                flat_pl += 100 / abs(p["odds"])
        else:
            flat_pl -= 1.0
    
    flat_stake_units = len(qualifying_picks)  # Total units wagered
    flat_stake_roi = (flat_pl / flat_stake_units * 100) if flat_stake_units > 0 else 0
    
    # Kelly stake P/L (variable units based on edge)
    kelly_pl = 0.0
    kelly_staked = 0.0
    for p in qualifying_picks:
        # Calculate quarter-Kelly stake
        ev = p["ev"]
        prob = p["model_prob"]
        odds = p["odds"]
        
        # Convert to decimal odds
        if odds >= 100:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))
        
        b = decimal_odds - 1
        q = 1 - prob
        
        # Full Kelly fraction
        full_kelly = (b * prob - q) / b if b > 0 else 0
        # Quarter Kelly
        kelly_fraction = max(0, min(0.05, full_kelly * 0.25))  # Cap at 5%
        kelly_units = kelly_fraction * 100  # Convert to units (assuming 100 unit bankroll)
        
        kelly_staked += kelly_units
        
        if p["hit"]:
            kelly_pl += kelly_units * b
        else:
            kelly_pl -= kelly_units
    
    kelly_stake_roi = (kelly_pl / kelly_staked * 100) if kelly_staked > 0 else 0
    
    # Average EV and CLV
    avg_ev = sum(p["ev"] for p in qualifying_picks) / len(qualifying_picks)
    clv_picks = [p for p in qualifying_picks if p["clv_cents"] is not None]
    avg_clv = sum(p["clv_cents"] for p in clv_picks) / len(clv_picks) if clv_picks else 0
    
    # Confidence buckets for breakdown
    buckets = [
        {"min": 0.50, "max": 0.55, "label": "50-55%"},
        {"min": 0.55, "max": 0.60, "label": "55-60%"},
        {"min": 0.60, "max": 0.65, "label": "60-65%"},
        {"min": 0.65, "max": 0.70, "label": "65-70%"},
        {"min": 0.70, "max": 1.00, "label": "70%+"},
    ]
    
    confidence_buckets = []
    for bucket in buckets:
        bucket_picks = [
            p for p in qualifying_picks
            if bucket["min"] <= p["confidence"] < bucket["max"]
        ]
        if bucket_picks:
            bucket_wins = sum(1 for p in bucket_picks if p["hit"])
            bucket_hit_rate = bucket_wins / len(bucket_picks)
            confidence_buckets.append({
                "label": bucket["label"],
                "count": len(bucket_picks),
                "wins": bucket_wins,
                "losses": len(bucket_picks) - bucket_wins,
                "hit_rate": round(bucket_hit_rate * 100, 1),
            })
    
    # Sample quality assessment
    if len(qualifying_picks) >= 100:
        sample_quality = "high"
    elif len(qualifying_picks) >= 30:
        sample_quality = "medium"
    else:
        sample_quality = "low"
    
    return {
        "qualifying_bets": len(qualifying_picks),
        "wins": wins,
        "losses": losses,
        "hit_rate": round(hit_rate * 100, 1),
        "flat_stake_units": round(flat_stake_units, 1),
        "flat_stake_profit": round(flat_pl, 2),
        "flat_stake_roi": round(flat_stake_roi, 2),
        "kelly_stake_units": round(kelly_staked, 2),
        "kelly_stake_profit": round(kelly_pl, 2),
        "kelly_stake_roi": round(kelly_stake_roi, 2),
        "avg_ev": round(avg_ev * 100, 2),
        "avg_clv_cents": round(avg_clv, 2),
        "date_range": {"start": str(start_date), "end": str(end_date)},
        "filters": {
            "sport_id": sport_id,
            "stat_type": stat_type,
            "side": side,
            "min_ev": min_ev,
            "min_confidence": min_confidence,
        },
        "confidence_buckets": confidence_buckets,
        "sample_quality": sample_quality,
    }
