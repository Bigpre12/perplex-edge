#!/usr/bin/env python3
"""
ADD BRAIN LEARNING ENDPOINTS - Add brain learning system endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_brain_learning_endpoints():
    """Add brain learning endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the brain learning endpoints
    brain_learning_code = '''

# Brain Learning System Endpoints
@router.get("/brain-learning-events")
async def get_brain_learning_events(limit: int = Query(50, description="Number of events to return")):
    """Get recent brain learning events"""
    try:
        # Return mock learning event data for now
        mock_events = [
            {
                "id": 1,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "learning_type": "model_improvement",
                "metric_name": "passing_yards_prediction_accuracy",
                "old_value": 0.52,
                "new_value": 0.71,
                "confidence": 0.85,
                "context": "Retrained passing yards predictor with 15k new data points. Added regularization and feature engineering.",
                "impact_assessment": "High impact - 19% accuracy improvement will increase recommendation success rate and user confidence.",
                "validated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "validation_result": "validated"
            },
            {
                "id": 2,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "learning_type": "parameter_tuning",
                "metric_name": "confidence_calculation_method",
                "old_value": 0.92,
                "new_value": 0.85,
                "confidence": 0.78,
                "context": "Adjusted confidence calculation to cap at 85% based on user feedback analysis.",
                "impact_assessment": "Medium impact - May reduce perceived confidence but improve user trust and long-term engagement.",
                "validated_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "validation_result": "validated"
            },
            {
                "id": 3,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
                "learning_type": "market_pattern",
                "metric_name": "line_movement_detection_threshold",
                "old_value": 0.05,
                "new_value": 0.03,
                "confidence": 0.92,
                "context": "Learned that smaller line movements (3%+) are more predictive of value opportunities than previously thought (5%+).",
                "impact_assessment": "High impact - Will identify 15% more value opportunities while maintaining false positive rate.",
                "validated_at": (datetime.now(timezone.utc) - timedelta(hours=11)).isoformat(),
                "validation_result": "validated"
            },
            {
                "id": 4,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat(),
                "learning_type": "user_behavior",
                "metric_name": "optimal_recommendation_count_per_hour",
                "old_value": 15.0,
                "new_value": 12.0,
                "confidence": 0.81,
                "context": "Analyzed user engagement patterns and found that users prefer quality over quantity. Reduced recommendation frequency.",
                "impact_assessment": "Medium impact - Will improve user engagement and reduce recommendation fatigue.",
                "validated_at": (datetime.now(timezone.utc) - timedelta(hours=16)).isoformat(),
                "validation_result": "validated"
            },
            {
                "id": 5,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat(),
                "learning_type": "risk_management",
                "metric_name": "max_parlay_legs",
                "old_value": 6,
                "new_value": 4,
                "confidence": 0.88,
                "context": "Learned from historical data that 4-leg parlays have optimal risk/reward ratio. 6-leg parlays showed diminishing returns.",
                "impact_assessment": "High impact - Will improve parlay success rate by 8-12% while maintaining EV.",
                "validated_at": (datetime.now(timezone.utc) - timedelta(hours=22)).isoformat(),
                "validation_result": "validated"
            }
        ]
        
        return {
            "events": mock_events[:limit],
            "total": len(mock_events),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain learning events data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-learning-performance")
async def get_brain_learning_performance(hours: int = Query(24, description="Hours of data to analyze")):
    """Get brain learning performance metrics"""
    try:
        # Return mock performance data
        return {
            "period_hours": hours,
            "total_events": 12,
            "validated_events": 12,
            "pending_events": 0,
            "rejected_events": 0,
            "validation_rate": 100.0,
            "avg_confidence": 0.81,
            "avg_improvement": 0.089,
            "learning_type_performance": [
                {
                    "learning_type": "model_improvement",
                    "total": 1,
                    "validated": 1,
                    "avg_confidence": 0.85,
                    "avg_improvement": 0.19
                },
                {
                    "learning_type": "parameter_tuning",
                    "total": 1,
                    "validated": 1,
                    "avg_confidence": 0.78,
                    "avg_improvement": -0.07
                },
                {
                    "learning_type": "market_pattern",
                    "total": 1,
                    "validated": 1,
                    "avg_confidence": 0.92,
                    "avg_improvement": 0.12
                },
                {
                    "learning_type": "user_behavior",
                    "total": 1,
                    "validated": 1,
                    "avg_confidence": 0.81,
                    "avg_improvement": 0.08
                },
                {
                    "learning_type": "risk_management",
                    "total": 1,
                    "validated": 1,
                    "avg_confidence": 0.88,
                    "avg_improvement": 0.10
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain learning performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-learning-status")
async def get_brain_learning_status():
    """Get current brain learning system status"""
    try:
        return {
            "status": "active",
            "active_learning": False,
            "last_learning_cycle": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "learning_algorithms": {
                "model_improvement": {
                    "status": "ready",
                    "last_run": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                    "success_rate": 0.85
                },
                "parameter_tuning": {
                    "status": "ready",
                    "last_run": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                    "success_rate": 0.78
                },
                "market_pattern": {
                    "status": "ready",
                    "last_run": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
                    "success_rate": 0.92
                },
                "user_behavior": {
                    "status": "ready",
                    "last_run": (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat(),
                    "success_rate": 0.81
                }
            },
            "auto_learning_enabled": True,
            "validation_queue_length": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain learning status data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-learning/run-cycle")
async def run_learning_cycle():
    """Run a brain learning cycle"""
    try:
        # Simulate running a learning cycle
        await asyncio.sleep(3)  # Simulate work
        
        return {
            "status": "completed",
            "events_generated": 12,
            "events_recorded": 12,
            "successful_algorithms": 12,
            "failed_algorithms": 0,
            "duration_ms": 3000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock learning cycle completed with 12 learning events"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-learning/validate")
async def validate_learning_event(learning_id: str = Query(..., description="Learning event ID to validate")):
    """Validate a specific learning event"""
    try:
        # Simulate validation
        await asyncio.sleep(1)  # Simulate validation work
        
        return {
            "status": "validated",
            "learning_id": learning_id,
            "validation_result": "validated",
            "actual_improvement": 0.19,
            "expected_improvement": 0.19,
            "validation_days": 7,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock validation completed for {learning_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "learning_id": learning_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-learning/record")
async def record_learning_event(learning_data: dict):
    """Record a new learning event"""
    try:
        # Simulate recording a learning event
        learning_id = f"learning-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "recorded",
            "learning_id": learning_id,
            "learning_type": learning_data.get("learning_type", "unknown"),
            "metric_name": learning_data.get("metric_name", "unknown"),
            "old_value": learning_data.get("old_value", 0),
            "new_value": learning_data.get("new_value", 0),
            "confidence": learning_data.get("confidence", 0.0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock learning event recorded"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", brain_learning_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += brain_learning_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Brain learning endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_brain_learning_endpoints())
