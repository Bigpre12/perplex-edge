from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from datetime import datetime, timezone
import textwrap

router = APIRouter()

@router.get("/working-player-props")
async def get_working_player_props_immediate(
    sport_id: int = Query(31, description="Sport ID"),
    limit: int = Query(10, description="Number of props to return"),
    db: AsyncSession = Depends(get_db)
):
    """Immediate working player props endpoint"""
    try:
        # Return mock data for now - this will work immediately
        mock_props = [
            {
                'id': 1,
                'player': {'name': 'Drake Maye', 'position': 'QB'},
                'market': {'stat_type': 'Passing Yards', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 245.5,
                'odds': -110,
                'edge': 0.12,
                'confidence_score': 0.85,
                'generated_at': '2026-02-08T22:00:00Z'
            },
            {
                'id': 2,
                'player': {'name': 'Sam Darnold', 'position': 'QB'},
                'market': {'stat_type': 'Passing Yards', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 235.5,
                'odds': -105,
                'edge': 0.08,
                'confidence_score': 0.78,
                'generated_at': '2026-02-08T22:00:00Z'
            },
            {
                'id': 3,
                'player': {'name': 'Drake Maye', 'position': 'QB'},
                'market': {'stat_type': 'Passing TDs', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 1.5,
                'odds': -115,
                'edge': 0.15,
                'confidence_score': 0.82,
                'generated_at': '2026-02-08T22:00:00Z'
            },
            {
                'id': 4,
                'player': {'name': 'Sam Darnold', 'position': 'QB'},
                'market': {'stat_type': 'Passing TDs', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 1.5,
                'odds': -110,
                'edge': 0.12,
                'confidence_score': 0.75,
                'generated_at': '2026-02-08T22:00:00Z'
            },
            {
                'id': 5,
                'player': {'name': 'Drake Maye', 'position': 'QB'},
                'market': {'stat_type': 'Completions', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 22.5,
                'odds': -105,
                'edge': 0.09,
                'confidence_score': 0.73,
                'generated_at': '2026-02-08T22:00:00Z'
            }
        ]
        
        return {
            'items': mock_props[:limit],
            'total': len(mock_props),
            'sport_id': sport_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'items': [],
            'total': 0,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Brain Metrics Endpoints
@router.get("/brain-metrics")
async def get_brain_metrics(db: AsyncSession = Depends(get_db)):
    """Get current brain business metrics"""
    try:
        # Return mock data for now
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_recommendations": 220,
            "recommendation_hit_rate": 0.66,
            "average_ev": 0.22,
            "clv_trend": 0.28,
            "prop_volume": 480,
            "user_confidence_score": 0.92,
            "api_response_time_ms": 85,
            "error_rate": 0.012,
            "throughput": 37.4,
            "system_metrics": {
                "cpu_usage": 0.67,
                "memory_usage": 0.46,
                "disk_usage": 0.48
            },
            "note": "Mock brain metrics data"
        }
            
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-metrics-summary")
async def get_brain_metrics_summary(
    hours: int = Query(24, description="Hours of data to summarize")
):
    """Get brain metrics summary for the last N hours"""
    try:
        # Return mock summary
        return {
            "period_hours": hours,
            "total_records": 10,
            "total_recommendations": 1850,
            "average_hit_rate": 0.58,
            "average_ev": 0.16,
            "max_hit_rate": 0.66,
            "min_hit_rate": 0.49,
            "avg_cpu_usage": 0.52,
            "avg_memory_usage": 0.56,
            "avg_disk_usage": 0.53,
            "note": "Mock brain metrics summary"
        }
            
    except Exception as e:
        return {
            "error": str(e),
            "period_hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



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



# Brain Healing System Endpoints
@router.get("/brain-healing-actions")
async def get_brain_healing_actions(limit: int = Query(50, description="Number of actions to return")):
    """Get recent brain healing actions"""
    try:
        # Return mock healing action data for now
        mock_actions = [
            {
                "id": 1,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "action": "increase_database_pool_size",
                "target": "database_connection_pool",
                "reason": "Database connection pool exhausted causing 8% error rate. Current pool size of 10 insufficient for peak load.",
                "result": "successful",
                "duration_ms": 2340,
                "details": {
                    "initial_pool_size": 10,
                    "new_pool_size": 20,
                    "error_rate_before": 0.08,
                    "error_rate_after": 0.015
                },
                "success_rate": 0.85,
                "consecutive_failures": 0
            },
            {
                "id": 2,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "action": "add_response_caching_layer",
                "target": "api_response_time",
                "reason": "API response time increased to 450ms average (threshold: 200ms). Identified bottleneck in player props calculation.",
                "result": "successful",
                "duration_ms": 4560,
                "details": {
                    "avg_response_time_before": 450,
                    "avg_response_time_after": 95,
                    "cache_hit_rate": 0.78,
                    "cache_ttl_seconds": 300
                },
                "success_rate": 0.92,
                "consecutive_failures": 0
            },
            {
                "id": 3,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "action": "restart_recommendation_service",
                "target": "memory_leak_recommendation_engine",
                "reason": "Memory usage consistently increasing to 95% over 2-hour period. Memory leak detected in recommendation engine.",
                "result": "successful",
                "duration_ms": 12340,
                "details": {
                    "memory_usage_before": 0.95,
                    "memory_usage_after": 0.42,
                    "service_downtime_ms": 2340,
                    "root_cause": "unreleased model references"
                },
                "success_rate": 0.78,
                "consecutive_failures": 1
            },
            {
                "id": 4,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                "action": "retrain_prediction_model",
                "target": "model_accuracy_degradation",
                "reason": "Model accuracy dropped from 68% to 52% over 24 hours. Detected concept drift in passing yards predictions.",
                "result": "successful",
                "duration_ms": 45670,
                "details": {
                    "accuracy_before": 0.52,
                    "accuracy_after": 0.71,
                    "model_type": "passing_yards_predictor",
                    "training_data_points": 15000
                },
                "success_rate": 0.88,
                "consecutive_failures": 0
            },
            {
                "id": 5,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "action": "switch_to_backup_odds_provider",
                "target": "external_odds_api_failure",
                "reason": "Primary odds API provider experiencing 40% timeout rate. Backup provider available with 99% uptime.",
                "result": "successful",
                "duration_ms": 890,
                "details": {
                    "primary_provider": "the_odds_api",
                    "backup_provider": "sportsdata_io",
                    "timeout_rate_before": 0.40,
                    "timeout_rate_after": 0.01
                },
                "success_rate": 0.95,
                "consecutive_failures": 0
            }
        ]
        
        return {
            "actions": mock_actions[:limit],
            "total": len(mock_actions),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain healing actions data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-healing-performance")
async def get_brain_healing_performance(hours: int = Query(24, description="Hours of data to analyze")):
    """Get brain healing performance metrics"""
    try:
        # Return mock performance data
        return {
            "period_hours": hours,
            "total_actions": 9,
            "successful_actions": 8,
            "pending_actions": 1,
            "failed_actions": 0,
            "overall_success_rate": 88.9,
            "avg_duration_ms": 13456.7,
            "avg_success_rate": 0.89,
            "action_performance": [
                {
                    "action": "switch_to_backup_odds_provider",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 890.0,
                    "avg_success_rate": 0.95
                },
                {
                    "action": "add_response_caching_layer",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 4560.0,
                    "avg_success_rate": 0.92
                },
                {
                    "action": "increase_database_pool_size",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 2340.0,
                    "avg_success_rate": 0.85
                },
                {
                    "action": "retrain_prediction_model",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 45670.0,
                    "avg_success_rate": 0.88
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock healing performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-healing-status")
async def get_brain_healing_status():
    """Get current brain healing system status"""
    try:
        return {
            "status": "healthy",
            "active_healing": False,
            "last_healing_cycle": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
            "healing_strategies": {
                "database_connection": {
                    "triggers": 2,
                    "last_action": "increase_database_pool_size",
                    "success_rate": 0.85
                },
                "api_response_time": {
                    "triggers": 2,
                    "last_action": "add_response_caching_layer",
                    "success_rate": 0.92
                },
                "memory_usage": {
                    "triggers": 2,
                    "last_action": "restart_recommendation_service",
                    "success_rate": 0.78
                },
                "model_accuracy": {
                    "triggers": 1,
                    "last_action": "retrain_prediction_model",
                    "success_rate": 0.88
                }
            },
            "auto_healing_enabled": True,
            "monitoring_active": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock healing status data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-healing/run-cycle")
async def run_healing_cycle():
    """Run a brain healing cycle"""
    try:
        # Simulate running a healing cycle
        await asyncio.sleep(2)  # Simulate work
        
        return {
            "status": "completed",
            "triggers_found": 0,
            "actions_executed": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "duration_ms": 2000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock healing cycle completed - no triggers detected"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-healing/trigger")
async def trigger_healing_action(healing_data: dict):
    """Manually trigger a healing action"""
    try:
        # Simulate triggering a healing action
        action = healing_data.get("action", "scale_resources")
        target = healing_data.get("target", "database_connection")
        
        await asyncio.sleep(1)  # Simulate work
        
        return {
            "status": "triggered",
            "action": action,
            "target": target,
            "correlation_id": f"healing-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "estimated_duration_ms": 5000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock healing action triggered: {action} for {target}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Brain Health Monitoring Endpoints
@router.get("/brain-health-status")
async def get_brain_health_status():
    """Get overall brain system health status"""
    try:
        return {
            "status": "healthy",
            "message": "All brain system components are operating normally",
            "overall_score": 0.87,
            "component_count": 12,
            "status_counts": {
                "healthy": 10,
                "warning": 2,
                "critical": 0,
                "error": 0
            },
            "component_health": {
                "database_connection_pool": {
                    "status": "healthy",
                    "score": 0.95,
                    "message": "Database connection pool operating normally",
                    "response_time_ms": 23
                },
                "api_response_time": {
                    "status": "healthy",
                    "score": 0.92,
                    "message": "API response times are optimal",
                    "response_time_ms": 12
                },
                "model_accuracy": {
                    "status": "healthy",
                    "score": 0.82,
                    "message": "Model accuracy is within acceptable range",
                    "response_time_ms": 34
                },
                "brain_decision_system": {
                    "status": "healthy",
                    "score": 0.82,
                    "message": "Brain decision system is functioning optimally",
                    "response_time_ms": 34
                },
                "brain_healing_system": {
                    "status": "healthy",
                    "score": 0.91,
                    "message": "Brain healing system is ready",
                    "response_time_ms": 25
                }
            },
            "monitoring_active": True,
            "auto_healing_enabled": True,
            "last_check": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain health status data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-health-checks")
async def get_brain_health_checks(limit: int = Query(50, description="Number of checks to return")):
    """Get recent brain health checks"""
    try:
        mock_checks = [
            {
                "id": 1,
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "component": "database_connection_pool",
                "status": "healthy",
                "message": "Database connection pool operating normally",
                "details": {
                    "active_connections": 8,
                    "max_connections": 20,
                    "pool_utilization": 0.40,
                    "avg_response_time_ms": 45,
                    "health_score": 0.95
                },
                "response_time_ms": 23,
                "error_count": 0
            },
            {
                "id": 2,
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat(),
                "component": "api_response_time",
                "status": "healthy",
                "message": "API response times are optimal",
                "details": {
                    "avg_response_time_ms": 95,
                    "requests_per_second": 45.2,
                    "cache_hit_rate": 0.78,
                    "health_score": 0.92
                },
                "response_time_ms": 12,
                "error_count": 0
            }
        ]
        
        return {
            "checks": mock_checks[:limit],
            "total": len(mock_checks),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain health checks data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-health-performance")
async def get_brain_health_performance(hours: int = Query(24, description="Hours of data to analyze")):
    """Get brain health performance metrics"""
    try:
        return {
            "period_hours": hours,
            "total_checks": 18,
            "healthy_checks": 16,
            "warning_checks": 2,
            "critical_checks": 0,
            "error_checks": 0,
            "overall_success_rate": 88.9,
            "avg_response_time_ms": 67.8,
            "avg_error_count": 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain health performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-health/run-check")
async def run_health_check(component: str = Query(..., description="Component to check")):
    """Run a health check for a specific component"""
    try:
        # Mock health check result
        mock_results = {
            "database_connection_pool": {
                "status": "healthy",
                "message": "Database connection pool operating normally",
                "response_time_ms": 23,
                "health_score": 0.95
            },
            "api_response_time": {
                "status": "healthy",
                "message": "API response times are optimal",
                "response_time_ms": 12,
                "health_score": 0.92
            }
        }
        
        result = mock_results.get(component, {
            "status": "error",
            "message": f"Unknown component: {component}",
            "response_time_ms": 0,
            "health_score": 0.0
        })
        
        return {
            "status": "completed",
            "component": component,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock health check completed for {component}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-health/run-all-checks")
async def run_all_health_checks():
    """Run health checks for all components"""
    try:
        return {
            "status": "completed",
            "total_checks": 12,
            "healthy": 10,
            "warning": 2,
            "critical": 0,
            "error": 0,
            "overall_score": 0.87,
            "duration_ms": 500,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock all health checks completed"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



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



# Game Results Tracking Endpoints
@router.get("/game-results")
async def get_game_results(date: str = Query(None, description="Date to filter (YYYY-MM-DD)"), sport_id: int = Query(None, description="Sport ID to filter")):
    """Get game results for a specific date"""
    try:
        # Return mock game results data for now
        mock_results = [
            {
                "id": 1,
                "game_id": 1001,
                "external_fixture_id": "nfl_2026_02_08_kc_buf",
                "home_score": 31,
                "away_score": 28,
                "period_scores": {
                    "Q1": {"home": 7, "away": 7},
                    "Q2": {"home": 10, "away": 14},
                    "Q3": {"home": 7, "away": 0},
                    "Q4": {"home": 7, "away": 7}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            },
            {
                "id": 2,
                "game_id": 1002,
                "external_fixture_id": "nfl_2026_02_08_phi_nyg",
                "home_score": 24,
                "away_score": 17,
                "period_scores": {
                    "Q1": {"home": 3, "away": 7},
                    "Q2": {"home": 14, "away": 3},
                    "Q3": {"home": 0, "away": 7},
                    "Q4": {"home": 7, "away": 0}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
            },
            {
                "id": 3,
                "game_id": 1003,
                "external_fixture_id": "nfl_2026_02_08_dal_sf",
                "home_score": 35,
                "away_score": 42,
                "period_scores": {
                    "Q1": {"home": 14, "away": 7},
                    "Q2": {"home": 7, "away": 14},
                    "Q3": {"home": 7, "away": 14},
                    "Q4": {"home": 7, "away": 7}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()
            },
            {
                "id": 4,
                "game_id": 2001,
                "external_fixture_id": "nba_2026_02_08_lal_bos",
                "home_score": 118,
                "away_score": 112,
                "period_scores": {
                    "Q1": {"home": 28, "away": 24},
                    "Q2": {"home": 32, "away": 30},
                    "Q3": {"home": 29, "away": 28},
                    "Q4": {"home": 29, "away": 30}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 5,
                "game_id": 1005,
                "external_fixture_id": "nfl_2026_02_09_ari_sea",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            }
        ]
        
        return {
            "results": mock_results,
            "total": len(mock_results),
            "date": date or datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/pending")
async def get_pending_games():
    """Get all pending games"""
    try:
        # Return mock pending games data for now
        mock_pending = [
            {
                "id": 5,
                "game_id": 1005,
                "external_fixture_id": "nfl_2026_02_09_ari_sea",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            },
            {
                "id": 6,
                "game_id": 2004,
                "external_fixture_id": "nba_2026_02_09_chi_cle",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        return {
            "pending_games": mock_pending,
            "total": len(mock_pending),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock pending games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/statistics")
async def get_game_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get game statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_games": 8,
            "settled_games": 6,
            "pending_games": 2,
            "avg_home_score": 28.5,
            "avg_away_score": 26.8,
            "avg_total_score": 55.3,
            "home_wins": 4,
            "away_wins": 2,
            "ties": 0,
            "home_win_rate": 66.7,
            "away_win_rate": 33.3,
            "tie_rate": 0.0,
            "by_sport": [
                {
                    "sport_id": 32,
                    "total_games": 5,
                    "settled_games": 4,
                    "avg_home_score": 30.0,
                    "avg_away_score": 28.8,
                    "home_wins": 3,
                    "away_wins": 1
                },
                {
                    "sport_id": 30,
                    "total_games": 3,
                    "settled_games": 2,
                    "avg_home_score": 25.5,
                    "avg_away_score": 24.0,
                    "home_wins": 1,
                    "away_wins": 1
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/{game_id}")
async def get_game_result_detail(game_id: int):
    """Get detailed game result by ID"""
    try:
        # Return mock detailed game result data for now
        mock_detail = {
            "id": 1,
            "game_id": game_id,
            "external_fixture_id": "nfl_2026_02_08_kc_buf",
            "home_score": 31,
            "away_score": 28,
            "period_scores": {
                "Q1": {"home": 7, "away": 7},
                "Q2": {"home": 10, "away": 14},
                "Q3": {"home": 7, "away": 0},
                "Q4": {"home": 7, "away": 7}
            },
            "is_settled": True,
            "settled_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "game_details": {
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "venue": "Arrowhead Stadium",
                "date": "2026-02-08",
                "start_time": "20:20 UTC",
                "duration": "3:15:00",
                "attendance": 76416,
                "weather": "Clear, 72°F"
            },
            "betting_summary": {
                "total_bets": 15420,
                "total_wagered": 3084000,
                "total_profit": 185040,
                "roi_percent": 6.0,
                "popular_bets": {
                    "moneyline": "KC -145",
                    "spread": "KC -2.5",
                    "total": "Over 59.5"
                }
            }
        }
        
        return mock_detail
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/game-results/settle")
async def settle_game_results(settlement_data: dict):
    """Settle game results"""
    try:
        # Simulate settling game results
        games_to_settle = settlement_data.get("games", [])
        
        settled_count = 0
        failed_count = 0
        settlement_results = []
        
        for game in games_to_settle:
            game_id = game.get("game_id")
            home_score = game.get("home_score")
            away_score = game.get("away_score")
            
            if not all([game_id, home_score is not None, away_score is not None]):
                failed_count += 1
                settlement_results.append({
                    "game_id": game_id,
                    "status": "failed",
                    "error": "Missing required fields"
                })
                continue
            
            # Simulate successful settlement
            settled_count += 1
            settlement_results.append({
                "game_id": game_id,
                "status": "settled",
                "home_score": home_score,
                "away_score": away_score,
                "settled_at": datetime.now(timezone.utc).isoformat()
            })
        
        return {
            "total_processed": len(games_to_settle),
            "settled_count": settled_count,
            "failed_count": failed_count,
            "settlement_results": settlement_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock settlement completed for {settled_count} games"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/game-results/create")
async def create_game_result(game_data: dict):
    """Create a new game result record"""
    try:
        # Simulate creating a game result
        game_id = game_data.get("game_id")
        external_fixture_id = game_data.get("external_fixture_id")
        
        if not all([game_id, external_fixture_id]):
            return {
                "status": "error",
                "error": "Missing required fields: game_id, external_fixture_id",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "created",
            "game_id": game_id,
            "external_fixture_id": external_fixture_id,
            "home_score": None,
            "away_score": None,
            "is_settled": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game result created for {game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.put("/game-results/{game_id}")
async def update_game_result(game_id: int, result_data: dict):
    """Update game result with scores"""
    try:
        # Simulate updating game result
        home_score = result_data.get("home_score")
        away_score = result_data.get("away_score")
        period_scores = result_data.get("period_scores", {})
        
        if not all([home_score is not None, away_score is not None]):
            return {
                "status": "error",
                "error": "Missing required fields: home_score, away_score",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "updated",
            "game_id": game_id,
            "home_score": home_score,
            "away_score": away_score,
            "period_scores": period_scores,
            "is_settled": True,
            "settled_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game result updated for {game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Games Management Endpoints
@router.get("/games")
async def get_games(sport_id: int = Query(None, description="Sport ID to filter"), 
                  status: str = Query(None, description="Game status to filter"),
                  start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
                  end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
                  limit: int = Query(50, description="Number of games to return")):
    """Get games with optional filters"""
    try:
        # Return mock games data for now
        mock_games = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 4,
                "sport_id": 32,
                "external_game_id": "nfl_ari_sea_20260209",
                "home_team_id": 390,
                "away_team_id": 391,
                "home_team_name": "Arizona Cardinals",
                "away_team_name": "Seattle Seahawks",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 5,
                "sport_id": 30,
                "external_game_id": "nba_chi_cle_20260209",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Chicago Bulls",
                "away_team_name": "Cleveland Cavaliers",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply filters
        filtered_games = mock_games
        if sport_id:
            filtered_games = [g for g in filtered_games if g['sport_id'] == sport_id]
        if status:
            filtered_games = [g for g in filtered_games if g['status'] == status]
        if start_date:
            filtered_games = [g for g in filtered_games if g['start_time'][:10] >= start_date]
        if end_date:
            filtered_games = [g for g in filtered_games if g['start_time'][:10] <= end_date]
        
        return {
            "games": filtered_games[:limit],
            "total": len(filtered_games),
            "filters": {
                "sport_id": sport_id,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/upcoming")
async def get_upcoming_games(hours: int = Query(24, description="Hours ahead to look"), 
                          sport_id: int = Query(None, description="Sport ID to filter")):
    """Get upcoming games"""
    try:
        # Return mock upcoming games data for now
        mock_upcoming = [
            {
                "id": 4,
                "sport_id": 32,
                "external_game_id": "nfl_ari_sea_20260209",
                "home_team_id": 390,
                "away_team_id": 391,
                "home_team_name": "Arizona Cardinals",
                "away_team_name": "Seattle Seahawks",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 5,
                "sport_id": 30,
                "external_game_id": "nba_chi_cle_20260209",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Chicago Bulls",
                "away_team_name": "Cleveland Cavaliers",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 6,
                "sport_id": 32,
                "external_game_id": "nfl_gb_phi_20260209",
                "home_team_id": 295,
                "away_team_id": 84,
                "home_team_name": "Green Bay Packers",
                "away_team_name": "Philadelphia Eagles",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_upcoming = [g for g in mock_upcoming if g['sport_id'] == sport_id]
        
        return {
            "upcoming_games": mock_upcoming,
            "total": len(mock_upcoming),
            "hours": hours,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock upcoming games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/recent")
async def get_recent_games(hours: int = Query(24, description="Hours back to look"), 
                        sport_id: int = Query(None, description="Sport ID to filter")):
    """Get recent games"""
    try:
        # Return mock recent games data for now
        mock_recent = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_recent = [g for g in mock_recent if g['sport_id'] == sport_id]
        
        return {
            "recent_games": mock_recent,
            "total": len(mock_recent),
            "hours": hours,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock recent games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/statistics")
async def get_games_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get games statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_games": 15,
            "final_games": 8,
            "scheduled_games": 7,
            "in_progress_games": 0,
            "cancelled_games": 0,
            "postponed_games": 0,
            "suspended_games": 0,
            "by_sport": [
                {
                    "sport_id": 32,
                    "total_games": 10,
                    "final_games": 6,
                    "scheduled_games": 4,
                    "in_progress_games": 0
                },
                {
                    "sport_id": 30,
                    "total_games": 5,
                    "final_games": 2,
                    "scheduled_games": 3,
                    "in_progress_games": 0
                }
            ],
            "by_date": [
                {
                    "date": "2026-02-08",
                    "total_games": 8,
                    "final_games": 5,
                    "scheduled_games": 3
                },
                {
                    "date": "2026-02-09",
                    "total_games": 7,
                    "final_games": 3,
                    "scheduled_games": 4
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock games statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/schedule")
async def get_game_schedule(start_date: str = Query(..., description="Start date (YYYY-MM-DD)"), 
                             end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
                             sport_id: int = Query(None, description="Sport ID to filter")):
    """Get game schedule for date range"""
    try:
        # Return mock schedule data for now
        mock_schedule = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply date and sport filters
        if sport_id:
            mock_schedule = [g for g in mock_schedule if g['sport_id'] == sport_id]
        
        if start_date and end_date:
            mock_schedule = [g for g in mock_schedule if start_date <= g['start_time'][:10] <= end_date]
        
        return {
            "schedule": mock_schedule,
            "start_date": start_date,
            "end_date": end_date,
            "sport_id": sport_id,
            "total": len(mock_schedule),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game schedule data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/{game_id}")
async def get_game_detail(game_id: int):
    """Get detailed game information"""
    try:
        # Return mock detailed game data for now
        mock_detail = {
            "id": game_id,
            "sport_id": 32,
            "external_game_id": "nfl_kc_buf_20260208",
            "home_team_id": 48,
            "away_team_id": 83,
            "home_team_name": "Kansas City Chiefs",
            "away_team_name": "Buffalo Bills",
            "sport_name": "NFL",
            "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "status": "final",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "season_id": 2026,
            "game_details": {
                "venue": "Arrowhead Stadium",
                "location": "Kansas City, MO",
                "attendance": 76416,
                "weather": "Clear, 72°F",
                "duration": "3:15:00",
                "broadcast": "CBS",
                "referees": ["John Smith", "Mike Johnson", "Bob Wilson"]
            },
            "betting_summary": {
                "total_bets": 15420,
                "total_wagered": 3084000,
                "total_profit": 185040,
                "roi_percent": 6.0,
                "popular_bets": {
                    "moneyline": "KC -145",
                    "spread": "KC -2.5",
                    "total": "Over 59.5"
                }
            }
        }
        
        return mock_detail
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/games/create")
async def create_game(game_data: dict):
    """Create a new game"""
    try:
        # Simulate creating a game
        game_id = game_data.get("game_id")
        external_game_id = game_data.get("external_game_id")
        home_team_id = game_data.get("home_team_id")
        away_team_id = game_data.get("away_team_id")
        start_time = game_data.get("start_time")
        
        if not all([game_id, external_game_id, home_team_id, away_team_id, start_time]):
            return {
                "status": "error",
                "error": "Missing required fields: game_id, external_game_id, home_team_id, away_team_id, start_time",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "created",
            "game_id": game_id,
            "external_game_id": external_game_id,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "start_time": start_time,
            "status": "scheduled",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game created for {external_game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.put("/games/{game_id}/status")
async def update_game_status(game_id: int, status: str = Query(..., description="New game status")):
    """Update game status"""
    try:
        # Simulate updating game status
        valid_statuses = ["scheduled", "in_progress", "final", "cancelled", "postponed", "suspended"]
        
        if status not in valid_statuses:
            return {
                "status": "error",
                "error": f"Invalid status: {status}. Valid statuses: {', '.join(valid_statuses)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "updated",
            "game_id": game_id,
            "new_status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game {game_id} status updated to {status}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/search")
async def search_games(query: str = Query(..., description="Search query"), 
                        sport_id: int = Query(None, description="Sport ID to filter"),
                        limit: int = Query(20, description="Number of results to return")):
    """Search games by external ID or team names"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                g for g in mock_results 
                if query_lower in g['external_game_id'].lower() or 
                   query_lower in g['home_team_name'].lower() or 
                   query_lower in g['away_team_name'].lower()
            ]
        
        # Apply sport filter
        if sport_id:
            mock_results = [g for g in mock_results if g['sport_id'] == sport_id]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "sport_id": sport_id,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Historical Odds NCAAB Endpoints
@router.get("/historical-odds-ncaab")
async def get_historical_odds_ncaab(game_id: int = Query(None, description="Game ID to filter"), 
                                  bookmaker: str = Query(None, description="Bookmaker to filter"),
                                  team: str = Query(None, description="Team name to filter"),
                                  days: int = Query(30, description="Days of data to return"),
                                  limit: int = Query(50, description="Number of odds to return")):
    """Get NCAA basketball historical odds with optional filters"""
    try:
        # Return mock historical odds data for now
        mock_odds = [
            {
                "id": 1,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 2,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 3,
                "sport": 32,
                "game_id": 1002,
                "home_team": "Kansas Jayhawks",
                "away_team": "Kentucky Wildcats",
                "home_odds": -110,
                "away_odds": -110,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat()
            },
            {
                "id": 4,
                "sport": 32,
                "game_id": 1003,
                "home_team": "UCLA Bruins",
                "away_team": "Gonzaga Bulldogs",
                "home_odds": 180,
                "away_odds": -220,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat(),
                "result": "away_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat()
            },
            {
                "id": 5,
                "sport": 32,
                "game_id": 1004,
                "home_team": "Michigan Wolverines",
                "away_team": "Ohio State Buckeyes",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_odds = mock_odds
        if game_id:
            filtered_odds = [o for o in filtered_odds if o['game_id'] == game_id]
        if bookmaker:
            filtered_odds = [o for o in filtered_odds if o['bookmaker'].lower() == bookmaker.lower()]
        if team:
            filtered_odds = [o for o in filtered_odds if team.lower() in o['home_team'].lower() or team.lower() in o['away_team'].lower()]
        
        return {
            "odds": filtered_odds[:limit],
            "total": len(filtered_odds),
            "filters": {
                "game_id": game_id,
                "bookmaker": bookmaker,
                "team": team,
                "days": days,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock NCAA basketball historical odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/game/{game_id}")
async def get_odds_by_game(game_id: int):
    """Get odds history for a specific game"""
    try:
        # Return mock odds history for a specific game
        mock_odds_history = [
            {
                "id": 1,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 2,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 3,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "bookmaker": "BetMGM",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 4,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat()
            },
            {
                "id": 5,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat()
            }
        ]
        
        return {
            "game_id": game_id,
            "home_team": "Duke Blue Devils",
            "away_team": "North Carolina Tar Heels",
            "odds_history": mock_odds_history,
            "total_snapshots": len(mock_odds_history),
            "bookmakers": list(set(o['bookmaker'] for o in mock_odds_history)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds history for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/movements/{game_id}")
async def get_odds_movements(game_id: int):
    """Get odds movements for a specific game"""
    try:
        # Return mock odds movements data
        mock_movements = [
            {
                "bookmaker": "DraftKings",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "DraftKings",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "home_movement": 10,
                "away_movement": -10,
                "draw_movement": 0,
                "prev_home_odds": -150,
                "prev_away_odds": 130,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "home_movement": -15,
                "away_movement": 15,
                "draw_movement": 0,
                "prev_home_odds": -145,
                "prev_away_odds": 125,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "BetMGM",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            }
        ]
        
        return {
            "game_id": game_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "bookmakers": list(set(m['bookmaker'] for m in mock_movements)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/comparison/{game_id}")
async def get_bookmaker_comparison(game_id: int):
    """Compare odds across bookmakers for a specific game"""
    try:
        # Return mock bookmaker comparison data
        mock_comparison = [
            {
                "bookmaker": "DraftKings",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "BetMGM",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "Caesars",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "PointsBet",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win"
            }
        ]
        
        # Calculate best odds
        best_home_odds = max(mock_comparison, key=lambda x: x['home_odds'])
        best_away_odds = min(mock_comparison, key=lambda x: x['away_odds'])
        
        return {
            "game_id": game_id,
            "home_team": "Duke Blue Devils",
            "away_team": "North Carolina Tar Heels",
            "comparison": mock_comparison,
            "best_home_odds": {
                "bookmaker": best_home_odds['bookmaker'],
                "odds": best_home_odds['home_odds']
            },
            "best_away_odds": {
                "bookmaker": best_away_odds['bookmaker'],
                "odds": best_away_odds['away_odds']
            },
            "total_bookmakers": len(mock_comparison),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock bookmaker comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/statistics")
async def get_historical_odds_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get NCAA basketball historical odds statistics"""
    try:
        # Return mock statistics data
        mock_stats = {
            "period_days": days,
            "total_odds": 28,
            "unique_games": 8,
            "unique_bookmakers": 6,
            "unique_teams": 16,
            "home_wins": 18,
            "away_wins": 10,
            "pending_games": 0,
            "home_win_rate": 64.3,
            "avg_home_odds": -45.7,
            "avg_away_odds": -45.7,
            "avg_draw_odds": None,
            "by_bookmaker": [
                {
                    "bookmaker": "DraftKings",
                    "total_odds": 8,
                    "unique_games": 8,
                    "home_wins": 5,
                    "away_wins": 3,
                    "pending_games": 0,
                    "avg_home_odds": -48.8,
                    "avg_away_odds": -48.8,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "FanDuel",
                    "total_odds": 6,
                    "unique_games": 6,
                    "home_wins": 4,
                    "away_wins": 2,
                    "pending_games": 0,
                    "avg_home_odds": -42.5,
                    "avg_away_odds": -42.5,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "BetMGM",
                    "total_odds": 5,
                    "unique_games": 5,
                    "home_wins": 3,
                    "away_wins": 2,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "Caesars",
                    "total_odds": 4,
                    "unique_games": 4,
                    "home_wins": 3,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -37.5,
                    "avg_away_odds": -37.5,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "PointsBet",
                    "total_odds": 3,
                    "unique_games": 3,
                    "home_wins": 2,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "Bet365",
                    "total_odds": 2,
                    "unique_games": 2,
                    "home_wins": 1,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                }
            ],
            "by_team": [
                {
                    "team": "Duke Blue Devils",
                    "total_games": 5,
                    "home_wins": 5,
                    "home_losses": 0,
                    "avg_home_odds": -150.0,
                    "avg_away_odds": 130.0
                },
                {
                    "team": "Kansas Jayhawks",
                    "total_games": 4,
                    "home_wins": 4,
                    "home_losses": 0,
                    "avg_home_odds": -110.0,
                    "avg_away_odds": -110.0
                },
                {
                    "team": "UCLA Bruins",
                    "total_games": 4,
                    "home_wins": 0,
                    "home_losses": 4,
                    "avg_home_odds": 180.0,
                    "avg_away_odds": -220.0
                },
                {
                    "team": "Michigan Wolverines",
                    "total_games": 3,
                    "home_wins": 3,
                    "home_losses": 0,
                    "avg_home_odds": -125.0,
                    "avg_away_odds": 105.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock NCAA basketball historical odds statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/efficiency")
async def get_odds_efficiency(days: int = Query(30, description="Days of data to analyze")):
    """Analyze odds efficiency and accuracy"""
    try:
        # Return mock efficiency analysis data
        mock_efficiency = {
            "period_days": days,
            "bookmaker_efficiency": [
                {
                    "bookmaker": "DraftKings",
                    "total_games": 8,
                    "home_wins": 5,
                    "away_wins": 3,
                    "avg_implied_home_prob": 60.0,
                    "avg_implied_away_prob": 40.0,
                    "actual_home_win_rate": 62.5,
                    "home_accuracy": 97.5,
                    "away_accuracy": 97.5,
                    "overall_accuracy": 97.5,
                    "home_edge": 2.5,
                    "away_edge": -2.5
                },
                {
                    "bookmaker": "FanDuel",
                    "total_games": 6,
                    "home_wins": 4,
                    "away_wins": 2,
                    "avg_implied_home_prob": 58.3,
                    "avg_implied_away_prob": 41.7,
                    "actual_home_win_rate": 66.7,
                    "home_accuracy": 91.6,
                    "away_accuracy": 91.6,
                    "overall_accuracy": 91.6,
                    "home_edge": 8.4,
                    "away_edge": -8.4
                },
                {
                    "bookmaker": "BetMGM",
                    "total_games": 5,
                    "home_wins": 3,
                    "away_wins": 2,
                    "avg_implied_home_prob": 60.0,
                    "avg_implied_away_prob": 40.0,
                    "actual_home_win_rate": 60.0,
                    "home_accuracy": 100.0,
                    "away_accuracy": 100.0,
                    "overall_accuracy": 100.0,
                    "home_edge": 0.0,
                    "away_edge": 0.0
                },
                {
                    "bookmaker": "Caesars",
                    "total_games": 4,
                    "home_wins": 3,
                    "away_wins": 1,
                    "avg_implied_home_prob": 56.3,
                    "avg_implied_away_prob": 43.8,
                    "actual_home_win_rate": 75.0,
                    "home_accuracy": 81.3,
                    "away_accuracy": 81.3,
                    "overall_accuracy": 81.3,
                    "home_edge": 18.7,
                    "away_edge": -18.7
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/search")
async def search_historical_odds(query: str = Query(..., description="Search query"), 
                                 days: int = Query(30, description="Days of data to search"),
                                 limit: int = Query(20, description="Number of results to return")):
    """Search NCAA basketball historical odds"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                o for o in mock_results 
                if query_lower in o['home_team'].lower() or 
                   query_lower in o['away_team'].lower() or 
                   query_lower in o['bookmaker'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "days": days,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Historical Performance Tracking Endpoints
@router.get("/historical-performances")
async def get_historical_performances(player: str = Query(None, description="Player name to filter"), 
                                      stat_type: str = Query(None, description="Stat type to filter"),
                                      limit: int = Query(50, description="Number of performances to return")):
    """Get historical performances with optional filters"""
    try:
        # Return mock historical performance data for now
        mock_performances = [
            {
                "id": 1,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "total_picks": 156,
                "hits": 98,
                "misses": 58,
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "total_picks": 89,
                "hits": 62,
                "misses": 27,
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "total_picks": 142,
                "hits": 87,
                "misses": 55,
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 4,
                "player_name": "LeBron James",
                "stat_type": "points",
                "total_picks": 178,
                "hits": 112,
                "misses": 66,
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "total_picks": 189,
                "hits": 121,
                "misses": 68,
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 6,
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "total_picks": 89,
                "hits": 56,
                "misses": 33,
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 7,
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "total_picks": 1245,
                "hits": 789,
                "misses": 456,
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 8,
                "player_name": "Sam Darnold",
                "stat_type": "passing_yards",
                "total_picks": 45,
                "hits": 22,
                "misses": 23,
                "hit_rate_percentage": 48.89,
                "avg_ev": -0.0234,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_performances = mock_performances
        if player:
            filtered_performances = [p for p in filtered_performances if player.lower() in p['player_name'].lower()]
        if stat_type:
            filtered_performances = [p for p in filtered_performances if stat_type.lower() in p['stat_type'].lower()]
        
        return {
            "performances": filtered_performances[:limit],
            "total": len(filtered_performances),
            "filters": {
                "player": player,
                "stat_type": stat_type,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock historical performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/top")
async def get_top_performers(limit: int = Query(10, description="Number of top performers to return"), 
                               stat_type: str = Query(None, description="Stat type to filter")):
    """Get top performers by hit rate"""
    try:
        # Return mock top performers data
        mock_top_performers = [
            {
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "total_picks": 189,
                "hits": 121,
                "misses": 68
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "total_picks": 89,
                "hits": 62,
                "misses": 27
            },
            {
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "total_picks": 89,
                "hits": 56,
                "misses": 33
            },
            {
                "player_name": "LeBron James",
                "stat_type": "points",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "total_picks": 178,
                "hits": 112,
                "misses": 66
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "total_picks": 1245,
                "hits": 789,
                "misses": 456
            },
            {
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "total_picks": 142,
                "hits": 87,
                "misses": 55
            },
            {
                "player_name": "Lamar Jackson",
                "stat_type": "rushing_yards",
                "hit_rate_percentage": 62.24,
                "avg_ev": 0.0897,
                "total_picks": 98,
                "hits": 61,
                "misses": 37
            },
            {
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0811,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Stephen Curry",
                "stat_type": "three_pointers",
                "hit_rate_percentage": 61.68,
                "avg_ev": 0.0889,
                "total_picks": 167,
                "hits": 103,
                "misses": 64
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_top_performers = [p for p in mock_top_performers if p['stat_type'] == stat_type]
        
        return {
            "top_performers": mock_top_performers[:limit],
            "total": len(mock_top_performers),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock top performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/best-ev")
async def get_best_ev_performers(limit: int = Query(10, description="Number of best EV performers to return"), 
                                   stat_type: str = Query(None, description="Stat type to filter")):
    """Get best performers by expected value"""
    try:
        # Return mock best EV performers data
        mock_best_ev = [
            {
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "total_picks": 189,
                "hits": 121,
                "misses": 68
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "total_picks": 89,
                "hits": 62,
                "misses": 27
            },
            {
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "total_picks": 89,
                "hits": 56,
                "misses": 33
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "total_picks": 1245,
                "hits": 789,
                "misses": 456
            },
            {
                "player_name": "Lamar Jackson",
                "stat_type": "rushing_yards",
                "hit_rate_percentage": 62.24,
                "avg_ev": 0.0897,
                "total_picks": 98,
                "hits": 61,
                "misses": 37
            },
            {
                "player_name": "Stephen Curry",
                "stat_type": "three_pointers",
                "hit_rate_percentage": 61.68,
                "avg_ev": 0.0889,
                "total_picks": 167,
                "hits": 103,
                "misses": 64
            },
            {
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "total_picks": 142,
                "hits": 87,
                "misses": 55
            },
            {
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0811,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "LeBron James",
                "stat_type": "points",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "total_picks": 178,
                "hits": 112,
                "misses": 66
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_best_ev = [p for p in mock_best_ev if p['stat_type'] == stat_type]
        
        return {
            "best_ev_performers": mock_best_ev[:limit],
            "total": len(mock_best_ev),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock best EV performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/worst")
async def get_worst_performers(limit: int = Query(10, description="Number of worst performers to return"), 
                                  stat_type: str = Query(None, description="Stat type to filter")):
    """Get worst performers by hit rate"""
    try:
        # Return mock worst performers data
        mock_worst = [
            {
                "player_name": "Russell Westbrook",
                "stat_type": "field_goal_percentage",
                "hit_rate_percentage": 46.27,
                "avg_ev": -0.0345,
                "total_picks": 67,
                "hits": 31,
                "misses": 36
            },
            {
                "player_name": "Mookie Betts",
                "stat_type": "batting_average",
                "hit_rate_percentage": 46.15,
                "avg_ev": -0.0289,
                "total_picks": 78,
                "hits": 36,
                "misses": 42
            },
            {
                "player_name": "Sam Darnold",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 48.89,
                "avg_ev": -0.0234,
                "total_picks": 45,
                "hits": 22,
                "misses": 23
            },
            {
                "player_name": "Shohei Ohtani",
                "stat_type": "home_runs",
                "hit_rate_percentage": 61.54,
                "avg_ev": 0.0834,
                "total_picks": 78,
                "hits": 48,
                "misses": 30
            },
            {
                "player_name": "Shohei Ohtani",
                "stat_type": "strikeouts",
                "hit_rate_percentage": 61.96,
                "avg_ev": 0.0798,
                "total_picks": 92,
                "hits": 57,
                "misses": 35
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_worst = [p for p in mock_worst if p['stat_type'] == stat_type]
        
        return {
            "worst_performers": mock_worst[:limit],
            "total": len(mock_worst),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock worst performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/statistics")
async def get_performance_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get performance statistics"""
    try:
        # Return mock statistics data
        mock_stats = {
            "period_days": days,
            "total_performances": 21,
            "unique_players": 11,
            "unique_stat_types": 12,
            "avg_hit_rate": 59.87,
            "avg_ev": 0.0634,
            "total_picks_all": 2478,
            "total_hits_all": 1483,
            "total_misses_all": 995,
            "by_stat_type": [
                {
                    "stat_type": "passing_touchdowns",
                    "total_performances": 1,
                    "avg_hit_rate": 69.66,
                    "avg_ev": 0.0921,
                    "total_picks": 89,
                    "total_hits": 62,
                    "unique_players": 1
                },
                {
                    "stat_type": "points",
                    "total_performances": 3,
                    "avg_hit_rate": 63.25,
                    "avg_ev": 0.0838,
                    "total_picks": 523,
                    "total_hits": 331,
                    "unique_players": 3
                },
                {
                    "stat_type": "home_runs",
                    "total_performances": 2,
                    "avg_hit_rate": 62.23,
                    "avg_ev": 0.0873,
                    "total_picks": 167,
                    "total_hits": 104,
                    "unique_players": 2
                },
                {
                    "stat_type": "passing_yards",
                    "total_performances": 3,
                    "avg_hit_rate": 57.66,
                    "avg_ev": 0.0466,
                    "total_picks": 343,
                    "total_hits": 207,
                    "unique_players": 3
                },
                {
                    "stat_type": "overall_predictions",
                    "total_performances": 4,
                    "avg_hit_rate": 62.90,
                    "avg_ev": 0.0807,
                    "total_picks": 2180,
                    "total_hits": 1370,
                    "unique_players": 1
                }
            ],
            "by_player": [
                {
                    "player_name": "Patrick Mahomes",
                    "total_performances": 2,
                    "avg_hit_rate": 66.24,
                    "avg_ev": 0.0882,
                    "total_picks": 245,
                    "total_hits": 160,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Stephen Curry",
                    "total_performances": 2,
                    "avg_hit_rate": 62.85,
                    "avg_ev": 0.0912,
                    "total_picks": 356,
                    "total_hits": 224,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Brain System",
                    "total_performances": 4,
                    "avg_hit_rate": 62.90,
                    "avg_ev": 0.0807,
                    "total_picks": 2180,
                    "total_hits": 1370,
                    "unique_stat_types": 4
                },
                {
                    "player_name": "Josh Allen",
                    "total_performances": 2,
                    "avg_hit_rate": 61.23,
                    "avg_ev": 0.0802,
                    "total_picks": 209,
                    "total_hits": 128,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "LeBron James",
                    "total_performances": 2,
                    "avg_hit_rate": 62.15,
                    "avg_ev": 0.0755,
                    "total_picks": 323,
                    "total_hits": 201,
                    "unique_stat_types": 2
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock performance statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/player/{player_name}")
async def get_player_performance(player_name: str, stat_type: str = Query(None, description="Stat type to filter")):
    """Get performance for a specific player"""
    try:
        # Return mock player performance data
        mock_player_data = {
            "player_name": player_name,
            "performances": [
                {
                    "id": 1,
                    "stat_type": "passing_yards",
                    "total_picks": 156,
                    "hits": 98,
                    "misses": 58,
                    "hit_rate_percentage": 62.82,
                    "avg_ev": 0.0842,
                    "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
                },
                {
                    "id": 2,
                    "stat_type": "passing_touchdowns",
                    "total_picks": 89,
                    "hits": 62,
                    "misses": 27,
                    "hit_rate_percentage": 69.66,
                    "avg_ev": 0.0921,
                    "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
                }
            ],
            "summary": {
                "total_performances": 2,
                "avg_hit_rate": 66.24,
                "avg_ev": 0.0882,
                "total_picks": 245,
                "total_hits": 160,
                "total_misses": 85,
                "unique_stat_types": 2
            }
        }
        
        # Apply stat type filter
        if stat_type:
            mock_player_data["performances"] = [p for p in mock_player_data["performances"] if p["stat_type"] == stat_type]
        
        return {
            "player_name": player_name,
            "performances": mock_player_data["performances"],
            "summary": mock_player_data["summary"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock performance data for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/search")
async def search_performances(query: str = Query(..., description="Search query"), 
                               limit: int = Query(20, description="Number of results to return")):
    """Search performances by player name or stat type"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "total_picks": 156,
                "hits": 98,
                "misses": 58,
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                p for p in mock_results 
                if query_lower in p['player_name'].lower() or 
                   query_lower in p['stat_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Injury Tracking Endpoints
@router.get("/injuries")
async def get_injuries(sport_id: int = Query(None, description="Sport ID to filter"), 
                        status: str = Query(None, description="Injury status to filter"),
                        player_id: int = Query(None, description="Player ID to filter"),
                        limit: int = Query(50, description="Number of injuries to return")):
    """Get injuries with optional filters"""
    try:
        # Return mock injury data for now
        mock_injuries = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": 66,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 24,
                "sport_id": 30,
                "player_id": 68,
                "status": "DAY_TO_DAY",
                "status_detail": "Hip",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 25,
                "sport_id": 30,
                "player_id": 69,
                "status": "OUT",
                "status_detail": "Toe",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 26,
                "sport_id": 30,
                "player_id": 70,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 27,
                "sport_id": 30,
                "player_id": 71,
                "status": "OUT",
                "status_detail": "Shoulder (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 28,
                "sport_id": 30,
                "player_id": 72,
                "status": "OUT",
                "status_detail": "Oblique",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 29,
                "sport_id": 30,
                "player_id": 27,
                "status": "OUT",
                "status_detail": "Foot/Toe",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 30,
                "sport_id": 30,
                "player_id": 30,
                "status": "OUT",
                "status_detail": "Calf",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 31,
                "sport_id": 32,
                "player_id": 101,
                "status": "QUESTIONABLE",
                "status_detail": "Concussion",
                "is_starter_flag": False,
                "probability": 0.3,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 32,
                "sport_id": 32,
                "player_id": 102,
                "status": "DOUBTFUL",
                "status_detail": "Ankle",
                "is_starter_flag": False,
                "probability": 0.4,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 34,
                "sport_id": 32,
                "player_id": 104,
                "status": "DAY_TO_DAY",
                "status_detail": "Shoulder",
                "is_starter_flag": False,
                "probability": 0.6,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 35,
                "sport_id": 32,
                "player_id": 105,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 36,
                "sport_id": 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_injuries = mock_injuries
        if sport_id:
            filtered_injuries = [i for i in filtered_injuries if i['sport_id'] == sport_id]
        if status:
            filtered_injuries = [i for i in filtered_injuries if i['status'] == status.upper()]
        if player_id:
            filtered_injuries = [i for i in filtered_injuries if i['player_id'] == player_id]
        
        return {
            "injuries": filtered_injuries[:limit],
            "total": len(filtered_injuries),
            "filters": {
                "sport_id": sport_id,
                "status": status,
                "player_id": player_id,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock injury data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "status": status,
            "player_id": player_id,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/active")
async def get_active_injuries(sport_id: int = Query(None, description="Sport ID to filter")):
    """Get currently active injuries"""
    try:
        # Return mock active injuries data for now
        mock_active = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": 66,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 24,
                "sport_id": 30,
                "player_id": 68,
                "status": "DAY_TO_DAY",
                "status_detail": "Hip",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 31,
                "sport_id": 32,
                "player_id": 101,
                "status": "QUESTIONABLE",
                "status_detail": "Concussion",
                "is_starter_flag": False,
                "probability": 0.3,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 32,
                "sport_id": 32,
                "player_id": 102,
                "status": "DOUBTFUL",
                "status_detail": "Ankle",
                "is_starter_flag": False,
                "probability": 0.4,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 36,
                "sport_id": 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 403,
                "sport_id": 32,
                'player_id': 403,
                'status': 'QUESTIONABLE',
                'status_detail': 'Concussion Protocol',
                'is_starter_flag': False,
                'probability': 0.25,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=3, hours=10)).isoformat()
            },
            {
                "id": 404,
                "sport_id': 32,
                'player_id': 404,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Back Strain',
                'is_starter_flag': False,
                'probability': 0.4,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=3, hours=10)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_active = [i for i in mock_active if i['sport_id'] == sport_id]
        
        return {
            "active_injuries": mock_active,
            "total": len(mock_active),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock active injuries data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/out")
async def get_out_injuries(sport_id: int = Query(None, description="Sport ID to filter")):
    """Get players who are out"""
    try:
        # Return mock out injuries data for now
        mock_out = [
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 25,
                "sport_id": 30,
                "player_id": 69,
                "status": "OUT",
                "status_detail": "Toe",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 26,
                "sport_id": 30,
                "player_id": 70,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 27,
                "sport_id": 30,
                "player_id": 71,
                "status": "OUT",
                "status_detail": "Shoulder (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 28,
                "sport_id": 30,
                "player_id": 72,
                "status": "OUT",
                "status_detail": "Oblique",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 29,
                "sport_id": 30,
                "player_id": 27,
                "status": "OUT",
                "status_detail": "Foot/Toe",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 30,
                "sport_id": 30,
                "player_id": 30,
                "status": "OUT",
                "status_detail": "Calf",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 35,
                "sport_id": 32,
                "player_id": 105,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_out = [i for i in mock_out if i['sport_id'] == sport_id]
        
        return {
            "out_injuries": mock_out,
            "total": len(mock_out),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock out injuries data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/statistics")
async def get_injury_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get injury statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_injuries": 21,
            "unique_sports": 4,
            "unique_players": 16,
            "out_injuries": 10,
            "day_to_day_injuries": 7,
            "questionable_injuries": 2,
            "doubtful_injuries": 1,
            "starter_injuries": 2,
            "avg_probability": 0.31,
            "official_injuries": 21,
            "by_sport": [
                {
                    "sport_id": 30,
                    "total_injuries": 10,
                    "out_injuries": 5,
                    "day_to_day_injuries": 5,
                    "questionable_injuries": 2,
                    "doubtful_injuries": 1,
                    "starter_injuries": 2,
                    "avg_probability": 0.40,
                    "unique_players": 10
                },
                {
                    "sport_id": 32,
                    "total_injuries": 7,
                    "out_injuries": 3,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 1,
                    "doubtful_injuries": 1,
                    "starter_injuries": 0,
                    "avg_probability": 0.33,
                    "unique_players": 7
                },
                {
                    "sport_id": 29,
                    "total_injuries": 4,
                    "out_injuries": 2,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 0,
                    "doubtful_injuries": 0,
                    "starter_injuries": 0,
                    "avg_probability": 0.20,
                    "unique_players": 4
                },
                {
                    "sport_id": 53,
                    "total_injuries": 4,
                    "out_injuries": 2,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 1,
                    "doubtful_injuries": 0,
                    "starter_injuries": 0,
                    "avg_probability": 0.25,
                    "unique_players": 4
                }
            ],
            "by_status": [
                {
                    "status": "OUT",
                    "total_injuries": 10,
                    "avg_probability": 0.0,
                    "starter_injuries": 2,
                    "unique_players": 10
                },
                {
                    "status": "DAY_TO_DAY",
                    "total_injuries": 7,
                    "avg_probability": 0.47,
                    "starter_injuries": 2,
                    "unique_players": 7
                },
                {
                    "status": "QUESTIONABLE",
                    "total_injuries": 3,
                    "avg_probability": 0.28,
                    "starter_injuries": 0,
                    "unique_players": 3
                },
                {
                    "status": "DOUBTFUL",
                    "total_injuries": 2,
                    "avg_probability": 0.35,
                    "starter_injuries": 0,
                    "unique_players": 2
                }
            ],
            "by_source": [
                {
                    "source": "official",
                    "total_injuries": 21,
                    "avg_probability": 0.31,
                    "unique_players": 16
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock injury statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/player/{player_id}")
async def get_player_injuries(player_id: int, sport_id: int = Query(None, description="Sport ID to filter")):
    """Get injuries for a specific player"""
    try:
        # Return mock player injury data for now
        mock_player_injuries = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": player_id,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": player_id,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": player_id,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_player_injuries = [i for i in mock_player_injuries if i['sport_id'] == sport_id]
        
        return {
            "player_id": player_id,
            "injuries": mock_player_injuries,
            "total": len(mock_player_injuries),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock injury data for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/impact-analysis/{sport_id}")
async def get_injury_impact_analysis(sport_id: int, days: int = Query(30, description="Days of data to analyze")):
    """Analyze injury impact on team performance"""
    try:
        # Return mock impact analysis data for now
        mock_impact = {
            "sport_id": sport_id,
            "period_days": days,
            "total_injuries": 10,
            "active_injuries": 5,
            "out_injuries": 3,
            "starter_injuries": 0,
            "starter_impact_score": 0.0,
            "active_impact_score": 50.0,
            "out_impact_score": 30.0,
            "weighted_impact": 0.3,
            "concerning_injuries": [
                {
                    "player_id": 103,
                    "status": "OUT",
                    "status_detail": "ACL Tear (Season-ending)",
                    "is_starter": False,
                    "probability": 0.0
                },
                {
                    "player_id": 101,
                    "status": "QUESTIONABLE",
                    "status_detail": "Concussion",
                    "is_starter": False,
                    "probability": 0.3
                }
            ],
            "impact_analysis": "Moderate impact - some active injuries",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock impact analysis for sport {sport_id}"
        }
        
        return mock_impact
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/trends/{sport_id}")
async def get_injury_trends(sport_id: int, days: int = Query(30, description="Days of data to analyze")):
    """Analyze injury trends over time"""
    try:
        # Return mock trend analysis data for now
        mock_trends = {
            "sport_id": sport_id,
            "period_days": days,
            "daily_trends": [
                {
                    "date": "2026-02-01",
                    "total_injuries": 5,
                    "out_injuries": 2,
                    "day_to_day_injuries": 3,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-02",
                    "total_injuries": 3,
                    "out_injuries": 1,
                    "day_to_day_injuries": 2,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-03",
                    "total_injuries": 2,
                    "out_injuries": 0,
                    "day_to_day_injuries": 2,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-04",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-05",
                    "total_injuries": 2,
                    "out_injuries": 1,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-06",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-07",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                }
            ],
            "trend_analysis": "Decreasing injuries - positive trend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock injury trends for sport {sport_id}"
        }
        
        return mock_trends
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/search")
async def search_injuries(query: str = Query(..., description="Search query"), 
                             sport_id: int = Query(None, description="Sport ID to filter"),
                             limit: int = Query(20, description="Number of results to return")):
    """Search injuries by player ID or status detail"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply filters
        if sport_id:
            mock_results = [r for r in mock_results if r['sport_id'] == sport_id]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in str(r['player_id']) or 
                   query_lower in r['status_detail'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "sport_id": sport_id,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Line Tracking Endpoints
@router.get("/lines")
async def get_lines(game_id: int = Query(None, description="Game ID to filter"), 
                   player_id: int = Query(None, description="Player ID to filter"),
                   sportsbook: str = Query(None, description="Sportsbook to filter"),
                   is_current: bool = Query(None, description="Filter current lines only"),
                   limit: int = Query(50, description="Number of lines to return")):
    """Get betting lines with optional filters"""
    try:
        # Return mock line data for now
        mock_lines = [
            {
                "id": 759109,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759110,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759111,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 15.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759112,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 15.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759113,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 16.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759114,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 16.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759115,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759116,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759117,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 12.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759118,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 12.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_lines = mock_lines
        if game_id:
            filtered_lines = [l for l in filtered_lines if l['game_id'] == game_id]
        if player_id:
            filtered_lines = [l for l in filtered_lines if l['player_id'] == player_id]
        if sportsbook:
            filtered_lines = [l for l in filtered_lines if l['sportsbook'].lower() == sportsbook.lower()]
        if is_current is not None:
            filtered_lines = [l for l in filtered_lines if l['is_current'] == is_current]
        
        return {
            "lines": filtered_lines[:limit],
            "total": len(filtered_lines),
            "filters": {
                "game_id": game_id,
                "player_id": player_id,
                "sportsbook": sportsbook,
                "is_current": is_current,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/current")
async def get_current_lines(game_id: int = Query(None, description="Game ID to filter"), 
                            player_id: int = Query(None, description="Player ID to filter")):
    """Get current betting lines"""
    try:
        # Return mock current lines data for now
        mock_current = [
            {
                "id": 759119,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759120,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759121,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759122,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759123,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759124,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759125,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759126,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759127,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "fanduel",
                "line_value": 29.0,
                "odds": -108,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759128,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "fanduel",
                "line_value": 29.0,
                "odds": -108,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Apply filters
        if game_id:
            mock_current = [l for l in mock_current if l['game_id'] == game_id]
        if player_id:
            mock_current = [l for l in mock_current if l['player_id'] == player_id]
        
        return {
            "current_lines": mock_current,
            "total": len(mock_current),
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock current lines data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/movements/{game_id}/{player_id}")
async def get_line_movements(game_id: int, player_id: int, market_id: int = Query(None, description="Market ID to filter")):
    """Get line movements for a specific game/player"""
    try:
        # Return mock line movements data for now
        mock_movements = [
            {
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "odds_movement": 0,
                "prev_line_value": 13.5,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "odds_movement": 0,
                "prev_line_value": 13.5,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_odds": -110
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            }
        ]
        
        # Apply market filter
        if market_id:
            mock_movements = [m for m in mock_movements if m['sportsbook'] == 'draftkings'] or m['sportsbook'] == 'fanduel']
        
        return {
            "game_id": game_id,
            "player_id": player_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock line movements for game {game_id}, player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/comparison/{game_id}/{player_id}")
async def get_sportsbook_comparison(game_id: int, player_id: int, market_id: int = Query(None, description="Market ID to filter")):
    """Compare lines across sportsbooks"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Calculate best odds
        best_over = max(mock_comparison, key=lambda x: x['odds'] if x['side'] == 'over' else float('inf'))
        best_under = max(mock_comparison, key=lambda x: x['odds'] if x['side'] == 'under' else float('inf'))
        
        return {
            "game_id": game_id,
            "player_id": player_id,
            "comparison": mock_comparison,
            "best_over_odds": {
                "sportsbook": best_over['sportsbook'],
                "line_value": best_over['line_value'],
                "odds": best_over['odds'],
                "side": best_over['side']
            },
            "best_under_odds": {
                "sportsbook": best_under['sportsbook'],
                "line_value": best_under['line_value'],
                "odds": best_under['odds'],
                "side": best_under['side']
            },
            "total_sportsbooks": len(set(c['sportsbook'] for c in mock_comparison)),
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock sportsbook comparison for game {game_id}, player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/statistics")
async def get_line_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get line statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_lines": 24,
            "unique_games": 4,
            "unique_markets": 6,
            "unique_players": 4,
            "unique_sportsbooks": 3,
            "current_lines": 10,
            "historical_lines": 14,
            "avg_line_value": 20.25,
            "avg_odds": -108,
            "over_lines": 12,
            "under_lines": 12,
            "by_sportsbook": [
                {
                    "sportsbook": "draftkings",
                    "total_lines": 10,
                    "current_lines": 4,
                    "unique_games": 4,
                    "unique_players": 4,
                    "avg_line_value": 18.5,
                    "avg_odds": -108,
                    "over_lines": 5,
                    "under_lines": 5
                },
                {
                    "sportsbook": "fanduel",
                    "total_lines": 8,
                    "current_lines": 4,
                    "unique_games": 3,
                    "unique_players": 3,
                    "avg_line_value": 21.25,
                    "avg_odds": -108,
                    "over_lines": 4,
                    "under_lines": 4
                },
                {
                    "sportsbook": "betmgm",
                    "total_lines": 6,
                    "current_lines": 2,
                    "unique_games": 2,
                    "unique_players": 2,
                    "avg_line_value": 22.0,
                    "avg_odds": -110,
                    "over_lines": 3,
                    "under_lines": 3
                }
            ],
            "by_side": [
                {
                    "side": "over",
                    "total_lines": 12,
                    "avg_line_value": 20.25,
                    "avg_odds": -108,
                    "unique_sportsbooks": 3,
                    "unique_players": 4
                },
                {
                    "side": "under",
                    "total_lines": 12,
                    "avg_line_value": 20.25,
                    "avg_odds": -108,
                    "unique_sportsbooks": 3,
                    "unique_players": 4
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/efficiency")
async def get_line_efficiency(hours: int = Query(24, description="Hours of data to analyze")):
    """Analyze line efficiency and market efficiency"""
    try:
        # Return mock efficiency analysis data for now
        mock_efficiency = {
            "period_hours": hours,
            "sportsbook_efficiency": [
                {
                    "sportsbook": "draftkings",
                    "total_lines": 10,
                    "significant_movements": 3,
                    "movement_rate": 30.0,
                    "avg_movement": 0.75,
                    "unique_games": 4,
                    "unique_players": 4,
                    "efficiency_score": 70.0
                },
                {
                    "sportsbook": "fanduel",
                    "total_lines": 8,
                    "significant_movements": 2,
                    "movement_rate": 25.0,
                    "avg_movement": 0.5,
                    "unique_games": 3,
                    "unique_players": 3,
                    "efficiency_score": 75.0
                },
                {
                    "sportsbook": "betmgm",
                    "total_lines": 6,
                    "significant_movements": 1,
                    "movement_rate": 16.7,
                    "avg_movement": 0.3,
                    "unique_games": 2,
                    "unique_players": 2,
                    "efficiency_score": 83.3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/search")
async def search_lines(query: str = Query(..., description="Search query"), 
                       sportsbook: str = Query(None, description="Sportsbook to filter"),
                       limit: int = Query(20, description="Number of results to return")):
    """Search lines by player ID or sportsbook"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 759109,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759125,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759129,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "sportsbook": "draftkings",
                "line_value": 285.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Apply filters
        if sportsbook:
            mock_results = [r for r in mock_results if r['sportsbook'].lower() == sportsbook.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in str(r['player_id']) or 
                   query_lower in r['sportsbook'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "sportsbook": sportsbook,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Live Odds NFL Endpoints
@router.get("/live-odds-nfl")
async def get_live_odds_nfl(game_id: int = Query(None, description="Game ID to filter"), 
                          team: str = Query(None, description="Team name to filter"),
                          bookmaker: str = Query(None, description="Sportsbook to filter"),
                          week: int = Query(None, description="Week to filter"),
                          limit: int = Query(50, description="Number of odds to return")):
    """Get live NFL odds with optional filters"""
    try:
        # Return mock live NFL odds data for now
        mock_odds = [
            {
                "id": 1,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 2,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 3,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "bookmaker": "BetMGM",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 4,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat()
            },
            {
                "id": 5,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -130,
                "away_odds": 110,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat()
            },
            {
                "id": 6,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 7,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            },
            {
                "id": 8,
                "sport": 1,
                "game_id": 2005,
                "home_team": "New England Patriots",
                "away_team": "New York Jets",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
            },
            {
                "id": 9,
                "sport": 1,
                "game_id": 2006,
                "home_team": "Baltimore Ravens",
                "away_team": "Pittsburgh Steelers",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
            },
            {
                "id": 10,
                "sport": 1,
                "game_id": 2007,
                "home_team": "Cincinnati Bengals",
                "away_team": "Cleveland Browns",
                "home_odds": -110,
                "away_odds": -110,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_odds = mock_odds
        if game_id:
            filtered_odds = [o for o in filtered_odds if o['game_id'] == game_id]
        if team:
            filtered_odds = [o for o in filtered_odds if team.lower() in o['home_team'].lower() or team.lower() in o['away_team'].lower()]
        if bookmaker:
            filtered_odds = [o for o in filtered_odds if o['bookmaker'].lower() == bookmaker.lower()]
        if week:
            filtered_odds = [o for o in filtered_odds if o['week'] == week]
        
        return {
            "odds": filtered_odds[:limit],
            "total": len(filtered_odds),
            "filters": {
                "game_id": game_id,
                "team": team,
                "bookmaker": bookmaker,
                "week": week,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/current")
async def get_current_live_odds_nfl(game_id: int = Query(None, description="Game ID to filter"), 
                                   bookmaker: str = Query(None, description="Sportsbook to filter")):
    """Get current live NFL odds"""
    try:
        # Return mock current live NFL odds data for now
        mock_current = [
            {
                "id": 11,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 12,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 13,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 14,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 15,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        if game_id:
            mock_current = [o for o in mock_current if o['game_id'] == game_id]
        if bookmaker:
            mock_current = [o for o in mock_current if o['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "current_odds": mock_current,
            "total": len(mock_current),
            "game_id": game_id,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock current live NFL odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/movements/{game_id}")
async def get_live_odds_nfl_movements(game_id: int, minutes: int = Query(30, description="Minutes of data to analyze")):
    """Get live NFL odds movements for a specific game"""
    try:
        # Return mock movements data for now
        mock_movements = [
            {
                "sportsbook": "DraftKings",
                "home_odds": -162,
                "away_odds": 142,
                "draw_odds": None,
                "timestamp": (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat(),
                "home_movement": 3,
                "away_movement": -3,
                "prev_home_odds": -165,
                "prev_away_odds": 145,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "DraftKings",
                "home_odds": -168,
                "away_odds": 148,
                "draw_odds": None,
                "timestamp": (datetime.now(timezone.utc) - timedelta(seconds=15)).isoformat(),
                "home_movement": -6,
                "away_movement": 6,
                "prev_home_odds": -162,
                "prev_away_odds": 142,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "DraftKings",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 3,
                "away_movement": -3,
                "prev_home_odds": -168,
                "prev_away_odds": 148,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "BetMGM",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            }
        ]
        
        return {
            "game_id": game_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock live NFL odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/comparison/{game_id}")
async def get_live_odds_nfl_comparison(game_id: int, minutes: int = Query(30, description="Minutes of data to analyze")):
    """Compare live NFL odds across sportsbooks for a specific game"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "sportsbook": "DraftKings",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "sportsbook": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "sportsbook": "BetMGM",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Calculate best odds
        best_home_odds = max(mock_comparison, key=lambda x: x['home_odds'] if x['home_odds'] < 0 else float('inf'))
        best_away_odds = max(mock_comparison, key=lambda x: x['away_odds'] if x['away_odds'] < 0 else float('inf'))
        
        return {
            "game_id": game_id,
            "comparison": mock_comparison,
            "best_home_odds": {
                "sportsbook": best_home_odds['sportsbook'],
                "line_value": best_home_odds['home_odds'],
                "odds": best_home_odds['odds']
            },
            "best_away_odds": {
                "best_away_odds": best_away_odds['sportsbook'],
                "line_value": best_away_odds['away_odds'],
                "odds": best_away_odds['odds']
            },
            "total_sportsbooks": len(mock_comparison),
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock sportsbook comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/statistics")
async def get_live_odds_nfl_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get live NFL odds statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_odds": 24,
            "unique_games": 8,
            "unique_teams": 16,
            "unique_opponents": 16,
            "unique_bookmakers": 3,
            "unique_weeks": 4,
            "avg_home_odds": -140.5,
            "avg_away_odds": 120.5,
            "home_favorites": 18,
            "away_favorites": 6,
            "draw_markets": 0,
            "by_sportsbook": [
                {
                    "bookmaker": "DraftKings",
                    "total_odds": 10,
                    "unique_games": 8,
                    "unique_weeks": 4,
                    "avg_home_odds": -145.0,
                    "avg_away_odds": 125.0,
                    "home_favorites": 8,
                    "away_favorites": 2,
                    "unique_teams": 16,
                    "unique_opponents": 16
                },
                {
                    "bookmaker": "FanDuel",
                    "total_odds": 8,
                    "unique_games": 6,
                    "unique_weeks": 3,
                    "avg_home_odds": -135.0,
                    "avg_away_odds": 115.0,
                    "home_favorites": 6,
                    "away_favorites": 2,
                    "unique_teams": 12,
                    "unique_opponents": 12
                },
                {
                    "bookmaker": "BetMGM",
                    "total_odds": 6,
                    "unique_games": 4,
                    "unique_weeks": 2,
                    "avg_home_odds": -150.0,
                    "avg_away_odds": 130.0,
                    "home_favorites": 4,
                    "away_favorites": 2,
                    "unique_teams": 8,
                    "unique_opponents": 8
                }
            ],
            "by_week": [
                {
                    "week": 20,
                    "season": 2026,
                    "total_odds": 6,
                    "unique_games": 2,
                    "avg_home_odds": -147.5,
                    "avg_away_odds": 127.5,
                    "home_favorites": 4,
                    "away_favorites": 2
                },
                {
                    "week": 18,
                    "season": 2026,
                    "total_odds": 12,
                    "unique_games": 4,
                    "avg_home_odds": -138.3,
                    "avg_away_odds": 118.3,
                    "home_favorites": 10,
                    "away_favorites": 2
                }
            ],
            "by_team": [
                {
                    "team": "Kansas City Chiefs",
                    "total_games": 3,
                    "home_wins": 3,
                    "away_wins": 0,
                    "avg_home_odds": -165.0,
                    "avg_away_odds": 145.0,
                    "unique_games": 1,
                    "unique_weeks": 1
                },
                {
                    "team": "Dallas Cowboys",
                    "total_games": 3,
                    "home_wins": 3,
                    "away_wins": 0,
                    "avg_home_odds": -280.0,
                    "avg_away_odds": 230.0,
                    "unique_games": 1,
                    "unique_weeks": 1
                }
            ],
            "by_odds_range": [
                {
                    "odds_range": "Heavy Favorite",
                    "total_odds": 3,
                    "avg_odds": -280.0,
                    "avg_away_odds": 230.0
                },
                {
                    "odds_range": "Strong Favorite",
                    "total_odds": 5,
                    "avg_odds": -190.0,
                    "avg_away_odds": 160.0
                },
                {
                    "odds_range": "Moderate Favorite",
                    "total_odds": 8,
                    "avg_odds": -140.0,
                    "avg_away_odds": 120.0
                },
                {
                    "odds_range": "Light Favorite",
                    "total_odds": 6,
                    "avg_odds": -110.0,
                    "avg_away_odds": -110.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/efficiency")
async def get_live_odds_nfl_efficiency(hours: int = Query(24, description="Hours of data to analyze")):
    """Analyze live NFL odds market efficiency and arbitrage opportunities"""
    try:
        # Return mock efficiency analysis data for now
        mock_efficiency = {
            "period_hours": hours,
            "total_arbitrage_opportunities": 8,
            "avg_home_range": 10.0,
            "avg_away_range": 10.0,
            "arbitrage_opportunities": [
                {
                    "game_id": 2001,
                    "home_team": "Kansas City Chiefs",
                    "away_team": "Buffalo Bills",
                    "week": 20,
                    "season": 2026,
                    "sportsbooks_count": 3,
                    "best_home_odds": -160,
                    "worst_home_odds": -170,
                    "best_away_odds": 140,
                    "worst_away_odds": 150,
                    "home_odds_range": 10,
                    "away_odds_range": 10,
                    "avg_home_odds": -165.0,
                    "avg_away_odds": 145.0
                },
                {
                    "game_id": 2002,
                    "home_team": "San Francisco 49ers",
                    "away_team": "Philadelphia Eagles",
                    "week": 20,
                    "season": 2026,
                    "sportsbooks_count": 2,
                    "best_home_odds": -125,
                    "worst_home_odds": -130,
                    "best_away_odds": 105,
                    "worst_away_odds": 110,
                    "home_odds_range": 5,
                    "away_odds_range": 5,
                    "avg_home_odds": -127.5,
                    "avg_away_odds": 107.5
                },
                {
                    "game_id": 2003,
                    "home_team": "Dallas Cowboys",
                    "away_team": "New York Giants",
                    "week": 18,
                    "season": 2026,
                    "sportsbooks_count": 3,
                    "best_home_odds": -275,
                    "worst_home_odds": -285,
                    "best_away_odds": 225,
                    "worst_away_odds": 235,
                    "home_odds_range": 10,
                    "away_odds_range": 10,
                    "avg_home_odds": -280.0,
                    "avg_away_odds": 230.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/week/{week}")
async def get_live_odds_nfl_by_week(week: int, season: int = Query(2026, description="Season to filter"), 
                                   bookmaker: str = Query(None, description="Sportsbook to filter")):
    """Get live NFL odds for a specific week"""
    try:
        # Return mock week data for now
        mock_week_odds = [
            {
                "id": 16,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 17,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            },
            {
                "id": 18,
                "sport": 1,
                "game_id": 2005,
                "home_team": "New England Patriots",
                "away_team": "New York Jets",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
            }
        ]
        
        # Apply bookmaker filter
        if bookmaker:
            mock_week_odds = [o for o in mock_week_odds if o['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "week": week,
            "season": season,
            "odds": mock_week_odds,
            "total": len(mock_week_odds),
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock live NFL odds for week {week}, season {season}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "week": week,
            "season": season,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/search")
async def search_live_odds_nfl(query: str = Query(..., description="Search query"), 
                              bookmaker: str = Query(None, description="Sportsbook to filter"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search live NFL odds by team name or sportsbook"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 6,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 7,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            }
        ]
        
        # Apply filters
        if bookmaker:
            mock_results = [r for r in mock_results if r['bookmaker'].lower() == bookmaker.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['home_team'].lower() or 
                   query_lower in r['away_team'].lower() or
                   query_lower in r['bookmaker'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "bookmaker": bookmaker,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Odds Snapshots Tracking Endpoints
@router.get("/odds-snapshots")
async def get_odds_snapshots(game_id: int = Query(None, description="Game ID to filter"), 
                           player_id: int = Query(None, description="Player ID to filter"),
                           bookmaker: str = Query(None, description="Bookmaker to filter"),
                           hours: int = Query(24, description="Hours of data to analyze"),
                           limit: int = Query(50, description="Number of snapshots to return")):
    """Get odds snapshots with optional filters"""
    try:
        # Return mock odds snapshots data for now
        mock_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 3,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.5",
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_92",
                "external_outcome_id": "over_28.5",
                "bookmaker": "DraftKings",
                "line_value": 28.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "external_fixture_id": "nfl_2026_664",
                "external_market_id": "player_pass_yards_101",
                "external_outcome_id": "over_285.5",
                "bookmaker": "DraftKings",
                "line_value": 285.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 6,
                "game_id": 666,
                "market_id": 201,
                "player_id": 201,
                "external_fixture_id": "mlb_2026_666",
                "external_market_id": "player_hr_201",
                "external_outcome_id": "over_1.5",
                "bookmaker": "DraftKings",
                "line_value": 1.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat()
            },
            {
                "id": 7,
                "game_id": 668,
                "market_id": 301,
                "player_id": 301,
                "external_fixture_id": "nhl_2026_668",
                "external_market_id": "player_points_301",
                "external_outcome_id": "over_1.5",
                "bookmaker": "DraftKings",
                "line_value": 1.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            }
        ]
        
        # Apply filters
        filtered_snapshots = mock_snapshots
        if game_id:
            filtered_snapshots = [s for s in filtered_snapshots if s['game_id'] == game_id]
        if player_id:
            filtered_snapshots = [s for s in filtered_snapshots if s['player_id'] == player_id]
        if bookmaker:
            filtered_snapshots = [s for s in filtered_snapshots if s['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "snapshots": filtered_snapshots[:limit],
            "total": len(filtered_snapshots),
            "filters": {
                "game_id": game_id,
                "player_id": player_id,
                "bookmaker": bookmaker,
                "hours": hours,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds snapshots data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/movements/{game_id}")
async def get_odds_movements(game_id: int, market_id: int = Query(None, description="Market ID to filter"),
                           player_id: int = Query(None, description="Player ID to filter"),
                           hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds movements for a specific game"""
    try:
        # Return mock movements data for now
        mock_movements = [
            {
                "bookmaker": "DraftKings",
                "line_value": 13.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9524,
                "american_odds": -105,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "price_movement": 0.0433,
                "odds_movement": 5,
                "prev_line_value": 13.5,
                "prev_price": 1.9091,
                "prev_american_odds": -110
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9524,
                "american_odds": -105,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": 14.0,
                "prev_price": 1.9524,
                "prev_american_odds": -105
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9412,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "line_movement": 0,
                "price_movement": -0.0112,
                "odds_movement": -3,
                "prev_line_value": 14.0,
                "prev_price": 1.9524,
                "prev_american_odds": -105
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9615,
                "american_odds": -103,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0203,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_price": 1.9412,
                "prev_american_odds": -108
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0091,
                "odds_movement": 1,
                "prev_line_value": 14.0,
                "prev_price": 1.9615,
                "prev_american_odds": -103
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0115,
                "odds_movement": 2,
                "prev_line_value": 13.5,
                "prev_price": 1.9231,
                "prev_american_odds": -108
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0140,
                "odds_movement": 2,
                "prev_line_value": 14.5,
                "prev_price": 1.9091,
                "prev_american_odds": -110
            }
        ]
        
        # Apply filters
        filtered_movements = mock_movements
        if market_id:
            # Filter by market_id logic would go here
            pass
        if player_id:
            # Filter by player_id logic would go here
            pass
        
        return {
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "movements": filtered_movements,
            "total_movements": len(filtered_movements),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/comparison/{game_id}")
async def get_odds_comparison(game_id: int, market_id: int = Query(None, description="Market ID to filter"),
                            player_id: int = Query(None, description="Player ID to filter"),
                            hours: int = Query(1, description="Hours of data to analyze")):
    """Compare odds across bookmakers for a specific game"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Calculate best odds
        best_over = max(mock_comparison, key=lambda x: x['price'] if x['side'] == 'over' else float('inf'))
        best_under = max(mock_comparison, key=lambda x: x['price'] if x['side'] == 'under' else float('inf'))
        
        return {
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "comparison": mock_comparison,
            "best_over_odds": {
                "bookmaker": best_over['bookmaker'],
                "line_value": best_over['line_value'],
                "price": best_over['price'],
                "american_odds": best_over['american_odds']
            },
            "best_under_odds": {
                "bookmaker": best_under['bookmaker'],
                "line_value": best_under['line_value'],
                "price": best_under['price'],
                "american_odds": best_under['american_odds']
            },
            "total_bookmakers": len(mock_comparison),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/statistics")
async def get_odds_snapshots_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_snapshots": 25,
            "unique_games": 4,
            "unique_markets": 6,
            "unique_players": 6,
            "unique_bookmakers": 3,
            "unique_fixtures": 4,
            "unique_external_markets": 6,
            "unique_external_outcomes": 12,
            "avg_line_value": 45.2,
            "avg_price": 1.9345,
            "avg_american_odds": -106,
            "over_snapshots": 18,
            "under_snapshots": 7,
            "active_snapshots": 25,
            "by_bookmaker": [
                {
                    "bookmaker": "DraftKings",
                    "total_snapshots": 12,
                    "unique_games": 4,
                    "unique_markets": 5,
                    "avg_line_value": 48.5,
                    "avg_price": 1.9412,
                    "avg_american_odds": -104,
                    "over_snapshots": 9,
                    "under_snapshots": 3
                },
                {
                    "bookmaker": "FanDuel",
                    "total_snapshots": 8,
                    "unique_games": 3,
                    "unique_markets": 4,
                    "avg_line_value": 42.1,
                    "avg_price": 1.9286,
                    "avg_american_odds": -107,
                    "over_snapshots": 6,
                    "under_snapshots": 2
                },
                {
                    "bookmaker": "BetMGM",
                    "total_snapshots": 5,
                    "unique_games": 2,
                    "unique_markets": 3,
                    "avg_line_value": 38.7,
                    "avg_price": 1.9162,
                    "avg_american_odds": -109,
                    "over_snapshots": 3,
                    "under_snapshots": 2
                }
            ],
            "by_game": [
                {
                    "game_id": 662,
                    "total_snapshots": 12,
                    "unique_markets": 2,
                    "unique_players": 2,
                    "unique_bookmakers": 3,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                    "last_snapshot": datetime.now(timezone.utc).isoformat()
                },
                {
                    "game_id": 664,
                    "total_snapshots": 4,
                    "unique_markets": 2,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
                },
                {
                    "game_id": 666,
                    "total_snapshots": 3,
                    "unique_markets": 2,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
                },
                {
                    "game_id": 668,
                    "total_snapshots": 2,
                    "unique_markets": 1,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
                }
            ],
            "by_side": [
                {
                    "side": "over",
                    "total_snapshots": 18,
                    "avg_line_value": 47.8,
                    "avg_price": 1.9456,
                    "avg_american_odds": -103,
                    "unique_bookmakers": 3,
                    "unique_games": 4
                },
                {
                    "side": "under",
                    "total_snapshots": 7,
                    "avg_line_value": 38.2,
                    "avg_price": 1.9091,
                    "avg_american_odds": -110,
                    "unique_bookmakers": 2,
                    "unique_games": 3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds snapshots statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/bookmaker/{bookmaker}")
async def get_odds_by_bookmaker(bookmaker: str, hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots from a specific bookmaker"""
    try:
        # Return mock bookmaker data for now
        mock_bookmaker_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": bookmaker,
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_92",
                "external_outcome_id": "over_28.5",
                "bookmaker": bookmaker,
                "line_value": 28.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "external_fixture_id": "nfl_2026_664",
                "external_market_id": "player_pass_yards_101",
                "external_outcome_id": "over_285.5",
                "bookmaker": bookmaker,
                "line_value": 285.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "bookmaker": bookmaker,
            "snapshots": mock_bookmaker_snapshots,
            "total": len(mock_bookmaker_snapshots),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds snapshots for {bookmaker}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/player/{player_id}")
async def get_odds_by_player(player_id: int, bookmaker: str = Query(None, description="Bookmaker to filter"),
                            hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots for a specific player"""
    try:
        # Return mock player data for now
        mock_player_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 3,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.5",
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply bookmaker filter
        if bookmaker:
            mock_player_snapshots = [s for s in mock_player_snapshots if s['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "player_id": player_id,
            "snapshots": mock_player_snapshots,
            "total": len(mock_player_snapshots),
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds snapshots for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/search")
async def search_odds_snapshots(query: str = Query(..., description="Search query"), 
                              bookmaker: str = Query(None, description="Bookmaker to filter"),
                              hours: int = Query(24, description="Hours of data to analyze"),
                              limit: int = Query(50, description="Number of results to return")):
    """Search odds snapshots by external IDs or bookmaker"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        if bookmaker:
            mock_results = [r for r in mock_results if r['bookmaker'].lower() == bookmaker.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['external_fixture_id'].lower() or 
                   query_lower in r['external_market_id'].lower() or
                   query_lower in r['external_outcome_id'].lower() or
                   query_lower in r['bookmaker'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "bookmaker": bookmaker,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "bookmaker": bookmaker,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Picks Management Endpoints
@router.get("/picks")
async def get_picks(game_id: int = Query(None, description="Game ID to filter"), 
                  player: str = Query(None, description="Player name to filter"),
                  stat_type: str = Query(None, description="Stat type to filter"),
                  min_ev: float = Query(0.0, description="Minimum EV percentage"),
                  min_confidence: float = Query(0.0, description="Minimum confidence"),
                  hours: int = Query(24, description="Hours of data to analyze"),
                  limit: int = Query(50, description="Number of picks to return")):
    """Get picks with optional filters"""
    try:
        # Return mock picks data for now
        mock_picks = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 3,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -105,
                "model_probability": 0.6100,
                "implied_probability": 0.5122,
                "ev_percentage": 19.09,
                "confidence": 87.0,
                "hit_rate": 63.5,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 668,
                "pick_type": "player_prop",
                "player_name": "Connor McDavid",
                "stat_type": "points",
                "line": 1.5,
                "odds": -108,
                "model_probability": 0.6000,
                "implied_probability": 0.5195,
                "ev_percentage": 15.40,
                "confidence": 85.0,
                "hit_rate": 62.8,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 7,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "line": 26.5,
                "odds": -108,
                "model_probability": 0.5900,
                "implied_probability": 0.5195,
                "ev_percentage": 13.58,
                "confidence": 86.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 8,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "line": 285.5,
                "odds": -110,
                "model_probability": 0.5800,
                "implied_probability": 0.5238,
                "ev_percentage": 10.75,
                "confidence": 84.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=3).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=3).isoformat()
            },
            {
                "id": 9,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -110,
                "model_probability": 0.5900,
                "implied_probability": 0.5238,
                "ev_percentage": 12.61,
                "confidence": 85.0,
                "hit_rate": 62.9,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply filters
        filtered_picks = mock_picks
        if game_id:
            filtered_picks = [p for p in filtered_picks if p['game_id'] == game_id]
        if player:
            filtered_picks = [p for p in filtered_picks if player.lower() in p['player_name'].lower()]
        if stat_type:
            filtered_picks = [p for p in filtered_picks if p['stat_type'].lower() == stat_type.lower()]
        if min_ev > 0:
            filtered_picks = [p for p in filtered_picks if p['ev_percentage'] >= min_ev]
        if min_confidence > 0:
            filtered_picks = [p for p in filtered_picks if p['confidence'] >= min_confidence]
        
        return {
            "picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "filters": {
                "game_id": game_id,
                "player": player,
                "stat_type": stat_type,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
                "hours": hours,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock picks data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/high-ev")
async def get_high_ev_picks(min_ev: float = Query(5.0, description="Minimum EV percentage"),
                           hours: int = Query(24, description="Hours of data to analyze"),
                           limit: int = Query(20, description="Number of picks to return")):
    """Get picks with high expected value"""
    try:
        # Return mock high EV picks data for now
        mock_high_ev = [
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 3,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -105,
                "model_probability": 0.6100,
                "implied_probability": 0.5122,
                "ev_percentage": 19.09,
                "confidence": 87.0,
                "hit_rate": 63.5,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply EV filter
        filtered_picks = [p for p in mock_high_ev if p['ev_percentage'] >= min_ev]
        
        return {
            "high_ev_picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "min_ev": min_ev,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock high EV picks (>= {min_ev}% EV)"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "min_ev": min_ev,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/high-confidence")
async def get_high_confidence_picks(min_confidence: float = Query(80.0, description="Minimum confidence"),
                                   hours: int = Query(24, description="Hours of data to analyze"),
                                   limit: int = Query(20, description="Number of picks to return")):
    """Get picks with high confidence"""
    try:
        # Return mock high confidence picks data for now
        mock_high_confidence = [
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply confidence filter
        filtered_picks = [p for p in mock_high_confidence if p['confidence'] >= min_confidence]
        
        return {
            "high_confidence_picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "min_confidence": min_confidence,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock high confidence picks (>= {min_confidence}% confidence)"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "min_confidence": min_confidence,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/statistics")
async def get_picks_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get picks statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_picks": 22,
            "unique_games": 4,
            "unique_players": 8,
            "unique_stat_types": 6,
            "unique_pick_types": 1,
            "avg_line": 45.8,
            "avg_odds": -110,
            "avg_model_prob": 0.5950,
            "avg_implied_prob": 0.5238,
            "avg_ev": 11.23,
            "avg_confidence": 84.5,
            "avg_hit_rate": 63.4,
            "high_ev_picks": 18,
            "high_confidence_picks": 16,
            "high_hit_rate_picks": 20,
            "by_player": [
                {
                    "player_name": "Patrick Mahomes",
                    "total_picks": 2,
                    "avg_ev": 15.52,
                    "avg_confidence": 87.5,
                    "avg_hit_rate": 65.0,
                    "avg_model_prob": 0.6050,
                    "avg_implied_prob": 0.5217,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                },
                {
                    "player_name": "Stephen Curry",
                    "total_picks": 3,
                    "avg_ev": 16.91,
                    "avg_confidence": 88.7,
                    "avg_hit_rate": 64.4,
                    "avg_model_prob": 0.6233,
                    "avg_implied_prob": 0.5295,
                    "high_ev_picks": 3,
                    "high_confidence_picks": 3
                },
                {
                    "player_name": "Aaron Judge",
                    "total_picks": 2,
                    "avg_ev": 15.85,
                    "avg_confidence": 86.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.6000,
                    "avg_implied_prob": 0.5180,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                },
                {
                    "player_name": "LeBron James",
                    "total_picks": 2,
                    "avg_ev": 13.49,
                    "avg_confidence": 87.0,
                    "avg_hit_rate": 63.3,
                    "avg_model_prob": 0.5950,
                    "avg_implied_prob": 0.5217,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                }
            ],
            "by_stat_type": [
                {
                    "stat_type": "points",
                    "total_picks": 8,
                    "avg_ev": 16.47,
                    "avg_confidence": 87.9,
                    "avg_hit_rate": 64.1,
                    "avg_model_prob": 0.6163,
                    "avg_implied_prob": 0.5257,
                    "high_ev_picks": 8
                },
                {
                    "stat_type": "passing_touchdowns",
                    "total_picks": 1,
                    "avg_ev": 21.28,
                    "avg_confidence": 91.0,
                    "avg_hit_rate": 66.8,
                    "avg_model_prob": 0.6300,
                    "avg_implied_prob": 0.5195,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "home_runs",
                    "total_picks": 2,
                    "avg_ev": 15.85,
                    "avg_confidence": 86.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.6000,
                    "avg_implied_prob": 0.5180,
                    "high_ev_picks": 2
                },
                {
                    "stat_type": "hits",
                    "total_picks": 1,
                    "avg_ev": 15.92,
                    "avg_confidence": 88.0,
                    "avg_hit_rate": 64.2,
                    "avg_model_prob": 0.6200,
                    "avg_implied_prob": 0.5349,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "passing_yards",
                    "total_picks": 1,
                    "avg_ev": 10.75,
                    "avg_confidence": 84.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.5800,
                    "avg_implied_prob": 0.5238,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "rebounds",
                    "total_picks": 1,
                    "avg_ev": 9.34,
                    "avg_confidence": 82.0,
                    "avg_hit_rate": 61.1,
                    "avg_model_prob": 0.5600,
                    "avg_implied_prob": 0.5122,
                    "high_ev_picks": 1
                }
            ],
            "ev_distribution": [
                {
                    "ev_category": "Very High EV (15%+)",
                    "total_picks": 8,
                    "avg_ev": 17.89,
                    "avg_confidence": 88.8,
                    "avg_hit_rate": 64.6
                },
                {
                    "ev_category": "High EV (10-15%)",
                    "total_picks": 10,
                    "avg_ev": 12.17,
                    "avg_confidence": 83.2,
                    "avg_hit_rate": 62.8
                },
                {
                    "ev_category": "Medium EV (5-10%)",
                    "total_picks": 4,
                    "avg_ev": 7.52,
                    "avg_confidence": 80.5,
                    "avg_hit_rate": 61.9
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock picks statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/player/{player_name}")
async def get_picks_by_player(player_name: str, hours: int = Query(24, description="Hours of data to analyze")):
    """Get picks for a specific player"""
    try:
        # Return mock player picks data for now
        mock_player_picks = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 11,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "three_pointers",
                "line": 4.5,
                "odds": -110,
                "model_probability": 0.5700,
                "implied_probability": 0.5238,
                "ev_percentage": 8.84,
                "confidence": 80.0,
                "hit_rate": 61.7,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "player_name": player_name,
            "picks": mock_player_picks,
            "total": len(mock_player_picks),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock picks for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_name": player_name,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/game/{game_id}")
async def get_picks_by_game(game_id: int):
    """Get picks for a specific game"""
    try:
        # Return mock game picks data for now
        mock_game_picks = [
            {
                "id": 1,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 4,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 7,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "line": 26.5,
                "odds": -108,
                "model_probability": 0.5900,
                "implied_probability": 0.5195,
                "ev_percentage": 13.58,
                "confidence": 86.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "game_id": game_id,
            "picks": mock_game_picks,
            "total": len(mock_game_picks),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock picks for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/search")
async def search_picks(query: str = Query(..., description="Search query"),
                      hours: int = Query(24, description="Hours of data to analyze"),
                      limit: int = Query(20, description="Number of results to return")):
    """Search picks by player name or stat type"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['player_name'].lower() or 
                   query_lower in r['stat_type'].lower() or
                   query_lower in r['pick_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Player Statistics Tracking Endpoints
@router.get("/player-stats")
async def get_player_stats(player: str = Query(None, description="Player name to filter"),
                             team: str = Query(None, description="Team name to filter"),
                             stat_type: str = Query(None, description="Stat type to filter"),
                             days: int = Query(30, description="Days of data to analyze"),
                             limit: int = Query(50, description="Number of stats to return")):
    """Get player statistics with optional filters"""
    try:
        # Return mock player stats data for now
        mock_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 31.2,
                "line": 28.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 4,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": "three_pointers",
                "actual_value": 4.5,
                "line": 4.0,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_yards",
                "actual_value": 298.5,
                "line": 285.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 6,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_touchdowns",
                "actual_value": 3.0,
                "line": 2.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 7,
                "player_name": "Aaron Judge",
                "team": "New York Yankees",
                "opponent": "Boston Red Sox",
                "date": (datetime.now(timezone.utc) - timedelta(days=6)).date().isoformat(),
                "stat_type": "home_runs",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat()
            },
            {
                "id": 8,
                "player_name": "Mike Trout",
                "team": "Los Angeles Angels",
                "opponent": "Seattle Mariners",
                "date": (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat(),
                "stat_type": "hits",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            },
            {
                "id": 9,
                "player_name": "Connor McDavid",
                "team": "Edmonton Oilers",
                "opponent": "Calgary Flames",
                "date": (datetime.now(timezone.utc) - timedelta(days=8)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            },
            {
                "id": 10,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Miami Heat",
                "date": datetime.now(timezone.utc).date().isoformat(),
                "stat_type": "points",
                "actual_value": 22.5,
                "line": 25.0,
                "result": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        filtered_stats = mock_stats
        if player:
            filtered_stats = [s for s in filtered_stats if player.lower() in s['player_name'].lower()]
        if team:
            filtered_stats = [s for s in filtered_stats if team.lower() in s['team'].lower()]
        if stat_type:
            filtered_stats = [s for s in filtered_stats if s['stat_type'].lower() == stat_type.lower()]
        
        return {
            "stats": filtered_stats[:limit],
            "total": len(filtered_stats),
            "filters": {
                "player": player,
                "team": team,
                "stat_type": stat_type,
                "days": days,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock player stats data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-statistics")
async def get_player_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get overall player statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_stats": 25,
            "unique_players": 8,
            "unique_teams": 8,
            "unique_opponents": 8,
            "unique_stat_types": 10,
            "unique_dates": 10,
            "avg_actual_value": 45.8,
            "avg_line": 42.3,
            "hits": 18,
            "misses": 7,
            "hit_rate_percentage": 72.0,
            "top_performers": [
                {
                    "player_name": "LeBron James",
                    "total_stats": 3,
                    "hits": 2,
                    "misses": 1,
                    "hit_rate_percentage": 66.67,
                    "avg_actual_value": 20.83,
                    "avg_line": 18.83,
                    "unique_stat_types": 3
                },
                {
                    "player_name": "Stephen Curry",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 17.85,
                    "avg_line": 16.25,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Patrick Mahomes",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 300.75,
                    "avg_line": 289.0,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Aaron Judge",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 2.5,
                    "avg_line": 2.0,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Mike Trout",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 1.75,
                    "avg_line": 1.5,
                    "unique_stat_types": 2
                }
            ],
            "stat_type_performance": [
                {
                    "stat_type": "points",
                    "total_stats": 8,
                    "hits": 6,
                    "misses": 2,
                    "hit_rate_percentage": 75.0,
                    "avg_actual_value": 27.56,
                    "avg_line": 25.69,
                    "unique_players": 5
                },
                {
                    "stat_type": "passing_yards",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 287.2,
                    "avg_line": 280.5,
                    "unique_players": 2
                },
                {
                    "stat_type": "home_runs",
                    "total_stats": 1,
                    "hits": 1,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 2.0,
                    "avg_line": 1.5,
                    "unique_players": 1
                },
                {
                    "stat_type": "rebounds",
                    "total_stats": 2,
                    "hits": 1,
                    "misses": 1,
                    "hit_rate_percentage": 50.0,
                    "avg_actual_value": 7.35,
                    "avg_line": 7.25,
                    "unique_players": 1
                },
                {
                    "stat_type": "assists",
                    "total_stats": 1,
                    "hits": 1,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 7.8,
                    "avg_line": 6.5,
                    "unique_players": 1
                }
            ],
            "over_under_performance": [
                {
                    "over_under_result": "OVER",
                    "total_stats": 20,
                    "hits": 15,
                    "misses": 5,
                    "hit_rate_percentage": 75.0
                },
                {
                    "over_under_result": "UNDER",
                    "total_stats": 5,
                    "hits": 3,
                    "misses": 2,
                    "hit_rate_percentage": 60.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock player statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/{player_name}")
async def get_player_stats_by_name(player_name: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific player"""
    try:
        # Return mock player stats data for now
        mock_player_stats = [
            {
                "id": 1,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 10,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Miami Heat",
                "date": datetime.now(timezone.utc).date().isoformat(),
                "stat_type": "points",
                "actual_value": 22.5,
                "line": 25.0,
                "result": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        return {
            "player_name": player_name,
            "stats": mock_player_stats,
            "total": len(mock_player_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_name": player_name,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/team/{team}")
async def get_player_stats_by_team(team: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific team"""
    try:
        # Return mock team stats data for now
        mock_team_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "LeBron James",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Anthony Davis",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "points",
                "actual_value": 18.5,
                "line": 20.5,
                "result": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        return {
            "team": team,
            "stats": mock_team_stats,
            "total": len(mock_team_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {team}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "team": team,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/stat/{stat_type}")
async def get_player_stats_by_stat_type(stat_type: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific stat type"""
    try:
        # Return mock stat type stats data for now
        mock_stat_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 31.2,
                "line": 28.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Kevin Durant",
                "team": "Phoenix Suns",
                "opponent": "Denver Nuggets",
                "date": (datetime.now(timezone.utc) - timedelta(days=3)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 25.8,
                "line": 26.5,
                "result": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            }
        ]
        
        return {
            "stat_type": stat_type,
            "stats": mock_stat_stats,
            "total": len(mock_stat_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {stat_type}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "stat_type": stat_type,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/search")
async def search_player_stats(query: str = Query(..., description="Search query"),
                              days: int = Query(30, description="Days of data to analyze"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search player stats by player name, team, or stat type"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_yards",
                "actual_value": 298.5,
                "line": 285.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['player_name'].lower() or 
                   query_lower in r['team'].lower() or
                   query_lower in r['opponent'].lower() or
                   query_lower in r['stat_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "days": days,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "days": days,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Shared Betting Cards Tracking Endpoints
@router.get("/shared-cards")
async def get_shared_cards(platform: str = Query(None, description="Platform to filter"),
                            sport: str = Query(None, description="Sport to filter"),
                            grade: str = Query(None, description="Grade to filter"),
                            trending: bool = Query(False, description="Get trending cards"),
                            performing: bool = Query(False, description="Get top performing cards"),
                            limit: int = Query(50, description="Number of cards to return")):
    """Get shared betting cards with optional filters"""
    try:
        # Return mock shared cards data for now
        mock_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "platform": "discord",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "rebounds", "line": 7.5, "odds": -110},
                    {"player": "Anthony Davis", "market": "rebounds", "line": 10.5, "odds": -110},
                    {"player": "Nikola Jokic", "market": "rebounds", "line": 11.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0143,
                "overall_grade": "B+",
                "label": "NBA Rebounds Master Parlay",
                "kelly_suggested_units": 1.8,
                "kelly_risk_level": "Medium",
                "view_count": 890,
                "settled": True,
                "won": False,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 3,
                "platform": "twitter",
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Patrick Mahomes", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Josh Allen", "market": "passing_yards", "line": 265.5, "odds": -110},
                    {"player": "Justin Herbert", "market": "passing_yards", "line": 275.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0357,
                "overall_grade": "A-",
                "label": "NFL QB Passing Yards Parlay",
                "kelly_suggested_units": 3.2,
                "kelly_risk_level": "High",
                "view_count": 2100,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            },
            {
                "id": 4,
                "platform": "reddit",
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Christian McCaffrey", "market": "rushing_yards", "line": 85.5, "odds": -110},
                    {"player": "Derrick Henry", "market": "rushing_yards", "line": 95.5, "odds": -110},
                    {"player": "Jonathan Taylor", "market": "rushing_yards", "line": 90.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0214,
                "overall_grade": "B",
                "label": "NFL RB Rushing Yards Parlay",
                "kelly_suggested_units": 2.1,
                "kelly_risk_level": "Medium",
                "view_count": 1560,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 5,
                "platform": "twitter",
                "sport_id": 2,
                "sport": "MLB",
                "legs": [
                    {"player": "Aaron Judge", "market": "home_runs", "line": 1.5, "odds": -110},
                    {"player": "Mike Trout", "market": "hits", "line": 1.5, "odds": -110},
                    {"player": "Shohei Ohtani", "market": "strikeouts", "line": 7.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0429,
                "overall_grade": "A",
                "label": "MLB Stars Multi-Stat Parlay",
                "kelly_suggested_units": 3.8,
                "kelly_risk_level": "High",
                "view_count": 1890,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            },
            {
                "id": 6,
                "platform": "discord",
                "sport_id": 32,
                "sport": "NCAA Basketball",
                "legs": [
                    {"player": "Zion Williamson", "market": "points", "line": 22.5, "odds": -110},
                    {"player": "Paolo Banchero", "market": "points", "line": 20.5, "odds": -110},
                    {"player": "Chet Holmgren", "market": "rebounds", "line": 8.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0214,
                "overall_grade": "B+",
                "label": "NCAA Basketball Stars Parlay",
                "kelly_suggested_units": 2.4,
                "kelly_risk_level": "Medium",
                "view_count": 1450,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=9)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            },
            {
                "id": 7,
                "platform": "twitter",
                "sport_id": 99,
                "sport": "Multi-Sport",
                "legs": [
                    {"player": "LeBron James", "sport": "NBA", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Patrick Mahomes", "sport": "NFL", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Aaron Judge", "sport": "MLB", "market": "home_runs", "line": 1.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0250,
                "overall_grade": "A-",
                "label": "Multi-Sport Superstars Parlay",
                "kelly_suggested_units": 2.8,
                "kelly_risk_level": "High",
                "view_count": 2340,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=11)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            },
            {
                "id": 8,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "Stephen Curry", "market": "three_pointers", "line": 4.5, "odds": -110},
                    {"player": "Klay Thompson", "market": "three_pointers", "line": 3.5, "odds": -110},
                    {"player": "Damian Lillard", "market": "three_pointers", "line": 3.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0321,
                "overall_grade": "A",
                "label": "NBA Three-Point Specialists Parlay",
                "kelly_suggested_units": 3.0,
                "kelly_risk_level": "High",
                "view_count": 890,
                "settled": False,
                "won": None,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_cards = mock_cards
        if platform:
            filtered_cards = [c for c in filtered_cards if c['platform'].lower() == platform.lower()]
        if sport:
            filtered_cards = [c for c in filtered_cards if c['sport'].lower() == sport.lower()]
        if grade:
            filtered_cards = [c for c in filtered_cards if c['overall_grade'].lower() == grade.lower()]
        
        # Apply sorting
        if trending:
            filtered_cards = sorted(filtered_cards, key=lambda x: x['view_count'], reverse=True)
        elif performing:
            filtered_cards = sorted(filtered_cards, key=lambda x: x['parlay_ev'], reverse=True)
        
        return {
            "cards": filtered_cards[:limit],
            "total": len(filtered_cards),
            "filters": {
                "platform": platform,
                "sport": sport,
                "grade": grade,
                "trending": trending,
                "performing": performing,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock shared cards data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/statistics")
async def get_shared_cards_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get shared cards statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_cards": 12,
            "unique_platforms": 4,
            "unique_sports": 6,
            "avg_total_odds": 6.00,
            "avg_decimal_odds": 7.00,
            "avg_parlay_probability": 0.1429,
            "avg_parlay_ev": 0.0250,
            "grade_a_cards": 4,
            "settled_cards": 10,
            "won_cards": 7,
            "lost_cards": 3,
            "total_views": 15460,
            "avg_views_per_card": 1288.3,
            "platform_performance": [
                {
                    "platform": "twitter",
                    "total_cards": 6,
                    "settled_cards": 5,
                    "won_cards": 4,
                    "win_rate_percentage": 80.0,
                    "avg_parlay_ev": 0.0300,
                    "total_views": 9360,
                    "avg_views_per_card": 1560.0
                },
                {
                    "platform": "discord",
                    "total_cards": 3,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0180,
                    "total_views": 4230,
                    "avg_views_per_card": 1410.0
                },
                {
                    "platform": "reddit",
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0210,
                    "total_views": 3010,
                    "avg_views_per_card": 1505.0
                },
                {
                    "platform": "telegram",
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 860,
                    "avg_views_per_card": 860.0
                }
            ],
            "sport_performance": [
                {
                    "sport_id": 30,
                    "total_cards": 4,
                    "settled_cards": 3,
                    "won_cards": 2,
                    "win_rate_percentage": 66.7,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 6480,
                    "avg_views_per_card": 1620.0
                },
                {
                    "sport_id": 1,
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 2,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0285,
                    "total_views": 3660,
                    "avg_views_per_card": 1830.0
                },
                {
                    "sport_id": 2,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0429,
                    "total_views": 1890,
                    "avg_views_per_card": 1890.0
                },
                {
                    "sport_id": 32,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0214,
                    "total_views": 1450,
                    "avg_views_per_card": 1450.0
                },
                {
                    "sport_id": 99,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 2340,
                    "avg_views_per_card": 2340.0
                }
            ],
            "grade_performance": [
                {
                    "overall_grade": "A",
                    "total_cards": 4,
                    "settled_cards": 3,
                    "won_cards": 3,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0340,
                    "avg_kelly_units": 3.1,
                    "total_views": 6920,
                    "avg_views_per_card": 1730.0
                },
                {
                    "overall_grade": "A-",
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 2,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0300,
                    "avg_kelly_units": 3.0,
                    "total_views": 4440,
                    "avg_views_per_card": 2220.0
                },
                {
                    "overall_grade": "B+",
                    "total_cards": 3,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0180,
                    "avg_kelly_units": 2.1,
                    "total_views": 3930,
                    "avg_views_per_card": 1310.0
                },
                {
                    "overall_grade": "B",
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 0,
                    "win_rate_percentage": 0.0,
                    "avg_parlay_ev": 0.0214,
                    "avg_kelly_units": 2.1,
                    "total_views": 1560,
                    "avg_views_per_card": 1560.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock shared cards statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/platform/{platform}")
async def get_shared_cards_by_platform(platform: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards for a specific platform"""
    try:
        # Return mock platform-specific cards data for now
        mock_platform_cards = [
            {
                "id": 1,
                "platform": platform,
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "platform": platform,
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Patrick Mahomes", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Josh Allen", "market": "passing_yards", "line": 265.5, "odds": -110},
                    {"player": "Justin Herbert", "market": "passing_yards", "line": 275.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0357,
                "overall_grade": "A-",
                "label": "NFL QB Passing Yards Parlay",
                "kelly_suggested_units": 3.2,
                "kelly_risk_level": "High",
                "view_count": 2100,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            }
        ]
        
        return {
            "platform": platform,
            "cards": mock_platform_cards[:limit],
            "total": len(mock_platform_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for {platform}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "platform": platform,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/sport/{sport}")
async def get_shared_cards_by_sport(sport: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards for a specific sport"""
    try:
        # Return mock sport-specific cards data for now
        mock_sport_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": sport,
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "platform": "discord",
                "sport_id": 30,
                "sport": sport,
                "legs": [
                    {"player": "LeBron James", "market": "rebounds", "line": 7.5, "odds": -110},
                    {"player": "Anthony Davis", "market": "rebounds", "line": 10.5, "odds": -110},
                    {"player": "Nikola Jokic", "market": "rebounds", "line": 11.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0143,
                "overall_grade": "B+",
                "label": "NBA Rebounds Master Parlay",
                "kelly_suggested_units": 1.8,
                "kelly_risk_level": "Medium",
                "view_count": 890,
                "settled": True,
                "won": False,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            }
        ]
        
        return {
            "sport": sport,
            "cards": mock_sport_cards[:limit],
            "total": len(mock_sport_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for {sport}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport": sport,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/grade/{grade}")
async def get_shared_cards_by_grade(grade: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards by grade"""
    try:
        # Return mock grade-specific cards data for now
        mock_grade_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": grade,
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "platform": "twitter",
                "sport_id": 2,
                "sport": "MLB",
                "legs": [
                    {"player": "Aaron Judge", "market": "home_runs", "line": 1.5, "odds": -110},
                    {"player": "Mike Trout", "market": "hits", "line": 1.5, "odds": -110},
                    {"player": "Shohei Ohtani", "market": "strikeouts", "line": 7.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0429,
                "overall_grade": grade,
                "label": "MLB Stars Multi-Stat Parlay",
                "kelly_suggested_units": 3.8,
                "kelly_risk_level": "High",
                "view_count": 1890,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            }
        ]
        
        return {
            "grade": grade,
            "cards": mock_grade_cards[:limit],
            "total": len(mock_grade_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for grade {grade}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "grade": grade,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/search")
async def search_shared_cards(query: str = Query(..., description="Search query"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search shared cards by label or legs"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 8,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "Stephen Curry", "market": "three_pointers", "line": 4.5, "odds": -110},
                    {"player": "Klay Thompson", "market": "three_pointers", "line": 3.5, "odds": -110},
                    {"player": "Damian Lillard", "market": "three_pointers", "line": 3.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0321,
                "overall_grade": "A",
                "label": "NBA Three-Point Specialists Parlay",
                "kelly_suggested_units": 3.0,
                "kelly_risk_level": "High",
                "view_count": 890,
                "settled": False,
                "won": None,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['label'].lower() or 
                   any(query_lower in leg['player'].lower() or 
                       query_lower in leg['market'].lower() 
                       for leg in r['legs'])
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Trade Details Tracking Endpoints
@router.get("/trade-details")
async def get_trade_details(trade_id: str = Query(None, description="Trade ID to filter"),
                           team_id: int = Query(None, description="Team ID to filter"),
                           player_id: int = Query(None, description="Player ID to filter"),
                           asset_type: str = Query(None, description="Asset type to filter"),
                           recent: bool = Query(False, description="Get recent trades"),
                           limit: int = Query(50, description="Number of trade details to return")):
    """Get trade details with optional filters"""
    try:
        # Return mock trade details data for now
        mock_trade_details = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_001",
                "player_id": 2,
                "from_team_id": 3,
                "to_team_id": 5,
                "asset_type": "player",
                "asset_description": "All-star guard with scoring ability",
                "player_name": "Devin Booker",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 3,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 4,
                "trade_id": "NBA_2024_002",
                "player_id": 4,
                "from_team_id": 7,
                "to_team_id": 4,
                "asset_type": "player",
                "asset_description": "Veteran center with defensive presence",
                "player_name": "Nikola Jokic",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 5,
                "trade_id": "NFL_2024_001",
                "player_id": 101,
                "from_team_id": 101,
                "to_team_id": 102,
                "asset_type": "player",
                "asset_description": "Elite quarterback with Super Bowl experience",
                "player_name": "Aaron Rodgers",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 6,
                "trade_id": "NFL_2024_001",
                "player_id": 102,
                "from_team_id": 102,
                "to_team_id": 101,
                "asset_type": "player",
                "asset_description": "Pro Bowl wide receiver with speed",
                "player_name": "Davante Adams",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 7,
                "trade_id": "MLB_2024_001",
                "player_id": 201,
                "from_team_id": 201,
                "to_team_id": 202,
                "asset_type": "player",
                "asset_description": "Power-hitting first baseman with MVP potential",
                "player_name": "Pete Alonso",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 8,
                "trade_id": "MLB_2024_001",
                "player_id": 202,
                "from_team_id": 202,
                "to_team_id": 201,
                "asset_type": "player",
                "asset_description": "Ace pitcher with strikeout ability",
                "player_name": "Jacob deGrom",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 9,
                "trade_id": "NHL_2024_001",
                "player_id": 301,
                "from_team_id": 301,
                "to_team_id": 302,
                "asset_type": "player",
                "asset_description": "Elite center with scoring ability",
                "player_name": "Connor McDavid",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 10,
                "trade_id": "NHL_2024_001",
                "player_id": 302,
                "from_team_id": 302,
                "to_team_id": 301,
                "asset_type": "player",
                "asset_description": "Power forward with physical presence",
                "player_name": "Nathan MacKinnon",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 11,
                "trade_id": "NBA_2024_005",
                "player_id": 9,
                "from_team_id": 11,
                "to_team_id": 12,
                "asset_type": "draft_pick",
                "asset_description": "2025 first round draft pick (lottery protected)",
                "player_name": "2025 1st Round Pick",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            },
            {
                "id": 12,
                "trade_id": "NBA_2024_005",
                "player_id": 10,
                "from_team_id": 12,
                "to_team_id": 11,
                "asset_type": "player",
                "asset_description": "Young center with defensive potential",
                "player_name": "Walker Kessler",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_trades = mock_trade_details
        if trade_id:
            filtered_trades = [t for t in filtered_trades if t['trade_id'] == trade_id]
        if team_id:
            filtered_trades = [t for t in filtered_trades if t['from_team_id'] == team_id or t['to_team_id'] == team_id]
        if player_id:
            filtered_trades = [t for t in filtered_trades if t['player_id'] == player_id]
        if asset_type:
            filtered_trades = [t for t in filtered_trades if t['asset_type'] == asset_type]
        
        # Apply sorting
        if recent:
            filtered_trades = sorted(filtered_trades, key=lambda x: x['created_at'], reverse=True)
        
        return {
            "trade_details": filtered_trades[:limit],
            "total": len(filtered_trades),
            "filters": {
                "trade_id": trade_id,
                "team_id": team_id,
                "player_id": player_id,
                "asset_type": asset_type,
                "recent": recent,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trade details data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/statistics")
async def get_trade_details_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get trade details statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_trade_records": 28,
            "unique_trades": 14,
            "unique_players": 28,
            "unique_from_teams": 12,
            "unique_to_teams": 12,
            "unique_asset_types": 2,
            "player_trades": 26,
            "draft_pick_trades": 2,
            "same_team_trades": 0,
            "different_team_trades": 28,
            "asset_type_stats": [
                {
                    "asset_type": "player",
                    "total_trades": 26,
                    "unique_trades": 13,
                    "unique_players": 26
                },
                {
                    "asset_type": "draft_pick",
                    "total_trades": 2,
                    "unique_trades": 1,
                    "unique_players": 2
                }
            ],
            "team_stats": [
                {
                    "team_id": 5,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 3,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 4,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 7,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 101,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                }
            ],
            "player_stats": [
                {
                    "player_id": 1,
                    "player_name": "Kevin Durant",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 2,
                    "player_name": "Devin Booker",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 3,
                    "player_name": "Kyle Lowry",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 4,
                    "player_name": "Nikola Jokic",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 101,
                    "player_name": "Aaron Rodgers",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trade details statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/trade/{trade_id}")
async def get_trade_details_by_trade_id(trade_id: str):
    """Get trade details for a specific trade"""
    try:
        # Return mock trade-specific data for now
        mock_trade_summary = {
            "trade_id": trade_id,
            "total_assets": 2,
            "from_teams": [5, 3],
            "to_teams": [3, 5],
            "player_assets": [
                {
                    "player_id": 1,
                    "player_name": "Kevin Durant",
                    "asset_type": "player",
                    "asset_description": "Star forward with championship experience",
                    "from_team_id": 5,
                    "to_team_id": 3
                },
                {
                    "player_id": 2,
                    "player_name": "Devin Booker",
                    "asset_type": "player",
                    "asset_description": "All-star guard with scoring ability",
                    "from_team_id": 3,
                    "to_team_id": 5
                }
            ],
            "draft_pick_assets": [],
            "other_assets": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        }
        
        return {
            "trade_summary": mock_trade_summary,
            "trade_id": trade_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade summary for {trade_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "trade_id": trade_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/team/{team_id}")
async def get_trade_details_by_team(team_id: int, role: str = Query("both", description="Team role: from, to, or both")):
    """Get trade details for a specific team"""
    try:
        # Return mock team-specific data for now
        mock_team_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": team_id,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": team_id,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        # Filter by role
        if role == "from":
            mock_team_trades = [t for t in mock_team_trades if t['from_team_id'] == team_id]
        elif role == "to":
            mock_team_trades = [t for t in mock_team_trades if t['to_team_id'] == team_id]
        
        return {
            "team_id": team_id,
            "role": role,
            "trade_details": mock_team_trades,
            "total": len(mock_team_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for team {team_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "team_id": team_id,
            "role": role,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/player/{player_id}")
async def get_trade_details_by_player(player_id: int):
    """Get trade details for a specific player"""
    try:
        # Return mock player-specific data for now
        mock_player_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": player_id,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_003",
                "player_id": player_id,
                "from_team_id": 6,
                "to_team_id": 8,
                "asset_type": "player",
                "asset_description": "Rising star with high potential",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
            }
        ]
        
        return {
            "player_id": player_id,
            "trade_details": mock_player_trades,
            "total": len(mock_player_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/asset-type/{asset_type}")
async def get_trade_details_by_asset_type(asset_type: str, limit: int = Query(50, description="Number of trade details to return")):
    """Get trade details by asset type"""
    try:
        # Return mock asset-type-specific data for now
        mock_asset_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": asset_type,
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": asset_type,
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "asset_type": asset_type,
            "trade_details": mock_asset_trades[:limit],
            "total": len(mock_asset_trades),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for asset type {asset_type}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "asset_type": asset_type,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/search")
async def search_trade_details(query: str = Query(..., description="Search query"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search trade details by player name or trade ID"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['trade_id'].lower() or 
                   query_lower in r['player_name'].lower() or 
                   (r['asset_description'] and query_lower in r['asset_description'].lower())
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Master Trade Tracking Endpoints
@router.get("/trades")
async def get_trades(season: int = Query(None, description="Season year to filter"),
                     source: str = Query(None, description="Source to filter"),
                     applied: bool = Query(None, description="Applied status to filter"),
                     recent: bool = Query(False, description="Get recent trades"),
                     limit: int = Query(50, description="Number of trades to return")):
    """Get master trades with optional filters"""
    try:
        # Return mock trades data for now
        mock_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": 2024,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 3,
                "trade_date": "2024-02-18",
                "season_year": 2024,
                "description": "The Indiana Pacers and Portland Trail Blazers completed a trade sending rising star Tyrese Haliburton to Portland in exchange for veteran scorer Damian Lillard. The Pacers get immediate championship help while the Trail Blazers build around their new young star.",
                "headline": "Pacers Send Haliburton to Trail Blazers for Lillard",
                "source_url": "https://www.bleacherreport.com/nba/articles/pacers-send-haliburton-to-trail-blazers-for-lillard",
                "source": "Bleacher Report",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": "NFL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 5,
                "trade_date": "2024-03-22",
                "season_year": 2024,
                "description": "The Carolina Panthers traded running back Christian McCaffrey to the San Francisco 49ers in exchange for veteran linebacker Bobby Wagner. The 49ers add an elite offensive weapon while the Panthers strengthen their defense.",
                "headline": "Panthers Trade McCaffrey to 49ers for Wagner",
                "source_url": "https://www.espn.com/nfl/story/_/id/23456789/panthers-trade-mccaffrey-to-49ers-for-wagner",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat()
            },
            {
                "id": 6,
                "trade_date": "2024-07-31",
                "season_year": 2024,
                "description": "The New York Mets traded power-hitting first baseman Pete Alonso to the Los Angeles Dodgers in exchange for ace pitcher Jacob deGrom. The Dodgers add a middle-of-the-order bat while the Mets acquire a frontline starter.",
                "headline": "Mets Trade Alonso to Dodgers for deGrom",
                "source_url": "https://www.mlb.com/trade-news/mets-trade-alonso-to-dodgers-for-degrom",
                "source": "MLB.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 7,
                "trade_date": "2024-07-28",
                "season_year": 2024,
                "description": "The Los Angeles Angels traded superstar Mike Trout to the San Diego Padres in exchange for All-Star third baseman Manny Machado. The Padres add a generational talent while the Angels get a proven power hitter.",
                "headline": "Angels Trade Trout to Padres for Machado",
                "source_url": "https://www.baseballamerica.com/mlb/angels-trade-trout-to-padres-for-machado",
                "source": "Baseball America",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=32)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=32)).isoformat()
            },
            {
                "id": 8,
                "trade_date": "2024-03-08",
                "season_year": 2024,
                "description": "The Edmonton Oilers traded elite center Connor McDavid to the Toronto Maple Leafs in exchange for power forward Nathan MacKinnon. The Maple Leafs get their franchise center while the Oilers add a dominant power forward.",
                "headline": "Oilers Trade McDavid to Maple Leafs for MacKinnon",
                "source_url": "https://www.tsn.ca/nhl/oilers-trade-mcdavid-to-maple-leafs-for-mackinnon",
                "source": "TSN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 9,
                "trade_date": "2024-03-12",
                "season_year": 2024,
                "description": "The Tampa Bay Lightning traded elite goaltender Andrei Vasilevskiy to the Colorado Avalanche in exchange for offensive defenseman Victor Hedman. The Avalanche add a Vezina-caliber goalie while the Lightning get a top-pairing defenseman.",
                "headline": "Lightning Trade Vasilevskiy to Avalanche for Hedman",
                "source_url": "https://www.nhl.com/news/lightning-trade-vasilevskiy-to-avalanche-for-hedman",
                "source": "NHL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 10,
                "trade_date": "2024-02-28",
                "season_year": 2024,
                "description": "The Indiana Pacers acquired a 2025 first-round draft pick from the Cleveland Cavaliers in exchange for young center Walker Kessler. The Pacers add future assets while the Cavaliers get immediate help in the paint.",
                "headline": "Pacers Acquire 2025 First-Round Pick from Cavaliers",
                "source_url": "https://www.theathletic.com/nba/pacers-acquire-2025-first-round-pick-from-cavaliers",
                "source": "The Athletic",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_trades = mock_trades
        if season:
            filtered_trades = [t for t in filtered_trades if t['season_year'] == season]
        if source:
            filtered_trades = [t for t in filtered_trades if t['source'] == source]
        if applied is not None:
            filtered_trades = [t for t in filtered_trades if t['is_applied'] == applied]
        
        # Apply sorting
        if recent:
            filtered_trades = sorted(filtered_trades, key=lambda x: x['trade_date'], reverse=True)
        
        return {
            "trades": filtered_trades[:limit],
            "total": len(filtered_trades),
            "filters": {
                "season": season,
                "source": source,
                "applied": applied,
                "recent": recent,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/statistics")
async def get_trades_statistics(days: int = Query(365, description="Days of data to analyze")):
    """Get master trades statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_trades": 14,
            "unique_seasons": 1,
            "unique_sources": 7,
            "applied_trades": 14,
            "pending_trades": 0,
            "earliest_trade": "2024-02-08",
            "latest_trade": "2024-07-31",
            "avg_description_length": 245.7,
            "avg_headline_length": 52.3,
            "season_stats": [
                {
                    "season_year": 2024,
                    "total_trades": 14,
                    "applied_trades": 14,
                    "unique_sources": 7
                }
            ],
            "source_stats": [
                {
                    "source": "ESPN",
                    "total_trades": 3,
                    "unique_seasons": 1,
                    "applied_trades": 3
                },
                {
                    "source": "NBA.com",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "Bleacher Report",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "NFL.com",
                    "total_trades": 2,
                    "unique_seasons": 1,
                    "applied_trades": 2
                },
                {
                    "source": "MLB.com",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "TSN",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "The Athletic",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                }
            ],
            "month_stats": [
                {
                    "trade_month": "2024-07-01T00:00:00+00:00",
                    "total_trades": 2,
                    "unique_seasons": 1,
                    "applied_trades": 2
                },
                {
                    "trade_month": "2024-03-01T00:00:00+00:00",
                    "total_trades": 5,
                    "unique_seasons": 1,
                    "applied_trades": 5
                },
                {
                    "trade_month": "2024-02-01T00:00:00+00:00",
                    "total_trades": 7,
                    "unique_seasons": 1,
                    "applied_trades": 7
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trades statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/season/{season}")
async def get_trades_by_season(season: int):
    """Get trades for a specific season"""
    try:
        # Return mock season-specific data for now
        mock_season_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": season,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": season,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "season": season,
            "trades": mock_season_trades,
            "total": len(mock_season_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trades for season {season}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "season": season,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/source/{source}")
async def get_trades_by_source(source: str):
    """Get trades from a specific source"""
    try:
        # Return mock source-specific data for now
        mock_source_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": source,
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": source,
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            }
        ]
        
        return {
            "source": source,
            "trades": mock_source_trades,
            "total": len(mock_source_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trades from {source}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/applied")
async def get_applied_trades():
    """Get applied trades"""
    try:
        # Return mock applied trades data for now
        mock_applied_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": 2024,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "trades": mock_applied_trades,
            "total": len(mock_applied_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock applied trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/pending")
async def get_pending_trades():
    """Get pending trades"""
    try:
        # Return mock pending trades data for now
        mock_pending_trades = [
            {
                "id": 11,
                "trade_date": "2024-08-15",
                "season_year": 2024,
                "description": "The Los Angeles Lakers and Miami Heat are discussing a potential trade that would send Anthony Davis to Miami in exchange for Bam Adebayo and future draft picks. The deal is still in negotiation stages.",
                "headline": "Lakers and Heat Discussing Davis for Adebayo Trade",
                "source_url": "https://www.espn.com/nba/story/_/id/34567890/lakers-heat-discussing-davis-for-adebayo-trade",
                "source": "ESPN",
                "is_applied": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            },
            {
                "id": 12,
                "trade_date": "2024-08-12",
                "season_year": 2024,
                "description": "The Dallas Cowboys and San Francisco 49ers are in talks about a trade that would send Dak Prescott to San Francisco in exchange for Trey Lance and multiple draft picks. The trade is pending league approval.",
                "headline": "Cowboys and 49ers in Trade Talks for Prescott",
                "source_url": "https://www.nfl.com/news/cowboys-49ers-in-trade-talks-for-prescott",
                "source": "NFL.com",
                "is_applied": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            }
        ]
        
        return {
            "trades": mock_pending_trades,
            "total": len(mock_pending_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock pending trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/search")
async def search_trades(query: str = Query(..., description="Search query"),
                        limit: int = Query(20, description="Number of results to return")):
    """Search trades by headline or description"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": "NFL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['headline'].lower() or 
                   query_lower in r['description'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# User Betting Tracking Endpoints
@router.get("/user-bets")
async def get_user_bets(sport: int = Query(None, description="Sport ID to filter"),
                        status: str = Query(None, description="Bet status to filter"),
                        sportsbook: str = Query(None, description="Sportsbook to filter"),
                        recent: bool = Query(False, description="Get recent bets"),
                        limit: int = Query(50, description="Number of bets to return")):
    """Get user bets with optional filters"""
    try:
        # Return mock user bets data for now
        mock_user_bets = [
            {
                "id": 1,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": "DraftKings",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 2,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 92,
                "market_type": "points",
                "side": "over",
                "line_value": 28.5,
                "sportsbook": "FanDuel",
                "opening_odds": -110,
                "stake": 55.00,
                "status": "lost",
                "actual_value": 26.0,
                "closing_odds": -115,
                "closing_line": 28.5,
                "clv_cents": -5.0,
                "profit_loss": -55.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=18)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "Steph Curry over 28.5 points - tough defense from Lakers",
                "model_pick_id": 2,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=18)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 3,
                "sport_id": 1,
                "game_id": 664,
                "player_id": 111,
                "market_type": "passing_yards",
                "side": "over",
                "line_value": 285.5,
                "sportsbook": "PointsBet",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 312.0,
                "closing_odds": -105,
                "closing_line": 285.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat(),
                "notes": "Patrick Mahomes over 285.5 yards - great matchup vs Bills",
                "model_pick_id": 5,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat()
            },
            {
                "id": 4,
                "sport_id": 2,
                "game_id": 666,
                "player_id": 201,
                "market_type": "home_runs",
                "side": "over",
                "line_value": 1.5,
                "sportsbook": "BetMGM",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 2.0,
                "closing_odds": -105,
                "closing_line": 1.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=23)).isoformat(),
                "notes": "Aaron Judge over 1.5 HRs - facing struggling pitcher",
                "model_pick_id": 9,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=23)).isoformat()
            },
            {
                "id": 5,
                "sport_id": 53,
                "game_id": 668,
                "player_id": 301,
                "market_type": "points",
                "side": "over",
                "line_value": 1.5,
                "sportsbook": "Bet365",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 2.0,
                "closing_odds": -105,
                "closing_line": 1.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=23)).isoformat(),
                "notes": "Connor McDavid over 1.5 points - always dangerous",
                "model_pick_id": 12,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=23)).isoformat()
            },
            {
                "id": 6,
                "sport_id": 30,
                "game_id": 669,
                "player_id": 105,
                "market_type": "points",
                "side": "over",
                "line_value": 22.5,
                "sportsbook": "FanDuel",
                "opening_odds": -110,
                "stake": 220.00,
                "status": "pending",
                "actual_value": None,
                "closing_odds": None,
                "closing_line": None,
                "clv_cents": None,
                "profit_loss": None,
                "placed_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "settled_at": None,
                "notes": "Jayson Tatum over 22.5 points - game in progress",
                "model_pick_id": 14,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 7,
                "sport_id": 1,
                "game_id": 670,
                "player_id": 115,
                "market_type": "passing_touchdowns",
                "side": "over",
                "line_value": 1.5,
                "sportsbook": "BetMGM",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "pending",
                "actual_value": None,
                "closing_odds": None,
                "closing_line": None,
                "clv_cents": None,
                "profit_loss": None,
                "placed_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "settled_at": None,
                "notes": "Joe Burrow over 1.5 TDs - primetime game",
                "model_pick_id": 15,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_bets = mock_user_bets
        if sport:
            filtered_bets = [b for b in filtered_bets if b['sport_id'] == sport]
        if status:
            filtered_bets = [b for b in filtered_bets if b['status'] == status]
        if sportsbook:
            filtered_bets = [b for b in filtered_bets if b['sportsbook'] == sportsbook]
        
        # Apply sorting
        if recent:
            filtered_bets = sorted(filtered_bets, key=lambda x: x['placed_at'], reverse=True)
        
        return {
            "user_bets": filtered_bets[:limit],
            "total": len(filtered_bets),
            "filters": {
                "sport": sport,
                "status": status,
                "sportsbook": sportsbook,
                "recent": recent,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock user bets data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/statistics")
async def get_user_bets_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get user bets statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_bets": 15,
            "unique_sports": 4,
            "unique_games": 10,
            "unique_players": 12,
            "unique_sportsbooks": 6,
            "unique_market_types": 8,
            "won_bets": 8,
            "lost_bets": 4,
            "pending_bets": 3,
            "total_stake": 1210.00,
            "total_profit_loss": 345.00,
            "avg_stake": 80.67,
            "avg_profit_loss": 23.00,
            "win_rate_percentage": 66.67,
            "total_clv_cents": 15.00,
            "avg_clv_cents": 1.00,
            "sport_stats": [
                {
                    "sport_id": 30,
                    "total_bets": 4,
                    "won_bets": 2,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 495.00,
                    "total_profit_loss": 45.00,
                    "win_rate_percentage": 66.67,
                    "avg_clv_cents": 0.00
                },
                {
                    "sport_id": 1,
                    "total_bets": 3,
                    "won_bets": 1,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 330.00,
                    "total_profit_loss": 45.00,
                    "win_rate_percentage": 50.00,
                    "avg_clv_cents": 0.00
                },
                {
                    "sport_id": 2,
                    "total_bets": 3,
                    "won_bets": 1,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 220.00,
                    "total_profit_loss": 45.00,
                    "win_rate_percentage": 50.00,
                    "avg_clv_cents": 0.00
                },
                {
                    "sport_id": 53,
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                }
            ],
            "sportsbook_stats": [
                {
                    "sportsbook": "DraftKings",
                    "total_bets": 2,
                    "won_bets": 1,
                    "lost_bets": 1,
                    "pending_bets": 0,
                    "total_stake": 220.00,
                    "total_profit_loss": 0.00,
                    "win_rate_percentage": 50.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "sportsbook": "FanDuel",
                    "total_bets": 3,
                    "won_bets": 1,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 385.00,
                    "total_profit_loss": -55.00,
                    "win_rate_percentage": 50.00,
                    "avg_clv_cents": -5.00
                },
                {
                    "sportsbook": "BetMGM",
                    "total_bets": 3,
                    "won_bets": 2,
                    "lost_bets": 0,
                    "pending_bets": 1,
                    "total_stake": 330.00,
                    "total_profit_loss": 200.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "sportsbook": "PointsBet",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "sportsbook": "Bet365",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "sportsbook": "Caesars",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 2.00
                }
            ],
            "market_stats": [
                {
                    "market_type": "points",
                    "total_bets": 4,
                    "won_bets": 2,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 495.00,
                    "total_profit_loss": 45.00,
                    "win_rate_percentage": 66.67,
                    "avg_clv_cents": 0.00
                },
                {
                    "market_type": "passing_yards",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "market_type": "home_runs",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "market_type": "points",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock user bets statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/sport/{sport_id}")
async def get_user_bets_by_sport(sport_id: int):
    """Get user bets for a specific sport"""
    try:
        # Return mock sport-specific data for now
        mock_sport_bets = [
            {
                "id": 1,
                "sport_id": sport_id,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": "DraftKings",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 2,
                "sport_id": sport_id,
                "game_id": 662,
                "player_id": 92,
                "market_type": "points",
                "side": "over",
                "line_value": 28.5,
                "sportsbook": "FanDuel",
                "opening_odds": -110,
                "stake": 55.00,
                "status": "lost",
                "actual_value": 26.0,
                "closing_odds": -115,
                "closing_line": 28.5,
                "clv_cents": -5.0,
                "profit_loss": -55.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=18)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "Steph Curry over 28.5 points - tough defense from Lakers",
                "model_pick_id": 2,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=18)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            }
        ]
        
        return {
            "sport_id": sport_id,
            "user_bets": mock_sport_bets,
            "total": len(mock_sport_bets),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock user bets for sport {sport_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/status/{status}")
async def get_user_bets_by_status(status: str):
    """Get user bets by status"""
    try:
        # Return mock status-specific data for now
        mock_status_bets = [
            {
                "id": 1,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": "DraftKings",
                "opening_odds": -110,
                "stake": 110.00,
                "status": status,
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 3,
                "sport_id": 1,
                "game_id": 664,
                "player_id": 111,
                "market_type": "passing_yards",
                "side": "over",
                "line_value": 285.5,
                "sportsbook": "PointsBet",
                "opening_odds": -110,
                "stake": 110.00,
                "status": status,
                "actual_value": 312.0,
                "closing_odds": -105,
                "closing_line": 285.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat(),
                "notes": "Patrick Mahomes over 285.5 yards - great matchup vs Bills",
                "model_pick_id": 5,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat()
            }
        ]
        
        return {
            "status": status,
            "user_bets": mock_status_bets,
            "total": len(mock_status_bets),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock user bets with status {status}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/sportsbook/{sportsbook}")
async def get_user_bets_by_sportsbook(sportsbook: str):
    """Get user bets from a specific sportsbook"""
    try:
        # Return mock sportsbook-specific data for now
        mock_sportsbook_bets = [
            {
                "id": 1,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": sportsbook,
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 4,
                "sport_id": 2,
                "game_id": 666,
                "player_id": 201,
                "market_type": "home_runs",
                "side": "over",
                "line_value": 1.5,
                "sportsbook": sportsbook,
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 2.0,
                "closing_odds": -105,
                "closing_line": 1.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=23)).isoformat(),
                "notes": "Aaron Judge over 1.5 HRs - facing struggling pitcher",
                "model_pick_id": 9,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=23)).isoformat()
            }
        ]
        
        return {
            "sportsbook": sportsbook,
            "user_bets": mock_sportsbook_bets,
            "total": len(mock_sportsbook_bets),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock user bets from {sportsbook}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sportsbook": sportsbook,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/search")
async def search_user_bets(query: str = Query(..., description="Search query"),
                           limit: int = Query(20, description="Number of results to return")):
    """Search user bets by market, side, or notes"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": "DraftKings",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 3,
                "sport_id": 1,
                "game_id": 664,
                "player_id": 111,
                "market_type": "passing_yards",
                "side": "over",
                "line_value": 285.5,
                "sportsbook": "PointsBet",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 312.0,
                "closing_odds": -105,
                "closing_line": 285.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat(),
                "notes": "Patrick Mahomes over 285.5 yards - great matchup vs Bills",
                "model_pick_id": 5,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['market_type'].lower() or 
                   query_lower in r['side'].lower() or 
                   (r['notes'] and query_lower in r['notes'].lower())
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Brain Anomaly Detection Endpoints
@router.get("/brain-anomalies")
async def get_brain_anomalies():
    """Get current brain anomalies"""
    try:
        # Return mock anomaly data for now
        mock_anomalies = [
            {
                "id": 1,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
                "metric_name": "recommendation_hit_rate",
                "baseline_value": 0.60,
                "current_value": 0.35,
                "change_pct": -41.7,
                "severity": "high",
                "status": "active",
                "details": "Recommendation hit rate dropped significantly during market volatility",
                "resolved_at": None,
                "resolution_method": None
            },
            {
                "id": 2,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=36)).isoformat(),
                "metric_name": "memory_usage",
                "baseline_value": 0.60,
                "current_value": 0.95,
                "change_pct": 58.3,
                "severity": "high",
                "status": "active",
                "details": "Memory usage approaching critical levels",
                "resolved_at": None,
                "resolution_method": None
            }
        ]
        
        return {
            "anomalies": mock_anomalies,
            "total": len(mock_anomalies),
            "active": len([a for a in mock_anomalies if a["status"] == "active"]),
            "resolved": len([a for a in mock_anomalies if a["status"] == "resolved"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock anomaly data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-anomalies-summary")
async def get_brain_anomalies_summary():
    """Get brain anomalies summary"""
    try:
        # Return mock summary
        return {
            "total_anomalies": 9,
            "active_anomalies": 2,
            "resolved_anomalies": 7,
            "high_severity": 4,
            "medium_severity": 4,
            "low_severity": 1,
            "most_common_metrics": [
                {"metric_name": "error_rate", "count": 2},
                {"metric_name": "recommendation_hit_rate", "count": 2}
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock anomaly summary"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/working-parlays")
async def get_working_parlays_immediate(
    sport_id: int = Query(31, description="Sport ID"),
    limit: int = Query(5, description="Number of parlays to return")
):
    """Immediate working parlay endpoint"""
    try:
        mock_parlays = [
            {
                'id': 1,
                'total_ev': 0.15,
                'total_odds': 275,
                'legs': [
                    {'player_name': 'Drake Maye', 'stat_type': 'Passing Yards', 'line_value': 245.5, 'side': 'over', 'odds': -110, 'edge': 0.12},
                    {'player_name': 'Sam Darnold', 'stat_type': 'Passing Yards', 'line_value': 235.5, 'side': 'over', 'odds': -105, 'edge': 0.08}
                ],
                'confidence_score': 0.75,
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 2,
                'total_ev': 0.18,
                'total_odds': 320,
                'legs': [
                    {'player_name': 'Drake Maye', 'stat_type': 'Passing TDs', 'line_value': 1.5, 'side': 'over', 'odds': -115, 'edge': 0.15},
                    {'player_name': 'Sam Darnold', 'stat_type': 'Passing TDs', 'line_value': 1.5, 'side': 'over', 'odds': -110, 'edge': 0.12}
                ],
                'confidence_score': 0.78,
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 3,
                'total_ev': 0.22,
                'total_odds': 450,
                'legs': [
                    {'player_name': 'Drake Maye', 'stat_type': 'Completions', 'line_value': 22.5, 'side': 'over', 'odds': -105, 'edge': 0.09},
                    {'player_name': 'Sam Darnold', 'stat_type': 'Completions', 'line_value': 21.5, 'side': 'over', 'odds': -110, 'edge': 0.11},
                    {'player_name': 'Drake Maye', 'stat_type': 'Passing Yards', 'line_value': 245.5, 'side': 'over', 'odds': -110, 'edge': 0.12}
                ],
                'confidence_score': 0.82,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        return {
            'parlays': mock_parlays[:limit],
            'total': len(mock_parlays),
            'sport_id': sport_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'parlays': [],
            'total': 0,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

@router.get("/monte-carlo")
async def get_monte_carlo_immediate():
    """Immediate Monte Carlo endpoint"""
    try:
        return {
            'game_id': 648,
            'sport_id': 31,
            'simulations_run': 10000,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'results': {
                'drake_mayne': {
                    'passing_yards': {'mean': 248.5, 'median': 245.0, 'std_dev': 45.2},
                    'passing_tds': {'mean': 1.8, 'median': 2.0, 'std_dev': 0.9},
                    'completions': {'mean': 23.2, 'median': 23.0, 'std_dev': 4.1}
                },
                'sam_darnold': {
                    'passing_yards': {'mean': 238.5, 'median': 235.0, 'std_dev': 42.8},
                    'passing_tds': {'mean': 1.6, 'median': 2.0, 'std_dev': 0.8},
                    'completions': {'mean': 22.1, 'median': 22.0, 'std_dev': 3.9}
                }
            },
            'probabilities': {
                'drake_mayne_passing_yards_over_245.5': 0.52,
                'sam_darnold_passing_yards_over_235.5': 0.48,
                'drake_mayne_passing_tds_over_1.5': 0.58,
                'sam_darnold_passing_tds_over_1.5': 0.54,
                'drake_mayne_completions_over_22.5': 0.56,
                'sam_darnold_completions_over_21.5': 0.53
            }
        }
    except Exception as e:
        return {'error': str(e), 'timestamp': datetime.now(timezone.utc).isoformat()}

@router.get("/super-bowl-props")
async def get_super_bowl_props_immediate():
    """Super Bowl specific props"""
    try:
        super_bowl_props = [
            {
                'id': 1,
                'player': {'name': 'Drake Maye', 'position': 'QB'},
                'market': {'stat_type': 'Passing Yards', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 245.5,
                'odds': -110,
                'edge': 0.12,
                'confidence_score': 0.85,
                'generated_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 2,
                'player': {'name': 'Sam Darnold', 'position': 'QB'},
                'market': {'stat_type': 'Passing Yards', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 235.5,
                'odds': -105,
                'edge': 0.08,
                'confidence_score': 0.78,
                'generated_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 3,
                'player': {'name': 'Drake Maye', 'position': 'QB'},
                'market': {'stat_type': 'Passing TDs', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 1.5,
                'odds': -115,
                'edge': 0.15,
                'confidence_score': 0.82,
                'generated_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 4,
                'player': {'name': 'Sam Darnold', 'position': 'QB'},
                'market': {'stat_type': 'Passing TDs', 'description': 'Over/Under'},
                'side': 'over',
                'line_value': 1.5,
                'odds': -110,
                'edge': 0.12,
                'confidence_score': 0.75,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        return {
            'items': super_bowl_props,
            'total': len(super_bowl_props),
            'game_id': 648,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            'items': [],
            'total': 0,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Brain Metrics Endpoints
@router.get("/brain-metrics")
async def get_brain_metrics(db: AsyncSession = Depends(get_db)):
    """Get current brain business metrics"""
    try:
        # Return mock data for now
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_recommendations": 220,
            "recommendation_hit_rate": 0.66,
            "average_ev": 0.22,
            "clv_trend": 0.28,
            "prop_volume": 480,
            "user_confidence_score": 0.92,
            "api_response_time_ms": 85,
            "error_rate": 0.012,
            "throughput": 37.4,
            "system_metrics": {
                "cpu_usage": 0.67,
                "memory_usage": 0.46,
                "disk_usage": 0.48
            },
            "note": "Mock brain metrics data"
        }
            
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-metrics-summary")
async def get_brain_metrics_summary(
    hours: int = Query(24, description="Hours of data to summarize")
):
    """Get brain metrics summary for the last N hours"""
    try:
        # Return mock summary
        return {
            "period_hours": hours,
            "total_records": 10,
            "total_recommendations": 1850,
            "average_hit_rate": 0.58,
            "average_ev": 0.16,
            "max_hit_rate": 0.66,
            "min_hit_rate": 0.49,
            "avg_cpu_usage": 0.52,
            "avg_memory_usage": 0.56,
            "avg_disk_usage": 0.53,
            "note": "Mock brain metrics summary"
        }
            
    except Exception as e:
        return {
            "error": str(e),
            "period_hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



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



# Brain Healing System Endpoints
@router.get("/brain-healing-actions")
async def get_brain_healing_actions(limit: int = Query(50, description="Number of actions to return")):
    """Get recent brain healing actions"""
    try:
        # Return mock healing action data for now
        mock_actions = [
            {
                "id": 1,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "action": "increase_database_pool_size",
                "target": "database_connection_pool",
                "reason": "Database connection pool exhausted causing 8% error rate. Current pool size of 10 insufficient for peak load.",
                "result": "successful",
                "duration_ms": 2340,
                "details": {
                    "initial_pool_size": 10,
                    "new_pool_size": 20,
                    "error_rate_before": 0.08,
                    "error_rate_after": 0.015
                },
                "success_rate": 0.85,
                "consecutive_failures": 0
            },
            {
                "id": 2,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "action": "add_response_caching_layer",
                "target": "api_response_time",
                "reason": "API response time increased to 450ms average (threshold: 200ms). Identified bottleneck in player props calculation.",
                "result": "successful",
                "duration_ms": 4560,
                "details": {
                    "avg_response_time_before": 450,
                    "avg_response_time_after": 95,
                    "cache_hit_rate": 0.78,
                    "cache_ttl_seconds": 300
                },
                "success_rate": 0.92,
                "consecutive_failures": 0
            },
            {
                "id": 3,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "action": "restart_recommendation_service",
                "target": "memory_leak_recommendation_engine",
                "reason": "Memory usage consistently increasing to 95% over 2-hour period. Memory leak detected in recommendation engine.",
                "result": "successful",
                "duration_ms": 12340,
                "details": {
                    "memory_usage_before": 0.95,
                    "memory_usage_after": 0.42,
                    "service_downtime_ms": 2340,
                    "root_cause": "unreleased model references"
                },
                "success_rate": 0.78,
                "consecutive_failures": 1
            },
            {
                "id": 4,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                "action": "retrain_prediction_model",
                "target": "model_accuracy_degradation",
                "reason": "Model accuracy dropped from 68% to 52% over 24 hours. Detected concept drift in passing yards predictions.",
                "result": "successful",
                "duration_ms": 45670,
                "details": {
                    "accuracy_before": 0.52,
                    "accuracy_after": 0.71,
                    "model_type": "passing_yards_predictor",
                    "training_data_points": 15000
                },
                "success_rate": 0.88,
                "consecutive_failures": 0
            },
            {
                "id": 5,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "action": "switch_to_backup_odds_provider",
                "target": "external_odds_api_failure",
                "reason": "Primary odds API provider experiencing 40% timeout rate. Backup provider available with 99% uptime.",
                "result": "successful",
                "duration_ms": 890,
                "details": {
                    "primary_provider": "the_odds_api",
                    "backup_provider": "sportsdata_io",
                    "timeout_rate_before": 0.40,
                    "timeout_rate_after": 0.01
                },
                "success_rate": 0.95,
                "consecutive_failures": 0
            }
        ]
        
        return {
            "actions": mock_actions[:limit],
            "total": len(mock_actions),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain healing actions data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-healing-performance")
async def get_brain_healing_performance(hours: int = Query(24, description="Hours of data to analyze")):
    """Get brain healing performance metrics"""
    try:
        # Return mock performance data
        return {
            "period_hours": hours,
            "total_actions": 9,
            "successful_actions": 8,
            "pending_actions": 1,
            "failed_actions": 0,
            "overall_success_rate": 88.9,
            "avg_duration_ms": 13456.7,
            "avg_success_rate": 0.89,
            "action_performance": [
                {
                    "action": "switch_to_backup_odds_provider",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 890.0,
                    "avg_success_rate": 0.95
                },
                {
                    "action": "add_response_caching_layer",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 4560.0,
                    "avg_success_rate": 0.92
                },
                {
                    "action": "increase_database_pool_size",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 2340.0,
                    "avg_success_rate": 0.85
                },
                {
                    "action": "retrain_prediction_model",
                    "total": 1,
                    "successful": 1,
                    "success_rate": 100.0,
                    "avg_duration_ms": 45670.0,
                    "avg_success_rate": 0.88
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock healing performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-healing-status")
async def get_brain_healing_status():
    """Get current brain healing system status"""
    try:
        return {
            "status": "healthy",
            "active_healing": False,
            "last_healing_cycle": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
            "healing_strategies": {
                "database_connection": {
                    "triggers": 2,
                    "last_action": "increase_database_pool_size",
                    "success_rate": 0.85
                },
                "api_response_time": {
                    "triggers": 2,
                    "last_action": "add_response_caching_layer",
                    "success_rate": 0.92
                },
                "memory_usage": {
                    "triggers": 2,
                    "last_action": "restart_recommendation_service",
                    "success_rate": 0.78
                },
                "model_accuracy": {
                    "triggers": 1,
                    "last_action": "retrain_prediction_model",
                    "success_rate": 0.88
                }
            },
            "auto_healing_enabled": True,
            "monitoring_active": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock healing status data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-healing/run-cycle")
async def run_healing_cycle():
    """Run a brain healing cycle"""
    try:
        # Simulate running a healing cycle
        await asyncio.sleep(2)  # Simulate work
        
        return {
            "status": "completed",
            "triggers_found": 0,
            "actions_executed": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "duration_ms": 2000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock healing cycle completed - no triggers detected"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-healing/trigger")
async def trigger_healing_action(healing_data: dict):
    """Manually trigger a healing action"""
    try:
        # Simulate triggering a healing action
        action = healing_data.get("action", "scale_resources")
        target = healing_data.get("target", "database_connection")
        
        await asyncio.sleep(1)  # Simulate work
        
        return {
            "status": "triggered",
            "action": action,
            "target": target,
            "correlation_id": f"healing-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "estimated_duration_ms": 5000,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock healing action triggered: {action} for {target}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Brain Health Monitoring Endpoints
@router.get("/brain-health-status")
async def get_brain_health_status():
    """Get overall brain system health status"""
    try:
        return {
            "status": "healthy",
            "message": "All brain system components are operating normally",
            "overall_score": 0.87,
            "component_count": 12,
            "status_counts": {
                "healthy": 10,
                "warning": 2,
                "critical": 0,
                "error": 0
            },
            "component_health": {
                "database_connection_pool": {
                    "status": "healthy",
                    "score": 0.95,
                    "message": "Database connection pool operating normally",
                    "response_time_ms": 23
                },
                "api_response_time": {
                    "status": "healthy",
                    "score": 0.92,
                    "message": "API response times are optimal",
                    "response_time_ms": 12
                },
                "model_accuracy": {
                    "status": "healthy",
                    "score": 0.82,
                    "message": "Model accuracy is within acceptable range",
                    "response_time_ms": 34
                },
                "brain_decision_system": {
                    "status": "healthy",
                    "score": 0.82,
                    "message": "Brain decision system is functioning optimally",
                    "response_time_ms": 34
                },
                "brain_healing_system": {
                    "status": "healthy",
                    "score": 0.91,
                    "message": "Brain healing system is ready",
                    "response_time_ms": 25
                }
            },
            "monitoring_active": True,
            "auto_healing_enabled": True,
            "last_check": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain health status data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-health-checks")
async def get_brain_health_checks(limit: int = Query(50, description="Number of checks to return")):
    """Get recent brain health checks"""
    try:
        mock_checks = [
            {
                "id": 1,
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "component": "database_connection_pool",
                "status": "healthy",
                "message": "Database connection pool operating normally",
                "details": {
                    "active_connections": 8,
                    "max_connections": 20,
                    "pool_utilization": 0.40,
                    "avg_response_time_ms": 45,
                    "health_score": 0.95
                },
                "response_time_ms": 23,
                "error_count": 0
            },
            {
                "id": 2,
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat(),
                "component": "api_response_time",
                "status": "healthy",
                "message": "API response times are optimal",
                "details": {
                    "avg_response_time_ms": 95,
                    "requests_per_second": 45.2,
                    "cache_hit_rate": 0.78,
                    "health_score": 0.92
                },
                "response_time_ms": 12,
                "error_count": 0
            }
        ]
        
        return {
            "checks": mock_checks[:limit],
            "total": len(mock_checks),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain health checks data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-health-performance")
async def get_brain_health_performance(hours: int = Query(24, description="Hours of data to analyze")):
    """Get brain health performance metrics"""
    try:
        return {
            "period_hours": hours,
            "total_checks": 18,
            "healthy_checks": 16,
            "warning_checks": 2,
            "critical_checks": 0,
            "error_checks": 0,
            "overall_success_rate": 88.9,
            "avg_response_time_ms": 67.8,
            "avg_error_count": 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain health performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-health/run-check")
async def run_health_check(component: str = Query(..., description="Component to check")):
    """Run a health check for a specific component"""
    try:
        # Mock health check result
        mock_results = {
            "database_connection_pool": {
                "status": "healthy",
                "message": "Database connection pool operating normally",
                "response_time_ms": 23,
                "health_score": 0.95
            },
            "api_response_time": {
                "status": "healthy",
                "message": "API response times are optimal",
                "response_time_ms": 12,
                "health_score": 0.92
            }
        }
        
        result = mock_results.get(component, {
            "status": "error",
            "message": f"Unknown component: {component}",
            "response_time_ms": 0,
            "health_score": 0.0
        })
        
        return {
            "status": "completed",
            "component": component,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock health check completed for {component}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-health/run-all-checks")
async def run_all_health_checks():
    """Run health checks for all components"""
    try:
        return {
            "status": "completed",
            "total_checks": 12,
            "healthy": 10,
            "warning": 2,
            "critical": 0,
            "error": 0,
            "overall_score": 0.87,
            "duration_ms": 500,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock all health checks completed"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



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



# Game Results Tracking Endpoints
@router.get("/game-results")
async def get_game_results(date: str = Query(None, description="Date to filter (YYYY-MM-DD)"), sport_id: int = Query(None, description="Sport ID to filter")):
    """Get game results for a specific date"""
    try:
        # Return mock game results data for now
        mock_results = [
            {
                "id": 1,
                "game_id": 1001,
                "external_fixture_id": "nfl_2026_02_08_kc_buf",
                "home_score": 31,
                "away_score": 28,
                "period_scores": {
                    "Q1": {"home": 7, "away": 7},
                    "Q2": {"home": 10, "away": 14},
                    "Q3": {"home": 7, "away": 0},
                    "Q4": {"home": 7, "away": 7}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            },
            {
                "id": 2,
                "game_id": 1002,
                "external_fixture_id": "nfl_2026_02_08_phi_nyg",
                "home_score": 24,
                "away_score": 17,
                "period_scores": {
                    "Q1": {"home": 3, "away": 7},
                    "Q2": {"home": 14, "away": 3},
                    "Q3": {"home": 0, "away": 7},
                    "Q4": {"home": 7, "away": 0}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
            },
            {
                "id": 3,
                "game_id": 1003,
                "external_fixture_id": "nfl_2026_02_08_dal_sf",
                "home_score": 35,
                "away_score": 42,
                "period_scores": {
                    "Q1": {"home": 14, "away": 7},
                    "Q2": {"home": 7, "away": 14},
                    "Q3": {"home": 7, "away": 14},
                    "Q4": {"home": 7, "away": 7}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()
            },
            {
                "id": 4,
                "game_id": 2001,
                "external_fixture_id": "nba_2026_02_08_lal_bos",
                "home_score": 118,
                "away_score": 112,
                "period_scores": {
                    "Q1": {"home": 28, "away": 24},
                    "Q2": {"home": 32, "away": 30},
                    "Q3": {"home": 29, "away": 28},
                    "Q4": {"home": 29, "away": 30}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 5,
                "game_id": 1005,
                "external_fixture_id": "nfl_2026_02_09_ari_sea",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            }
        ]
        
        return {
            "results": mock_results,
            "total": len(mock_results),
            "date": date or datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/pending")
async def get_pending_games():
    """Get all pending games"""
    try:
        # Return mock pending games data for now
        mock_pending = [
            {
                "id": 5,
                "game_id": 1005,
                "external_fixture_id": "nfl_2026_02_09_ari_sea",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            },
            {
                "id": 6,
                "game_id": 2004,
                "external_fixture_id": "nba_2026_02_09_chi_cle",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        return {
            "pending_games": mock_pending,
            "total": len(mock_pending),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock pending games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/statistics")
async def get_game_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get game statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_games": 8,
            "settled_games": 6,
            "pending_games": 2,
            "avg_home_score": 28.5,
            "avg_away_score": 26.8,
            "avg_total_score": 55.3,
            "home_wins": 4,
            "away_wins": 2,
            "ties": 0,
            "home_win_rate": 66.7,
            "away_win_rate": 33.3,
            "tie_rate": 0.0,
            "by_sport": [
                {
                    "sport_id": 32,
                    "total_games": 5,
                    "settled_games": 4,
                    "avg_home_score": 30.0,
                    "avg_away_score": 28.8,
                    "home_wins": 3,
                    "away_wins": 1
                },
                {
                    "sport_id": 30,
                    "total_games": 3,
                    "settled_games": 2,
                    "avg_home_score": 25.5,
                    "avg_away_score": 24.0,
                    "home_wins": 1,
                    "away_wins": 1
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/{game_id}")
async def get_game_result_detail(game_id: int):
    """Get detailed game result by ID"""
    try:
        # Return mock detailed game result data for now
        mock_detail = {
            "id": 1,
            "game_id": game_id,
            "external_fixture_id": "nfl_2026_02_08_kc_buf",
            "home_score": 31,
            "away_score": 28,
            "period_scores": {
                "Q1": {"home": 7, "away": 7},
                "Q2": {"home": 10, "away": 14},
                "Q3": {"home": 7, "away": 0},
                "Q4": {"home": 7, "away": 7}
            },
            "is_settled": True,
            "settled_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "game_details": {
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "venue": "Arrowhead Stadium",
                "date": "2026-02-08",
                "start_time": "20:20 UTC",
                "duration": "3:15:00",
                "attendance": 76416,
                "weather": "Clear, 72°F"
            },
            "betting_summary": {
                "total_bets": 15420,
                "total_wagered": 3084000,
                "total_profit": 185040,
                "roi_percent": 6.0,
                "popular_bets": {
                    "moneyline": "KC -145",
                    "spread": "KC -2.5",
                    "total": "Over 59.5"
                }
            }
        }
        
        return mock_detail
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/game-results/settle")
async def settle_game_results(settlement_data: dict):
    """Settle game results"""
    try:
        # Simulate settling game results
        games_to_settle = settlement_data.get("games", [])
        
        settled_count = 0
        failed_count = 0
        settlement_results = []
        
        for game in games_to_settle:
            game_id = game.get("game_id")
            home_score = game.get("home_score")
            away_score = game.get("away_score")
            
            if not all([game_id, home_score is not None, away_score is not None]):
                failed_count += 1
                settlement_results.append({
                    "game_id": game_id,
                    "status": "failed",
                    "error": "Missing required fields"
                })
                continue
            
            # Simulate successful settlement
            settled_count += 1
            settlement_results.append({
                "game_id": game_id,
                "status": "settled",
                "home_score": home_score,
                "away_score": away_score,
                "settled_at": datetime.now(timezone.utc).isoformat()
            })
        
        return {
            "total_processed": len(games_to_settle),
            "settled_count": settled_count,
            "failed_count": failed_count,
            "settlement_results": settlement_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock settlement completed for {settled_count} games"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/game-results/create")
async def create_game_result(game_data: dict):
    """Create a new game result record"""
    try:
        # Simulate creating a game result
        game_id = game_data.get("game_id")
        external_fixture_id = game_data.get("external_fixture_id")
        
        if not all([game_id, external_fixture_id]):
            return {
                "status": "error",
                "error": "Missing required fields: game_id, external_fixture_id",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "created",
            "game_id": game_id,
            "external_fixture_id": external_fixture_id,
            "home_score": None,
            "away_score": None,
            "is_settled": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game result created for {game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.put("/game-results/{game_id}")
async def update_game_result(game_id: int, result_data: dict):
    """Update game result with scores"""
    try:
        # Simulate updating game result
        home_score = result_data.get("home_score")
        away_score = result_data.get("away_score")
        period_scores = result_data.get("period_scores", {})
        
        if not all([home_score is not None, away_score is not None]):
            return {
                "status": "error",
                "error": "Missing required fields: home_score, away_score",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "updated",
            "game_id": game_id,
            "home_score": home_score,
            "away_score": away_score,
            "period_scores": period_scores,
            "is_settled": True,
            "settled_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game result updated for {game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Games Management Endpoints
@router.get("/games")
async def get_games(sport_id: int = Query(None, description="Sport ID to filter"), 
                  status: str = Query(None, description="Game status to filter"),
                  start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
                  end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
                  limit: int = Query(50, description="Number of games to return")):
    """Get games with optional filters"""
    try:
        # Return mock games data for now
        mock_games = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 4,
                "sport_id": 32,
                "external_game_id": "nfl_ari_sea_20260209",
                "home_team_id": 390,
                "away_team_id": 391,
                "home_team_name": "Arizona Cardinals",
                "away_team_name": "Seattle Seahawks",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 5,
                "sport_id": 30,
                "external_game_id": "nba_chi_cle_20260209",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Chicago Bulls",
                "away_team_name": "Cleveland Cavaliers",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply filters
        filtered_games = mock_games
        if sport_id:
            filtered_games = [g for g in filtered_games if g['sport_id'] == sport_id]
        if status:
            filtered_games = [g for g in filtered_games if g['status'] == status]
        if start_date:
            filtered_games = [g for g in filtered_games if g['start_time'][:10] >= start_date]
        if end_date:
            filtered_games = [g for g in filtered_games if g['start_time'][:10] <= end_date]
        
        return {
            "games": filtered_games[:limit],
            "total": len(filtered_games),
            "filters": {
                "sport_id": sport_id,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/upcoming")
async def get_upcoming_games(hours: int = Query(24, description="Hours ahead to look"), 
                          sport_id: int = Query(None, description="Sport ID to filter")):
    """Get upcoming games"""
    try:
        # Return mock upcoming games data for now
        mock_upcoming = [
            {
                "id": 4,
                "sport_id": 32,
                "external_game_id": "nfl_ari_sea_20260209",
                "home_team_id": 390,
                "away_team_id": 391,
                "home_team_name": "Arizona Cardinals",
                "away_team_name": "Seattle Seahawks",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 5,
                "sport_id": 30,
                "external_game_id": "nba_chi_cle_20260209",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Chicago Bulls",
                "away_team_name": "Cleveland Cavaliers",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 6,
                "sport_id": 32,
                "external_game_id": "nfl_gb_phi_20260209",
                "home_team_id": 295,
                "away_team_id": 84,
                "home_team_name": "Green Bay Packers",
                "away_team_name": "Philadelphia Eagles",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_upcoming = [g for g in mock_upcoming if g['sport_id'] == sport_id]
        
        return {
            "upcoming_games": mock_upcoming,
            "total": len(mock_upcoming),
            "hours": hours,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock upcoming games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/recent")
async def get_recent_games(hours: int = Query(24, description="Hours back to look"), 
                        sport_id: int = Query(None, description="Sport ID to filter")):
    """Get recent games"""
    try:
        # Return mock recent games data for now
        mock_recent = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_recent = [g for g in mock_recent if g['sport_id'] == sport_id]
        
        return {
            "recent_games": mock_recent,
            "total": len(mock_recent),
            "hours": hours,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock recent games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/statistics")
async def get_games_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get games statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_games": 15,
            "final_games": 8,
            "scheduled_games": 7,
            "in_progress_games": 0,
            "cancelled_games": 0,
            "postponed_games": 0,
            "suspended_games": 0,
            "by_sport": [
                {
                    "sport_id": 32,
                    "total_games": 10,
                    "final_games": 6,
                    "scheduled_games": 4,
                    "in_progress_games": 0
                },
                {
                    "sport_id": 30,
                    "total_games": 5,
                    "final_games": 2,
                    "scheduled_games": 3,
                    "in_progress_games": 0
                }
            ],
            "by_date": [
                {
                    "date": "2026-02-08",
                    "total_games": 8,
                    "final_games": 5,
                    "scheduled_games": 3
                },
                {
                    "date": "2026-02-09",
                    "total_games": 7,
                    "final_games": 3,
                    "scheduled_games": 4
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock games statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/schedule")
async def get_game_schedule(start_date: str = Query(..., description="Start date (YYYY-MM-DD)"), 
                             end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
                             sport_id: int = Query(None, description="Sport ID to filter")):
    """Get game schedule for date range"""
    try:
        # Return mock schedule data for now
        mock_schedule = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply date and sport filters
        if sport_id:
            mock_schedule = [g for g in mock_schedule if g['sport_id'] == sport_id]
        
        if start_date and end_date:
            mock_schedule = [g for g in mock_schedule if start_date <= g['start_time'][:10] <= end_date]
        
        return {
            "schedule": mock_schedule,
            "start_date": start_date,
            "end_date": end_date,
            "sport_id": sport_id,
            "total": len(mock_schedule),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game schedule data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/{game_id}")
async def get_game_detail(game_id: int):
    """Get detailed game information"""
    try:
        # Return mock detailed game data for now
        mock_detail = {
            "id": game_id,
            "sport_id": 32,
            "external_game_id": "nfl_kc_buf_20260208",
            "home_team_id": 48,
            "away_team_id": 83,
            "home_team_name": "Kansas City Chiefs",
            "away_team_name": "Buffalo Bills",
            "sport_name": "NFL",
            "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "status": "final",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "season_id": 2026,
            "game_details": {
                "venue": "Arrowhead Stadium",
                "location": "Kansas City, MO",
                "attendance": 76416,
                "weather": "Clear, 72°F",
                "duration": "3:15:00",
                "broadcast": "CBS",
                "referees": ["John Smith", "Mike Johnson", "Bob Wilson"]
            },
            "betting_summary": {
                "total_bets": 15420,
                "total_wagered": 3084000,
                "total_profit": 185040,
                "roi_percent": 6.0,
                "popular_bets": {
                    "moneyline": "KC -145",
                    "spread": "KC -2.5",
                    "total": "Over 59.5"
                }
            }
        }
        
        return mock_detail
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/games/create")
async def create_game(game_data: dict):
    """Create a new game"""
    try:
        # Simulate creating a game
        game_id = game_data.get("game_id")
        external_game_id = game_data.get("external_game_id")
        home_team_id = game_data.get("home_team_id")
        away_team_id = game_data.get("away_team_id")
        start_time = game_data.get("start_time")
        
        if not all([game_id, external_game_id, home_team_id, away_team_id, start_time]):
            return {
                "status": "error",
                "error": "Missing required fields: game_id, external_game_id, home_team_id, away_team_id, start_time",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "created",
            "game_id": game_id,
            "external_game_id": external_game_id,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "start_time": start_time,
            "status": "scheduled",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game created for {external_game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.put("/games/{game_id}/status")
async def update_game_status(game_id: int, status: str = Query(..., description="New game status")):
    """Update game status"""
    try:
        # Simulate updating game status
        valid_statuses = ["scheduled", "in_progress", "final", "cancelled", "postponed", "suspended"]
        
        if status not in valid_statuses:
            return {
                "status": "error",
                "error": f"Invalid status: {status}. Valid statuses: {', '.join(valid_statuses)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "updated",
            "game_id": game_id,
            "new_status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game {game_id} status updated to {status}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/search")
async def search_games(query: str = Query(..., description="Search query"), 
                        sport_id: int = Query(None, description="Sport ID to filter"),
                        limit: int = Query(20, description="Number of results to return")):
    """Search games by external ID or team names"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                g for g in mock_results 
                if query_lower in g['external_game_id'].lower() or 
                   query_lower in g['home_team_name'].lower() or 
                   query_lower in g['away_team_name'].lower()
            ]
        
        # Apply sport filter
        if sport_id:
            mock_results = [g for g in mock_results if g['sport_id'] == sport_id]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "sport_id": sport_id,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Historical Odds NCAAB Endpoints
@router.get("/historical-odds-ncaab")
async def get_historical_odds_ncaab(game_id: int = Query(None, description="Game ID to filter"), 
                                  bookmaker: str = Query(None, description="Bookmaker to filter"),
                                  team: str = Query(None, description="Team name to filter"),
                                  days: int = Query(30, description="Days of data to return"),
                                  limit: int = Query(50, description="Number of odds to return")):
    """Get NCAA basketball historical odds with optional filters"""
    try:
        # Return mock historical odds data for now
        mock_odds = [
            {
                "id": 1,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 2,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 3,
                "sport": 32,
                "game_id": 1002,
                "home_team": "Kansas Jayhawks",
                "away_team": "Kentucky Wildcats",
                "home_odds": -110,
                "away_odds": -110,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat()
            },
            {
                "id": 4,
                "sport": 32,
                "game_id": 1003,
                "home_team": "UCLA Bruins",
                "away_team": "Gonzaga Bulldogs",
                "home_odds": 180,
                "away_odds": -220,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat(),
                "result": "away_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat()
            },
            {
                "id": 5,
                "sport": 32,
                "game_id": 1004,
                "home_team": "Michigan Wolverines",
                "away_team": "Ohio State Buckeyes",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_odds = mock_odds
        if game_id:
            filtered_odds = [o for o in filtered_odds if o['game_id'] == game_id]
        if bookmaker:
            filtered_odds = [o for o in filtered_odds if o['bookmaker'].lower() == bookmaker.lower()]
        if team:
            filtered_odds = [o for o in filtered_odds if team.lower() in o['home_team'].lower() or team.lower() in o['away_team'].lower()]
        
        return {
            "odds": filtered_odds[:limit],
            "total": len(filtered_odds),
            "filters": {
                "game_id": game_id,
                "bookmaker": bookmaker,
                "team": team,
                "days": days,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock NCAA basketball historical odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/game/{game_id}")
async def get_odds_by_game(game_id: int):
    """Get odds history for a specific game"""
    try:
        # Return mock odds history for a specific game
        mock_odds_history = [
            {
                "id": 1,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 2,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 3,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "bookmaker": "BetMGM",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 4,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat()
            },
            {
                "id": 5,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat()
            }
        ]
        
        return {
            "game_id": game_id,
            "home_team": "Duke Blue Devils",
            "away_team": "North Carolina Tar Heels",
            "odds_history": mock_odds_history,
            "total_snapshots": len(mock_odds_history),
            "bookmakers": list(set(o['bookmaker'] for o in mock_odds_history)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds history for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/movements/{game_id}")
async def get_odds_movements(game_id: int):
    """Get odds movements for a specific game"""
    try:
        # Return mock odds movements data
        mock_movements = [
            {
                "bookmaker": "DraftKings",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "DraftKings",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "home_movement": 10,
                "away_movement": -10,
                "draw_movement": 0,
                "prev_home_odds": -150,
                "prev_away_odds": 130,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "home_movement": -15,
                "away_movement": 15,
                "draw_movement": 0,
                "prev_home_odds": -145,
                "prev_away_odds": 125,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "BetMGM",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            }
        ]
        
        return {
            "game_id": game_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "bookmakers": list(set(m['bookmaker'] for m in mock_movements)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/comparison/{game_id}")
async def get_bookmaker_comparison(game_id: int):
    """Compare odds across bookmakers for a specific game"""
    try:
        # Return mock bookmaker comparison data
        mock_comparison = [
            {
                "bookmaker": "DraftKings",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "BetMGM",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "Caesars",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "PointsBet",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win"
            }
        ]
        
        # Calculate best odds
        best_home_odds = max(mock_comparison, key=lambda x: x['home_odds'])
        best_away_odds = min(mock_comparison, key=lambda x: x['away_odds'])
        
        return {
            "game_id": game_id,
            "home_team": "Duke Blue Devils",
            "away_team": "North Carolina Tar Heels",
            "comparison": mock_comparison,
            "best_home_odds": {
                "bookmaker": best_home_odds['bookmaker'],
                "odds": best_home_odds['home_odds']
            },
            "best_away_odds": {
                "bookmaker": best_away_odds['bookmaker'],
                "odds": best_away_odds['away_odds']
            },
            "total_bookmakers": len(mock_comparison),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock bookmaker comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/statistics")
async def get_historical_odds_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get NCAA basketball historical odds statistics"""
    try:
        # Return mock statistics data
        mock_stats = {
            "period_days": days,
            "total_odds": 28,
            "unique_games": 8,
            "unique_bookmakers": 6,
            "unique_teams": 16,
            "home_wins": 18,
            "away_wins": 10,
            "pending_games": 0,
            "home_win_rate": 64.3,
            "avg_home_odds": -45.7,
            "avg_away_odds": -45.7,
            "avg_draw_odds": None,
            "by_bookmaker": [
                {
                    "bookmaker": "DraftKings",
                    "total_odds": 8,
                    "unique_games": 8,
                    "home_wins": 5,
                    "away_wins": 3,
                    "pending_games": 0,
                    "avg_home_odds": -48.8,
                    "avg_away_odds": -48.8,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "FanDuel",
                    "total_odds": 6,
                    "unique_games": 6,
                    "home_wins": 4,
                    "away_wins": 2,
                    "pending_games": 0,
                    "avg_home_odds": -42.5,
                    "avg_away_odds": -42.5,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "BetMGM",
                    "total_odds": 5,
                    "unique_games": 5,
                    "home_wins": 3,
                    "away_wins": 2,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "Caesars",
                    "total_odds": 4,
                    "unique_games": 4,
                    "home_wins": 3,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -37.5,
                    "avg_away_odds": -37.5,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "PointsBet",
                    "total_odds": 3,
                    "unique_games": 3,
                    "home_wins": 2,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "Bet365",
                    "total_odds": 2,
                    "unique_games": 2,
                    "home_wins": 1,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                }
            ],
            "by_team": [
                {
                    "team": "Duke Blue Devils",
                    "total_games": 5,
                    "home_wins": 5,
                    "home_losses": 0,
                    "avg_home_odds": -150.0,
                    "avg_away_odds": 130.0
                },
                {
                    "team": "Kansas Jayhawks",
                    "total_games": 4,
                    "home_wins": 4,
                    "home_losses": 0,
                    "avg_home_odds": -110.0,
                    "avg_away_odds": -110.0
                },
                {
                    "team": "UCLA Bruins",
                    "total_games": 4,
                    "home_wins": 0,
                    "home_losses": 4,
                    "avg_home_odds": 180.0,
                    "avg_away_odds": -220.0
                },
                {
                    "team": "Michigan Wolverines",
                    "total_games": 3,
                    "home_wins": 3,
                    "home_losses": 0,
                    "avg_home_odds": -125.0,
                    "avg_away_odds": 105.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock NCAA basketball historical odds statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/efficiency")
async def get_odds_efficiency(days: int = Query(30, description="Days of data to analyze")):
    """Analyze odds efficiency and accuracy"""
    try:
        # Return mock efficiency analysis data
        mock_efficiency = {
            "period_days": days,
            "bookmaker_efficiency": [
                {
                    "bookmaker": "DraftKings",
                    "total_games": 8,
                    "home_wins": 5,
                    "away_wins": 3,
                    "avg_implied_home_prob": 60.0,
                    "avg_implied_away_prob": 40.0,
                    "actual_home_win_rate": 62.5,
                    "home_accuracy": 97.5,
                    "away_accuracy": 97.5,
                    "overall_accuracy": 97.5,
                    "home_edge": 2.5,
                    "away_edge": -2.5
                },
                {
                    "bookmaker": "FanDuel",
                    "total_games": 6,
                    "home_wins": 4,
                    "away_wins": 2,
                    "avg_implied_home_prob": 58.3,
                    "avg_implied_away_prob": 41.7,
                    "actual_home_win_rate": 66.7,
                    "home_accuracy": 91.6,
                    "away_accuracy": 91.6,
                    "overall_accuracy": 91.6,
                    "home_edge": 8.4,
                    "away_edge": -8.4
                },
                {
                    "bookmaker": "BetMGM",
                    "total_games": 5,
                    "home_wins": 3,
                    "away_wins": 2,
                    "avg_implied_home_prob": 60.0,
                    "avg_implied_away_prob": 40.0,
                    "actual_home_win_rate": 60.0,
                    "home_accuracy": 100.0,
                    "away_accuracy": 100.0,
                    "overall_accuracy": 100.0,
                    "home_edge": 0.0,
                    "away_edge": 0.0
                },
                {
                    "bookmaker": "Caesars",
                    "total_games": 4,
                    "home_wins": 3,
                    "away_wins": 1,
                    "avg_implied_home_prob": 56.3,
                    "avg_implied_away_prob": 43.8,
                    "actual_home_win_rate": 75.0,
                    "home_accuracy": 81.3,
                    "away_accuracy": 81.3,
                    "overall_accuracy": 81.3,
                    "home_edge": 18.7,
                    "away_edge": -18.7
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/search")
async def search_historical_odds(query: str = Query(..., description="Search query"), 
                                 days: int = Query(30, description="Days of data to search"),
                                 limit: int = Query(20, description="Number of results to return")):
    """Search NCAA basketball historical odds"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                o for o in mock_results 
                if query_lower in o['home_team'].lower() or 
                   query_lower in o['away_team'].lower() or 
                   query_lower in o['bookmaker'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "days": days,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Historical Performance Tracking Endpoints
@router.get("/historical-performances")
async def get_historical_performances(player: str = Query(None, description="Player name to filter"), 
                                      stat_type: str = Query(None, description="Stat type to filter"),
                                      limit: int = Query(50, description="Number of performances to return")):
    """Get historical performances with optional filters"""
    try:
        # Return mock historical performance data for now
        mock_performances = [
            {
                "id": 1,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "total_picks": 156,
                "hits": 98,
                "misses": 58,
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "total_picks": 89,
                "hits": 62,
                "misses": 27,
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "total_picks": 142,
                "hits": 87,
                "misses": 55,
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 4,
                "player_name": "LeBron James",
                "stat_type": "points",
                "total_picks": 178,
                "hits": 112,
                "misses": 66,
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "total_picks": 189,
                "hits": 121,
                "misses": 68,
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 6,
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "total_picks": 89,
                "hits": 56,
                "misses": 33,
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 7,
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "total_picks": 1245,
                "hits": 789,
                "misses": 456,
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 8,
                "player_name": "Sam Darnold",
                "stat_type": "passing_yards",
                "total_picks": 45,
                "hits": 22,
                "misses": 23,
                "hit_rate_percentage": 48.89,
                "avg_ev": -0.0234,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_performances = mock_performances
        if player:
            filtered_performances = [p for p in filtered_performances if player.lower() in p['player_name'].lower()]
        if stat_type:
            filtered_performances = [p for p in filtered_performances if stat_type.lower() in p['stat_type'].lower()]
        
        return {
            "performances": filtered_performances[:limit],
            "total": len(filtered_performances),
            "filters": {
                "player": player,
                "stat_type": stat_type,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock historical performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/top")
async def get_top_performers(limit: int = Query(10, description="Number of top performers to return"), 
                               stat_type: str = Query(None, description="Stat type to filter")):
    """Get top performers by hit rate"""
    try:
        # Return mock top performers data
        mock_top_performers = [
            {
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "total_picks": 189,
                "hits": 121,
                "misses": 68
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "total_picks": 89,
                "hits": 62,
                "misses": 27
            },
            {
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "total_picks": 89,
                "hits": 56,
                "misses": 33
            },
            {
                "player_name": "LeBron James",
                "stat_type": "points",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "total_picks": 178,
                "hits": 112,
                "misses": 66
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "total_picks": 1245,
                "hits": 789,
                "misses": 456
            },
            {
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "total_picks": 142,
                "hits": 87,
                "misses": 55
            },
            {
                "player_name": "Lamar Jackson",
                "stat_type": "rushing_yards",
                "hit_rate_percentage": 62.24,
                "avg_ev": 0.0897,
                "total_picks": 98,
                "hits": 61,
                "misses": 37
            },
            {
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0811,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Stephen Curry",
                "stat_type": "three_pointers",
                "hit_rate_percentage": 61.68,
                "avg_ev": 0.0889,
                "total_picks": 167,
                "hits": 103,
                "misses": 64
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_top_performers = [p for p in mock_top_performers if p['stat_type'] == stat_type]
        
        return {
            "top_performers": mock_top_performers[:limit],
            "total": len(mock_top_performers),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock top performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/best-ev")
async def get_best_ev_performers(limit: int = Query(10, description="Number of best EV performers to return"), 
                                   stat_type: str = Query(None, description="Stat type to filter")):
    """Get best performers by expected value"""
    try:
        # Return mock best EV performers data
        mock_best_ev = [
            {
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "total_picks": 189,
                "hits": 121,
                "misses": 68
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "total_picks": 89,
                "hits": 62,
                "misses": 27
            },
            {
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "total_picks": 89,
                "hits": 56,
                "misses": 33
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "total_picks": 1245,
                "hits": 789,
                "misses": 456
            },
            {
                "player_name": "Lamar Jackson",
                "stat_type": "rushing_yards",
                "hit_rate_percentage": 62.24,
                "avg_ev": 0.0897,
                "total_picks": 98,
                "hits": 61,
                "misses": 37
            },
            {
                "player_name": "Stephen Curry",
                "stat_type": "three_pointers",
                "hit_rate_percentage": 61.68,
                "avg_ev": 0.0889,
                "total_picks": 167,
                "hits": 103,
                "misses": 64
            },
            {
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "total_picks": 142,
                "hits": 87,
                "misses": 55
            },
            {
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0811,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "LeBron James",
                "stat_type": "points",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "total_picks": 178,
                "hits": 112,
                "misses": 66
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_best_ev = [p for p in mock_best_ev if p['stat_type'] == stat_type]
        
        return {
            "best_ev_performers": mock_best_ev[:limit],
            "total": len(mock_best_ev),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock best EV performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/worst")
async def get_worst_performers(limit: int = Query(10, description="Number of worst performers to return"), 
                                  stat_type: str = Query(None, description="Stat type to filter")):
    """Get worst performers by hit rate"""
    try:
        # Return mock worst performers data
        mock_worst = [
            {
                "player_name": "Russell Westbrook",
                "stat_type": "field_goal_percentage",
                "hit_rate_percentage": 46.27,
                "avg_ev": -0.0345,
                "total_picks": 67,
                "hits": 31,
                "misses": 36
            },
            {
                "player_name": "Mookie Betts",
                "stat_type": "batting_average",
                "hit_rate_percentage": 46.15,
                "avg_ev": -0.0289,
                "total_picks": 78,
                "hits": 36,
                "misses": 42
            },
            {
                "player_name": "Sam Darnold",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 48.89,
                "avg_ev": -0.0234,
                "total_picks": 45,
                "hits": 22,
                "misses": 23
            },
            {
                "player_name": "Shohei Ohtani",
                "stat_type": "home_runs",
                "hit_rate_percentage": 61.54,
                "avg_ev": 0.0834,
                "total_picks": 78,
                "hits": 48,
                "misses": 30
            },
            {
                "player_name": "Shohei Ohtani",
                "stat_type": "strikeouts",
                "hit_rate_percentage": 61.96,
                "avg_ev": 0.0798,
                "total_picks": 92,
                "hits": 57,
                "misses": 35
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_worst = [p for p in mock_worst if p['stat_type'] == stat_type]
        
        return {
            "worst_performers": mock_worst[:limit],
            "total": len(mock_worst),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock worst performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/statistics")
async def get_performance_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get performance statistics"""
    try:
        # Return mock statistics data
        mock_stats = {
            "period_days": days,
            "total_performances": 21,
            "unique_players": 11,
            "unique_stat_types": 12,
            "avg_hit_rate": 59.87,
            "avg_ev": 0.0634,
            "total_picks_all": 2478,
            "total_hits_all": 1483,
            "total_misses_all": 995,
            "by_stat_type": [
                {
                    "stat_type": "passing_touchdowns",
                    "total_performances": 1,
                    "avg_hit_rate": 69.66,
                    "avg_ev": 0.0921,
                    "total_picks": 89,
                    "total_hits": 62,
                    "unique_players": 1
                },
                {
                    "stat_type": "points",
                    "total_performances": 3,
                    "avg_hit_rate": 63.25,
                    "avg_ev": 0.0838,
                    "total_picks": 523,
                    "total_hits": 331,
                    "unique_players": 3
                },
                {
                    "stat_type": "home_runs",
                    "total_performances": 2,
                    "avg_hit_rate": 62.23,
                    "avg_ev": 0.0873,
                    "total_picks": 167,
                    "total_hits": 104,
                    "unique_players": 2
                },
                {
                    "stat_type": "passing_yards",
                    "total_performances": 3,
                    "avg_hit_rate": 57.66,
                    "avg_ev": 0.0466,
                    "total_picks": 343,
                    "total_hits": 207,
                    "unique_players": 3
                },
                {
                    "stat_type": "overall_predictions",
                    "total_performances": 4,
                    "avg_hit_rate": 62.90,
                    "avg_ev": 0.0807,
                    "total_picks": 2180,
                    "total_hits": 1370,
                    "unique_players": 1
                }
            ],
            "by_player": [
                {
                    "player_name": "Patrick Mahomes",
                    "total_performances": 2,
                    "avg_hit_rate": 66.24,
                    "avg_ev": 0.0882,
                    "total_picks": 245,
                    "total_hits": 160,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Stephen Curry",
                    "total_performances": 2,
                    "avg_hit_rate": 62.85,
                    "avg_ev": 0.0912,
                    "total_picks": 356,
                    "total_hits": 224,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Brain System",
                    "total_performances": 4,
                    "avg_hit_rate": 62.90,
                    "avg_ev": 0.0807,
                    "total_picks": 2180,
                    "total_hits": 1370,
                    "unique_stat_types": 4
                },
                {
                    "player_name": "Josh Allen",
                    "total_performances": 2,
                    "avg_hit_rate": 61.23,
                    "avg_ev": 0.0802,
                    "total_picks": 209,
                    "total_hits": 128,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "LeBron James",
                    "total_performances": 2,
                    "avg_hit_rate": 62.15,
                    "avg_ev": 0.0755,
                    "total_picks": 323,
                    "total_hits": 201,
                    "unique_stat_types": 2
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock performance statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/player/{player_name}")
async def get_player_performance(player_name: str, stat_type: str = Query(None, description="Stat type to filter")):
    """Get performance for a specific player"""
    try:
        # Return mock player performance data
        mock_player_data = {
            "player_name": player_name,
            "performances": [
                {
                    "id": 1,
                    "stat_type": "passing_yards",
                    "total_picks": 156,
                    "hits": 98,
                    "misses": 58,
                    "hit_rate_percentage": 62.82,
                    "avg_ev": 0.0842,
                    "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
                },
                {
                    "id": 2,
                    "stat_type": "passing_touchdowns",
                    "total_picks": 89,
                    "hits": 62,
                    "misses": 27,
                    "hit_rate_percentage": 69.66,
                    "avg_ev": 0.0921,
                    "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
                }
            ],
            "summary": {
                "total_performances": 2,
                "avg_hit_rate": 66.24,
                "avg_ev": 0.0882,
                "total_picks": 245,
                "total_hits": 160,
                "total_misses": 85,
                "unique_stat_types": 2
            }
        }
        
        # Apply stat type filter
        if stat_type:
            mock_player_data["performances"] = [p for p in mock_player_data["performances"] if p["stat_type"] == stat_type]
        
        return {
            "player_name": player_name,
            "performances": mock_player_data["performances"],
            "summary": mock_player_data["summary"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock performance data for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/search")
async def search_performances(query: str = Query(..., description="Search query"), 
                               limit: int = Query(20, description="Number of results to return")):
    """Search performances by player name or stat type"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "total_picks": 156,
                "hits": 98,
                "misses": 58,
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                p for p in mock_results 
                if query_lower in p['player_name'].lower() or 
                   query_lower in p['stat_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Injury Tracking Endpoints
@router.get("/injuries")
async def get_injuries(sport_id: int = Query(None, description="Sport ID to filter"), 
                        status: str = Query(None, description="Injury status to filter"),
                        player_id: int = Query(None, description="Player ID to filter"),
                        limit: int = Query(50, description="Number of injuries to return")):
    """Get injuries with optional filters"""
    try:
        # Return mock injury data for now
        mock_injuries = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": 66,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 24,
                "sport_id": 30,
                "player_id": 68,
                "status": "DAY_TO_DAY",
                "status_detail": "Hip",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 25,
                "sport_id": 30,
                "player_id": 69,
                "status": "OUT",
                "status_detail": "Toe",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 26,
                "sport_id": 30,
                "player_id": 70,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 27,
                "sport_id": 30,
                "player_id": 71,
                "status": "OUT",
                "status_detail": "Shoulder (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 28,
                "sport_id": 30,
                "player_id": 72,
                "status": "OUT",
                "status_detail": "Oblique",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 29,
                "sport_id": 30,
                "player_id": 27,
                "status": "OUT",
                "status_detail": "Foot/Toe",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 30,
                "sport_id": 30,
                "player_id": 30,
                "status": "OUT",
                "status_detail": "Calf",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 31,
                "sport_id": 32,
                "player_id": 101,
                "status": "QUESTIONABLE",
                "status_detail": "Concussion",
                "is_starter_flag": False,
                "probability": 0.3,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 32,
                "sport_id": 32,
                "player_id": 102,
                "status": "DOUBTFUL",
                "status_detail": "Ankle",
                "is_starter_flag": False,
                "probability": 0.4,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 34,
                "sport_id": 32,
                "player_id": 104,
                "status": "DAY_TO_DAY",
                "status_detail": "Shoulder",
                "is_starter_flag": False,
                "probability": 0.6,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 35,
                "sport_id": 32,
                "player_id": 105,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 36,
                "sport_id": 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_injuries = mock_injuries
        if sport_id:
            filtered_injuries = [i for i in filtered_injuries if i['sport_id'] == sport_id]
        if status:
            filtered_injuries = [i for i in filtered_injuries if i['status'] == status.upper()]
        if player_id:
            filtered_injuries = [i for i in filtered_injuries if i['player_id'] == player_id]
        
        return {
            "injuries": filtered_injuries[:limit],
            "total": len(filtered_injuries),
            "filters": {
                "sport_id": sport_id,
                "status": status,
                "player_id": player_id,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock injury data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "status": status,
            "player_id": player_id,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/active")
async def get_active_injuries(sport_id: int = Query(None, description="Sport ID to filter")):
    """Get currently active injuries"""
    try:
        # Return mock active injuries data for now
        mock_active = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": 66,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 24,
                "sport_id": 30,
                "player_id": 68,
                "status": "DAY_TO_DAY",
                "status_detail": "Hip",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 31,
                "sport_id": 32,
                "player_id": 101,
                "status": "QUESTIONABLE",
                "status_detail": "Concussion",
                "is_starter_flag": False,
                "probability": 0.3,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 32,
                "sport_id": 32,
                "player_id": 102,
                "status": "DOUBTFUL",
                "status_detail": "Ankle",
                "is_starter_flag": False,
                "probability": 0.4,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 36,
                "sport_id": 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 403,
                "sport_id": 32,
                'player_id': 403,
                'status': 'QUESTIONABLE',
                'status_detail': 'Concussion Protocol',
                'is_starter_flag': False,
                'probability': 0.25,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=3, hours=10)).isoformat()
            },
            {
                "id": 404,
                "sport_id': 32,
                'player_id': 404,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Back Strain',
                'is_starter_flag': False,
                'probability': 0.4,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=3, hours=10)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_active = [i for i in mock_active if i['sport_id'] == sport_id]
        
        return {
            "active_injuries": mock_active,
            "total": len(mock_active),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock active injuries data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/out")
async def get_out_injuries(sport_id: int = Query(None, description="Sport ID to filter")):
    """Get players who are out"""
    try:
        # Return mock out injuries data for now
        mock_out = [
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 25,
                "sport_id": 30,
                "player_id": 69,
                "status": "OUT",
                "status_detail": "Toe",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 26,
                "sport_id": 30,
                "player_id": 70,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 27,
                "sport_id": 30,
                "player_id": 71,
                "status": "OUT",
                "status_detail": "Shoulder (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 28,
                "sport_id": 30,
                "player_id": 72,
                "status": "OUT",
                "status_detail": "Oblique",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 29,
                "sport_id": 30,
                "player_id": 27,
                "status": "OUT",
                "status_detail": "Foot/Toe",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 30,
                "sport_id": 30,
                "player_id": 30,
                "status": "OUT",
                "status_detail": "Calf",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 35,
                "sport_id": 32,
                "player_id": 105,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_out = [i for i in mock_out if i['sport_id'] == sport_id]
        
        return {
            "out_injuries": mock_out,
            "total": len(mock_out),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock out injuries data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/statistics")
async def get_injury_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get injury statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_injuries": 21,
            "unique_sports": 4,
            "unique_players": 16,
            "out_injuries": 10,
            "day_to_day_injuries": 7,
            "questionable_injuries": 2,
            "doubtful_injuries": 1,
            "starter_injuries": 2,
            "avg_probability": 0.31,
            "official_injuries": 21,
            "by_sport": [
                {
                    "sport_id": 30,
                    "total_injuries": 10,
                    "out_injuries": 5,
                    "day_to_day_injuries": 5,
                    "questionable_injuries": 2,
                    "doubtful_injuries": 1,
                    "starter_injuries": 2,
                    "avg_probability": 0.40,
                    "unique_players": 10
                },
                {
                    "sport_id": 32,
                    "total_injuries": 7,
                    "out_injuries": 3,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 1,
                    "doubtful_injuries": 1,
                    "starter_injuries": 0,
                    "avg_probability": 0.33,
                    "unique_players": 7
                },
                {
                    "sport_id": 29,
                    "total_injuries": 4,
                    "out_injuries": 2,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 0,
                    "doubtful_injuries": 0,
                    "starter_injuries": 0,
                    "avg_probability": 0.20,
                    "unique_players": 4
                },
                {
                    "sport_id": 53,
                    "total_injuries": 4,
                    "out_injuries": 2,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 1,
                    "doubtful_injuries": 0,
                    "starter_injuries": 0,
                    "avg_probability": 0.25,
                    "unique_players": 4
                }
            ],
            "by_status": [
                {
                    "status": "OUT",
                    "total_injuries": 10,
                    "avg_probability": 0.0,
                    "starter_injuries": 2,
                    "unique_players": 10
                },
                {
                    "status": "DAY_TO_DAY",
                    "total_injuries": 7,
                    "avg_probability": 0.47,
                    "starter_injuries": 2,
                    "unique_players": 7
                },
                {
                    "status": "QUESTIONABLE",
                    "total_injuries": 3,
                    "avg_probability": 0.28,
                    "starter_injuries": 0,
                    "unique_players": 3
                },
                {
                    "status": "DOUBTFUL",
                    "total_injuries": 2,
                    "avg_probability": 0.35,
                    "starter_injuries": 0,
                    "unique_players": 2
                }
            ],
            "by_source": [
                {
                    "source": "official",
                    "total_injuries": 21,
                    "avg_probability": 0.31,
                    "unique_players": 16
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock injury statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/player/{player_id}")
async def get_player_injuries(player_id: int, sport_id: int = Query(None, description="Sport ID to filter")):
    """Get injuries for a specific player"""
    try:
        # Return mock player injury data for now
        mock_player_injuries = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": player_id,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": player_id,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": player_id,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_player_injuries = [i for i in mock_player_injuries if i['sport_id'] == sport_id]
        
        return {
            "player_id": player_id,
            "injuries": mock_player_injuries,
            "total": len(mock_player_injuries),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock injury data for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/impact-analysis/{sport_id}")
async def get_injury_impact_analysis(sport_id: int, days: int = Query(30, description="Days of data to analyze")):
    """Analyze injury impact on team performance"""
    try:
        # Return mock impact analysis data for now
        mock_impact = {
            "sport_id": sport_id,
            "period_days": days,
            "total_injuries": 10,
            "active_injuries": 5,
            "out_injuries": 3,
            "starter_injuries": 0,
            "starter_impact_score": 0.0,
            "active_impact_score": 50.0,
            "out_impact_score": 30.0,
            "weighted_impact": 0.3,
            "concerning_injuries": [
                {
                    "player_id": 103,
                    "status": "OUT",
                    "status_detail": "ACL Tear (Season-ending)",
                    "is_starter": False,
                    "probability": 0.0
                },
                {
                    "player_id": 101,
                    "status": "QUESTIONABLE",
                    "status_detail": "Concussion",
                    "is_starter": False,
                    "probability": 0.3
                }
            ],
            "impact_analysis": "Moderate impact - some active injuries",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock impact analysis for sport {sport_id}"
        }
        
        return mock_impact
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/trends/{sport_id}")
async def get_injury_trends(sport_id: int, days: int = Query(30, description="Days of data to analyze")):
    """Analyze injury trends over time"""
    try:
        # Return mock trend analysis data for now
        mock_trends = {
            "sport_id": sport_id,
            "period_days": days,
            "daily_trends": [
                {
                    "date": "2026-02-01",
                    "total_injuries": 5,
                    "out_injuries": 2,
                    "day_to_day_injuries": 3,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-02",
                    "total_injuries": 3,
                    "out_injuries": 1,
                    "day_to_day_injuries": 2,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-03",
                    "total_injuries": 2,
                    "out_injuries": 0,
                    "day_to_day_injuries": 2,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-04",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-05",
                    "total_injuries": 2,
                    "out_injuries": 1,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-06",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-07",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                }
            ],
            "trend_analysis": "Decreasing injuries - positive trend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock injury trends for sport {sport_id}"
        }
        
        return mock_trends
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/search")
async def search_injuries(query: str = Query(..., description="Search query"), 
                             sport_id: int = Query(None, description="Sport ID to filter"),
                             limit: int = Query(20, description="Number of results to return")):
    """Search injuries by player ID or status detail"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply filters
        if sport_id:
            mock_results = [r for r in mock_results if r['sport_id'] == sport_id]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in str(r['player_id']) or 
                   query_lower in r['status_detail'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "sport_id": sport_id,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Line Tracking Endpoints
@router.get("/lines")
async def get_lines(game_id: int = Query(None, description="Game ID to filter"), 
                   player_id: int = Query(None, description="Player ID to filter"),
                   sportsbook: str = Query(None, description="Sportsbook to filter"),
                   is_current: bool = Query(None, description="Filter current lines only"),
                   limit: int = Query(50, description="Number of lines to return")):
    """Get betting lines with optional filters"""
    try:
        # Return mock line data for now
        mock_lines = [
            {
                "id": 759109,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759110,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759111,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 15.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759112,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 15.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759113,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 16.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759114,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 16.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759115,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759116,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759117,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 12.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759118,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 12.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_lines = mock_lines
        if game_id:
            filtered_lines = [l for l in filtered_lines if l['game_id'] == game_id]
        if player_id:
            filtered_lines = [l for l in filtered_lines if l['player_id'] == player_id]
        if sportsbook:
            filtered_lines = [l for l in filtered_lines if l['sportsbook'].lower() == sportsbook.lower()]
        if is_current is not None:
            filtered_lines = [l for l in filtered_lines if l['is_current'] == is_current]
        
        return {
            "lines": filtered_lines[:limit],
            "total": len(filtered_lines),
            "filters": {
                "game_id": game_id,
                "player_id": player_id,
                "sportsbook": sportsbook,
                "is_current": is_current,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/current")
async def get_current_lines(game_id: int = Query(None, description="Game ID to filter"), 
                            player_id: int = Query(None, description="Player ID to filter")):
    """Get current betting lines"""
    try:
        # Return mock current lines data for now
        mock_current = [
            {
                "id": 759119,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759120,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759121,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759122,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759123,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759124,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759125,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759126,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759127,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "fanduel",
                "line_value": 29.0,
                "odds": -108,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759128,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "fanduel",
                "line_value": 29.0,
                "odds": -108,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Apply filters
        if game_id:
            mock_current = [l for l in mock_current if l['game_id'] == game_id]
        if player_id:
            mock_current = [l for l in mock_current if l['player_id'] == player_id]
        
        return {
            "current_lines": mock_current,
            "total": len(mock_current),
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock current lines data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/movements/{game_id}/{player_id}")
async def get_line_movements(game_id: int, player_id: int, market_id: int = Query(None, description="Market ID to filter")):
    """Get line movements for a specific game/player"""
    try:
        # Return mock line movements data for now
        mock_movements = [
            {
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "odds_movement": 0,
                "prev_line_value": 13.5,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "odds_movement": 0,
                "prev_line_value": 13.5,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_odds": -110
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            }
        ]
        
        # Apply market filter
        if market_id:
            mock_movements = [m for m in mock_movements if m['sportsbook'] == 'draftkings'] or m['sportsbook'] == 'fanduel']
        
        return {
            "game_id": game_id,
            "player_id": player_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock line movements for game {game_id}, player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/comparison/{game_id}/{player_id}")
async def get_sportsbook_comparison(game_id: int, player_id: int, market_id: int = Query(None, description="Market ID to filter")):
    """Compare lines across sportsbooks"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Calculate best odds
        best_over = max(mock_comparison, key=lambda x: x['odds'] if x['side'] == 'over' else float('inf'))
        best_under = max(mock_comparison, key=lambda x: x['odds'] if x['side'] == 'under' else float('inf'))
        
        return {
            "game_id": game_id,
            "player_id": player_id,
            "comparison": mock_comparison,
            "best_over_odds": {
                "sportsbook": best_over['sportsbook'],
                "line_value": best_over['line_value'],
                "odds": best_over['odds'],
                "side": best_over['side']
            },
            "best_under_odds": {
                "sportsbook": best_under['sportsbook'],
                "line_value": best_under['line_value'],
                "odds": best_under['odds'],
                "side": best_under['side']
            },
            "total_sportsbooks": len(set(c['sportsbook'] for c in mock_comparison)),
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock sportsbook comparison for game {game_id}, player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/statistics")
async def get_line_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get line statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_lines": 24,
            "unique_games": 4,
            "unique_markets": 6,
            "unique_players": 4,
            "unique_sportsbooks": 3,
            "current_lines": 10,
            "historical_lines": 14,
            "avg_line_value": 20.25,
            "avg_odds": -108,
            "over_lines": 12,
            "under_lines": 12,
            "by_sportsbook": [
                {
                    "sportsbook": "draftkings",
                    "total_lines": 10,
                    "current_lines": 4,
                    "unique_games": 4,
                    "unique_players": 4,
                    "avg_line_value": 18.5,
                    "avg_odds": -108,
                    "over_lines": 5,
                    "under_lines": 5
                },
                {
                    "sportsbook": "fanduel",
                    "total_lines": 8,
                    "current_lines": 4,
                    "unique_games": 3,
                    "unique_players": 3,
                    "avg_line_value": 21.25,
                    "avg_odds": -108,
                    "over_lines": 4,
                    "under_lines": 4
                },
                {
                    "sportsbook": "betmgm",
                    "total_lines": 6,
                    "current_lines": 2,
                    "unique_games": 2,
                    "unique_players": 2,
                    "avg_line_value": 22.0,
                    "avg_odds": -110,
                    "over_lines": 3,
                    "under_lines": 3
                }
            ],
            "by_side": [
                {
                    "side": "over",
                    "total_lines": 12,
                    "avg_line_value": 20.25,
                    "avg_odds": -108,
                    "unique_sportsbooks": 3,
                    "unique_players": 4
                },
                {
                    "side": "under",
                    "total_lines": 12,
                    "avg_line_value": 20.25,
                    "avg_odds": -108,
                    "unique_sportsbooks": 3,
                    "unique_players": 4
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/efficiency")
async def get_line_efficiency(hours: int = Query(24, description="Hours of data to analyze")):
    """Analyze line efficiency and market efficiency"""
    try:
        # Return mock efficiency analysis data for now
        mock_efficiency = {
            "period_hours": hours,
            "sportsbook_efficiency": [
                {
                    "sportsbook": "draftkings",
                    "total_lines": 10,
                    "significant_movements": 3,
                    "movement_rate": 30.0,
                    "avg_movement": 0.75,
                    "unique_games": 4,
                    "unique_players": 4,
                    "efficiency_score": 70.0
                },
                {
                    "sportsbook": "fanduel",
                    "total_lines": 8,
                    "significant_movements": 2,
                    "movement_rate": 25.0,
                    "avg_movement": 0.5,
                    "unique_games": 3,
                    "unique_players": 3,
                    "efficiency_score": 75.0
                },
                {
                    "sportsbook": "betmgm",
                    "total_lines": 6,
                    "significant_movements": 1,
                    "movement_rate": 16.7,
                    "avg_movement": 0.3,
                    "unique_games": 2,
                    "unique_players": 2,
                    "efficiency_score": 83.3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/search")
async def search_lines(query: str = Query(..., description="Search query"), 
                       sportsbook: str = Query(None, description="Sportsbook to filter"),
                       limit: int = Query(20, description="Number of results to return")):
    """Search lines by player ID or sportsbook"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 759109,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759125,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759129,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "sportsbook": "draftkings",
                "line_value": 285.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Apply filters
        if sportsbook:
            mock_results = [r for r in mock_results if r['sportsbook'].lower() == sportsbook.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in str(r['player_id']) or 
                   query_lower in r['sportsbook'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "sportsbook": sportsbook,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Live Odds NFL Endpoints
@router.get("/live-odds-nfl")
async def get_live_odds_nfl(game_id: int = Query(None, description="Game ID to filter"), 
                          team: str = Query(None, description="Team name to filter"),
                          bookmaker: str = Query(None, description="Sportsbook to filter"),
                          week: int = Query(None, description="Week to filter"),
                          limit: int = Query(50, description="Number of odds to return")):
    """Get live NFL odds with optional filters"""
    try:
        # Return mock live NFL odds data for now
        mock_odds = [
            {
                "id": 1,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 2,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 3,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "bookmaker": "BetMGM",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 4,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat()
            },
            {
                "id": 5,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -130,
                "away_odds": 110,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat()
            },
            {
                "id": 6,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 7,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            },
            {
                "id": 8,
                "sport": 1,
                "game_id": 2005,
                "home_team": "New England Patriots",
                "away_team": "New York Jets",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
            },
            {
                "id": 9,
                "sport": 1,
                "game_id": 2006,
                "home_team": "Baltimore Ravens",
                "away_team": "Pittsburgh Steelers",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
            },
            {
                "id": 10,
                "sport": 1,
                "game_id": 2007,
                "home_team": "Cincinnati Bengals",
                "away_team": "Cleveland Browns",
                "home_odds": -110,
                "away_odds": -110,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_odds = mock_odds
        if game_id:
            filtered_odds = [o for o in filtered_odds if o['game_id'] == game_id]
        if team:
            filtered_odds = [o for o in filtered_odds if team.lower() in o['home_team'].lower() or team.lower() in o['away_team'].lower()]
        if bookmaker:
            filtered_odds = [o for o in filtered_odds if o['bookmaker'].lower() == bookmaker.lower()]
        if week:
            filtered_odds = [o for o in filtered_odds if o['week'] == week]
        
        return {
            "odds": filtered_odds[:limit],
            "total": len(filtered_odds),
            "filters": {
                "game_id": game_id,
                "team": team,
                "bookmaker": bookmaker,
                "week": week,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/current")
async def get_current_live_odds_nfl(game_id: int = Query(None, description="Game ID to filter"), 
                                   bookmaker: str = Query(None, description="Sportsbook to filter")):
    """Get current live NFL odds"""
    try:
        # Return mock current live NFL odds data for now
        mock_current = [
            {
                "id": 11,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 12,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 13,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 14,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 15,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        if game_id:
            mock_current = [o for o in mock_current if o['game_id'] == game_id]
        if bookmaker:
            mock_current = [o for o in mock_current if o['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "current_odds": mock_current,
            "total": len(mock_current),
            "game_id": game_id,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock current live NFL odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/movements/{game_id}")
async def get_live_odds_nfl_movements(game_id: int, minutes: int = Query(30, description="Minutes of data to analyze")):
    """Get live NFL odds movements for a specific game"""
    try:
        # Return mock movements data for now
        mock_movements = [
            {
                "sportsbook": "DraftKings",
                "home_odds": -162,
                "away_odds": 142,
                "draw_odds": None,
                "timestamp": (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat(),
                "home_movement": 3,
                "away_movement": -3,
                "prev_home_odds": -165,
                "prev_away_odds": 145,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "DraftKings",
                "home_odds": -168,
                "away_odds": 148,
                "draw_odds": None,
                "timestamp": (datetime.now(timezone.utc) - timedelta(seconds=15)).isoformat(),
                "home_movement": -6,
                "away_movement": 6,
                "prev_home_odds": -162,
                "prev_away_odds": 142,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "DraftKings",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 3,
                "away_movement": -3,
                "prev_home_odds": -168,
                "prev_away_odds": 148,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "BetMGM",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            }
        ]
        
        return {
            "game_id": game_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock live NFL odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/comparison/{game_id}")
async def get_live_odds_nfl_comparison(game_id: int, minutes: int = Query(30, description="Minutes of data to analyze")):
    """Compare live NFL odds across sportsbooks for a specific game"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "sportsbook": "DraftKings",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "sportsbook": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "sportsbook": "BetMGM",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Calculate best odds
        best_home_odds = max(mock_comparison, key=lambda x: x['home_odds'] if x['home_odds'] < 0 else float('inf'))
        best_away_odds = max(mock_comparison, key=lambda x: x['away_odds'] if x['away_odds'] < 0 else float('inf'))
        
        return {
            "game_id": game_id,
            "comparison": mock_comparison,
            "best_home_odds": {
                "sportsbook": best_home_odds['sportsbook'],
                "line_value": best_home_odds['home_odds'],
                "odds": best_home_odds['odds']
            },
            "best_away_odds": {
                "best_away_odds": best_away_odds['sportsbook'],
                "line_value": best_away_odds['away_odds'],
                "odds": best_away_odds['odds']
            },
            "total_sportsbooks": len(mock_comparison),
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock sportsbook comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/statistics")
async def get_live_odds_nfl_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get live NFL odds statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_odds": 24,
            "unique_games": 8,
            "unique_teams": 16,
            "unique_opponents": 16,
            "unique_bookmakers": 3,
            "unique_weeks": 4,
            "avg_home_odds": -140.5,
            "avg_away_odds": 120.5,
            "home_favorites": 18,
            "away_favorites": 6,
            "draw_markets": 0,
            "by_sportsbook": [
                {
                    "bookmaker": "DraftKings",
                    "total_odds": 10,
                    "unique_games": 8,
                    "unique_weeks": 4,
                    "avg_home_odds": -145.0,
                    "avg_away_odds": 125.0,
                    "home_favorites": 8,
                    "away_favorites": 2,
                    "unique_teams": 16,
                    "unique_opponents": 16
                },
                {
                    "bookmaker": "FanDuel",
                    "total_odds": 8,
                    "unique_games": 6,
                    "unique_weeks": 3,
                    "avg_home_odds": -135.0,
                    "avg_away_odds": 115.0,
                    "home_favorites": 6,
                    "away_favorites": 2,
                    "unique_teams": 12,
                    "unique_opponents": 12
                },
                {
                    "bookmaker": "BetMGM",
                    "total_odds": 6,
                    "unique_games": 4,
                    "unique_weeks": 2,
                    "avg_home_odds": -150.0,
                    "avg_away_odds": 130.0,
                    "home_favorites": 4,
                    "away_favorites": 2,
                    "unique_teams": 8,
                    "unique_opponents": 8
                }
            ],
            "by_week": [
                {
                    "week": 20,
                    "season": 2026,
                    "total_odds": 6,
                    "unique_games": 2,
                    "avg_home_odds": -147.5,
                    "avg_away_odds": 127.5,
                    "home_favorites": 4,
                    "away_favorites": 2
                },
                {
                    "week": 18,
                    "season": 2026,
                    "total_odds": 12,
                    "unique_games": 4,
                    "avg_home_odds": -138.3,
                    "avg_away_odds": 118.3,
                    "home_favorites": 10,
                    "away_favorites": 2
                }
            ],
            "by_team": [
                {
                    "team": "Kansas City Chiefs",
                    "total_games": 3,
                    "home_wins": 3,
                    "away_wins": 0,
                    "avg_home_odds": -165.0,
                    "avg_away_odds": 145.0,
                    "unique_games": 1,
                    "unique_weeks": 1
                },
                {
                    "team": "Dallas Cowboys",
                    "total_games": 3,
                    "home_wins": 3,
                    "away_wins": 0,
                    "avg_home_odds": -280.0,
                    "avg_away_odds": 230.0,
                    "unique_games": 1,
                    "unique_weeks": 1
                }
            ],
            "by_odds_range": [
                {
                    "odds_range": "Heavy Favorite",
                    "total_odds": 3,
                    "avg_odds": -280.0,
                    "avg_away_odds": 230.0
                },
                {
                    "odds_range": "Strong Favorite",
                    "total_odds": 5,
                    "avg_odds": -190.0,
                    "avg_away_odds": 160.0
                },
                {
                    "odds_range": "Moderate Favorite",
                    "total_odds": 8,
                    "avg_odds": -140.0,
                    "avg_away_odds": 120.0
                },
                {
                    "odds_range": "Light Favorite",
                    "total_odds": 6,
                    "avg_odds": -110.0,
                    "avg_away_odds": -110.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/efficiency")
async def get_live_odds_nfl_efficiency(hours: int = Query(24, description="Hours of data to analyze")):
    """Analyze live NFL odds market efficiency and arbitrage opportunities"""
    try:
        # Return mock efficiency analysis data for now
        mock_efficiency = {
            "period_hours": hours,
            "total_arbitrage_opportunities": 8,
            "avg_home_range": 10.0,
            "avg_away_range": 10.0,
            "arbitrage_opportunities": [
                {
                    "game_id": 2001,
                    "home_team": "Kansas City Chiefs",
                    "away_team": "Buffalo Bills",
                    "week": 20,
                    "season": 2026,
                    "sportsbooks_count": 3,
                    "best_home_odds": -160,
                    "worst_home_odds": -170,
                    "best_away_odds": 140,
                    "worst_away_odds": 150,
                    "home_odds_range": 10,
                    "away_odds_range": 10,
                    "avg_home_odds": -165.0,
                    "avg_away_odds": 145.0
                },
                {
                    "game_id": 2002,
                    "home_team": "San Francisco 49ers",
                    "away_team": "Philadelphia Eagles",
                    "week": 20,
                    "season": 2026,
                    "sportsbooks_count": 2,
                    "best_home_odds": -125,
                    "worst_home_odds": -130,
                    "best_away_odds": 105,
                    "worst_away_odds": 110,
                    "home_odds_range": 5,
                    "away_odds_range": 5,
                    "avg_home_odds": -127.5,
                    "avg_away_odds": 107.5
                },
                {
                    "game_id": 2003,
                    "home_team": "Dallas Cowboys",
                    "away_team": "New York Giants",
                    "week": 18,
                    "season": 2026,
                    "sportsbooks_count": 3,
                    "best_home_odds": -275,
                    "worst_home_odds": -285,
                    "best_away_odds": 225,
                    "worst_away_odds": 235,
                    "home_odds_range": 10,
                    "away_odds_range": 10,
                    "avg_home_odds": -280.0,
                    "avg_away_odds": 230.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/week/{week}")
async def get_live_odds_nfl_by_week(week: int, season: int = Query(2026, description="Season to filter"), 
                                   bookmaker: str = Query(None, description="Sportsbook to filter")):
    """Get live NFL odds for a specific week"""
    try:
        # Return mock week data for now
        mock_week_odds = [
            {
                "id": 16,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 17,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            },
            {
                "id": 18,
                "sport": 1,
                "game_id": 2005,
                "home_team": "New England Patriots",
                "away_team": "New York Jets",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
            }
        ]
        
        # Apply bookmaker filter
        if bookmaker:
            mock_week_odds = [o for o in mock_week_odds if o['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "week": week,
            "season": season,
            "odds": mock_week_odds,
            "total": len(mock_week_odds),
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock live NFL odds for week {week}, season {season}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "week": week,
            "season": season,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/search")
async def search_live_odds_nfl(query: str = Query(..., description="Search query"), 
                              bookmaker: str = Query(None, description="Sportsbook to filter"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search live NFL odds by team name or sportsbook"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 6,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 7,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            }
        ]
        
        # Apply filters
        if bookmaker:
            mock_results = [r for r in mock_results if r['bookmaker'].lower() == bookmaker.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['home_team'].lower() or 
                   query_lower in r['away_team'].lower() or
                   query_lower in r['bookmaker'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "bookmaker": bookmaker,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Odds Snapshots Tracking Endpoints
@router.get("/odds-snapshots")
async def get_odds_snapshots(game_id: int = Query(None, description="Game ID to filter"), 
                           player_id: int = Query(None, description="Player ID to filter"),
                           bookmaker: str = Query(None, description="Bookmaker to filter"),
                           hours: int = Query(24, description="Hours of data to analyze"),
                           limit: int = Query(50, description="Number of snapshots to return")):
    """Get odds snapshots with optional filters"""
    try:
        # Return mock odds snapshots data for now
        mock_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 3,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.5",
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_92",
                "external_outcome_id": "over_28.5",
                "bookmaker": "DraftKings",
                "line_value": 28.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "external_fixture_id": "nfl_2026_664",
                "external_market_id": "player_pass_yards_101",
                "external_outcome_id": "over_285.5",
                "bookmaker": "DraftKings",
                "line_value": 285.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 6,
                "game_id": 666,
                "market_id": 201,
                "player_id": 201,
                "external_fixture_id": "mlb_2026_666",
                "external_market_id": "player_hr_201",
                "external_outcome_id": "over_1.5",
                "bookmaker": "DraftKings",
                "line_value": 1.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat()
            },
            {
                "id": 7,
                "game_id": 668,
                "market_id": 301,
                "player_id": 301,
                "external_fixture_id": "nhl_2026_668",
                "external_market_id": "player_points_301",
                "external_outcome_id": "over_1.5",
                "bookmaker": "DraftKings",
                "line_value": 1.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            }
        ]
        
        # Apply filters
        filtered_snapshots = mock_snapshots
        if game_id:
            filtered_snapshots = [s for s in filtered_snapshots if s['game_id'] == game_id]
        if player_id:
            filtered_snapshots = [s for s in filtered_snapshots if s['player_id'] == player_id]
        if bookmaker:
            filtered_snapshots = [s for s in filtered_snapshots if s['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "snapshots": filtered_snapshots[:limit],
            "total": len(filtered_snapshots),
            "filters": {
                "game_id": game_id,
                "player_id": player_id,
                "bookmaker": bookmaker,
                "hours": hours,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds snapshots data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/movements/{game_id}")
async def get_odds_movements(game_id: int, market_id: int = Query(None, description="Market ID to filter"),
                           player_id: int = Query(None, description="Player ID to filter"),
                           hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds movements for a specific game"""
    try:
        # Return mock movements data for now
        mock_movements = [
            {
                "bookmaker": "DraftKings",
                "line_value": 13.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9524,
                "american_odds": -105,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "price_movement": 0.0433,
                "odds_movement": 5,
                "prev_line_value": 13.5,
                "prev_price": 1.9091,
                "prev_american_odds": -110
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9524,
                "american_odds": -105,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": 14.0,
                "prev_price": 1.9524,
                "prev_american_odds": -105
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9412,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "line_movement": 0,
                "price_movement": -0.0112,
                "odds_movement": -3,
                "prev_line_value": 14.0,
                "prev_price": 1.9524,
                "prev_american_odds": -105
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9615,
                "american_odds": -103,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0203,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_price": 1.9412,
                "prev_american_odds": -108
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0091,
                "odds_movement": 1,
                "prev_line_value": 14.0,
                "prev_price": 1.9615,
                "prev_american_odds": -103
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0115,
                "odds_movement": 2,
                "prev_line_value": 13.5,
                "prev_price": 1.9231,
                "prev_american_odds": -108
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0140,
                "odds_movement": 2,
                "prev_line_value": 14.5,
                "prev_price": 1.9091,
                "prev_american_odds": -110
            }
        ]
        
        # Apply filters
        filtered_movements = mock_movements
        if market_id:
            # Filter by market_id logic would go here
            pass
        if player_id:
            # Filter by player_id logic would go here
            pass
        
        return {
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "movements": filtered_movements,
            "total_movements": len(filtered_movements),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/comparison/{game_id}")
async def get_odds_comparison(game_id: int, market_id: int = Query(None, description="Market ID to filter"),
                            player_id: int = Query(None, description="Player ID to filter"),
                            hours: int = Query(1, description="Hours of data to analyze")):
    """Compare odds across bookmakers for a specific game"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Calculate best odds
        best_over = max(mock_comparison, key=lambda x: x['price'] if x['side'] == 'over' else float('inf'))
        best_under = max(mock_comparison, key=lambda x: x['price'] if x['side'] == 'under' else float('inf'))
        
        return {
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "comparison": mock_comparison,
            "best_over_odds": {
                "bookmaker": best_over['bookmaker'],
                "line_value": best_over['line_value'],
                "price": best_over['price'],
                "american_odds": best_over['american_odds']
            },
            "best_under_odds": {
                "bookmaker": best_under['bookmaker'],
                "line_value": best_under['line_value'],
                "price": best_under['price'],
                "american_odds": best_under['american_odds']
            },
            "total_bookmakers": len(mock_comparison),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/statistics")
async def get_odds_snapshots_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_snapshots": 25,
            "unique_games": 4,
            "unique_markets": 6,
            "unique_players": 6,
            "unique_bookmakers": 3,
            "unique_fixtures": 4,
            "unique_external_markets": 6,
            "unique_external_outcomes": 12,
            "avg_line_value": 45.2,
            "avg_price": 1.9345,
            "avg_american_odds": -106,
            "over_snapshots": 18,
            "under_snapshots": 7,
            "active_snapshots": 25,
            "by_bookmaker": [
                {
                    "bookmaker": "DraftKings",
                    "total_snapshots": 12,
                    "unique_games": 4,
                    "unique_markets": 5,
                    "avg_line_value": 48.5,
                    "avg_price": 1.9412,
                    "avg_american_odds": -104,
                    "over_snapshots": 9,
                    "under_snapshots": 3
                },
                {
                    "bookmaker": "FanDuel",
                    "total_snapshots": 8,
                    "unique_games": 3,
                    "unique_markets": 4,
                    "avg_line_value": 42.1,
                    "avg_price": 1.9286,
                    "avg_american_odds": -107,
                    "over_snapshots": 6,
                    "under_snapshots": 2
                },
                {
                    "bookmaker": "BetMGM",
                    "total_snapshots": 5,
                    "unique_games": 2,
                    "unique_markets": 3,
                    "avg_line_value": 38.7,
                    "avg_price": 1.9162,
                    "avg_american_odds": -109,
                    "over_snapshots": 3,
                    "under_snapshots": 2
                }
            ],
            "by_game": [
                {
                    "game_id": 662,
                    "total_snapshots": 12,
                    "unique_markets": 2,
                    "unique_players": 2,
                    "unique_bookmakers": 3,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                    "last_snapshot": datetime.now(timezone.utc).isoformat()
                },
                {
                    "game_id": 664,
                    "total_snapshots": 4,
                    "unique_markets": 2,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
                },
                {
                    "game_id": 666,
                    "total_snapshots": 3,
                    "unique_markets": 2,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
                },
                {
                    "game_id": 668,
                    "total_snapshots": 2,
                    "unique_markets": 1,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
                }
            ],
            "by_side": [
                {
                    "side": "over",
                    "total_snapshots": 18,
                    "avg_line_value": 47.8,
                    "avg_price": 1.9456,
                    "avg_american_odds": -103,
                    "unique_bookmakers": 3,
                    "unique_games": 4
                },
                {
                    "side": "under",
                    "total_snapshots": 7,
                    "avg_line_value": 38.2,
                    "avg_price": 1.9091,
                    "avg_american_odds": -110,
                    "unique_bookmakers": 2,
                    "unique_games": 3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds snapshots statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/bookmaker/{bookmaker}")
async def get_odds_by_bookmaker(bookmaker: str, hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots from a specific bookmaker"""
    try:
        # Return mock bookmaker data for now
        mock_bookmaker_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": bookmaker,
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_92",
                "external_outcome_id": "over_28.5",
                "bookmaker": bookmaker,
                "line_value": 28.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "external_fixture_id": "nfl_2026_664",
                "external_market_id": "player_pass_yards_101",
                "external_outcome_id": "over_285.5",
                "bookmaker": bookmaker,
                "line_value": 285.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "bookmaker": bookmaker,
            "snapshots": mock_bookmaker_snapshots,
            "total": len(mock_bookmaker_snapshots),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds snapshots for {bookmaker}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/player/{player_id}")
async def get_odds_by_player(player_id: int, bookmaker: str = Query(None, description="Bookmaker to filter"),
                            hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots for a specific player"""
    try:
        # Return mock player data for now
        mock_player_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 3,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.5",
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply bookmaker filter
        if bookmaker:
            mock_player_snapshots = [s for s in mock_player_snapshots if s['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "player_id": player_id,
            "snapshots": mock_player_snapshots,
            "total": len(mock_player_snapshots),
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds snapshots for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/search")
async def search_odds_snapshots(query: str = Query(..., description="Search query"), 
                              bookmaker: str = Query(None, description="Bookmaker to filter"),
                              hours: int = Query(24, description="Hours of data to analyze"),
                              limit: int = Query(50, description="Number of results to return")):
    """Search odds snapshots by external IDs or bookmaker"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        if bookmaker:
            mock_results = [r for r in mock_results if r['bookmaker'].lower() == bookmaker.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['external_fixture_id'].lower() or 
                   query_lower in r['external_market_id'].lower() or
                   query_lower in r['external_outcome_id'].lower() or
                   query_lower in r['bookmaker'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "bookmaker": bookmaker,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "bookmaker": bookmaker,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Picks Management Endpoints
@router.get("/picks")
async def get_picks(game_id: int = Query(None, description="Game ID to filter"), 
                  player: str = Query(None, description="Player name to filter"),
                  stat_type: str = Query(None, description="Stat type to filter"),
                  min_ev: float = Query(0.0, description="Minimum EV percentage"),
                  min_confidence: float = Query(0.0, description="Minimum confidence"),
                  hours: int = Query(24, description="Hours of data to analyze"),
                  limit: int = Query(50, description="Number of picks to return")):
    """Get picks with optional filters"""
    try:
        # Return mock picks data for now
        mock_picks = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 3,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -105,
                "model_probability": 0.6100,
                "implied_probability": 0.5122,
                "ev_percentage": 19.09,
                "confidence": 87.0,
                "hit_rate": 63.5,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 668,
                "pick_type": "player_prop",
                "player_name": "Connor McDavid",
                "stat_type": "points",
                "line": 1.5,
                "odds": -108,
                "model_probability": 0.6000,
                "implied_probability": 0.5195,
                "ev_percentage": 15.40,
                "confidence": 85.0,
                "hit_rate": 62.8,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 7,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "line": 26.5,
                "odds": -108,
                "model_probability": 0.5900,
                "implied_probability": 0.5195,
                "ev_percentage": 13.58,
                "confidence": 86.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 8,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "line": 285.5,
                "odds": -110,
                "model_probability": 0.5800,
                "implied_probability": 0.5238,
                "ev_percentage": 10.75,
                "confidence": 84.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=3).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=3).isoformat()
            },
            {
                "id": 9,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -110,
                "model_probability": 0.5900,
                "implied_probability": 0.5238,
                "ev_percentage": 12.61,
                "confidence": 85.0,
                "hit_rate": 62.9,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply filters
        filtered_picks = mock_picks
        if game_id:
            filtered_picks = [p for p in filtered_picks if p['game_id'] == game_id]
        if player:
            filtered_picks = [p for p in filtered_picks if player.lower() in p['player_name'].lower()]
        if stat_type:
            filtered_picks = [p for p in filtered_picks if p['stat_type'].lower() == stat_type.lower()]
        if min_ev > 0:
            filtered_picks = [p for p in filtered_picks if p['ev_percentage'] >= min_ev]
        if min_confidence > 0:
            filtered_picks = [p for p in filtered_picks if p['confidence'] >= min_confidence]
        
        return {
            "picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "filters": {
                "game_id": game_id,
                "player": player,
                "stat_type": stat_type,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
                "hours": hours,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock picks data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/high-ev")
async def get_high_ev_picks(min_ev: float = Query(5.0, description="Minimum EV percentage"),
                           hours: int = Query(24, description="Hours of data to analyze"),
                           limit: int = Query(20, description="Number of picks to return")):
    """Get picks with high expected value"""
    try:
        # Return mock high EV picks data for now
        mock_high_ev = [
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 3,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -105,
                "model_probability": 0.6100,
                "implied_probability": 0.5122,
                "ev_percentage": 19.09,
                "confidence": 87.0,
                "hit_rate": 63.5,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply EV filter
        filtered_picks = [p for p in mock_high_ev if p['ev_percentage'] >= min_ev]
        
        return {
            "high_ev_picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "min_ev": min_ev,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock high EV picks (>= {min_ev}% EV)"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "min_ev": min_ev,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/high-confidence")
async def get_high_confidence_picks(min_confidence: float = Query(80.0, description="Minimum confidence"),
                                   hours: int = Query(24, description="Hours of data to analyze"),
                                   limit: int = Query(20, description="Number of picks to return")):
    """Get picks with high confidence"""
    try:
        # Return mock high confidence picks data for now
        mock_high_confidence = [
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply confidence filter
        filtered_picks = [p for p in mock_high_confidence if p['confidence'] >= min_confidence]
        
        return {
            "high_confidence_picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "min_confidence": min_confidence,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock high confidence picks (>= {min_confidence}% confidence)"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "min_confidence": min_confidence,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/statistics")
async def get_picks_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get picks statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_picks": 22,
            "unique_games": 4,
            "unique_players": 8,
            "unique_stat_types": 6,
            "unique_pick_types": 1,
            "avg_line": 45.8,
            "avg_odds": -110,
            "avg_model_prob": 0.5950,
            "avg_implied_prob": 0.5238,
            "avg_ev": 11.23,
            "avg_confidence": 84.5,
            "avg_hit_rate": 63.4,
            "high_ev_picks": 18,
            "high_confidence_picks": 16,
            "high_hit_rate_picks": 20,
            "by_player": [
                {
                    "player_name": "Patrick Mahomes",
                    "total_picks": 2,
                    "avg_ev": 15.52,
                    "avg_confidence": 87.5,
                    "avg_hit_rate": 65.0,
                    "avg_model_prob": 0.6050,
                    "avg_implied_prob": 0.5217,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                },
                {
                    "player_name": "Stephen Curry",
                    "total_picks": 3,
                    "avg_ev": 16.91,
                    "avg_confidence": 88.7,
                    "avg_hit_rate": 64.4,
                    "avg_model_prob": 0.6233,
                    "avg_implied_prob": 0.5295,
                    "high_ev_picks": 3,
                    "high_confidence_picks": 3
                },
                {
                    "player_name": "Aaron Judge",
                    "total_picks": 2,
                    "avg_ev": 15.85,
                    "avg_confidence": 86.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.6000,
                    "avg_implied_prob": 0.5180,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                },
                {
                    "player_name": "LeBron James",
                    "total_picks": 2,
                    "avg_ev": 13.49,
                    "avg_confidence": 87.0,
                    "avg_hit_rate": 63.3,
                    "avg_model_prob": 0.5950,
                    "avg_implied_prob": 0.5217,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                }
            ],
            "by_stat_type": [
                {
                    "stat_type": "points",
                    "total_picks": 8,
                    "avg_ev": 16.47,
                    "avg_confidence": 87.9,
                    "avg_hit_rate": 64.1,
                    "avg_model_prob": 0.6163,
                    "avg_implied_prob": 0.5257,
                    "high_ev_picks": 8
                },
                {
                    "stat_type": "passing_touchdowns",
                    "total_picks": 1,
                    "avg_ev": 21.28,
                    "avg_confidence": 91.0,
                    "avg_hit_rate": 66.8,
                    "avg_model_prob": 0.6300,
                    "avg_implied_prob": 0.5195,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "home_runs",
                    "total_picks": 2,
                    "avg_ev": 15.85,
                    "avg_confidence": 86.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.6000,
                    "avg_implied_prob": 0.5180,
                    "high_ev_picks": 2
                },
                {
                    "stat_type": "hits",
                    "total_picks": 1,
                    "avg_ev": 15.92,
                    "avg_confidence": 88.0,
                    "avg_hit_rate": 64.2,
                    "avg_model_prob": 0.6200,
                    "avg_implied_prob": 0.5349,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "passing_yards",
                    "total_picks": 1,
                    "avg_ev": 10.75,
                    "avg_confidence": 84.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.5800,
                    "avg_implied_prob": 0.5238,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "rebounds",
                    "total_picks": 1,
                    "avg_ev": 9.34,
                    "avg_confidence": 82.0,
                    "avg_hit_rate": 61.1,
                    "avg_model_prob": 0.5600,
                    "avg_implied_prob": 0.5122,
                    "high_ev_picks": 1
                }
            ],
            "ev_distribution": [
                {
                    "ev_category": "Very High EV (15%+)",
                    "total_picks": 8,
                    "avg_ev": 17.89,
                    "avg_confidence": 88.8,
                    "avg_hit_rate": 64.6
                },
                {
                    "ev_category": "High EV (10-15%)",
                    "total_picks": 10,
                    "avg_ev": 12.17,
                    "avg_confidence": 83.2,
                    "avg_hit_rate": 62.8
                },
                {
                    "ev_category": "Medium EV (5-10%)",
                    "total_picks": 4,
                    "avg_ev": 7.52,
                    "avg_confidence": 80.5,
                    "avg_hit_rate": 61.9
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock picks statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/player/{player_name}")
async def get_picks_by_player(player_name: str, hours: int = Query(24, description="Hours of data to analyze")):
    """Get picks for a specific player"""
    try:
        # Return mock player picks data for now
        mock_player_picks = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 11,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "three_pointers",
                "line": 4.5,
                "odds": -110,
                "model_probability": 0.5700,
                "implied_probability": 0.5238,
                "ev_percentage": 8.84,
                "confidence": 80.0,
                "hit_rate": 61.7,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "player_name": player_name,
            "picks": mock_player_picks,
            "total": len(mock_player_picks),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock picks for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_name": player_name,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/game/{game_id}")
async def get_picks_by_game(game_id: int):
    """Get picks for a specific game"""
    try:
        # Return mock game picks data for now
        mock_game_picks = [
            {
                "id": 1,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 4,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 7,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "line": 26.5,
                "odds": -108,
                "model_probability": 0.5900,
                "implied_probability": 0.5195,
                "ev_percentage": 13.58,
                "confidence": 86.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "game_id": game_id,
            "picks": mock_game_picks,
            "total": len(mock_game_picks),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock picks for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/search")
async def search_picks(query: str = Query(..., description="Search query"),
                      hours: int = Query(24, description="Hours of data to analyze"),
                      limit: int = Query(20, description="Number of results to return")):
    """Search picks by player name or stat type"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['player_name'].lower() or 
                   query_lower in r['stat_type'].lower() or
                   query_lower in r['pick_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Player Statistics Tracking Endpoints
@router.get("/player-stats")
async def get_player_stats(player: str = Query(None, description="Player name to filter"),
                             team: str = Query(None, description="Team name to filter"),
                             stat_type: str = Query(None, description="Stat type to filter"),
                             days: int = Query(30, description="Days of data to analyze"),
                             limit: int = Query(50, description="Number of stats to return")):
    """Get player statistics with optional filters"""
    try:
        # Return mock player stats data for now
        mock_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 31.2,
                "line": 28.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 4,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": "three_pointers",
                "actual_value": 4.5,
                "line": 4.0,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_yards",
                "actual_value": 298.5,
                "line": 285.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 6,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_touchdowns",
                "actual_value": 3.0,
                "line": 2.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 7,
                "player_name": "Aaron Judge",
                "team": "New York Yankees",
                "opponent": "Boston Red Sox",
                "date": (datetime.now(timezone.utc) - timedelta(days=6)).date().isoformat(),
                "stat_type": "home_runs",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat()
            },
            {
                "id": 8,
                "player_name": "Mike Trout",
                "team": "Los Angeles Angels",
                "opponent": "Seattle Mariners",
                "date": (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat(),
                "stat_type": "hits",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            },
            {
                "id": 9,
                "player_name": "Connor McDavid",
                "team": "Edmonton Oilers",
                "opponent": "Calgary Flames",
                "date": (datetime.now(timezone.utc) - timedelta(days=8)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            },
            {
                "id": 10,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Miami Heat",
                "date": datetime.now(timezone.utc).date().isoformat(),
                "stat_type": "points",
                "actual_value": 22.5,
                "line": 25.0,
                "result": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        filtered_stats = mock_stats
        if player:
            filtered_stats = [s for s in filtered_stats if player.lower() in s['player_name'].lower()]
        if team:
            filtered_stats = [s for s in filtered_stats if team.lower() in s['team'].lower()]
        if stat_type:
            filtered_stats = [s for s in filtered_stats if s['stat_type'].lower() == stat_type.lower()]
        
        return {
            "stats": filtered_stats[:limit],
            "total": len(filtered_stats),
            "filters": {
                "player": player,
                "team": team,
                "stat_type": stat_type,
                "days": days,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock player stats data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-statistics")
async def get_player_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get overall player statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_stats": 25,
            "unique_players": 8,
            "unique_teams": 8,
            "unique_opponents": 8,
            "unique_stat_types": 10,
            "unique_dates": 10,
            "avg_actual_value": 45.8,
            "avg_line": 42.3,
            "hits": 18,
            "misses": 7,
            "hit_rate_percentage": 72.0,
            "top_performers": [
                {
                    "player_name": "LeBron James",
                    "total_stats": 3,
                    "hits": 2,
                    "misses": 1,
                    "hit_rate_percentage": 66.67,
                    "avg_actual_value": 20.83,
                    "avg_line": 18.83,
                    "unique_stat_types": 3
                },
                {
                    "player_name": "Stephen Curry",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 17.85,
                    "avg_line": 16.25,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Patrick Mahomes",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 300.75,
                    "avg_line": 289.0,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Aaron Judge",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 2.5,
                    "avg_line": 2.0,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Mike Trout",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 1.75,
                    "avg_line": 1.5,
                    "unique_stat_types": 2
                }
            ],
            "stat_type_performance": [
                {
                    "stat_type": "points",
                    "total_stats": 8,
                    "hits": 6,
                    "misses": 2,
                    "hit_rate_percentage": 75.0,
                    "avg_actual_value": 27.56,
                    "avg_line": 25.69,
                    "unique_players": 5
                },
                {
                    "stat_type": "passing_yards",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 287.2,
                    "avg_line": 280.5,
                    "unique_players": 2
                },
                {
                    "stat_type": "home_runs",
                    "total_stats": 1,
                    "hits": 1,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 2.0,
                    "avg_line": 1.5,
                    "unique_players": 1
                },
                {
                    "stat_type": "rebounds",
                    "total_stats": 2,
                    "hits": 1,
                    "misses": 1,
                    "hit_rate_percentage": 50.0,
                    "avg_actual_value": 7.35,
                    "avg_line": 7.25,
                    "unique_players": 1
                },
                {
                    "stat_type": "assists",
                    "total_stats": 1,
                    "hits": 1,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 7.8,
                    "avg_line": 6.5,
                    "unique_players": 1
                }
            ],
            "over_under_performance": [
                {
                    "over_under_result": "OVER",
                    "total_stats": 20,
                    "hits": 15,
                    "misses": 5,
                    "hit_rate_percentage": 75.0
                },
                {
                    "over_under_result": "UNDER",
                    "total_stats": 5,
                    "hits": 3,
                    "misses": 2,
                    "hit_rate_percentage": 60.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock player statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/{player_name}")
async def get_player_stats_by_name(player_name: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific player"""
    try:
        # Return mock player stats data for now
        mock_player_stats = [
            {
                "id": 1,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 10,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Miami Heat",
                "date": datetime.now(timezone.utc).date().isoformat(),
                "stat_type": "points",
                "actual_value": 22.5,
                "line": 25.0,
                "result": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        return {
            "player_name": player_name,
            "stats": mock_player_stats,
            "total": len(mock_player_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_name": player_name,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/team/{team}")
async def get_player_stats_by_team(team: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific team"""
    try:
        # Return mock team stats data for now
        mock_team_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "LeBron James",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Anthony Davis",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "points",
                "actual_value": 18.5,
                "line": 20.5,
                "result": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        return {
            "team": team,
            "stats": mock_team_stats,
            "total": len(mock_team_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {team}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "team": team,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/stat/{stat_type}")
async def get_player_stats_by_stat_type(stat_type: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific stat type"""
    try:
        # Return mock stat type stats data for now
        mock_stat_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 31.2,
                "line": 28.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Kevin Durant",
                "team": "Phoenix Suns",
                "opponent": "Denver Nuggets",
                "date": (datetime.now(timezone.utc) - timedelta(days=3)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 25.8,
                "line": 26.5,
                "result": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            }
        ]
        
        return {
            "stat_type": stat_type,
            "stats": mock_stat_stats,
            "total": len(mock_stat_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {stat_type}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "stat_type": stat_type,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/search")
async def search_player_stats(query: str = Query(..., description="Search query"),
                              days: int = Query(30, description="Days of data to analyze"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search player stats by player name, team, or stat type"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_yards",
                "actual_value": 298.5,
                "line": 285.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['player_name'].lower() or 
                   query_lower in r['team'].lower() or
                   query_lower in r['opponent'].lower() or
                   query_lower in r['stat_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "days": days,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "days": days,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Shared Betting Cards Tracking Endpoints
@router.get("/shared-cards")
async def get_shared_cards(platform: str = Query(None, description="Platform to filter"),
                            sport: str = Query(None, description="Sport to filter"),
                            grade: str = Query(None, description="Grade to filter"),
                            trending: bool = Query(False, description="Get trending cards"),
                            performing: bool = Query(False, description="Get top performing cards"),
                            limit: int = Query(50, description="Number of cards to return")):
    """Get shared betting cards with optional filters"""
    try:
        # Return mock shared cards data for now
        mock_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "platform": "discord",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "rebounds", "line": 7.5, "odds": -110},
                    {"player": "Anthony Davis", "market": "rebounds", "line": 10.5, "odds": -110},
                    {"player": "Nikola Jokic", "market": "rebounds", "line": 11.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0143,
                "overall_grade": "B+",
                "label": "NBA Rebounds Master Parlay",
                "kelly_suggested_units": 1.8,
                "kelly_risk_level": "Medium",
                "view_count": 890,
                "settled": True,
                "won": False,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 3,
                "platform": "twitter",
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Patrick Mahomes", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Josh Allen", "market": "passing_yards", "line": 265.5, "odds": -110},
                    {"player": "Justin Herbert", "market": "passing_yards", "line": 275.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0357,
                "overall_grade": "A-",
                "label": "NFL QB Passing Yards Parlay",
                "kelly_suggested_units": 3.2,
                "kelly_risk_level": "High",
                "view_count": 2100,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            },
            {
                "id": 4,
                "platform": "reddit",
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Christian McCaffrey", "market": "rushing_yards", "line": 85.5, "odds": -110},
                    {"player": "Derrick Henry", "market": "rushing_yards", "line": 95.5, "odds": -110},
                    {"player": "Jonathan Taylor", "market": "rushing_yards", "line": 90.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0214,
                "overall_grade": "B",
                "label": "NFL RB Rushing Yards Parlay",
                "kelly_suggested_units": 2.1,
                "kelly_risk_level": "Medium",
                "view_count": 1560,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 5,
                "platform": "twitter",
                "sport_id": 2,
                "sport": "MLB",
                "legs": [
                    {"player": "Aaron Judge", "market": "home_runs", "line": 1.5, "odds": -110},
                    {"player": "Mike Trout", "market": "hits", "line": 1.5, "odds": -110},
                    {"player": "Shohei Ohtani", "market": "strikeouts", "line": 7.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0429,
                "overall_grade": "A",
                "label": "MLB Stars Multi-Stat Parlay",
                "kelly_suggested_units": 3.8,
                "kelly_risk_level": "High",
                "view_count": 1890,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            },
            {
                "id": 6,
                "platform": "discord",
                "sport_id": 32,
                "sport": "NCAA Basketball",
                "legs": [
                    {"player": "Zion Williamson", "market": "points", "line": 22.5, "odds": -110},
                    {"player": "Paolo Banchero", "market": "points", "line": 20.5, "odds": -110},
                    {"player": "Chet Holmgren", "market": "rebounds", "line": 8.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0214,
                "overall_grade": "B+",
                "label": "NCAA Basketball Stars Parlay",
                "kelly_suggested_units": 2.4,
                "kelly_risk_level": "Medium",
                "view_count": 1450,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=9)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            },
            {
                "id": 7,
                "platform": "twitter",
                "sport_id": 99,
                "sport": "Multi-Sport",
                "legs": [
                    {"player": "LeBron James", "sport": "NBA", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Patrick Mahomes", "sport": "NFL", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Aaron Judge", "sport": "MLB", "market": "home_runs", "line": 1.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0250,
                "overall_grade": "A-",
                "label": "Multi-Sport Superstars Parlay",
                "kelly_suggested_units": 2.8,
                "kelly_risk_level": "High",
                "view_count": 2340,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=11)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            },
            {
                "id": 8,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "Stephen Curry", "market": "three_pointers", "line": 4.5, "odds": -110},
                    {"player": "Klay Thompson", "market": "three_pointers", "line": 3.5, "odds": -110},
                    {"player": "Damian Lillard", "market": "three_pointers", "line": 3.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0321,
                "overall_grade": "A",
                "label": "NBA Three-Point Specialists Parlay",
                "kelly_suggested_units": 3.0,
                "kelly_risk_level": "High",
                "view_count": 890,
                "settled": False,
                "won": None,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_cards = mock_cards
        if platform:
            filtered_cards = [c for c in filtered_cards if c['platform'].lower() == platform.lower()]
        if sport:
            filtered_cards = [c for c in filtered_cards if c['sport'].lower() == sport.lower()]
        if grade:
            filtered_cards = [c for c in filtered_cards if c['overall_grade'].lower() == grade.lower()]
        
        # Apply sorting
        if trending:
            filtered_cards = sorted(filtered_cards, key=lambda x: x['view_count'], reverse=True)
        elif performing:
            filtered_cards = sorted(filtered_cards, key=lambda x: x['parlay_ev'], reverse=True)
        
        return {
            "cards": filtered_cards[:limit],
            "total": len(filtered_cards),
            "filters": {
                "platform": platform,
                "sport": sport,
                "grade": grade,
                "trending": trending,
                "performing": performing,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock shared cards data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/statistics")
async def get_shared_cards_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get shared cards statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_cards": 12,
            "unique_platforms": 4,
            "unique_sports": 6,
            "avg_total_odds": 6.00,
            "avg_decimal_odds": 7.00,
            "avg_parlay_probability": 0.1429,
            "avg_parlay_ev": 0.0250,
            "grade_a_cards": 4,
            "settled_cards": 10,
            "won_cards": 7,
            "lost_cards": 3,
            "total_views": 15460,
            "avg_views_per_card": 1288.3,
            "platform_performance": [
                {
                    "platform": "twitter",
                    "total_cards": 6,
                    "settled_cards": 5,
                    "won_cards": 4,
                    "win_rate_percentage": 80.0,
                    "avg_parlay_ev": 0.0300,
                    "total_views": 9360,
                    "avg_views_per_card": 1560.0
                },
                {
                    "platform": "discord",
                    "total_cards": 3,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0180,
                    "total_views": 4230,
                    "avg_views_per_card": 1410.0
                },
                {
                    "platform": "reddit",
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0210,
                    "total_views": 3010,
                    "avg_views_per_card": 1505.0
                },
                {
                    "platform": "telegram",
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 860,
                    "avg_views_per_card": 860.0
                }
            ],
            "sport_performance": [
                {
                    "sport_id": 30,
                    "total_cards": 4,
                    "settled_cards": 3,
                    "won_cards": 2,
                    "win_rate_percentage": 66.7,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 6480,
                    "avg_views_per_card": 1620.0
                },
                {
                    "sport_id": 1,
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 2,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0285,
                    "total_views": 3660,
                    "avg_views_per_card": 1830.0
                },
                {
                    "sport_id": 2,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0429,
                    "total_views": 1890,
                    "avg_views_per_card": 1890.0
                },
                {
                    "sport_id": 32,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0214,
                    "total_views": 1450,
                    "avg_views_per_card": 1450.0
                },
                {
                    "sport_id": 99,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 2340,
                    "avg_views_per_card": 2340.0
                }
            ],
            "grade_performance": [
                {
                    "overall_grade": "A",
                    "total_cards": 4,
                    "settled_cards": 3,
                    "won_cards": 3,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0340,
                    "avg_kelly_units": 3.1,
                    "total_views": 6920,
                    "avg_views_per_card": 1730.0
                },
                {
                    "overall_grade": "A-",
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 2,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0300,
                    "avg_kelly_units": 3.0,
                    "total_views": 4440,
                    "avg_views_per_card": 2220.0
                },
                {
                    "overall_grade": "B+",
                    "total_cards": 3,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0180,
                    "avg_kelly_units": 2.1,
                    "total_views": 3930,
                    "avg_views_per_card": 1310.0
                },
                {
                    "overall_grade": "B",
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 0,
                    "win_rate_percentage": 0.0,
                    "avg_parlay_ev": 0.0214,
                    "avg_kelly_units": 2.1,
                    "total_views": 1560,
                    "avg_views_per_card": 1560.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock shared cards statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/platform/{platform}")
async def get_shared_cards_by_platform(platform: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards for a specific platform"""
    try:
        # Return mock platform-specific cards data for now
        mock_platform_cards = [
            {
                "id": 1,
                "platform": platform,
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "platform": platform,
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Patrick Mahomes", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Josh Allen", "market": "passing_yards", "line": 265.5, "odds": -110},
                    {"player": "Justin Herbert", "market": "passing_yards", "line": 275.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0357,
                "overall_grade": "A-",
                "label": "NFL QB Passing Yards Parlay",
                "kelly_suggested_units": 3.2,
                "kelly_risk_level": "High",
                "view_count": 2100,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            }
        ]
        
        return {
            "platform": platform,
            "cards": mock_platform_cards[:limit],
            "total": len(mock_platform_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for {platform}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "platform": platform,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/sport/{sport}")
async def get_shared_cards_by_sport(sport: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards for a specific sport"""
    try:
        # Return mock sport-specific cards data for now
        mock_sport_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": sport,
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "platform": "discord",
                "sport_id": 30,
                "sport": sport,
                "legs": [
                    {"player": "LeBron James", "market": "rebounds", "line": 7.5, "odds": -110},
                    {"player": "Anthony Davis", "market": "rebounds", "line": 10.5, "odds": -110},
                    {"player": "Nikola Jokic", "market": "rebounds", "line": 11.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0143,
                "overall_grade": "B+",
                "label": "NBA Rebounds Master Parlay",
                "kelly_suggested_units": 1.8,
                "kelly_risk_level": "Medium",
                "view_count": 890,
                "settled": True,
                "won": False,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            }
        ]
        
        return {
            "sport": sport,
            "cards": mock_sport_cards[:limit],
            "total": len(mock_sport_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for {sport}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport": sport,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/grade/{grade}")
async def get_shared_cards_by_grade(grade: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards by grade"""
    try:
        # Return mock grade-specific cards data for now
        mock_grade_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": grade,
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "platform": "twitter",
                "sport_id": 2,
                "sport": "MLB",
                "legs": [
                    {"player": "Aaron Judge", "market": "home_runs", "line": 1.5, "odds": -110},
                    {"player": "Mike Trout", "market": "hits", "line": 1.5, "odds": -110},
                    {"player": "Shohei Ohtani", "market": "strikeouts", "line": 7.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0429,
                "overall_grade": grade,
                "label": "MLB Stars Multi-Stat Parlay",
                "kelly_suggested_units": 3.8,
                "kelly_risk_level": "High",
                "view_count": 1890,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            }
        ]
        
        return {
            "grade": grade,
            "cards": mock_grade_cards[:limit],
            "total": len(mock_grade_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for grade {grade}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "grade": grade,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/search")
async def search_shared_cards(query: str = Query(..., description="Search query"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search shared cards by label or legs"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 8,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "Stephen Curry", "market": "three_pointers", "line": 4.5, "odds": -110},
                    {"player": "Klay Thompson", "market": "three_pointers", "line": 3.5, "odds": -110},
                    {"player": "Damian Lillard", "market": "three_pointers", "line": 3.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0321,
                "overall_grade": "A",
                "label": "NBA Three-Point Specialists Parlay",
                "kelly_suggested_units": 3.0,
                "kelly_risk_level": "High",
                "view_count": 890,
                "settled": False,
                "won": None,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['label'].lower() or 
                   any(query_lower in leg['player'].lower() or 
                       query_lower in leg['market'].lower() 
                       for leg in r['legs'])
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Trade Details Tracking Endpoints
@router.get("/trade-details")
async def get_trade_details(trade_id: str = Query(None, description="Trade ID to filter"),
                           team_id: int = Query(None, description="Team ID to filter"),
                           player_id: int = Query(None, description="Player ID to filter"),
                           asset_type: str = Query(None, description="Asset type to filter"),
                           recent: bool = Query(False, description="Get recent trades"),
                           limit: int = Query(50, description="Number of trade details to return")):
    """Get trade details with optional filters"""
    try:
        # Return mock trade details data for now
        mock_trade_details = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_001",
                "player_id": 2,
                "from_team_id": 3,
                "to_team_id": 5,
                "asset_type": "player",
                "asset_description": "All-star guard with scoring ability",
                "player_name": "Devin Booker",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 3,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 4,
                "trade_id": "NBA_2024_002",
                "player_id": 4,
                "from_team_id": 7,
                "to_team_id": 4,
                "asset_type": "player",
                "asset_description": "Veteran center with defensive presence",
                "player_name": "Nikola Jokic",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 5,
                "trade_id": "NFL_2024_001",
                "player_id": 101,
                "from_team_id": 101,
                "to_team_id": 102,
                "asset_type": "player",
                "asset_description": "Elite quarterback with Super Bowl experience",
                "player_name": "Aaron Rodgers",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 6,
                "trade_id": "NFL_2024_001",
                "player_id": 102,
                "from_team_id": 102,
                "to_team_id": 101,
                "asset_type": "player",
                "asset_description": "Pro Bowl wide receiver with speed",
                "player_name": "Davante Adams",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 7,
                "trade_id": "MLB_2024_001",
                "player_id": 201,
                "from_team_id": 201,
                "to_team_id": 202,
                "asset_type": "player",
                "asset_description": "Power-hitting first baseman with MVP potential",
                "player_name": "Pete Alonso",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 8,
                "trade_id": "MLB_2024_001",
                "player_id": 202,
                "from_team_id": 202,
                "to_team_id": 201,
                "asset_type": "player",
                "asset_description": "Ace pitcher with strikeout ability",
                "player_name": "Jacob deGrom",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 9,
                "trade_id": "NHL_2024_001",
                "player_id": 301,
                "from_team_id": 301,
                "to_team_id": 302,
                "asset_type": "player",
                "asset_description": "Elite center with scoring ability",
                "player_name": "Connor McDavid",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 10,
                "trade_id": "NHL_2024_001",
                "player_id": 302,
                "from_team_id": 302,
                "to_team_id": 301,
                "asset_type": "player",
                "asset_description": "Power forward with physical presence",
                "player_name": "Nathan MacKinnon",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 11,
                "trade_id": "NBA_2024_005",
                "player_id": 9,
                "from_team_id": 11,
                "to_team_id": 12,
                "asset_type": "draft_pick",
                "asset_description": "2025 first round draft pick (lottery protected)",
                "player_name": "2025 1st Round Pick",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            },
            {
                "id": 12,
                "trade_id": "NBA_2024_005",
                "player_id": 10,
                "from_team_id": 12,
                "to_team_id": 11,
                "asset_type": "player",
                "asset_description": "Young center with defensive potential",
                "player_name": "Walker Kessler",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_trades = mock_trade_details
        if trade_id:
            filtered_trades = [t for t in filtered_trades if t['trade_id'] == trade_id]
        if team_id:
            filtered_trades = [t for t in filtered_trades if t['from_team_id'] == team_id or t['to_team_id'] == team_id]
        if player_id:
            filtered_trades = [t for t in filtered_trades if t['player_id'] == player_id]
        if asset_type:
            filtered_trades = [t for t in filtered_trades if t['asset_type'] == asset_type]
        
        # Apply sorting
        if recent:
            filtered_trades = sorted(filtered_trades, key=lambda x: x['created_at'], reverse=True)
        
        return {
            "trade_details": filtered_trades[:limit],
            "total": len(filtered_trades),
            "filters": {
                "trade_id": trade_id,
                "team_id": team_id,
                "player_id": player_id,
                "asset_type": asset_type,
                "recent": recent,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trade details data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/statistics")
async def get_trade_details_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get trade details statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_trade_records": 28,
            "unique_trades": 14,
            "unique_players": 28,
            "unique_from_teams": 12,
            "unique_to_teams": 12,
            "unique_asset_types": 2,
            "player_trades": 26,
            "draft_pick_trades": 2,
            "same_team_trades": 0,
            "different_team_trades": 28,
            "asset_type_stats": [
                {
                    "asset_type": "player",
                    "total_trades": 26,
                    "unique_trades": 13,
                    "unique_players": 26
                },
                {
                    "asset_type": "draft_pick",
                    "total_trades": 2,
                    "unique_trades": 1,
                    "unique_players": 2
                }
            ],
            "team_stats": [
                {
                    "team_id": 5,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 3,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 4,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 7,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 101,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                }
            ],
            "player_stats": [
                {
                    "player_id": 1,
                    "player_name": "Kevin Durant",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 2,
                    "player_name": "Devin Booker",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 3,
                    "player_name": "Kyle Lowry",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 4,
                    "player_name": "Nikola Jokic",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 101,
                    "player_name": "Aaron Rodgers",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trade details statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/trade/{trade_id}")
async def get_trade_details_by_trade_id(trade_id: str):
    """Get trade details for a specific trade"""
    try:
        # Return mock trade-specific data for now
        mock_trade_summary = {
            "trade_id": trade_id,
            "total_assets": 2,
            "from_teams": [5, 3],
            "to_teams": [3, 5],
            "player_assets": [
                {
                    "player_id": 1,
                    "player_name": "Kevin Durant",
                    "asset_type": "player",
                    "asset_description": "Star forward with championship experience",
                    "from_team_id": 5,
                    "to_team_id": 3
                },
                {
                    "player_id": 2,
                    "player_name": "Devin Booker",
                    "asset_type": "player",
                    "asset_description": "All-star guard with scoring ability",
                    "from_team_id": 3,
                    "to_team_id": 5
                }
            ],
            "draft_pick_assets": [],
            "other_assets": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        }
        
        return {
            "trade_summary": mock_trade_summary,
            "trade_id": trade_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade summary for {trade_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "trade_id": trade_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/team/{team_id}")
async def get_trade_details_by_team(team_id: int, role: str = Query("both", description="Team role: from, to, or both")):
    """Get trade details for a specific team"""
    try:
        # Return mock team-specific data for now
        mock_team_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": team_id,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": team_id,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        # Filter by role
        if role == "from":
            mock_team_trades = [t for t in mock_team_trades if t['from_team_id'] == team_id]
        elif role == "to":
            mock_team_trades = [t for t in mock_team_trades if t['to_team_id'] == team_id]
        
        return {
            "team_id": team_id,
            "role": role,
            "trade_details": mock_team_trades,
            "total": len(mock_team_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for team {team_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "team_id": team_id,
            "role": role,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/player/{player_id}")
async def get_trade_details_by_player(player_id: int):
    """Get trade details for a specific player"""
    try:
        # Return mock player-specific data for now
        mock_player_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": player_id,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_003",
                "player_id": player_id,
                "from_team_id": 6,
                "to_team_id": 8,
                "asset_type": "player",
                "asset_description": "Rising star with high potential",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
            }
        ]
        
        return {
            "player_id": player_id,
            "trade_details": mock_player_trades,
            "total": len(mock_player_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/asset-type/{asset_type}")
async def get_trade_details_by_asset_type(asset_type: str, limit: int = Query(50, description="Number of trade details to return")):
    """Get trade details by asset type"""
    try:
        # Return mock asset-type-specific data for now
        mock_asset_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": asset_type,
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": asset_type,
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "asset_type": asset_type,
            "trade_details": mock_asset_trades[:limit],
            "total": len(mock_asset_trades),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for asset type {asset_type}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "asset_type": asset_type,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/search")
async def search_trade_details(query: str = Query(..., description="Search query"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search trade details by player name or trade ID"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['trade_id'].lower() or 
                   query_lower in r['player_name'].lower() or 
                   (r['asset_description'] and query_lower in r['asset_description'].lower())
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Master Trade Tracking Endpoints
@router.get("/trades")
async def get_trades(season: int = Query(None, description="Season year to filter"),
                     source: str = Query(None, description="Source to filter"),
                     applied: bool = Query(None, description="Applied status to filter"),
                     recent: bool = Query(False, description="Get recent trades"),
                     limit: int = Query(50, description="Number of trades to return")):
    """Get master trades with optional filters"""
    try:
        # Return mock trades data for now
        mock_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": 2024,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 3,
                "trade_date": "2024-02-18",
                "season_year": 2024,
                "description": "The Indiana Pacers and Portland Trail Blazers completed a trade sending rising star Tyrese Haliburton to Portland in exchange for veteran scorer Damian Lillard. The Pacers get immediate championship help while the Trail Blazers build around their new young star.",
                "headline": "Pacers Send Haliburton to Trail Blazers for Lillard",
                "source_url": "https://www.bleacherreport.com/nba/articles/pacers-send-haliburton-to-trail-blazers-for-lillard",
                "source": "Bleacher Report",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": "NFL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 5,
                "trade_date": "2024-03-22",
                "season_year": 2024,
                "description": "The Carolina Panthers traded running back Christian McCaffrey to the San Francisco 49ers in exchange for veteran linebacker Bobby Wagner. The 49ers add an elite offensive weapon while the Panthers strengthen their defense.",
                "headline": "Panthers Trade McCaffrey to 49ers for Wagner",
                "source_url": "https://www.espn.com/nfl/story/_/id/23456789/panthers-trade-mccaffrey-to-49ers-for-wagner",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat()
            },
            {
                "id": 6,
                "trade_date": "2024-07-31",
                "season_year": 2024,
                "description": "The New York Mets traded power-hitting first baseman Pete Alonso to the Los Angeles Dodgers in exchange for ace pitcher Jacob deGrom. The Dodgers add a middle-of-the-order bat while the Mets acquire a frontline starter.",
                "headline": "Mets Trade Alonso to Dodgers for deGrom",
                "source_url": "https://www.mlb.com/trade-news/mets-trade-alonso-to-dodgers-for-degrom",
                "source": "MLB.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 7,
                "trade_date": "2024-07-28",
                "season_year": 2024,
                "description": "The Los Angeles Angels traded superstar Mike Trout to the San Diego Padres in exchange for All-Star third baseman Manny Machado. The Padres add a generational talent while the Angels get a proven power hitter.",
                "headline": "Angels Trade Trout to Padres for Machado",
                "source_url": "https://www.baseballamerica.com/mlb/angels-trade-trout-to-padres-for-machado",
                "source": "Baseball America",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=32)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=32)).isoformat()
            },
            {
                "id": 8,
                "trade_date": "2024-03-08",
                "season_year": 2024,
                "description": "The Edmonton Oilers traded elite center Connor McDavid to the Toronto Maple Leafs in exchange for power forward Nathan MacKinnon. The Maple Leafs get their franchise center while the Oilers add a dominant power forward.",
                "headline": "Oilers Trade McDavid to Maple Leafs for MacKinnon",
                "source_url": "https://www.tsn.ca/nhl/oilers-trade-mcdavid-to-maple-leafs-for-mackinnon",
                "source": "TSN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 9,
                "trade_date": "2024-03-12",
                "season_year": 2024,
                "description": "The Tampa Bay Lightning traded elite goaltender Andrei Vasilevskiy to the Colorado Avalanche in exchange for offensive defenseman Victor Hedman. The Avalanche add a Vezina-caliber goalie while the Lightning get a top-pairing defenseman.",
                "headline": "Lightning Trade Vasilevskiy to Avalanche for Hedman",
                "source_url": "https://www.nhl.com/news/lightning-trade-vasilevskiy-to-avalanche-for-hedman",
                "source": "NHL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 10,
                "trade_date": "2024-02-28",
                "season_year": 2024,
                "description": "The Indiana Pacers acquired a 2025 first-round draft pick from the Cleveland Cavaliers in exchange for young center Walker Kessler. The Pacers add future assets while the Cavaliers get immediate help in the paint.",
                "headline": "Pacers Acquire 2025 First-Round Pick from Cavaliers",
                "source_url": "https://www.theathletic.com/nba/pacers-acquire-2025-first-round-pick-from-cavaliers",
                "source": "The Athletic",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_trades = mock_trades
        if season:
            filtered_trades = [t for t in filtered_trades if t['season_year'] == season]
        if source:
            filtered_trades = [t for t in filtered_trades if t['source'] == source]
        if applied is not None:
            filtered_trades = [t for t in filtered_trades if t['is_applied'] == applied]
        
        # Apply sorting
        if recent:
            filtered_trades = sorted(filtered_trades, key=lambda x: x['trade_date'], reverse=True)
        
        return {
            "trades": filtered_trades[:limit],
            "total": len(filtered_trades),
            "filters": {
                "season": season,
                "source": source,
                "applied": applied,
                "recent": recent,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/statistics")
async def get_trades_statistics(days: int = Query(365, description="Days of data to analyze")):
    """Get master trades statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_trades": 14,
            "unique_seasons": 1,
            "unique_sources": 7,
            "applied_trades": 14,
            "pending_trades": 0,
            "earliest_trade": "2024-02-08",
            "latest_trade": "2024-07-31",
            "avg_description_length": 245.7,
            "avg_headline_length": 52.3,
            "season_stats": [
                {
                    "season_year": 2024,
                    "total_trades": 14,
                    "applied_trades": 14,
                    "unique_sources": 7
                }
            ],
            "source_stats": [
                {
                    "source": "ESPN",
                    "total_trades": 3,
                    "unique_seasons": 1,
                    "applied_trades": 3
                },
                {
                    "source": "NBA.com",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "Bleacher Report",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "NFL.com",
                    "total_trades": 2,
                    "unique_seasons": 1,
                    "applied_trades": 2
                },
                {
                    "source": "MLB.com",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "TSN",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "The Athletic",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                }
            ],
            "month_stats": [
                {
                    "trade_month": "2024-07-01T00:00:00+00:00",
                    "total_trades": 2,
                    "unique_seasons": 1,
                    "applied_trades": 2
                },
                {
                    "trade_month": "2024-03-01T00:00:00+00:00",
                    "total_trades": 5,
                    "unique_seasons": 1,
                    "applied_trades": 5
                },
                {
                    "trade_month": "2024-02-01T00:00:00+00:00",
                    "total_trades": 7,
                    "unique_seasons": 1,
                    "applied_trades": 7
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trades statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/season/{season}")
async def get_trades_by_season(season: int):
    """Get trades for a specific season"""
    try:
        # Return mock season-specific data for now
        mock_season_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": season,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": season,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "season": season,
            "trades": mock_season_trades,
            "total": len(mock_season_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trades for season {season}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "season": season,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/source/{source}")
async def get_trades_by_source(source: str):
    """Get trades from a specific source"""
    try:
        # Return mock source-specific data for now
        mock_source_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": source,
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": source,
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            }
        ]
        
        return {
            "source": source,
            "trades": mock_source_trades,
            "total": len(mock_source_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trades from {source}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/applied")
async def get_applied_trades():
    """Get applied trades"""
    try:
        # Return mock applied trades data for now
        mock_applied_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": 2024,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "trades": mock_applied_trades,
            "total": len(mock_applied_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock applied trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/pending")
async def get_pending_trades():
    """Get pending trades"""
    try:
        # Return mock pending trades data for now
        mock_pending_trades = [
            {
                "id": 11,
                "trade_date": "2024-08-15",
                "season_year": 2024,
                "description": "The Los Angeles Lakers and Miami Heat are discussing a potential trade that would send Anthony Davis to Miami in exchange for Bam Adebayo and future draft picks. The deal is still in negotiation stages.",
                "headline": "Lakers and Heat Discussing Davis for Adebayo Trade",
                "source_url": "https://www.espn.com/nba/story/_/id/34567890/lakers-heat-discussing-davis-for-adebayo-trade",
                "source": "ESPN",
                "is_applied": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            },
            {
                "id": 12,
                "trade_date": "2024-08-12",
                "season_year": 2024,
                "description": "The Dallas Cowboys and San Francisco 49ers are in talks about a trade that would send Dak Prescott to San Francisco in exchange for Trey Lance and multiple draft picks. The trade is pending league approval.",
                "headline": "Cowboys and 49ers in Trade Talks for Prescott",
                "source_url": "https://www.nfl.com/news/cowboys-49ers-in-trade-talks-for-prescott",
                "source": "NFL.com",
                "is_applied": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            }
        ]
        
        return {
            "trades": mock_pending_trades,
            "total": len(mock_pending_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock pending trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/search")
async def search_trades(query: str = Query(..., description="Search query"),
                        limit: int = Query(20, description="Number of results to return")):
    """Search trades by headline or description"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": "NFL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['headline'].lower() or 
                   query_lower in r['description'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# User Betting Tracking Endpoints
@router.get("/user-bets")
async def get_user_bets(sport: int = Query(None, description="Sport ID to filter"),
                        status: str = Query(None, description="Bet status to filter"),
                        sportsbook: str = Query(None, description="Sportsbook to filter"),
                        recent: bool = Query(False, description="Get recent bets"),
                        limit: int = Query(50, description="Number of bets to return")):
    """Get user bets with optional filters"""
    try:
        # Return mock user bets data for now
        mock_user_bets = [
            {
                "id": 1,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": "DraftKings",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 2,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 92,
                "market_type": "points",
                "side": "over",
                "line_value": 28.5,
                "sportsbook": "FanDuel",
                "opening_odds": -110,
                "stake": 55.00,
                "status": "lost",
                "actual_value": 26.0,
                "closing_odds": -115,
                "closing_line": 28.5,
                "clv_cents": -5.0,
                "profit_loss": -55.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=18)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "Steph Curry over 28.5 points - tough defense from Lakers",
                "model_pick_id": 2,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=18)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 3,
                "sport_id": 1,
                "game_id": 664,
                "player_id": 111,
                "market_type": "passing_yards",
                "side": "over",
                "line_value": 285.5,
                "sportsbook": "PointsBet",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 312.0,
                "closing_odds": -105,
                "closing_line": 285.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat(),
                "notes": "Patrick Mahomes over 285.5 yards - great matchup vs Bills",
                "model_pick_id": 5,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat()
            },
            {
                "id": 4,
                "sport_id": 2,
                "game_id": 666,
                "player_id": 201,
                "market_type": "home_runs",
                "side": "over",
                "line_value": 1.5,
                "sportsbook": "BetMGM",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 2.0,
                "closing_odds": -105,
                "closing_line": 1.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=23)).isoformat(),
                "notes": "Aaron Judge over 1.5 HRs - facing struggling pitcher",
                "model_pick_id": 9,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=23)).isoformat()
            },
            {
                "id": 5,
                "sport_id": 53,
                "game_id": 668,
                "player_id": 301,
                "market_type": "points",
                "side": "over",
                "line_value": 1.5,
                "sportsbook": "Bet365",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 2.0,
                "closing_odds": -105,
                "closing_line": 1.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=23)).isoformat(),
                "notes": "Connor McDavid over 1.5 points - always dangerous",
                "model_pick_id": 12,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=23)).isoformat()
            },
            {
                "id": 6,
                "sport_id": 30,
                "game_id": 669,
                "player_id": 105,
                "market_type": "points",
                "side": "over",
                "line_value": 22.5,
                "sportsbook": "FanDuel",
                "opening_odds": -110,
                "stake": 220.00,
                "status": "pending",
                "actual_value": None,
                "closing_odds": None,
                "closing_line": None,
                "clv_cents": None,
                "profit_loss": None,
                "placed_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "settled_at": None,
                "notes": "Jayson Tatum over 22.5 points - game in progress",
                "model_pick_id": 14,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 7,
                "sport_id": 1,
                "game_id": 670,
                "player_id": 115,
                "market_type": "passing_touchdowns",
                "side": "over",
                "line_value": 1.5,
                "sportsbook": "BetMGM",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "pending",
                "actual_value": None,
                "closing_odds": None,
                "closing_line": None,
                "clv_cents": None,
                "profit_loss": None,
                "placed_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "settled_at": None,
                "notes": "Joe Burrow over 1.5 TDs - primetime game",
                "model_pick_id": 15,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_bets = mock_user_bets
        if sport:
            filtered_bets = [b for b in filtered_bets if b['sport_id'] == sport]
        if status:
            filtered_bets = [b for b in filtered_bets if b['status'] == status]
        if sportsbook:
            filtered_bets = [b for b in filtered_bets if b['sportsbook'] == sportsbook]
        
        # Apply sorting
        if recent:
            filtered_bets = sorted(filtered_bets, key=lambda x: x['placed_at'], reverse=True)
        
        return {
            "user_bets": filtered_bets[:limit],
            "total": len(filtered_bets),
            "filters": {
                "sport": sport,
                "status": status,
                "sportsbook": sportsbook,
                "recent": recent,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock user bets data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/statistics")
async def get_user_bets_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get user bets statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_bets": 15,
            "unique_sports": 4,
            "unique_games": 10,
            "unique_players": 12,
            "unique_sportsbooks": 6,
            "unique_market_types": 8,
            "won_bets": 8,
            "lost_bets": 4,
            "pending_bets": 3,
            "total_stake": 1210.00,
            "total_profit_loss": 345.00,
            "avg_stake": 80.67,
            "avg_profit_loss": 23.00,
            "win_rate_percentage": 66.67,
            "total_clv_cents": 15.00,
            "avg_clv_cents": 1.00,
            "sport_stats": [
                {
                    "sport_id": 30,
                    "total_bets": 4,
                    "won_bets": 2,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 495.00,
                    "total_profit_loss": 45.00,
                    "win_rate_percentage": 66.67,
                    "avg_clv_cents": 0.00
                },
                {
                    "sport_id": 1,
                    "total_bets": 3,
                    "won_bets": 1,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 330.00,
                    "total_profit_loss": 45.00,
                    "win_rate_percentage": 50.00,
                    "avg_clv_cents": 0.00
                },
                {
                    "sport_id": 2,
                    "total_bets": 3,
                    "won_bets": 1,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 220.00,
                    "total_profit_loss": 45.00,
                    "win_rate_percentage": 50.00,
                    "avg_clv_cents": 0.00
                },
                {
                    "sport_id": 53,
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                }
            ],
            "sportsbook_stats": [
                {
                    "sportsbook": "DraftKings",
                    "total_bets": 2,
                    "won_bets": 1,
                    "lost_bets": 1,
                    "pending_bets": 0,
                    "total_stake": 220.00,
                    "total_profit_loss": 0.00,
                    "win_rate_percentage": 50.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "sportsbook": "FanDuel",
                    "total_bets": 3,
                    "won_bets": 1,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 385.00,
                    "total_profit_loss": -55.00,
                    "win_rate_percentage": 50.00,
                    "avg_clv_cents": -5.00
                },
                {
                    "sportsbook": "BetMGM",
                    "total_bets": 3,
                    "won_bets": 2,
                    "lost_bets": 0,
                    "pending_bets": 1,
                    "total_stake": 330.00,
                    "total_profit_loss": 200.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "sportsbook": "PointsBet",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "sportsbook": "Bet365",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "sportsbook": "Caesars",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 2.00
                }
            ],
            "market_stats": [
                {
                    "market_type": "points",
                    "total_bets": 4,
                    "won_bets": 2,
                    "lost_bets": 1,
                    "pending_bets": 1,
                    "total_stake": 495.00,
                    "total_profit_loss": 45.00,
                    "win_rate_percentage": 66.67,
                    "avg_clv_cents": 0.00
                },
                {
                    "market_type": "passing_yards",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "market_type": "home_runs",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                },
                {
                    "market_type": "points",
                    "total_bets": 1,
                    "won_bets": 1,
                    "lost_bets": 0,
                    "pending_bets": 0,
                    "total_stake": 110.00,
                    "total_profit_loss": 100.00,
                    "win_rate_percentage": 100.00,
                    "avg_clv_cents": 5.00
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock user bets statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/sport/{sport_id}")
async def get_user_bets_by_sport(sport_id: int):
    """Get user bets for a specific sport"""
    try:
        # Return mock sport-specific data for now
        mock_sport_bets = [
            {
                "id": 1,
                "sport_id": sport_id,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": "DraftKings",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 2,
                "sport_id": sport_id,
                "game_id": 662,
                "player_id": 92,
                "market_type": "points",
                "side": "over",
                "line_value": 28.5,
                "sportsbook": "FanDuel",
                "opening_odds": -110,
                "stake": 55.00,
                "status": "lost",
                "actual_value": 26.0,
                "closing_odds": -115,
                "closing_line": 28.5,
                "clv_cents": -5.0,
                "profit_loss": -55.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=18)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "Steph Curry over 28.5 points - tough defense from Lakers",
                "model_pick_id": 2,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=18)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            }
        ]
        
        return {
            "sport_id": sport_id,
            "user_bets": mock_sport_bets,
            "total": len(mock_sport_bets),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock user bets for sport {sport_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/status/{status}")
async def get_user_bets_by_status(status: str):
    """Get user bets by status"""
    try:
        # Return mock status-specific data for now
        mock_status_bets = [
            {
                "id": 1,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": "DraftKings",
                "opening_odds": -110,
                "stake": 110.00,
                "status": status,
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 3,
                "sport_id": 1,
                "game_id": 664,
                "player_id": 111,
                "market_type": "passing_yards",
                "side": "over",
                "line_value": 285.5,
                "sportsbook": "PointsBet",
                "opening_odds": -110,
                "stake": 110.00,
                "status": status,
                "actual_value": 312.0,
                "closing_odds": -105,
                "closing_line": 285.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat(),
                "notes": "Patrick Mahomes over 285.5 yards - great matchup vs Bills",
                "model_pick_id": 5,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat()
            }
        ]
        
        return {
            "status": status,
            "user_bets": mock_status_bets,
            "total": len(mock_status_bets),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock user bets with status {status}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/sportsbook/{sportsbook}")
async def get_user_bets_by_sportsbook(sportsbook: str):
    """Get user bets from a specific sportsbook"""
    try:
        # Return mock sportsbook-specific data for now
        mock_sportsbook_bets = [
            {
                "id": 1,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": sportsbook,
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 4,
                "sport_id": 2,
                "game_id": 666,
                "player_id": 201,
                "market_type": "home_runs",
                "side": "over",
                "line_value": 1.5,
                "sportsbook": sportsbook,
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 2.0,
                "closing_odds": -105,
                "closing_line": 1.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=23)).isoformat(),
                "notes": "Aaron Judge over 1.5 HRs - facing struggling pitcher",
                "model_pick_id": 9,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=23)).isoformat()
            }
        ]
        
        return {
            "sportsbook": sportsbook,
            "user_bets": mock_sportsbook_bets,
            "total": len(mock_sportsbook_bets),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock user bets from {sportsbook}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sportsbook": sportsbook,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/user-bets/search")
async def search_user_bets(query: str = Query(..., description="Search query"),
                           limit: int = Query(20, description="Number of results to return")):
    """Search user bets by market, side, or notes"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "sport_id": 30,
                "game_id": 662,
                "player_id": 91,
                "market_type": "points",
                "side": "over",
                "line_value": 24.5,
                "sportsbook": "DraftKings",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 28.0,
                "closing_odds": -105,
                "closing_line": 24.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat(),
                "notes": "LeBron James over 24.5 points - strong matchup vs Warriors",
                "model_pick_id": 1,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=19)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1, hours=22)).isoformat()
            },
            {
                "id": 3,
                "sport_id": 1,
                "game_id": 664,
                "player_id": 111,
                "market_type": "passing_yards",
                "side": "over",
                "line_value": 285.5,
                "sportsbook": "PointsBet",
                "opening_odds": -110,
                "stake": 110.00,
                "status": "won",
                "actual_value": 312.0,
                "closing_odds": -105,
                "closing_line": 285.5,
                "clv_cents": 5.0,
                "profit_loss": 100.00,
                "placed_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat(),
                "notes": "Patrick Mahomes over 285.5 yards - great matchup vs Bills",
                "model_pick_id": 5,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=17)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3, hours=21)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['market_type'].lower() or 
                   query_lower in r['side'].lower() or 
                   (r['notes'] and query_lower in r['notes'].lower())
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Brain Anomaly Detection Endpoints
@router.get("/brain-anomalies")
async def get_brain_anomalies():
    """Get current brain anomalies"""
    try:
        # Return mock anomaly data for now
        mock_anomalies = [
            {
                "id": 1,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
                "metric_name": "recommendation_hit_rate",
                "baseline_value": 0.60,
                "current_value": 0.35,
                "change_pct": -41.7,
                "severity": "high",
                "status": "active",
                "details": "Recommendation hit rate dropped significantly during market volatility",
                "resolved_at": None,
                "resolution_method": None
            },
            {
                "id": 2,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=36)).isoformat(),
                "metric_name": "memory_usage",
                "baseline_value": 0.60,
                "current_value": 0.95,
                "change_pct": 58.3,
                "severity": "high",
                "status": "active",
                "details": "Memory usage approaching critical levels",
                "resolved_at": None,
                "resolution_method": None
            }
        ]
        
        return {
            "anomalies": mock_anomalies,
            "total": len(mock_anomalies),
            "active": len([a for a in mock_anomalies if a["status"] == "active"]),
            "resolved": len([a for a in mock_anomalies if a["status"] == "resolved"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock anomaly data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-anomalies-summary")
async def get_brain_anomalies_summary():
    """Get brain anomalies summary"""
    try:
        # Return mock summary
        return {
            "total_anomalies": 9,
            "active_anomalies": 2,
            "resolved_anomalies": 7,
            "high_severity": 4,
            "medium_severity": 4,
            "low_severity": 1,
            "most_common_metrics": [
                {"metric_name": "error_rate", "count": 2},
                {"metric_name": "recommendation_hit_rate", "count": 2}
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock anomaly summary"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
