#!/usr/bin/env python3
"""
ADD BRAIN CALIBRATION ENDPOINTS - Add brain calibration analysis endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_brain_calibration_endpoints():
    """Add brain calibration endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the brain calibration endpoints
    brain_calibration_code = '''

# Brain Calibration Analysis Endpoints
@router.get("/brain-calibration-summary")
async def get_brain_calibration_summary(sport_id: int = Query(32, description="Sport ID"), days: int = Query(30, description="Days of data to analyze")):
    """Get brain calibration summary for a sport"""
    try:
        # Return mock calibration summary data for now
        mock_summary = {
            "sport_id": sport_id,
            "period_days": days,
            "date_range": f"{(datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')} to {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            "total_buckets": 5,
            "overall_barrier_score": 0.753,
            "calibration_slope": 1.12,
            "calibration_intercept": -0.05,
            "r_squared": 0.842,
            "mean_squared_error": 0.123,
            "mean_absolute_error": 0.089,
            "total_profit": 3536.45,
            "total_wagered": 13900,
            "roi_percent": 25.44,
            "bucket_performance": [
                {
                    "bucket": "50-55",
                    "predicted_prob": 0.5366,
                    "actual_hit_rate": 0.55,
                    "sample_size": 20,
                    "deviation": 0.0134,
                    "profit": 100.01,
                    "roi": 5.0,
                    "barrier_score": 0.247
                },
                {
                    "bucket": "55-60",
                    "predicted_prob": 0.5732,
                    "actual_hit_rate": 0.5942,
                    "sample_size": 69,
                    "deviation": 0.021,
                    "profit": 927.31,
                    "roi": 13.44,
                    "barrier_score": 0.24
                },
                {
                    "bucket": "60-65",
                    "predicted_prob": 0.6222,
                    "actual_hit_rate": 0.7568,
                    "sample_size": 37,
                    "deviation": 0.1346,
                    "profit": 1645.48,
                    "roi": 44.47,
                    "barrier_score": 0.2031
                },
                {
                    "bucket": "65-70",
                    "predicted_prob": 0.6731,
                    "actual_hit_rate": 0.6923,
                    "sample_size": 13,
                    "deviation": 0.0192,
                    "profit": 418.19,
                    "roi": 32.17,
                    "barrier_score": 0.2111
                },
                {
                    "bucket": "70-75",
                    "predicted_prob": 0.718,
                    "actual_hit_rate": 0.8571,
                    "sample_size": 7,
                    "deviation": 0.1391,
                    "profit": 445.46,
                    "roi": 63.64,
                    "barrier_score": 0.1376
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain calibration summary data"
        }
        
        return mock_summary
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-calibration-analysis")
async def run_brain_calibration_analysis(sport_id: int = Query(32, description="Sport ID"), days: int = Query(30, description="Days of data to analyze")):
    """Run complete brain calibration analysis"""
    try:
        # Return mock calibration analysis data for now
        mock_analysis = {
            "sport_id": sport_id,
            "analysis_period_days": days,
            "analysis": {
                "date_range": f"{(datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')} (last {days} days)",
                "total_buckets": 5,
                "barrier_score": 0.753,
                "calibration_slope": 1.12,
                "calibration_intercept": -0.05,
                "r_squared": 0.842,
                "mean_squared_error": 0.123,
                "mean_absolute_error": 0.089,
                "total_profit": 3536.45,
                "total_wagered": 13900,
                "roi_percent": 25.44
            },
            "issues": [
                {
                    "type": "confidence_mismatch",
                    "severity": "medium",
                    "description": "Bucket 60-65 shows 0.135 deviation",
                    "recommendation": "Adjust probability predictions for this bucket"
                },
                {
                    "type": "confidence_mismatch",
                    "severity": "medium",
                    "description": "Bucket 70-75 shows 0.139 deviation",
                    "recommendation": "Adjust probability predictions for this bucket"
                }
            ],
            "suggestions": [
                {
                    "category": "probability_adjustment",
                    "priority": "high",
                    "title": "Adjust Probability Scaling",
                    "description": "Calibration slope of 1.12 indicates overconfidence",
                    "expected_improvement": "Better alignment between predicted and actual outcomes",
                    "implementation": "Apply probability scaling function"
                },
                {
                    "category": "bucket_adjustment",
                    "priority": "medium",
                    "title": "Adjust Bucket 60-65 shows 0.135 deviation",
                    "description": "Reduce confidence in over-performing bucket",
                    "expected_improvement": "5-10% improvement in accuracy",
                    "implementation": "Adjust predicted probabilities for 60-65% range"
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain calibration analysis data"
        }
        
        return mock_analysis
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-calibration-comparison")
async def get_brain_calibration_comparison(days: int = Query(30, description="Days of data to compare")):
    """Get cross-sport calibration comparison"""
    try:
        # Return mock comparison data for now
        mock_comparison = {
            "period_days": days,
            "date_range": f"{(datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')} to {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            "sport_comparison": {
                "NFL": {
                    "sport_id": 32,
                    "barrier_score": 0.753,
                    "r_squared": 0.842,
                    "mean_squared_error": 0.123,
                    "mean_absolute_error": 0.089,
                    "total_profit": 3536.45,
                    "roi_percent": 25.44,
                    "total_wagered": 13900,
                    "bucket_count": 5
                },
                "NBA": {
                    "sport_id": 30,
                    "barrier_score": 0.687,
                    "r_squared": 0.789,
                    "mean_squared_error": 0.156,
                    "mean_absolute_error": 0.102,
                    "total_profit": 2145.67,
                    "roi_percent": 18.23,
                    "total_wagered": 11750,
                    "bucket_count": 4
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock cross-sport calibration comparison data"
        }
        
        return mock_comparison
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-calibration-issues")
async def get_brain_calibration_issues(sport_id: int = Query(32, description="Sport ID")):
    """Get calibration issues for a sport"""
    try:
        # Return mock issues data for now
        mock_issues = [
            {
                "type": "confidence_mismatch",
                "severity": "medium",
                "description": "Bucket 60-65 shows 0.135 deviation",
                "recommendation": "Adjust probability predictions for this bucket"
            },
            {
                "type": "confidence_mismatch",
                "severity": "medium",
                "description": "Bucket 70-75 shows 0.139 deviation",
                "recommendation": "Adjust probability predictions for this bucket"
            },
            {
                "type": "overconfidence",
                "severity": "medium",
                "description": "Calibration slope of 1.12 indicates overconfidence",
                "recommendation": "Apply probability scaling function"
            }
        ]
        
        return {
            "sport_id": sport_id,
            "issues": mock_issues,
            "total_issues": len(mock_issues),
            "high_severity": 0,
            "medium_severity": 3,
            "low_severity": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock calibration issues data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-calibration-improvements")
async def get_brain_calibration_improvements(sport_id: int = Query(32, description="Sport ID")):
    """Get calibration improvement suggestions"""
    try:
        # Return mock suggestions data for now
        mock_suggestions = [
            {
                "category": "probability_adjustment",
                "priority": "high",
                "title": "Adjust Probability Scaling",
                "description": "Calibration slope of 1.12 indicates overconfidence",
                "expected_improvement": "Better alignment between predicted and actual outcomes",
                "implementation": "Apply probability scaling function"
            },
            {
                "category": "bucket_adjustment",
                "priority": "medium",
                "title": "Adjust Bucket 60-65 Performance",
                "description": "Reduce confidence in over-performing bucket",
                "expected_improvement": "5-10% improvement in accuracy",
                "implementation": "Adjust predicted probabilities for 60-65% range"
            },
            {
                "category": "bucket_adjustment",
                "priority": "medium",
                "title": "Adjust Bucket 70-75 Performance",
                "description": "Reduce confidence in over-performing bucket",
                "expected_improvement": "5-10% improvement in accuracy",
                "implementation": "Adjust predicted probabilities for 70-75% range"
            }
        ]
        
        return {
            "sport_id": sport_id,
            "suggestions": mock_suggestions,
            "total_suggestions": len(mock_suggestions),
            "high_priority": 1,
            "medium_priority": 2,
            "low_priority": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock calibration improvement suggestions data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", brain_calibration_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += brain_calibration_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Brain calibration endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_brain_calibration_endpoints())
