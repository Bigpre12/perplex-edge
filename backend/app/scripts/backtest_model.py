"""
Model Backtesting Script - Validate model performance on historical data
"""

import asyncio
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np

# Add the backend directory to the path
sys.path.append('/app')

from app.core.database import get_db
from app.models import ModelPick, Game, Player, Market, PickResult
from app.services.model_validation import model_validator
from app.services.results_api import results_api

class ModelBacktester:
    """Backtesting system for model validation."""
    
    def __init__(self):
        self.min_sample_size = 100  # Minimum picks for meaningful backtest
    
    async def backtest_month(self, year: int, month: int, sport_id: int = 30) -> Dict[str, Any]:
        """
        Backtest model performance for a specific month.
        
        Args:
            year: Year to backtest
            month: Month to backtest
            sport_id: Sport ID (default 30 for NBA)
        
        Returns:
            Backtest results and analysis
        """
        try:
            # Get picks for the month
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            
            async with get_db() as db:
                # Get all picks from the month
                query = select(ModelPick).options(
                    selectinload(ModelPick.result),
                    selectinload(ModelPick.player),
                    selectinload(ModelPick.market)
                ).where(
                    and_(
                        ModelPick.sport_id == sport_id,
                        ModelPick.generated_at >= start_date,
                        ModelPick.generated_at < end_date,
                        ModelPick.result_id.isnot(None)  # Only graded picks
                    )
                ).order_by(ModelPick.generated_at)
                
                result = await db.execute(query)
                picks = result.scalars().all()
                
                if len(picks) < self.min_sample_size:
                    return {
                        "status": "insufficient_data",
                        "message": f"Only {len(picks)} graded picks found. Need at least {self.min_sample_size}",
                        "period": f"{year}-{month:02d}",
                        "picks_analyzed": len(picks)
                    }
                
                # Analyze performance
                analysis = await self.analyze_pick_performance(picks)
                
                # Calculate ROI
                roi_analysis = self.calculate_roi(picks)
                
                # Compare predicted vs actual
                calibration_analysis = await self.analyze_calibration(picks)
                
                return {
                    "status": "success",
                    "period": f"{year}-{month:02d}",
                    "picks_analyzed": len(picks),
                    "performance": analysis,
                    "roi": roi_analysis,
                    "calibration": calibration_analysis,
                    "recommendation": self.get_backtest_recommendation(analysis, calibration_analysis),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "period": f"{year}-{month:02d}"
            }
    
    async def analyze_pick_performance(self, picks: List[ModelPick]) -> Dict[str, Any]:
        """Analyze pick performance metrics."""
        
        wins = sum(1 for pick in picks if pick.result and pick.result.result == "WIN")
        losses = len(picks) - wins
        
        win_rate = (wins / len(picks)) * 100 if picks else 0
        
        # Calculate average model probability
        avg_model_prob = sum(pick.model_probability for pick in picks) / len(picks) if picks else 0
        
        # Calculate average claimed EV
        avg_claimed_ev = sum(pick.expected_value for pick in picks) / len(picks) if picks else 0
        
        # Calculate actual EV based on results
        actual_ev = self.calculate_actual_ev(picks)
        
        # Calculate confidence distribution
        confidence_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for pick in picks:
            if pick.confidence_score < 0.6:
                confidence_levels["LOW"] += 1
            elif pick.confidence_score < 0.8:
                confidence_levels["MEDIUM"] += 1
            else:
                confidence_levels["HIGH"] += 1
        
        return {
            "total_picks": len(picks),
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "avg_model_probability": round(avg_model_prob, 3),
            "avg_claimed_ev": round(avg_claimed_ev, 4),
            "actual_ev": round(actual_ev, 4),
            "ev_difference": round(avg_claimed_ev - actual_ev, 4),
            "confidence_distribution": confidence_levels,
            "performance_rating": self.get_performance_rating(win_rate, actual_ev)
        }
    
    def calculate_actual_ev(self, picks: List[ModelPick]) -> float:
        """Calculate actual EV based on real results."""
        
        total_profit = 0.0
        total_bets = 0.0
        
        for pick in picks:
            if not pick.result or not pick.odds:
                continue
            
            # Calculate profit/loss for this pick
            if pick.result.result == "WIN":
                if pick.odds > 0:
                    profit = pick.odds / 100
                else:
                    profit = 100 / abs(pick.odds)
                total_profit += profit
            else:
                total_profit -= 1.0  # Lost the bet
            
            total_bets += 1.0
        
        return (total_profit / total_bets) if total_bets > 0 else 0.0
    
    def calculate_roi(self, picks: List[ModelPick]) -> Dict[str, Any]:
        """Calculate ROI and financial metrics."""
        
        total_bets = len(picks)
        total_profit = 0.0
        wins = 0
        
        for pick in picks:
            if not pick.result or not pick.odds:
                continue
            
            if pick.result.result == "WIN":
                wins += 1
                if pick.odds > 0:
                    profit = pick.odds / 100
                else:
                    profit = 100 / abs(pick.odds)
                total_profit += profit
            else:
                total_profit -= 1.0
        
        roi = (total_profit / total_bets) * 100 if total_bets > 0 else 0
        
        # Calculate CLV metrics if available
        clv_picks = [p for p in picks if p.clv_percentage is not None]
        avg_clv = sum(p.clv_percentage for p in clv_picks) / len(clv_picks) if clv_picks else 0
        
        positive_clv = sum(1 for p in clv_picks if p.clv_percentage > 0)
        positive_clv_rate = (positive_clv / len(clv_picks)) * 100 if clv_picks else 0
        
        return {
            "total_bets": total_bets,
            "total_profit": round(total_profit, 2),
            "roi": round(roi, 2),
            "win_rate": round((wins / total_bets) * 100, 2) if total_bets > 0 else 0,
            "avg_clv": round(avg_clv, 2),
            "positive_clv_rate": round(positive_clv_rate, 2),
            "clv_samples": len(clv_picks),
            "profit_per_100_bets": round((total_profit / total_bets) * 100, 2) if total_bets > 0 else 0
        }
    
    async def analyze_calibration(self, picks: List[ModelPick]) -> Dict[str, Any]:
        """Analyze model calibration (predicted vs actual probabilities)."""
        
        # Group picks by probability ranges
        prob_buckets = {
            "0.25-0.35": {"predicted": [], "actual": []},
            "0.35-0.45": {"predicted": [], "actual": []},
            "0.45-0.55": {"predicted": [], "actual": []},
            "0.55-0.65": {"predicted": [], "actual": []},
            "0.65-0.75": {"predicted": [], "actual": []}
        }
        
        for pick in picks:
            if not pick.result:
                continue
                
            prob = pick.model_probability
            actual = 1 if pick.result.result == "WIN" else 0
            
            # Bucket by probability
            if prob <= 0.35:
                prob_buckets["0.25-0.35"]["predicted"].append(prob)
                prob_buckets["0.25-0.35"]["actual"].append(actual)
            elif prob <= 0.45:
                prob_buckets["0.35-0.45"]["predicted"].append(prob)
                prob_buckets["0.35-0.45"]["actual"].append(actual)
            elif prob <= 0.55:
                prob_buckets["0.45-0.55"]["predicted"].append(prob)
                prob_buckets["0.45-0.55"]["actual"].append(actual)
            elif prob <= 0.65:
                prob_buckets["0.55-0.65"]["predicted"].append(prob)
                prob_buckets["0.55-0.65"]["actual"].append(actual)
            else:
                prob_buckets["0.65-0.75"]["predicted"].append(prob)
                prob_buckets["0.65-0.75"]["actual"].append(actual)
        
        # Calculate calibration metrics
        calibration_data = {}
        total_predicted = 0
        total_actual = 0
        
        for bucket, data in prob_buckets.items():
            if data["predicted"]:
                pred_avg = sum(data["predicted"]) / len(data["predicted"])
                actual_avg = sum(data["actual"]) / len(data["actual"])
                diff = abs(pred_avg - actual_avg)
                
                calibration_data[bucket] = {
                    "predicted": round(pred_avg, 3),
                    "actual": round(actual_avg, 3),
                    "difference": round(diff, 3),
                    "sample_size": len(data["predicted"]),
                    "is_well_calibrated": diff < 0.05
                }
                
                total_predicted += sum(data["predicted"])
                total_actual += sum(data["actual"])
        
        # Overall calibration
        overall_predicted = total_predicted / len(picks) if picks else 0
        overall_actual = total_actual / len(picks) if picks else 0
        overall_diff = abs(overall_predicted - overall_actual)
        
        return {
            "overall_predicted": round(overall_predicted, 3),
            "overall_actual": round(overall_actual, 3),
            "overall_difference": round(overall_diff, 3),
            "is_well_calibrated": overall_diff < 0.05,
            "bucket_analysis": calibration_data,
            "calibration_score": round(max(0, 1 - overall_diff) * 100, 2)
        }
    
    def get_performance_rating(self, win_rate: float, actual_ev: float) -> str:
        """Get performance rating based on metrics."""
        
        if win_rate >= 56 and actual_ev >= 3:
            return "EXCELLENT"
        elif win_rate >= 54 and actual_ev >= 1:
            return "GOOD"
        elif win_rate >= 52 and actual_ev >= 0:
            return "ACCEPTABLE"
        elif win_rate >= 50:
            return "MARGINAL"
        else:
            return "POOR"
    
    def get_backtest_recommendation(self, performance: Dict, calibration: Dict) -> List[str]:
        """Get recommendations based on backtest results."""
        
        recommendations = []
        
        win_rate = performance.get("win_rate", 0)
        actual_ev = performance.get("actual_ev", 0)
        is_calibrated = calibration.get("is_well_calibrated", False)
        
        if win_rate < 52:
            recommendations.append("Model win rate below 52% - major recalibration needed")
        elif win_rate < 54:
            recommendations.append("Model win rate marginal - consider conservative adjustments")
        
        if actual_ev < 0:
            recommendations.append("Negative actual EV - model is losing money")
        elif actual_ev < 2:
            recommendations.append("Low actual EV - model needs improvement")
        
        if not is_calibrated:
            recommendations.append("Model not well-calibrated - probability estimates need adjustment")
        
        if performance.get("ev_difference", 0) > 0.05:
            recommendations.append("Large gap between claimed and actual EV - review EV calculations")
        
        if not recommendations:
            recommendations.append("Model performance is acceptable - continue monitoring")
        
        return recommendations

async def run_backtest():
    """Run a comprehensive backtest on recent data."""
    
    print("🔍 MODEL BACKTESTING ANALYSIS")
    print("=" * 50)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    # Backtest January 2026
    print("📊 BACKTESTING JANUARY 2026:")
    try:
        backtester = ModelBacktester()
        jan_results = await backtester.backtest_month(2026, 1)
        
        if jan_results["status"] == "success":
            perf = jan_results["performance"]
            roi = jan_results["roi"]
            cal = jan_results["calibration"]
            
            print(f"   Picks Analyzed: {jan_results['picks_analyzed']}")
            print(f"   Win Rate: {perf['win_rate']}%")
            print(f"   Actual EV: {perf['actual_ev']}%")
            print(f"   Claimed EV: {perf['avg_claimed_ev']}%")
            print(f"   EV Difference: {perf['ev_difference']}%")
            print(f"   ROI: {roi['roi']}%")
            print(f"   Calibration: {'✅ Well-calibrated' if cal['is_well_calibrated'] else '❌ Poorly calibrated'}")
            print(f"   Performance Rating: {perf['performance_rating']}")
            print()
            
            print("📋 RECOMMENDATIONS:")
            for rec in jan_results["recommendation"]:
                print(f"   • {rec}")
        else:
            print(f"   Status: {jan_results['status']}")
            print(f"   Message: {jan_results.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    print("=" * 50)
    print("🎯 BACKTESTING COMPLETE")

if __name__ == "__main__":
    asyncio.run(run_backtest())
