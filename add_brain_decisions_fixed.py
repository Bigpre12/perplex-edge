#!/usr/bin/env python3
"""
ADD BRAIN DECISIONS ENDPOINTS - Add brain decision tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_brain_decisions_endpoints():
    """Add brain decision endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the brain decisions endpoints
    brain_decisions_code = '''

# Brain Decision Tracking Endpoints
@router.get("/brain-decisions")
async def get_brain_decisions(limit: int = Query(50, description="Number of decisions to return")):
    """Get recent brain decisions"""
    try:
        # Return mock decision data for now
        mock_decisions = [
            {
                "id": 1,
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "category": "player_recommendation",
                "action": "recommend_drake_mayne_passing_yards_over",
                "reasoning": "Drake Maye has shown consistent passing performance with 65% completion rate over last 4 games. Weather conditions are favorable (no wind, 72F). Defense ranks 25th against pass allowing 245 yards per game. EV calculation shows 12% edge with 85% confidence.",
                "outcome": "successful",
                "details": {
                    "player_name": "Drake Maye",
                    "stat_type": "Passing Yards",
                    "line_value": 245.5,
                    "side": "over",
                    "odds": -110,
                    "edge": 0.12,
                    "confidence": 0.85
                },
                "duration_ms": 125,
                "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
            },
            {
                "id": 2,
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "category": "parlay_construction",
                "action": "build_two_leg_parlay",
                "reasoning": "Combining Drake Maye passing yards over (12% edge) with Sam Darnold passing TDs under (8% edge). Correlation analysis shows low correlation (r=0.15) between these outcomes. Combined EV of 22% with parlay odds of +275.",
                "outcome": "successful",
                "details": {
                    "parlay_type": "two_leg",
                    "total_ev": 0.22,
                    "parlay_odds": 275,
                    "legs": [
                        {
                            "player": "Drake Maye",
                            "stat": "Passing Yards",
                            "line": 245.5,
                            "side": "over",
                            "edge": 0.12
                        },
                        {
                            "player": "Sam Darnold",
                            "stat": "Passing TDs",
                            "line": 1.5,
                            "side": "under",
                            "edge": 0.08
                        }
                    ]
                },
                "duration_ms": 245,
                "correlation_id": "234e5678-e89b-12d3-a456-426614174001"
            }
        ]
        
        return {
            "decisions": mock_decisions[:limit],
            "total": len(mock_decisions),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain decisions data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-decisions-performance")
async def get_brain_decisions_performance(hours: int = Query(24, description="Hours of data to analyze")):
    """Get brain decision performance metrics"""
    try:
        # Return mock performance data
        return {
            "period_hours": hours,
            "total_decisions": 8,
            "successful_decisions": 6,
            "pending_decisions": 2,
            "failed_decisions": 0,
            "overall_success_rate": 75.0,
            "avg_duration_ms": 426.25,
            "category_performance": [
                {
                    "category": "player_recommendation",
                    "total": 2,
                    "successful": 2,
                    "success_rate": 100.0,
                    "avg_duration_ms": 111.5
                },
                {
                    "category": "parlay_construction",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 245.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock decision performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", brain_decisions_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += brain_decisions_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Brain decisions endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_brain_decisions_endpoints())
