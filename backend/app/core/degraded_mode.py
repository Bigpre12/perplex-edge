"""
Degraded mode service for graceful degradation when external services fail.

Provides:
- Automatic detection of service failures
- Serving stale data with degraded flag
- Auto-recovery when services return
"""
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from dataclasses import dataclass, field

from app.core.logging import get_logger
from app.core.resilience import CircuitBreakerRegistry

logger = get_logger(__name__)


@dataclass
class ServiceStatus:
    """Status of an external service."""
    name: str
    is_healthy: bool = True
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    consecutive_failures: int = 0
    is_degraded: bool = False
    degraded_since: Optional[datetime] = None


@dataclass
class DegradedResponse:
    """Response wrapper for degraded mode."""
    data: Any
    is_degraded: bool = False
    degraded_reason: Optional[str] = None
    data_age_seconds: Optional[float] = None
    source: str = "live"  # "live", "cache", "stale", "fallback"


class DegradedModeManager:
    """
    Manages degraded mode for external services.
    
    Features:
    - Track service health
    - Determine if service is in degraded mode
    - Provide stale data when services are down
    - Auto-recovery detection
    """
    
    # Thresholds for entering degraded mode
    DEGRADED_THRESHOLD_FAILURES = 3
    DEGRADED_THRESHOLD_SECONDS = 300  # 5 minutes
    
    # Maximum age of stale data to serve
    MAX_STALE_DATA_AGE_SECONDS = 3600  # 1 hour
    
    def __init__(self):
        self._services: dict[str, ServiceStatus] = {}
    
    def get_or_create_service(self, name: str) -> ServiceStatus:
        """Get or create a service status tracker."""
        if name not in self._services:
            self._services[name] = ServiceStatus(name=name)
        return self._services[name]
    
    def record_success(self, service_name: str) -> None:
        """Record a successful service call."""
        service = self.get_or_create_service(service_name)
        service.is_healthy = True
        service.last_success = datetime.now(timezone.utc)
        service.consecutive_failures = 0
        
        # Exit degraded mode on success
        if service.is_degraded:
            logger.info(
                "service_recovered",
                service=service_name,
                degraded_duration_seconds=(
                    (datetime.now(timezone.utc) - service.degraded_since).total_seconds()
                    if service.degraded_since else None
                ),
            )
            service.is_degraded = False
            service.degraded_since = None
    
    def record_failure(self, service_name: str, error: Optional[str] = None) -> None:
        """Record a failed service call."""
        service = self.get_or_create_service(service_name)
        service.is_healthy = False
        service.last_failure = datetime.now(timezone.utc)
        service.failure_count += 1
        service.consecutive_failures += 1
        
        # Enter degraded mode if threshold exceeded
        if (
            not service.is_degraded
            and service.consecutive_failures >= self.DEGRADED_THRESHOLD_FAILURES
        ):
            service.is_degraded = True
            service.degraded_since = datetime.now(timezone.utc)
            logger.warning(
                "service_entering_degraded_mode",
                service=service_name,
                consecutive_failures=service.consecutive_failures,
                error=error,
            )
    
    def is_degraded(self, service_name: str) -> bool:
        """Check if a service is in degraded mode."""
        service = self._services.get(service_name)
        if not service:
            return False
        return service.is_degraded
    
    def should_serve_stale_data(
        self,
        service_name: str,
        data_timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Determine if stale data should be served for a service.
        
        Returns True if:
        - Service is in degraded mode
        - Data is not too old (within MAX_STALE_DATA_AGE_SECONDS)
        """
        if not self.is_degraded(service_name):
            return False
        
        if data_timestamp is None:
            return True  # No timestamp, assume usable
        
        age_seconds = (datetime.now(timezone.utc) - data_timestamp).total_seconds()
        return age_seconds <= self.MAX_STALE_DATA_AGE_SECONDS
    
    def get_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all tracked services."""
        result = {}
        for name, service in self._services.items():
            result[name] = {
                "is_healthy": service.is_healthy,
                "is_degraded": service.is_degraded,
                "last_success": service.last_success.isoformat() if service.last_success else None,
                "last_failure": service.last_failure.isoformat() if service.last_failure else None,
                "failure_count": service.failure_count,
                "consecutive_failures": service.consecutive_failures,
                "degraded_since": service.degraded_since.isoformat() if service.degraded_since else None,
            }
        return result
    
    def get_overall_status(self) -> str:
        """Get overall system status."""
        if not self._services:
            return "healthy"
        
        degraded_count = sum(1 for s in self._services.values() if s.is_degraded)
        unhealthy_count = sum(1 for s in self._services.values() if not s.is_healthy)
        
        if degraded_count > 0:
            return "degraded"
        if unhealthy_count > 0:
            return "warning"
        return "healthy"


# Global instance
degraded_mode = DegradedModeManager()


def wrap_with_degraded_mode(
    service_name: str,
    fallback_data: Any = None,
    get_cached_data: Optional[callable] = None,
):
    """
    Decorator to wrap a service call with degraded mode support.
    
    Usage:
        @wrap_with_degraded_mode("odds_api", fallback_data=[])
        async def fetch_odds():
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                degraded_mode.record_success(service_name)
                return DegradedResponse(
                    data=result,
                    is_degraded=False,
                    source="live",
                )
            except Exception as e:
                degraded_mode.record_failure(service_name, str(e))
                
                # Try to get cached data
                if get_cached_data:
                    try:
                        cached = await get_cached_data(*args, **kwargs)
                        if cached is not None:
                            logger.warning(
                                "serving_cached_data",
                                service=service_name,
                                reason=str(e)[:100],
                            )
                            return DegradedResponse(
                                data=cached,
                                is_degraded=True,
                                degraded_reason=f"{service_name} unavailable: {str(e)[:50]}",
                                source="cache",
                            )
                    except Exception:
                        pass
                
                # Use fallback data
                if fallback_data is not None:
                    logger.warning(
                        "serving_fallback_data",
                        service=service_name,
                        reason=str(e)[:100],
                    )
                    return DegradedResponse(
                        data=fallback_data,
                        is_degraded=True,
                        degraded_reason=f"{service_name} unavailable: {str(e)[:50]}",
                        source="fallback",
                    )
                
                # Re-raise if no fallback available
                raise
        
        return wrapper
    return decorator


# Helper to check circuit breaker integration
def sync_with_circuit_breakers() -> None:
    """Sync degraded mode status with circuit breakers."""
    cb_status = CircuitBreakerRegistry.get_status()
    
    for name, info in cb_status.items():
        service = degraded_mode.get_or_create_service(name)
        
        # If circuit breaker is open, mark service as degraded
        if info.get("state") == "open":
            if not service.is_degraded:
                service.is_degraded = True
                service.degraded_since = datetime.now(timezone.utc)
                logger.warning(
                    "circuit_breaker_triggered_degraded_mode",
                    service=name,
                )
