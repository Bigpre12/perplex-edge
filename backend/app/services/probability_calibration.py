"""
Probability Calibration Service - Fix overconfident model predictions
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from scipy.stats import beta
from sklearn.isotonic import IsotonicRegression

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Game, Player, Market
from app.core.database import get_session_maker

class ProbabilityCalibrator:
    """Calibrates model probabilities using market efficiency and historical performance."""
    
    def __init__(self):
        self.isotonic_regressor = IsotonicRegression(out_of_bounds='clip')
        self.calibration_data = {}
        self.market_efficiency_factor = 0.05  # Max 5% edge over market
        
    def calibrate_probability(
        self, 
        model_prob: float, 
        implied_prob: float, 
        sample_size: int,
        market_type: str = "player_props"
    ) -> float:
        """
        Calibrate model probability using market efficiency and sample size.
        
        Args:
            model_prob: Raw model probability (0-1)
            implied_prob: Implied probability from odds (0-1)
            sample_size: Sample size used for model prediction
            market_type: Type of market (affects efficiency)
        
        Returns:
            Calibrated probability (0-1)
        """
        # 1. Sample size regression to mean
        if sample_size < 10:
            regression_factor = 0.3  # Heavy regression for small samples
        elif sample_size < 30:
            regression_factor = 0.5
        elif sample_size < 50:
            regression_factor = 0.7
        else:
            regression_factor = 0.85
        
        league_avg = 0.5  # 50% league average
        regressed_prob = (model_prob * regression_factor) + (league_avg * (1 - regression_factor))
        
        # 2. Market efficiency adjustment
        if market_type == "player_props":
            max_edge = 0.08  # 8% max edge for props
        elif market_type == "game_lines":
            max_edge = 0.03  # 3% max edge for game lines
        else:
            max_edge = 0.05  # 5% default max edge
        
        # Blend with market probability
        market_weight = 0.7  # Trust market more
        model_weight = 0.3  # Trust model less
        
        blended_prob = (model_weight * regressed_prob) + (market_weight * implied_prob)
        
        # 3. Apply market efficiency constraint
        max_prob = implied_prob + max_edge
        calibrated_prob = min(blended_prob, max_prob)
        
        # 4. Ensure reasonable bounds
        return max(0.45, min(0.65, calibrated_prob))
    
    def calculate_confidence_interval(
        self, 
        probability: float, 
        sample_size: int,
        confidence_level: float = 0.95
    ) -> tuple[float, float]:
        """
        Calculate confidence interval for probability prediction.
        
        Args:
            probability: Calibrated probability
            sample_size: Sample size
            confidence_level: Confidence level (0-1)
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if sample_size < 10:
            # Wide intervals for small samples
            margin = 0.15
        elif sample_size < 30:
            margin = 0.10
        elif sample_size < 50:
            margin = 0.08
        else:
            margin = 0.05
        
        alpha = 1 - confidence_level
        lower = max(0.25, probability - margin)
        upper = min(0.75, probability + margin)
        
        return (lower, upper)
    
    def calculate_kelly_fraction(
        self, 
        probability: float, 
        odds: int,
        bankroll: float,
        confidence: float = 0.5
    ) -> float:
        """
        Calculate optimal Kelly fraction for bet sizing.
        
        Args:
            probability: Win probability (0-1)
            odds: American odds
            bankroll: Total bankroll
            confidence: Confidence in prediction (0-1)
        
        Returns:
            Kelly fraction (0-1)
        """
        # Calculate decimal odds
        if odds < 0:
            decimal_odds = 100 / abs(odds) + 1
        else:
            decimal_odds = odds / 100 + 1
        
        # Calculate edge
        edge = (probability * decimal_odds) - 1
        
        # Calculate Kelly fraction
        kelly_fraction = edge / (decimal_odds - 1)
        
        # Apply confidence adjustment (reduce bet size for low confidence)
        confidence_adjustment = min(1.0, confidence * 2)
        adjusted_kelly = kelly_fraction * confidence_adjustment
        
        # Limit to reasonable range (0-25% of bankroll)
        return max(0.0, min(0.25, adjusted_kelly))
    
    async def fit_isotonic_calibration(
        self, 
        db: AsyncSession,
        sport_id: int,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Fit isotonic regression using historical pick results.
        
        Args:
            db: Database session
            sport_id: Sport ID
            days_back: Number of days of historical data
        
        Returns:
            Calibration metrics
        """
        # Get historical picks with results
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.generated_at >= cutoff_date,
                ModelPick.result.isnot(None)  # Only picks with results
            )
        )
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if len(picks) < 50:
            return {
                "status": "insufficient_data",
                "message": f"Only {len(picks)} picks with results found",
                "min_required": 50
            }
        
        # Prepare training data
        model_probs = []
        actual_outcomes = []
        
        for pick in picks:
            model_probs.append(pick.model_probability)
            actual_outcomes.append(1 if pick.result.hit else 0)
        
        # Fit isotonic regression
        self.isotonic_regressor.fit(model_probs, actual_outcomes)
        
        # Calculate calibration metrics
        calibrated_probs = self.isotonic_regressor.predict(model_probs)
        
        # Calculate Brier score (lower is better)
        brier_score = np.mean((calibrated_probs - np.array(actual_outcomes)) ** 2)
        
        # Calculate reliability diagram data
        reliability_data = self._calculate_reliability_diagram(calibrated_probs, actual_outcomes)
        
        return {
            "status": "success",
            "picks_used": len(picks),
            "brier_score": brier_score,
            "reliability": reliability_data,
            "calibration_date": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_reliability_diagram(
        self, 
        predicted_probs: List[float], 
        actual_outcomes: List[int]
    ) -> Dict[str, Any]:
        """Calculate reliability diagram data for calibration visualization."""
        
        bins = np.linspace(0.45, 0.65, 5)  # 5 bins from 45% to 65%
        reliability_data = []
        
        for i in range(len(bins) - 1):
            lower = bins[i]
            upper = bins[i + 1]
            
            # Find picks in this bin
            bin_mask = (np.array(predicted_probs) >= lower) & (np.array(predicted_probs) < upper)
            bin_outcomes = np.array(actual_outcomes)[bin_mask]
            
            if len(bin_outcomes) > 0:
                actual_freq = np.mean(bin_outcomes)
                predicted_freq = (lower + upper) / 2
                
                reliability_data.append({
                    "predicted_probability": predicted_freq,
                    "actual_frequency": actual_freq,
                    "sample_size": len(bin_outcomes),
                    "lower_bound": lower,
                    "upper_bound": upper
                })
        
        return {
            "bins": reliability_data,
            "total_samples": len(predicted_probs)
        }
    
    async def get_calibration_metrics(
        self, 
        db: AsyncSession,
        sport_id: int
    ) -> Dict[str, Any]:
        """Get current calibration metrics for a sport."""
        
        # Get recent picks with results
        recent_date = datetime.now(timezone.utc) - timedelta(days=7)
        
        query = select(ModelPick).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.generated_at >= recent_date,
                ModelPick.result.isnot(None)
            )
        )
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if not picks:
            return {
                "status": "no_data",
                "message": "No recent picks with results found"
            }
        
        # Calculate metrics
        total_picks = len(picks)
        winning_picks = sum(1 for pick in picks if pick.result.hit)
        overall_win_rate = winning_picks / total_picks
        
        # Group by confidence level
        confidence_groups = {
            "high": [],      # > 0.7
            "medium": [],    # 0.6-0.7
            "low": [],       # < 0.6
        }
        
        for pick in picks:
            conf = pick.confidence_score
            if conf > 0.7:
                confidence_groups["high"].append(pick)
            elif conf >= 0.6:
                confidence_groups["medium"].append(pick)
            else:
                confidence_groups["low"].append(pick)
        
        # Calculate win rates by confidence
        confidence_win_rates = {}
        for level, group_picks in confidence_groups.items():
            if group_picks:
                wins = sum(1 for pick in group_picks if pick.result.hit)
                confidence_win_rates[level] = wins / len(group_picks)
            else:
                confidence_win_rates[level] = 0.0
        
        # Calculate average EV by confidence
        confidence_evs = {}
        for level, group_picks in confidence_groups.items():
            if group_picks:
                avg_ev = sum(pick.expected_value for pick in group_picks) / len(group_picks)
                confidence_evs[level] = avg_ev
            else:
                confidence_evs[level] = 0.0
        
        return {
            "status": "success",
            "total_picks": total_picks,
            "overall_win_rate": overall_win_rate,
            "confidence_win_rates": confidence_win_rates,
            "confidence_evs": confidence_evs,
            "calibration_date": datetime.now(timezone.utc).isoformat()
        }
