"""
Model Validation Service - Backtesting and performance validation
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Game, Player, Market, PickResult

logger = logging.getLogger(__name__)

class ModelValidator:
    """Validates model performance through backtesting and CLV tracking."""
    
    def __init__(self):
        self.validation_results = {}
    
    async def validate_model_calibration(
        self,
        db: AsyncSession,
        sport_id: int = 30,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Validate model calibration on historical data.
        
        Args:
            db: Database session
            sport_id: Sport ID to validate
            days_back: Days of historical data to use
        
        Returns:
            Validation results with calibration metrics
        """
        
        # Get historical picks with results
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        query = select(ModelPick).options(
            selectinload(ModelPick.result),
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.generated_at >= cutoff_date,
                ModelPick.result_id.isnot(None)  # Only picks with results
            )
        ).order_by(ModelPick.generated_at.desc())
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if len(picks) < 50:
            return {
                "status": "insufficient_data",
                "message": f"Only {len(picks)} graded picks found. Need at least 50 for validation.",
                "picks_analyzed": len(picks)
            }
        
        # Calculate calibration metrics
        model_probs = []
        actual_results = []
        ev_values = []
        
        for pick in picks:
            if pick.result:
                model_probs.append(pick.model_probability)
                actual_results.append(1 if pick.result.result == "WIN" else 0)
                ev_values.append(pick.expected_value)
        
        # Calculate actual hit rate vs predicted
        predicted_hit_rate = sum(model_probs) / len(model_probs)
        actual_hit_rate = sum(actual_results) / len(actual_results)
        
        # Calculate calibration error
        calibration_error = abs(predicted_hit_rate - actual_hit_rate)
        
        # Calculate Brier score (proper scoring rule)
        brier_score = sum((prob - result) ** 2 for prob, result in zip(model_probs, actual_results)) / len(model_probs)
        
        # Calculate average EV
        avg_ev = sum(ev_values) / len(ev_values)
        
        # Calculate by probability buckets
        prob_buckets = {
            "0.25-0.35": {"pred": [], "actual": []},
            "0.35-0.45": {"pred": [], "actual": []},
            "0.45-0.55": {"pred": [], "actual": []},
            "0.55-0.65": {"pred": [], "actual": []},
            "0.65-0.75": {"pred": [], "actual": []}
        }
        
        for prob, result in zip(model_probs, actual_results):
            if prob <= 0.35:
                prob_buckets["0.25-0.35"]["pred"].append(prob)
                prob_buckets["0.25-0.35"]["actual"].append(result)
            elif prob <= 0.45:
                prob_buckets["0.35-0.45"]["pred"].append(prob)
                prob_buckets["0.35-0.45"]["actual"].append(result)
            elif prob <= 0.55:
                prob_buckets["0.45-0.55"]["pred"].append(prob)
                prob_buckets["0.45-0.55"]["actual"].append(result)
            elif prob <= 0.65:
                prob_buckets["0.55-0.65"]["pred"].append(prob)
                prob_buckets["0.55-0.65"]["actual"].append(result)
            else:
                prob_buckets["0.65-0.75"]["pred"].append(prob)
                prob_buckets["0.65-0.75"]["actual"].append(result)
        
        # Calculate bucket calibration
        bucket_calibration = {}
        for bucket, data in prob_buckets.items():
            if data["pred"]:
                pred_avg = sum(data["pred"]) / len(data["pred"])
                actual_avg = sum(data["actual"]) / len(data["actual"])
                bucket_calibration[bucket] = {
                    "predicted": round(pred_avg, 3),
                    "actual": round(actual_avg, 3),
                    "difference": round(abs(pred_avg - actual_avg), 3),
                    "sample_size": len(data["pred"])
                }
        
        # Determine if model is well-calibrated
        is_well_calibrated = calibration_error < 0.05  # Within 5%
        
        return {
            "status": "success",
            "validation_date": datetime.now(timezone.utc).isoformat(),
            "picks_analyzed": len(picks),
            "time_period_days": days_back,
            "calibration_metrics": {
                "predicted_hit_rate": round(predicted_hit_rate, 3),
                "actual_hit_rate": round(actual_hit_rate, 3),
                "calibration_error": round(calibration_error, 3),
                "brier_score": round(brier_score, 4),
                "average_ev": round(avg_ev, 4),
                "is_well_calibrated": is_well_calibrated
            },
            "bucket_calibration": bucket_calibration,
            "recommendation": self._get_calibration_recommendation(calibration_error, is_well_calibrated),
            "disclaimer": "Model validation based on historical performance. Past results do not guarantee future performance."
        }
    
    def _get_calibration_recommendation(self, calibration_error: float, is_well_calibrated: bool) -> str:
        """Get recommendation based on calibration results."""
        
        if is_well_calibrated:
            return "Model appears well-calibrated. Continue monitoring performance."
        elif calibration_error > 0.15:
            return "Model shows significant calibration issues. Consider retraining with more conservative probability estimates."
        elif calibration_error > 0.10:
            return "Model shows moderate calibration issues. Review probability calculation methods."
        else:
            return "Model shows minor calibration issues. Monitor closely and consider adjustments."
    
    async def calculate_clv_performance(
        self,
        db: AsyncSession,
        sport_id: int = 30,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate CLV (Closing Line Value) performance.
        
        Args:
            db: Database session
            sport_id: Sport ID to analyze
            days_back: Days to analyze
        
        Returns:
            CLV performance metrics
        """
        
        # Get picks with CLV data
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        query = select(ModelPick).options(
            selectinload(ModelPick.result),
            selectinload(ModelPick.player)
        ).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.generated_at >= cutoff_date,
                ModelPick.closing_odds.isnot(None),
                ModelPick.result_id.isnot(None)
            )
        ).order_by(ModelPick.generated_at.desc())
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if len(picks) < 20:
            return {
                "status": "insufficient_data",
                "message": f"Only {len(picks)} picks with CLV data found.",
                "picks_analyzed": len(picks)
            }
        
        # Calculate CLV metrics
        positive_clv_picks = []
        negative_clv_picks = []
        clv_values = []
        
        for pick in picks:
            if pick.result and pick.closing_odds and pick.odds:
                # Calculate CLV percentage
                entry_odds = pick.odds
                closing_odds = pick.closing_odds
                
                if entry_odds != 0 and closing_odds != 0:
                    clv_pct = ((entry_odds - closing_odds) / abs(closing_odds)) * 100
                    clv_values.append(clv_pct)
                    
                    if clv_pct > 0:
                        positive_clv_picks.append({
                            "player": pick.player.name if pick.player else "Unknown",
                            "clv_percentage": clv_pct,
                            "result": pick.result.result,
                            "entry_odds": entry_odds,
                            "closing_odds": closing_odds
                        })
                    else:
                        negative_clv_picks.append({
                            "player": pick.player.name if pick.player else "Unknown",
                            "clv_percentage": clv_pct,
                            "result": pick.result.result,
                            "entry_odds": entry_odds,
                            "closing_odds": closing_odds
                        })
        
        # Calculate hit rates by CLV
        positive_clv_wins = sum(1 for p in positive_clv_picks if p["result"] == "WIN")
        negative_clv_wins = sum(1 for p in negative_clv_picks if p["result"] == "WIN")
        
        positive_clv_hit_rate = positive_clv_wins / len(positive_clv_picks) if positive_clv_picks else 0
        negative_clv_hit_rate = negative_clv_wins / len(negative_clv_picks) if negative_clv_picks else 0
        
        avg_clv = sum(clv_values) / len(clv_values) if clv_values else 0
        
        # Determine if model shows positive CLV
        positive_clv_edge = positive_clv_hit_rate > 0.5 and len(positive_clv_picks) > 0
        
        return {
            "status": "success",
            "validation_date": datetime.now(timezone.utc).isoformat(),
            "picks_analyzed": len(picks),
            "clv_metrics": {
                "average_clv": round(avg_clv, 2),
                "positive_clv_picks": len(positive_clv_picks),
                "negative_clv_picks": len(negative_clv_picks),
                "positive_clv_hit_rate": round(positive_clv_hit_rate, 3),
                "negative_clv_hit_rate": round(negative_clv_hit_rate, 3),
                "positive_clv_edge": positive_clv_edge,
                "clv_distribution": {
                    "top_10_pct": len([c for c in clv_values if c >= 10]),
                    "top_5_pct": len([c for c in clv_values if c >= 5]),
                    "bottom_5_pct": len([c for c in clv_values if c <= -5]),
                    "bottom_10_pct": len([c for c in clv_values if c <= -10])
                }
            },
            "sample_picks": {
                "best_clv": sorted(positive_clv_picks, key=lambda x: x["clv_percentage"], reverse=True)[:5],
                "worst_clv": sorted(negative_clv_picks, key=lambda x: x["clv_percentage"])[:5]
            },
            "recommendation": self._get_clv_recommendation(positive_clv_edge, avg_clv),
            "disclaimer": "CLV analysis based on available data. Market efficiency varies by sport and market."
        }
    
    def _get_clv_recommendation(self, positive_clv_edge: bool, avg_clv: float) -> str:
        """Get recommendation based on CLV performance."""
        
        if positive_clv_edge and avg_clv > 2:
            return "Model shows positive CLV edge. Continue current approach."
        elif positive_clv_edge:
            return "Model shows positive CLV but modest values. Consider optimizing entry timing."
        elif avg_clv < -2:
            return "Model shows negative CLV. Review timing and market efficiency assumptions."
        else:
            return "CLV performance is neutral. Monitor for developing patterns."
    
    async def generate_model_status_report(
        self,
        db: AsyncSession,
        sport_id: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive model status report.
        
        Args:
            db: Database session
            sport_id: Sport ID to analyze
        
        Returns:
            Comprehensive model status report
        """
        
        # Get calibration validation
        calibration_result = await self.validate_model_calibration(db, sport_id, days_back=30)
        
        # Get CLV performance
        clv_result = await self.calculate_clv_performance(db, sport_id, days_back=30)
        
        # Get overall pick statistics
        total_picks_query = select(func.count(ModelPick.id)).where(ModelPick.sport_id == sport_id)
        total_picks_result = await db.execute(total_picks_query)
        total_picks = total_picks_result.scalar()
        
        graded_picks_query = select(func.count(ModelPick.id)).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.result_id.isnot(None)
            )
        )
        graded_picks_result = await db.execute(graded_picks_query)
        graded_picks = graded_picks_result.scalar()
        
        # Determine overall model status
        model_status = "BETA"
        confidence_level = "LOW"
        
        if calibration_result.get("status") == "success" and clv_result.get("status") == "success":
            is_calibrated = calibration_result["calibration_metrics"]["is_well_calibrated"]
            has_clv_edge = clv_result["clv_metrics"]["positive_clv_edge"]
            
            if is_calibrated and has_clv_edge and graded_picks >= 100:
                model_status = "PRODUCTION"
                confidence_level = "HIGH"
            elif is_calibrated and graded_picks >= 50:
                model_status = "ADVANCED_BETA"
                confidence_level = "MEDIUM"
        
        return {
            "status": "success",
            "report_date": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "model_status": model_status,
            "confidence_level": confidence_level,
            "pick_statistics": {
                "total_picks": total_picks,
                "graded_picks": graded_picks,
                "grading_rate": round(graded_picks / total_picks * 100, 1) if total_picks > 0 else 0
            },
            "calibration_validation": calibration_result,
            "clv_performance": clv_result,
            "overall_assessment": self._get_overall_assessment(model_status, confidence_level),
            "recommendations": self._get_overall_recommendations(model_status, calibration_result, clv_result),
            "disclaimer": "Model status based on available data. Sports betting involves risk. Never bet more than you can afford to lose."
        }
    
    def _get_overall_assessment(self, model_status: str, confidence_level: str) -> str:
        """Get overall assessment based on model status."""
        
        assessments = {
            "BETA": "Model in beta testing phase. Use with caution and small stakes.",
            "ADVANCED_BETA": "Model showing promising results in beta testing. Monitor performance closely.",
            "PRODUCTION": "Model has demonstrated consistent performance. Ready for regular use."
        }
        
        base_assessment = assessments.get(model_status, "Model status unknown.")
        
        confidence_text = {
            "LOW": "Limited data available.",
            "MEDIUM": "Moderate confidence in results.",
            "HIGH": "High confidence in model performance."
        }
        
        return f"{base_assessment} {confidence_text.get(confidence_level, '')}"
    
    def _get_overall_recommendations(self, model_status: str, calibration_result: Dict, clv_result: Dict) -> List[str]:
        """Get overall recommendations based on all validation results."""
        
        recommendations = []
        
        # Always include responsible gambling
        recommendations.append("Always bet responsibly and within your means.")
        recommendations.append("Use small stakes while model is in beta testing.")
        
        if calibration_result.get("status") == "success":
            cal_error = calibration_result["calibration_metrics"]["calibration_error"]
            if cal_error > 0.10:
                recommendations.append("Review probability calibration - model may be overconfident.")
        
        if clv_result.get("status") == "success":
            avg_clv = clv_result["clv_metrics"]["average_clv"]
            if avg_clv < -1:
                recommendations.append("Consider timing improvements - negative CLV detected.")
        
        if model_status == "BETA":
            recommendations.append("Monitor model performance closely before increasing stakes.")
            recommendations.append("Track your own results to validate model performance.")
        
        return recommendations

# Global validator instance
model_validator = ModelValidator()
