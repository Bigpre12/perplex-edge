"""
Brain Health Monitoring Service - Comprehensive health check system
"""
import asyncio
import asyncpg
import os
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"

class HealthMetric(Enum):
    """Health metric types"""
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    UTILIZATION = "utilization"
    ACCURACY = "accuracy"
    AVAILABILITY = "availability"

@dataclass
class HealthCheck:
    """Health check result"""
    component: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    response_time_ms: int
    error_count: int = 0
    health_score: float = 0.0

@dataclass
class HealthThreshold:
    """Health check thresholds"""
    component: str
    metric: HealthMetric
    warning_threshold: float
    critical_threshold: float
    error_threshold: float

class BrainHealthMonitor:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.health_thresholds = self._initialize_health_thresholds()
        self.monitoring_active = False
        
    def _initialize_health_thresholds(self) -> Dict[str, List[HealthThreshold]]:
        """Initialize health thresholds for different components"""
        return {
            "database_connection_pool": [
                HealthThreshold("database_connection_pool", HealthMetric.UTILIZATION, 0.60, 0.80, 0.90),
                HealthThreshold("database_connection_pool", HealthMetric.ERROR_RATE, 0.02, 0.05, 0.10),
                HealthThreshold("database_connection_pool", HealthMetric.RESPONSE_TIME, 100, 200, 500)
            ],
            "api_response_time": [
                HealthThreshold("api_response_time", HealthMetric.RESPONSE_TIME, 200, 500, 1000),
                HealthThreshold("api_response_time", HealthMetric.ERROR_RATE, 0.02, 0.05, 0.10),
                HealthThreshold("api_response_time", HealthMetric.THROUGHPUT, 20, 10, 5)
            ],
            "memory_usage": [
                HealthThreshold("memory_usage", HealthMetric.UTILIZATION, 0.60, 0.80, 0.90),
                HealthThreshold("memory_usage", HealthMetric.ERROR_RATE, 0.01, 0.05, 0.10)
            ],
            "cpu_usage": [
                HealthThreshold("cpu_usage", HealthMetric.UTILIZATION, 0.60, 0.80, 0.90),
                HealthThreshold("cpu_usage", HealthMetric.ERROR_RATE, 0.01, 0.05, 0.10)
            ],
            "disk_space": [
                HealthThreshold("disk_space", HealthMetric.UTILIZATION, 0.70, 0.85, 0.95),
                HealthThreshold("disk_space", HealthMetric.ERROR_RATE, 0.01, 0.02, 0.05)
            ],
            "model_accuracy": [
                HealthThreshold("model_accuracy", HealthMetric.ACCURACY, 0.75, 0.65, 0.55),
                HealthThreshold("model_accuracy", HealthMetric.ERROR_RATE, 0.05, 0.10, 0.20)
            ],
            "external_apis": [
                HealthThreshold("external_apis", HealthMetric.RESPONSE_TIME, 500, 1000, 2000),
                HealthThreshold("external_apis", HealthMetric.ERROR_RATE, 0.02, 0.05, 0.10),
                HealthThreshold("external_apis", HealthMetric.AVAILABILITY, 0.95, 0.90, 0.80)
            ]
        }
    
    async def run_health_check(self, component: str) -> HealthCheck:
        """Run a health check for a specific component"""
        start_time = time.time()
        
        try:
            # Get current metrics for the component
            metrics = await self._get_component_metrics(component)
            
            # Evaluate health based on thresholds
            status, message, details, health_score = self._evaluate_health(component, metrics)
            
            response_time_ms = int((time.time() - start_time) * 1000)
            error_count = metrics.get('error_count', 0)
            
            health_check = HealthCheck(
                component=component,
                status=status,
                message=message,
                details=details,
                response_time_ms=response_time_ms,
                error_count=error_count,
                health_score=health_score
            )
            
            # Record the health check
            await self._record_health_check(health_check)
            
            return health_check
            
        except Exception as e:
            logger.error(f"Error running health check for {component}: {e}")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return HealthCheck(
                component=component,
                status=HealthStatus.ERROR,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)},
                response_time_ms=response_time_ms,
                error_count=1,
                health_score=0.0
            )
    
    async def _get_component_metrics(self, component: str) -> Dict[str, Any]:
        """Get current metrics for a component"""
        # This would connect to actual monitoring systems
        # For now, return mock data based on component
        
        mock_metrics = {
            "database_connection_pool": {
                "active_connections": 8,
                "max_connections": 20,
                "pool_utilization": 0.40,
                "avg_response_time_ms": 45,
                "connection_timeout_rate": 0.01,
                "error_count": 0
            },
            "api_response_time": {
                "avg_response_time_ms": 95,
                "p95_response_time_ms": 180,
                "requests_per_second": 45.2,
                "cache_hit_rate": 0.78,
                "error_count": 0
            },
            "memory_usage": {
                "current_usage": 0.42,
                "max_acceptable": 0.85,
                "available_memory_gb": 11.6,
                "total_memory_gb": 20,
                "gc_pressure": "low",
                "error_count": 0
            },
            "cpu_usage": {
                "current_usage": 0.45,
                "max_acceptable": 0.80,
                "cpu_cores": 8,
                "load_average": [0.42, 0.48, 0.45, 0.43],
                "process_count": 45,
                "error_count": 0
            },
            "disk_space": {
                "current_usage": 0.78,
                "max_acceptable": 0.90,
                "available_space_gb": 4.4,
                "total_space_gb": 20,
                "disk_io_utilization": 0.35,
                "error_count": 0
            },
            "model_accuracy": {
                "current_accuracy": 0.71,
                "minimum_acceptable": 0.65,
                "model_type": "passing_yards_predictor",
                "validation_accuracy": 0.69,
                "error_count": 0
            },
            "external_apis": {
                "provider": "sportsdata_io",
                "response_time_ms": 145,
                "timeout_rate": 0.01,
                "success_rate": 0.99,
                "error_count": 0
            },
            "brain_decision_system": {
                "decisions_per_hour": 45,
                "avg_decision_time_ms": 426,
                "success_rate": 0.75,
                "active_healing_actions": 0,
                "error_count": 0
            },
            "brain_healing_system": {
                "auto_healing_enabled": True,
                "last_healing_cycle": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "healing_success_rate": 0.889,
                "active_monitors": 8,
                "error_count": 0
            }
        }
        
        return mock_metrics.get(component, {"error_count": 1})
    
    def _evaluate_health(self, component: str, metrics: Dict[str, Any]) -> tuple[HealthStatus, str, Dict[str, Any], float]:
        """Evaluate health based on metrics and thresholds"""
        thresholds = self.health_thresholds.get(component, [])
        
        if not thresholds:
            return HealthStatus.WARNING, f"No thresholds defined for {component}", metrics, 0.5
        
        worst_status = HealthStatus.HEALTHY
        worst_message = "All metrics within acceptable range"
        health_score = 1.0
        
        for threshold in thresholds:
            current_value = self._get_metric_value(metrics, threshold.metric)
            
            if current_value is None:
                continue
            
            status, message, score = self._evaluate_metric_threshold(threshold, current_value)
            
            # Use the worst (most severe) status
            if self._status_is_worse(status, worst_status):
                worst_status = status
                worst_message = message
            
            health_score = min(health_score, score)
        
        return worst_status, worst_message, metrics, health_score
    
    def _get_metric_value(self, metrics: Dict[str, Any], metric: HealthMetric) -> Optional[float]:
        """Extract metric value from metrics dictionary"""
        metric_mappings = {
            HealthMetric.RESPONSE_TIME: ['avg_response_time_ms', 'response_time_ms'],
            HealthMetric.ERROR_RATE: ['error_rate', 'timeout_rate'],
            HealthMetric.THROUGHPUT: ['requests_per_second', 'decisions_per_hour'],
            HealthMetric.UTILIZATION: ['pool_utilization', 'current_usage', 'disk_usage', 'cpu_usage'],
            HealthMetric.ACCURACY: ['current_accuracy', 'success_rate'],
            HealthMetric.AVAILABILITY: ['success_rate', 'availability']
        }
        
        for field in metric_mappings.get(metric, []):
            if field in metrics:
                return float(metrics[field])
        
        return None
    
    def _evaluate_metric_threshold(self, threshold: HealthThreshold, current_value: float) -> tuple[HealthStatus, str, float]:
        """Evaluate a single metric against thresholds"""
        if current_value >= threshold.error_threshold:
            score = 0.0
            status = HealthStatus.CRITICAL
            message = f"{threshold.metric.value} is critical: {current_value} (threshold: {threshold.error_threshold})"
        elif current_value >= threshold.critical_threshold:
            score = 0.3
            status = HealthStatus.WARNING
            message = f"{threshold.metric.value} requires attention: {current_value} (threshold: {threshold.critical_threshold})"
        elif current_value >= threshold.warning_threshold:
            score = 0.7
            status = HealthStatus.WARNING
            message = f"{threshold.metric.value} is elevated: {current_value} (threshold: {threshold.warning_threshold})"
        else:
            score = 1.0
            status = HealthStatus.HEALTHY
            message = f"{threshold.metric.value} is optimal: {current_value}"
        
        return status, message, score
    
    def _status_is_worse(self, status1: HealthStatus, status2: HealthStatus) -> bool:
        """Check if status1 is worse than status2"""
        status_order = {
            HealthStatus.ERROR: 4,
            HealthStatus.CRITICAL: 3,
            HealthStatus.WARNING: 2,
            HealthStatus.HEALTHY: 1
        }
        return status_order[status1] > status_order[status2]
    
    async def _record_health_check(self, health_check: HealthCheck):
        """Record a health check in the database"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            await conn.execute("""
                INSERT INTO brain_health_checks (
                    component, status, message, details,
                    response_time_ms, error_count
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, 
                health_check.component,
                health_check.status.value,
                health_check.message,
                json.dumps(health_check.details),
                health_check.response_time_ms,
                health_check.error_count
            )
            
            await conn.close()
            logger.info(f"Recorded health check: {health_check.component} - {health_check.status.value}")
            
        except Exception as e:
            logger.error(f"Error recording health check: {e}")
    
    async def run_all_health_checks(self) -> List[HealthCheck]:
        """Run health checks for all components"""
        all_checks = []
        
        for component in self.health_thresholds.keys():
            try:
                health_check = await self.run_health_check(component)
                all_checks.append(health_check)
            except Exception as e:
                logger.error(f"Error running health check for {component}: {e}")
                # Add an error health check
                all_checks.append(HealthCheck(
                    component=component,
                    status=HealthStatus.ERROR,
                    message=f"Health check failed: {str(e)}",
                    details={"error": str(e)},
                    response_time_ms=0,
                    error_count=1,
                    health_score=0.0
                ))
        
        return all_checks
    
    async def get_overall_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        try:
            recent_checks = await self.run_all_health_checks()
            
            if not recent_checks:
                return {
                    "status": "unknown",
                    "message": "No health checks available",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate overall status
            status_counts = {
                HealthStatus.HEALTHY: 0,
                HealthStatus.WARNING: 0,
                HealthStatus.CRITICAL: 0,
                HealthStatus.ERROR: 0
            }
            
            total_score = 0
            component_health = {}
            
            for check in recent_checks:
                status_counts[check.status] += 1
                total_score += check.health_score
                component_health[check.component] = {
                    "status": check.status.value,
                    "score": check.health_score,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms
                }
            
            # Determine overall status
            if status_counts[HealthStatus.ERROR] > 0:
                overall_status = HealthStatus.ERROR
                overall_message = f"{status_counts[HealthStatus.ERROR]} components have errors"
            elif status_counts[HealthStatus.CRITICAL] > 0:
                overall_status = HealthStatus.CRITICAL
                overall_message = f"{status_counts[HealthStatus.CRITICAL]} components are critical"
            elif status_counts[HealthStatus.WARNING] > 0:
                overall_status = HealthStatus.WARNING
                overall_message = f"{status_counts[HealthStatus.WARNING]} components have warnings"
            else:
                overall_status = HealthStatus.HEALTHY
                overall_message = "All components are healthy"
            
            avg_score = total_score / len(recent_checks) if recent_checks else 0
            
            return {
                "status": overall_status.value,
                "message": overall_message,
                "overall_score": avg_score,
                "component_count": len(recent_checks),
                "status_counts": {k.value: v for k, v in status_counts.items()},
                "component_health": component_health,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting overall health status: {e}")
            return {
                "status": "error",
                "message": f"Unable to determine health status: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_health_history(self, hours: int = 24) -> List[Dict]:
        """Get health check history"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetch("""
                SELECT * FROM brain_health_checks 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                ORDER BY timestamp DESC
            """, hours)
            
            await conn.close()
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Error getting health history: {e}")
            return []
    
    async def get_health_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get health performance metrics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall performance
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_checks,
                    COUNT(CASE WHEN status = 'healthy' THEN 1 END) as healthy_checks,
                    COUNT(CASE WHEN status = 'warning' THEN 1 END) as warning_checks,
                    COUNT(CASE WHEN status = 'critical' THEN 1 END) as critical_checks,
                    COUNT(CASE WHEN status = 'error' THEN 1 END) as error_checks,
                    AVG(response_time_ms) as avg_response_time_ms,
                    AVG(error_count) as avg_error_count
                FROM brain_health_checks 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
            """, hours)
            
            # Component performance
            components = await conn.fetch("""
                SELECT 
                    component,
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'healthy' THEN 1 END) as healthy,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(error_count) as avg_error_count,
                    AVG(details->>'health_score') as avg_health_score
                FROM brain_health_checks 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                GROUP BY component
                ORDER BY total DESC
            """, hours)
            
            await conn.close()
            
            success_rate = (overall['healthy_checks'] / overall['total_checks'] * 100) if overall['total_checks'] > 0 else 0
            
            return {
                'period_hours': hours,
                'total_checks': overall['total_checks'],
                'healthy_checks': overall['healthy_checks'],
                'warning_checks': overall['warning_checks'],
                'critical_checks': overall['critical_checks'],
                'error_checks': overall['error_checks'],
                'overall_success_rate': success_rate,
                'avg_response_time_ms': overall['avg_response_time_ms'],
                'avg_error_count': overall['avg_error_count'],
                'component_performance': [dict(row) for row in components]
            }
            
        except Exception as e:
            logger.error(f"Error getting health performance: {e}")
            return {}

# Global instance
health_monitor = BrainHealthMonitor()

async def run_health_check(component: str):
    """Run a health check for a component"""
    return await health_monitor.run_health_check(component)

async def get_overall_health_status():
    """Get overall health status"""
    return await health_monitor.get_overall_health_status()

if __name__ == "__main__":
    # Test health monitoring
    async def test():
        # Test a single health check
        check = await run_health_check("database_connection_pool")
        print(f"Health check: {check.status.value} - {check.message}")
        
        # Get overall status
        status = await get_overall_health_status()
        print(f"Overall status: {status['status']} - {status['message']}")
        
        # Get performance
        performance = await health_monitor.get_health_performance()
        print(f"Performance: {performance}")
    
    asyncio.run(test())
