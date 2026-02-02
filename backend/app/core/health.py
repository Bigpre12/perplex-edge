"""
Comprehensive health check module for Perplex Engine.

Provides health checks for all dependencies:
- Database connectivity
- External API health (quota, connectivity)
- Cache health
- Background scheduler status
- Data freshness
"""
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.resilience import CircuitBreakerRegistry

logger = get_logger(__name__)


class HealthStatus:
    """Health check result."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    
    def __init__(
        self,
        status: str,
        component: str,
        message: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        latency_ms: Optional[float] = None,
    ):
        self.status = status
        self.component = component
        self.message = message
        self.details = details or {}
        self.latency_ms = latency_ms
        self.checked_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "component": self.component,
            "message": self.message,
            "details": self.details,
            "latency_ms": self.latency_ms,
            "checked_at": self.checked_at.isoformat(),
        }
    
    @property
    def is_healthy(self) -> bool:
        return self.status == self.HEALTHY


async def check_database(db: AsyncSession) -> HealthStatus:
    """Check database connectivity and basic operations."""
    import time
    start = time.perf_counter()
    
    try:
        # Simple query to check connectivity
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        
        latency_ms = (time.perf_counter() - start) * 1000
        
        return HealthStatus(
            status=HealthStatus.HEALTHY,
            component="database",
            message="Database connection successful",
            latency_ms=round(latency_ms, 2),
        )
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        logger.error("health_check_database_failed", error=str(e)[:200])
        return HealthStatus(
            status=HealthStatus.UNHEALTHY,
            component="database",
            message=f"Database connection failed: {str(e)[:100]}",
            latency_ms=round(latency_ms, 2),
        )


async def check_odds_api_quota() -> HealthStatus:
    """Check Odds API quota status."""
    from app.services.odds_provider import get_quota_status
    
    try:
        quota = get_quota_status()
        remaining = quota.get("remaining", 0)
        used = quota.get("used", 0)
        
        # Determine health based on remaining quota
        if remaining > 100:
            status = HealthStatus.HEALTHY
            message = f"Quota healthy: {remaining} requests remaining"
        elif remaining > 20:
            status = HealthStatus.DEGRADED
            message = f"Quota low: {remaining} requests remaining"
        else:
            status = HealthStatus.UNHEALTHY
            message = f"Quota critical: {remaining} requests remaining"
        
        return HealthStatus(
            status=status,
            component="odds_api",
            message=message,
            details={
                "remaining": remaining,
                "used": used,
            },
        )
    except Exception as e:
        logger.error("health_check_odds_api_failed", error=str(e)[:200])
        return HealthStatus(
            status=HealthStatus.DEGRADED,
            component="odds_api",
            message=f"Could not check quota: {str(e)[:100]}",
        )


async def check_cache() -> HealthStatus:
    """Check cache health."""
    from app.services.memory_cache import memory_cache
    
    try:
        stats = memory_cache.stats()
        
        return HealthStatus(
            status=HealthStatus.HEALTHY,
            component="cache",
            message="Cache operational",
            details={
                "size": stats.get("size", 0),
                "hit_rate": stats.get("hit_rate", 0),
            },
        )
    except Exception as e:
        logger.error("health_check_cache_failed", error=str(e)[:200])
        return HealthStatus(
            status=HealthStatus.DEGRADED,
            component="cache",
            message=f"Cache check failed: {str(e)[:100]}",
        )


async def check_scheduler() -> HealthStatus:
    """Check background scheduler status."""
    from app.scheduler import get_scheduler_status
    
    try:
        status = get_scheduler_status()
        
        if status.get("enabled", False):
            running_tasks = status.get("running_tasks", [])
            return HealthStatus(
                status=HealthStatus.HEALTHY,
                component="scheduler",
                message=f"Scheduler running with {len(running_tasks)} tasks",
                details={
                    "enabled": True,
                    "task_count": len(running_tasks),
                },
            )
        else:
            return HealthStatus(
                status=HealthStatus.DEGRADED,
                component="scheduler",
                message="Scheduler disabled",
                details={"enabled": False},
            )
    except Exception as e:
        logger.error("health_check_scheduler_failed", error=str(e)[:200])
        return HealthStatus(
            status=HealthStatus.UNHEALTHY,
            component="scheduler",
            message=f"Scheduler check failed: {str(e)[:100]}",
        )


async def check_data_freshness(db: AsyncSession) -> HealthStatus:
    """Check if data is fresh (synced recently)."""
    from app.models import SyncMetadata
    
    try:
        # Check last sync time for each sport
        result = await db.execute(
            select(SyncMetadata)
            .order_by(SyncMetadata.last_sync_at.desc())
            .limit(5)
        )
        syncs = result.scalars().all()
        
        if not syncs:
            return HealthStatus(
                status=HealthStatus.DEGRADED,
                component="data_freshness",
                message="No sync metadata found",
            )
        
        # Check if most recent sync was within last 30 minutes
        now = datetime.now(timezone.utc)
        most_recent = max(s.last_sync_at for s in syncs if s.last_sync_at)
        
        if most_recent:
            age_minutes = (now - most_recent.replace(tzinfo=timezone.utc)).total_seconds() / 60
            
            if age_minutes < 30:
                status = HealthStatus.HEALTHY
                message = f"Data synced {int(age_minutes)} minutes ago"
            elif age_minutes < 120:
                status = HealthStatus.DEGRADED
                message = f"Data synced {int(age_minutes)} minutes ago (stale)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Data synced {int(age_minutes)} minutes ago (very stale)"
            
            return HealthStatus(
                status=status,
                component="data_freshness",
                message=message,
                details={
                    "last_sync_minutes_ago": round(age_minutes, 1),
                    "sports_synced": len(syncs),
                },
            )
        
        return HealthStatus(
            status=HealthStatus.DEGRADED,
            component="data_freshness",
            message="No sync timestamps available",
        )
    except Exception as e:
        logger.error("health_check_data_freshness_failed", error=str(e)[:200])
        return HealthStatus(
            status=HealthStatus.DEGRADED,
            component="data_freshness",
            message=f"Could not check data freshness: {str(e)[:100]}",
        )


def check_circuit_breakers() -> HealthStatus:
    """Check circuit breaker status for external services."""
    try:
        status = CircuitBreakerRegistry.get_status()
        
        open_breakers = [
            name for name, info in status.items()
            if info.get("state") == "open"
        ]
        
        if not status:
            return HealthStatus(
                status=HealthStatus.HEALTHY,
                component="circuit_breakers",
                message="No circuit breakers registered",
            )
        
        if open_breakers:
            return HealthStatus(
                status=HealthStatus.DEGRADED,
                component="circuit_breakers",
                message=f"Circuit breakers open: {', '.join(open_breakers)}",
                details=status,
            )
        
        return HealthStatus(
            status=HealthStatus.HEALTHY,
            component="circuit_breakers",
            message=f"All {len(status)} circuit breakers closed",
            details=status,
        )
    except Exception as e:
        logger.error("health_check_circuit_breakers_failed", error=str(e)[:200])
        return HealthStatus(
            status=HealthStatus.DEGRADED,
            component="circuit_breakers",
            message=f"Could not check circuit breakers: {str(e)[:100]}",
        )


def check_degraded_mode() -> HealthStatus:
    """Check degraded mode status."""
    try:
        from app.core.degraded_mode import degraded_mode
        
        status = degraded_mode.get_status()
        overall = degraded_mode.get_overall_status()
        
        degraded_services = [
            name for name, info in status.items()
            if info.get("is_degraded")
        ]
        
        if not status:
            return HealthStatus(
                status=HealthStatus.HEALTHY,
                component="degraded_mode",
                message="No services tracked",
            )
        
        if degraded_services:
            return HealthStatus(
                status=HealthStatus.DEGRADED,
                component="degraded_mode",
                message=f"Degraded services: {', '.join(degraded_services)}",
                details=status,
            )
        
        return HealthStatus(
            status=HealthStatus.HEALTHY,
            component="degraded_mode",
            message=f"All {len(status)} services healthy",
            details=status,
        )
    except Exception as e:
        logger.error("health_check_degraded_mode_failed", error=str(e)[:200])
        return HealthStatus(
            status=HealthStatus.DEGRADED,
            component="degraded_mode",
            message=f"Could not check degraded mode: {str(e)[:100]}",
        )


async def run_all_health_checks(db: AsyncSession) -> dict[str, Any]:
    """
    Run all health checks and return comprehensive health report.
    
    Returns:
        dict with overall status and individual component statuses
    """
    import time
    start = time.perf_counter()
    
    # Run all checks
    checks = [
        await check_database(db),
        await check_odds_api_quota(),
        await check_cache(),
        await check_scheduler(),
        await check_data_freshness(db),
        check_circuit_breakers(),
        check_degraded_mode(),
    ]
    
    # Determine overall status
    statuses = [c.status for c in checks]
    if all(s == HealthStatus.HEALTHY for s in statuses):
        overall_status = HealthStatus.HEALTHY
    elif any(s == HealthStatus.UNHEALTHY for s in statuses):
        overall_status = HealthStatus.UNHEALTHY
    else:
        overall_status = HealthStatus.DEGRADED
    
    total_latency = (time.perf_counter() - start) * 1000
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latency_ms": round(total_latency, 2),
        "components": {c.component: c.to_dict() for c in checks},
        "summary": {
            "healthy": sum(1 for s in statuses if s == HealthStatus.HEALTHY),
            "degraded": sum(1 for s in statuses if s == HealthStatus.DEGRADED),
            "unhealthy": sum(1 for s in statuses if s == HealthStatus.UNHEALTHY),
        },
    }


async def run_quick_health_check(db: AsyncSession) -> dict[str, Any]:
    """
    Run quick health check (database only) for liveness probes.
    
    Returns:
        dict with basic status
    """
    db_check = await check_database(db)
    
    return {
        "status": db_check.status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_check.status,
    }
