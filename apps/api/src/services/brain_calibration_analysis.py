#!/usr/bin/env python3
"""
BRAIN CALIBRATION ANALYSIS - Analyze and improve brain calibration metrics
"""
import asyncio
import asyncpg
import os
import json
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CalibrationBucket:
    """Calibration bucket data structure"""
    date: str
    sport_id: int
    probability_bucket: str
    bucket_min: float
    bucket_max: float
    predicted_prob: float
    actual_hit_rate: float
    sample_size: int
    barrier_score: float
    total_wagered: int
    total_profit: float
    roi_percent: float
    avg_clv_cents: Optional[float]

@dataclass
class CalibrationAnalysis:
    """Calibration analysis results"""
    sport_id: int
    date: str
    total_buckets: int
    brier_score: float
    calibration_slope: float
    calibration_intercept: float
    r_squared: float
    mean_squared_error: float
    mean_absolute_error: float
    total_profit: float
    total_wagered: int
    roi_percent: float
    bucket_analysis: List[CalibrationBucket]

class BrainCalibrationService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def get_calibration_data(self, sport_id: int, start_date: str = None, end_date: str = None) -> List[CalibrationBucket]:
        """Get calibration data for a specific sport"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM calibration_metrics 
                WHERE sport_id = $1
            """
            
            params = [sport_id]
            
            if start_date:
                query += " AND date >= $2"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= $3"
                params.append(end_date)
            
            query += " ORDER BY date, probability_bucket"
            
            result = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                CalibrationBucket(
                    date=row['date'],
                    sport_id=row['sport_id'],
                    probability_bucket=row['probability_bucket'],
                    bucket_min=row['bucket_min'],
                    bucket_max=row['bucket_max'],
                    predicted_prob=row['predicted_prob'],
                    actual_hit_rate=row['actual_hit_rate'],
                    sample_size=row['sample_size'],
                    barrier_score=row['barrier_score'],
                    total_wagered=row['total_wagered'],
                    total_profit=row['total_profit'],
                    roi_percent=row['roi_percent'],
                    avg_clv_cents=row.get('avg_clv_cents')
                )
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Error getting calibration data: {e}")
            return []
    
    async def analyze_calibration(self, sport_id: int, start_date: str = None, end_date: str = None) -> CalibrationAnalysis:
        """Analyze calibration for a sport"""
        try:
            buckets = await self.get_calibration_data(sport_id, start_date, end_date)
            
            if not buckets:
                return CalibrationAnalysis(
                    sport_id=sport_id,
                    date=start_date or datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                    total_buckets=0,
                    barrier_score=0.0,
                    calibration_slope=0.0,
                    calibration_intercept=0.0,
                    r_squared=0.0,
                    mean_squared_error=0.0,
                    mean_absolute_error=0.0,
                    total_profit=0.0,
                    total_wagered=0,
                    roi_percent=0.0,
                    bucket_analysis=[]
                )
            
            # Extract data for analysis
            predicted_probs = [b.predicted_prob for b in buckets]
            actual_hit_rates = [b.actual_hit_rate for b in buckets]
            
            # Calculate calibration metrics
            calibration_slope, calibration_intercept = np.polyfit(predicted_probs, actual_hit_rates, 1)
            r_squared = np.corrcoef(predicted_probs, actual_hit_rates)[0]**2 if len(predicted_probs) > 1 else 0
            mean_squared_error = np.mean([(p - a)**2 for p, a in zip(predicted_probs, actual_hit_rates)])
            mean_absolute_error = np.mean([abs(p - a) for p, a in zip(predicted_probs, actual_hit_rates)])
            
            # Calculate barrier score (Brier Score)
            total_wagered = sum(b.total_wagered for b in buckets)
            barrier_score = 1 - (2 * mean_squared_error)
            
            # Calculate total profit and ROI
            total_profit = sum(b.total_profit for b in buckets)
            roi_percent = (total_profit / total_wagered * 100) if total_wagered > 0 else 0
            
            return CalibrationAnalysis(
                sport_id=sport_id,
                date=buckets[0].date if buckets else datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                total_buckets=len(buckets),
                barrier_score=barrier_score,
                calibration_slope=calibration_slope,
                calibration_intercept=calibration_intercept,
                r_squared=r_squared,
                mean_squared_error=mean_squared_error,
                mean_absolute_error=mean_absolute_error,
                total_profit=total_profit,
                total_wagered=total_wagered,
                roi_percent=roi_percent,
                bucket_analysis=buckets
            )
            
        except Exception as e:
            logger.error(f"Error analyzing calibration: {e}")
            return CalibrationAnalysis(
                sport_id=sport_id,
                date=start_date or datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                total_buckets=0,
                barrier_score=0.0,
                calibration_slope=0.0,
                calibration_intercept=0.0,
                r_squared=0.0,
                mean_squared_error=0.0,
                mean_absolute_error=0.0,
                total_profit=0.0,
                total_wagered=0,
                roi_percent=0.0,
                bucket_analysis=[]
            )
    
    async def get_calibration_summary(self, sport_id: int, days: int = 30) -> Dict[str, Any]:
        """Get calibration summary for a sport"""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = (end_date - timedelta(days=days)).strftime('%Y-%m-%d')
            
            analysis = await self.analyze_calibration(sport_id, start_date, end_date)
            
            # Get bucket performance breakdown
            bucket_performance = []
            for bucket in analysis.bucket_analysis:
                performance = {
                    'bucket': bucket.probability_bucket,
                    'predicted_prob': bucket.predicted_prob,
                    'actual_hit_rate': bucket.actual_hit_rate,
                    'sample_size': bucket.sample_size,
                    'deviation': bucket.actual_hit_rate - bucket.predicted_prob,
                    'profit': bucket.total_profit,
                    'roi': bucket.roi_percent,
                    'barrier_score': bucket.barrier_score
                }
                bucket_performance.append(performance)
            
            return {
                'sport_id': sport_id,
                'period_days': days,
                'date_range': f"{start_date} to {end_date}",
                'total_buckets': analysis.total_buckets,
                'overall_barrier_score': analysis.barrier_score,
                'calibration_slope': analysis.calibration_slope,
                'calibration_intercept': analysis.calibration_intercept,
                'r_squared': analysis.r_squared,
                'mean_squared_error': analysis.mean_squared_error,
                'mean_absolute_error': analysis.mean_absolute_error,
                'total_profit': analysis.total_profit,
                'total_wagered': analysis.total_wagered,
                'roi_percent': analysis.roi_percent,
                'bucket_performance': bucket_performance,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting calibration summary: {e}")
            return {}
    
    async def get_cross_sport_comparison(self, days: int = 30) -> Dict[str, Any]:
        """Compare calibration across different sports"""
        try:
            sports = [32, 30]  # NFL, NBA
            sport_analyses = {}
            
            for sport_id in sports:
                end_date = datetime.now(timezone.utc)
                start_date = (end_date - timedelta(days=days)).strftime('%Y-%m-%d')
                
                analysis = await self.analyze_calibration(sport_id, start_date, end_date)
                sport_analyses[sport_id] = analysis
            
            if len(sport_analyses) < 2:
                return {
                    'error': 'Insufficient data for comparison',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate comparison metrics
            sport_names = {32: 'NFL', 30: 'NBA'}
            
            comparison = {
                'period_days': days,
                'date_range': f"{(end_date - timedelta(days=days)).strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'sport_comparison': {},
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            for sport_id, analysis in sport_analyses.items():
                sport_name = sport_names.get(sport_id, f"Sport {sport_id}")
                
                comparison['sport_comparison'][sport_name] = {
                    'sport_id': sport_id,
                    'barrier_score': analysis.barrier_score,
                    'r_squared': analysis.r_squared,
                    'mean_squared_error': analysis.mean_squared_error,
                    'mean_absolute_error': analysis.mean_absolute_error,
                    'total_profit': analysis.total_profit,
                    'roi_percent': analysis.roi_percent,
                    'total_wagered': analysis.total_wagered,
                    'bucket_count': analysis.total_buckets
                }
            
            return comparison
            
        except Exception as e:
            sport_analyses = {}
            logger.error(f"Error getting cross-sport comparison: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def identify_calibration_issues(self, sport_id: int) -> List[Dict[str, Any]]:
        """Identify calibration issues that need attention"""
        try:
            analysis = await self.analyze_calibration(sport_id)
            
            issues = []
            
            # Check for poor calibration
            if analysis.barrier_score < 0.8:
                issues.append({
                    'type': 'poor_calibration',
                    'severity': 'high',
                    'description': f'Barrier score of {analysis.barrier_score:.3f} indicates poor calibration',
                    'recommendation': 'Consider retraining probability models'
                })
            
            # Check for over/under confidence
            for bucket in analysis.bucket_analysis:
                deviation = abs(bucket.actual_hit_rate - bucket.predicted_prob)
                if deviation > 0.15:  # 15% deviation threshold
                    issues.append({
                        'type': 'confidence_mismatch',
                        'severity': 'medium',
                        'description': f'Bucket {bucket.probability_bucket} shows {deviation:.3f} deviation',
                        'recommendation': 'Adjust probability predictions for this bucket'
                    })
            
            # Check for insufficient sample size
            for bucket in analysis.bucket_analysis:
                if bucket.sample_size < 10:
                    issues.append({
                        'type': 'insufficient_data',
                        'severity': 'medium',
                        'description': f'Bucket {bucket.probability_bucket} has only {bucket.sample_size} samples',
                        'recommendation': 'Collect more data for this probability range'
                    })
            
            # Check for negative ROI
            if analysis.roi_percent < -5:
                issues.append({
                    'type': 'negative_roi',
                    'severity': 'high',
                    'description': f'ROI of {analysis.roi_percent:.1f}% indicates poor performance',
                    'recommendation': 'Review betting strategy and probability models'
                })
            
            # Check for low R-squared
            if analysis.r_squared < 0.7:
                issues.append({
                    'type': 'low_r_squared',
                    'severity': 'medium',
                    'description': f'R-squared of {analysis.r_squared:.3f} indicates poor model fit',
                    'recommendation': 'Improve model feature engineering'
                })
            
            return issues
            
        except Exception as e:
            logger.error(f"Error identifying calibration issues: {e}")
            return []
    
    async def suggest_calibration_improvements(self, sport_id: int) -> List[Dict[str, Any]]:
        """Suggest calibration improvements"""
        try:
            analysis = await self.analyze_calibration(sport_id)
            issues = await self.identify_calibration_issues(sport_id)
            
            suggestions = []
            
            # General improvements based on analysis
            if analysis.barrier_score < 0.8:
                suggestions.append({
                    'category': 'model_retraining',
                    'priority': 'high',
                    'title': 'Retrain Probability Models',
                    'description': 'Current barrier score indicates poor model calibration',
                    'expected_improvement': '15-25% improvement in barrier score',
                    'implementation': 'Use recent data and improved regularization'
                })
            
            if analysis.calibration_slope < 0.8 or analysis.calibration_slope > 1.2:
                suggestions.append({
                    'category': 'probability_adjustment',
                    'priority': 'high',
                    'title': 'Adjust Probability Scaling',
                    'description': f'Calibration slope of {analysis.calibration_slope:.3f} indicates misaligned probabilities',
                    'expected_improvement': 'Better alignment between predicted and actual outcomes',
                    'implementation': 'Apply probability scaling function'
                })
            
            if analysis.r_squared < 0.7:
                suggestions.append({
                    'category': 'feature_engineering',
                    'priority': 'medium',
                    'title': 'Improve Feature Engineering',
                    'description': f'R-squared of {analysis.r_squared:.3f} suggests poor model fit',
                    'expected_improvement': '10-20% improvement in model fit',
                    'implementation': 'Add more relevant features and interactions'
                })
            
            # Specific bucket improvements
            for issue in issues:
                if issue['type'] == 'confidence_mismatch':
                    suggestions.append({
                        'category': 'bucket_adjustment',
                        'priority': 'medium',
                        'title': f'Adjust {issue['description']}',
                        'description': 'Reduce confidence in over/under-performing buckets',
                        'expected_improvement': '5-10% improvement in accuracy',
                        'implementation': 'Adjust predicted probabilities for specific ranges'
                    })
                elif issue['type'] == 'insufficient_data':
                    suggestions.append({
                        'category': 'data_collection',
                        'priority': 'medium',
                        'title': f'Increase Sample Size',
                        'description': f'{issue['description']}',
                        'expected_improvement': 'More reliable statistical analysis',
                        'implementation': 'Focus data collection on problematic ranges'
                    })
            
            # Remove duplicates
            unique_suggestions = []
            seen = set()
            for suggestion in suggestions:
                key = f"{suggestion['category']}_{suggestion['title']}"
                if key not in seen:
                    unique_suggestions.append(suggestion)
                    seen.add(key)
            
            return unique_suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting improvements: {e}")
            return []
    
    async def run_calibration_analysis(self, sport_id: int, days: int = 30) -> Dict[str, Any]:
        """Run complete calibration analysis"""
        try:
            analysis = await self.analyze_calibration(sport_id, days)
            issues = await self.identify_calibration_issues(sport_id)
            suggestions = await self.suggest_calibration_improvements(sport_id)
            
            return {
                'sport_id': sport_id,
                'analysis_period_days': days,
                'analysis': {
                    'date_range': f"{analysis.date} (last {days} days)",
                    'total_buckets': analysis.total_buckets,
                    'barrier_score': analysis.barrier_score,
                    'calibration_slope': analysis.calibration_slope,
                    'calibration_intercept': analysis.calibration_intercept,
                    'r_squared': analysis.r_squared,
                    'mean_squared_error': analysis.mean_squared_error,
                    'mean_absolute_error': analysis.mean_absolute_error,
                    'total_profit': analysis.total_profit,
                    'total_wagered': analysis.total_wagered,
                    'roi_percent': analysis.roi_percent
                },
                'issues': issues,
                'suggestions': suggestions,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running calibration analysis: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

# Global instance
calibration_service = BrainCalibrationService()

async def run_calibration_analysis(sport_id: int, days: int = 30):
    """Run calibration analysis for a sport"""
    return await calibration_service.run_calibration_analysis(sport_id, days)

async def get_calibration_summary(sport_id: int, days: int = 30):
    """Get calibration summary for a sport"""
    return await calibration_service.get_calibration_summary(sport_id, days)

if __name__ == "__main__":
    # Test calibration service
    async def test():
        # Test calibration analysis
        analysis = await run_calibration_analysis(32, 30)  # NFL
        print(f"Calibration Analysis: {analysis.get('analysis', {}).get('barrier_score', 0):.3f}")
        
        # Test calibration summary
        summary = await get_calibration_summary(32, 30)
        print(f"Calibration Summary: {summary.get('total_buckets', 0)} buckets")
        
        # Test cross-sport comparison
        comparison = await calibration_service.get_cross_sport_comparison(30)
        print(f"Cross-Sport Comparison: {len(comparison.get('sport_comparison', {}))} sports")
    
    asyncio.run(test())
