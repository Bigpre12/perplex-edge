#!/usr/bin/env python3
"""
ADD BRAIN DECISIONS TO IMMEDIATE WORKING ROUTER
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

# Read the current immediate_working.py file
with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
    content = f.read()

# Add brain decisions endpoints at the end
brain_decisions_endpoints = """

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
                "reasoning": "Drake Maye has shown consistent passing performance with 65% completion rate over last 4 games. Weather conditions are favorable (no wind, 72°F). Defense ranks 25th against pass allowing 245 yards per game. EV calculation shows 12% edge with 85% confidence.",
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
            },
            {
                "id": 3,
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "category": "risk_management",
                "action": "approve_high_ev_parlay",
                "reasoning": "Parlay shows 22% combined EV which exceeds our 15% threshold. Individual legs have strong confidence scores (85% and 78%). Correlation is low (0.15) reducing risk. Total exposure within daily limits.",
                "outcome": "successful",
                "details": {
                    "parlay_ev": 0.22,
                    "threshold_ev": 0.15,
                    "confidence_scores": [0.85, 0.78],
                    "correlation": 0.15,
                    "risk_score": 0.3,
                    "risk_threshold": 0.5
                },
                "duration_ms": 156,
                "correlation_id": "345e6789-e89b-12d3-a456-426614174002"
            },
            {
                "id": 4,
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "category": "market_analysis",
                "action": "identify_market_inefficiency",
                "reasoning": "Detected significant line movement on Drake Maye passing yards from 235.5 to 245.5 over 6 hours. Volume analysis shows 65% of bets on over, yet line moved further up. Sharp money indicator suggests professional action.",
                "outcome": "pending",
                "details": {
                    "player": "Drake Maye",
                    "stat": "Passing Yards",
                    "initial_line": 235.5,
                    "current_line": 245.5,
                    "line_movement": 10.0,
                    "volume_distribution": {"over_percent": 0.65, "under_percent": 0.35},
                    "sharp_money_indicator": 0.78
                },
                "duration_ms": 189,
                "correlation_id": "456e7890-e89b-12d3-a456-426614174003"
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
                },
                {
                    "category": "risk_management",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 156.0
                },
                {
                    "category": "market_analysis",
                    "total": 1,
                    "successful": 0,
                    "success_rate": 0.0,
                    "avg_duration_ms": 189.0
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

@router.get("/brain-decisions-timeline")
async def get_brain_decisions_timeline(hours: int = Query(24, description="Hours of timeline data")):
    """Get brain decisions timeline"""
    try:
        # Return mock timeline data
        return {
            "period_hours": hours,
            "timeline": [
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                    "category": "user_feedback",
                    "action": "adjust_confidence_threshold",
                    "outcome": "pending",
                    "duration_ms": 456
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                    "category": "anomaly_response",
                    "action": "handle_high_error_rate",
                    "outcome": "successful",
                    "duration_ms": 890
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                    "category": "player_recommendation",
                    "action": "recommend_drake_mayne_passing_yards_over",
                    "outcome": "successful",
                    "duration_ms": 125
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                    "category": "parlay_construction",
                    "action": "build_two_leg_parlay",
                    "outcome": "successful",
                    "duration_ms": 245
                }
            ],
            "total_events": 4,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock timeline data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-decisions/record")
async def record_brain_decision(decision_data: dict):
    """Record a new brain decision"""
    try:
        # Simulate recording a decision
        correlation_id = f"mock-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "recorded",
            "correlation_id": correlation_id,
            "decision": {
                "category": decision_data.get("category", "unknown"),
                "action": decision_data.get("action", "unknown"),
                "reasoning": decision_data.get("reasoning", ""),
                "outcome": "pending"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock decision recorded"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-decisions/{correlation_id}/outcome")
async def update_decision_outcome(correlation_id: str, outcome: str = Query(..., description="Decision outcome")):
    """Update the outcome of a decision"""
    try:
        return {
            "status": "updated",
            "correlation_id": correlation_id,
            "outcome": outcome,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock outcome update for {correlation_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
"""

# Add the endpoints to the file
if "# Brain Anomaly Detection Endpoints" in content:
    # Add before the anomaly endpoints
    content = content.replace("# Brain Anomaly Detection Endpoints", brain_decisions_endpoints + "\n# Brain Anomaly Detection Endpoints")
else:
    # Add at the end
    content += brain_decisions_endpoints

# Write the updated content back
with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
    f.write(content)

print("Brain decisions endpoints added to immediate working router")
