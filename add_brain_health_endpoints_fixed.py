#!/usr/bin/env python3
"""
ADD BRAIN HEALTH ENDPOINTS - Add brain health monitoring endpoints (fixed)
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_brain_health_endpoints():
    """Add brain health monitoring endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the brain health endpoints
    brain_health_code = '''

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
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", brain_health_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += brain_health_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Brain health monitoring endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_brain_health_endpoints())
