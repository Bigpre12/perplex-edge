"""
Brain Persistence Service - PostgreSQL integration for brain operations.

Provides persistent storage for brain decisions, health checks, healing actions,
and system state with automatic cleanup and analytics capabilities.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, delete, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_session_maker
from app.models.brain_state import (
    BrainDecision, BrainHealthCheck, BrainHealingAction, 
    BrainSystemState, BrainAnomaly, BrainBusinessMetrics,
    BrainCorrelation, BrainLearning
)

logger = logging.getLogger(__name__)


class BrainPersistenceService:
    """Service for persisting brain state and operations to PostgreSQL."""
    
    def __init__(self):
        self.session_maker = get_session_maker()
        self._cleanup_enabled = True
        self._retention_days = {
            "decisions": 30,      # Keep decisions for 30 days
            "health_checks": 7,  # Keep health checks for 7 days
            "healing_actions": 30, # Keep healing actions for 30 days
            "anomalies": 90,     # Keep anomalies for 90 days
            "metrics": 365,      # Keep business metrics for 1 year
            "correlations": 1,   # Keep correlations for 1 day
            "learning": 365,     # Keep learning data for 1 year
        }
    
    async def log_decision(
        self,
        category: str,
        action: str,
        reasoning: str,
        outcome: str,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: int = 0,
        correlation_id: Optional[str] = None
    ) -> int:
        """Persist a brain decision to PostgreSQL."""
        try:
            async with self.session_maker() as db:
                decision = BrainDecision(
                    category=category,
                    action=action,
                    reasoning=reasoning,
                    outcome=outcome,
                    details=details or {},
                    duration_ms=duration_ms,
                    correlation_id=correlation_id
                )
                
                db.add(decision)
                await db.commit()
                await db.refresh(decision)
                
                logger.debug(f"[BRAIN:PERSIST] Decision logged: {category}/{action} -> {outcome} (ID: {decision.id})")
                return decision.id
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to log decision: {e}")
            return -1
    
    async def log_health_check(
        self,
        component: str,
        status: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        response_time_ms: int = 0,
        error_count: int = 0
    ) -> int:
        """Persist a health check to PostgreSQL."""
        try:
            async with self.session_maker() as db:
                health_check = BrainHealthCheck(
                    component=component,
                    status=status,
                    message=message,
                    details=details or {},
                    response_time_ms=response_time_ms,
                    error_count=error_count
                )
                
                db.add(health_check)
                await db.commit()
                await db.refresh(health_check)
                
                logger.debug(f"[BRAIN:PERSIST] Health check logged: {component} -> {status} (ID: {health_check.id})")
                return health_check.id
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to log health check: {e}")
            return -1
    
    async def log_healing_action(
        self,
        action: str,
        target: str,
        reason: str,
        result: str,
        duration_ms: int = 0,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Persist a healing action to PostgreSQL."""
        try:
            async with self.session_maker() as db:
                healing_action = BrainHealingAction(
                    action=action,
                    target=target,
                    reason=reason,
                    result=result,
                    duration_ms=duration_ms,
                    details=details or {}
                )
                
                db.add(healing_action)
                await db.commit()
                await db.refresh(healing_action)
                
                logger.debug(f"[BRAIN:PERSIST] Healing action logged: {action} on {target} -> {result} (ID: {healing_action.id})")
                return healing_action.id
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to log healing action: {e}")
            return -1
    
    async def save_system_state(self, state_data: Dict[str, Any]) -> int:
        """Save current brain system state to PostgreSQL."""
        try:
            async with self.session_maker() as db:
                system_state = BrainSystemState(
                    cycle_count=state_data.get("cycle_count", 0),
                    overall_status=state_data.get("overall_status", "initializing"),
                    heals_attempted=state_data.get("heals_attempted", 0),
                    heals_succeeded=state_data.get("heals_succeeded", 0),
                    consecutive_failures=state_data.get("consecutive_failures", {}),
                    sport_priority=state_data.get("sport_priority", {}),
                    quota_budget=state_data.get("quota_budget", {}),
                    auto_commit_enabled=state_data.get("auto_commit_enabled", True),
                    git_commits_made=state_data.get("git_commits_made", 0),
                    betting_opportunities_found=state_data.get("betting_opportunities_found", 0),
                    strong_bets_identified=state_data.get("strong_bets_identified", 0),
                    last_betting_scan=state_data.get("last_betting_scan"),
                    top_betting_opportunities=state_data.get("top_betting_opportunities", []),
                    last_cycle_duration_ms=state_data.get("last_cycle_duration_ms", 0),
                    uptime_hours=state_data.get("uptime_hours", 0.0)
                )
                
                db.add(system_state)
                await db.commit()
                await db.refresh(system_state)
                
                logger.debug(f"[BRAIN:PERSIST] System state saved (ID: {system_state.id})")
                return system_state.id
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to save system state: {e}")
            return -1
    
    async def log_anomaly(
        self,
        metric_name: str,
        baseline_value: float,
        current_value: float,
        change_pct: float,
        severity: str,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Log an anomaly detected by the brain."""
        try:
            async with self.session_maker() as db:
                anomaly = BrainAnomaly(
                    metric_name=metric_name,
                    baseline_value=baseline_value,
                    current_value=current_value,
                    change_pct=change_pct,
                    severity=severity,
                    details=details or {}
                )
                
                db.add(anomaly)
                await db.commit()
                await db.refresh(anomaly)
                
                logger.debug(f"[BRAIN:PERSIST] Anomaly logged: {metric_name} ({severity}) (ID: {anomaly.id})")
                return anomaly.id
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to log anomaly: {e}")
            return -1
    
    async def log_business_metrics(self, metrics: Dict[str, Any]) -> int:
        """Log business metrics for trend analysis."""
        try:
            async with self.session_maker() as db:
                business_metrics = BrainBusinessMetrics(
                    total_recommendations=metrics.get("total_recommendations", 0),
                    recommendation_hit_rate=metrics.get("recommendation_hit_rate", 0.0),
                    average_ev=metrics.get("average_ev", 0.0),
                    clv_trend=metrics.get("clv_trend", 0.0),
                    prop_volume=metrics.get("prop_volume", 0),
                    user_confidence_score=metrics.get("user_confidence_score", 0.0),
                    api_response_time_ms=metrics.get("api_response_time_ms", 0.0),
                    error_rate=metrics.get("error_rate", 0.0),
                    throughput=metrics.get("throughput", 0.0),
                    cpu_usage=metrics.get("cpu_usage", 0.0),
                    memory_usage=metrics.get("memory_usage", 0.0),
                    disk_usage=metrics.get("disk_usage", 0.0)
                )
                
                db.add(business_metrics)
                await db.commit()
                await db.refresh(business_metrics)
                
                logger.debug(f"[BRAIN:PERSIST] Business metrics logged (ID: {business_metrics.id})")
                return business_metrics.id
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to log business metrics: {e}")
            return -1
    
    async def start_correlation(
        self,
        correlation_id: str,
        operation_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Start tracking a correlation."""
        try:
            async with self.session_maker() as db:
                correlation = BrainCorrelation(
                    correlation_id=correlation_id,
                    operation_type=operation_type,
                    details=details or {},
                    events=[]
                )
                
                db.add(correlation)
                await db.commit()
                
                logger.debug(f"[BRAIN:PERSIST] Correlation started: {correlation_id} ({operation_type})")
                return True
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to start correlation: {e}")
            return False
    
    async def add_correlation_event(self, correlation_id: str, event: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Add an event to a correlation timeline."""
        try:
            async with self.session_maker() as db:
                result = await db.execute(
                    select(BrainCorrelation).where(BrainCorrelation.correlation_id == correlation_id)
                )
                correlation = result.scalar_one_or_none()
                
                if correlation:
                    event_data = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "event": event,
                        "data": data or {}
                    }
                    
                    # Add event to timeline
                    events = correlation.events or []
                    events.append(event_data)
                    correlation.events = events
                    
                    await db.commit()
                    logger.debug(f"[BRAIN:PERSIST] Event added to correlation {correlation_id}: {event}")
                    return True
                else:
                    logger.warning(f"[BRAIN:PERSIST] Correlation not found: {correlation_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to add correlation event: {e}")
            return False
    
    async def complete_correlation(
        self,
        correlation_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Complete a correlation with status and result."""
        try:
            async with self.session_maker() as db:
                correlation = await db.execute(
                    select(BrainCorrelation).where(BrainCorrelation.correlation_id == correlation_id)
                )
                correlation = correlation.scalar_one_or_none()
                
                if correlation:
                    correlation.status = status
                    correlation.completed_at = datetime.now(timezone.utc)
                    correlation.result = result or {}
                    correlation.error_message = error_message
                    
                    # Calculate duration
                    if correlation.started_at:
                        correlation.duration_ms = int(
                            (correlation.completed_at - correlation.started_at).total_seconds() * 1000
                        )
                    
                    await db.commit()
                    logger.debug(f"[BRAIN:PERSIST] Correlation completed: {correlation_id} -> {status}")
                    return True
                else:
                    logger.warning(f"[BRAIN:PERSIST] Correlation not found: {correlation_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to complete correlation: {e}")
            return False
    
    async def get_recent_decisions(self, limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent brain decisions."""
        try:
            async with self.session_maker() as db:
                query = select(BrainDecision).order_by(BrainDecision.timestamp.desc())
                
                if category:
                    query = query.where(BrainDecision.category == category)
                
                query = query.limit(limit)
                result = await db.execute(query)
                decisions = result.scalars().all()
                
                return [
                    {
                        "id": d.id,
                        "timestamp": d.timestamp.isoformat(),
                        "category": d.category,
                        "action": d.action,
                        "reasoning": d.reasoning,
                        "outcome": d.outcome,
                        "details": d.details,
                        "duration_ms": d.duration_ms,
                        "correlation_id": d.correlation_id
                    }
                    for d in decisions
                ]
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to get recent decisions: {e}")
            return []
    
    async def get_health_trends(self, component: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health check trends for analysis."""
        try:
            async with self.session_maker() as db:
                since = datetime.now(timezone.utc) - timedelta(hours=hours)
                
                query = select(BrainHealthCheck).where(BrainHealthCheck.timestamp >= since)
                
                if component:
                    query = query.where(BrainHealthCheck.component == component)
                
                query = query.order_by(BrainHealthCheck.timestamp.desc())
                result = await db.execute(query)
                health_checks = result.scalars().all()
                
                return [
                    {
                        "id": h.id,
                        "timestamp": h.timestamp.isoformat(),
                        "component": h.component,
                        "status": h.status,
                        "message": h.message,
                        "details": h.details,
                        "response_time_ms": h.response_time_ms,
                        "error_count": h.error_count
                    }
                    for h in health_checks
                ]
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to get health trends: {e}")
            return []
    
    async def get_anomaly_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get anomaly summary for the specified time period."""
        try:
            async with self.session_maker() as db:
                since = datetime.now(timezone.utc) - timedelta(hours=hours)
                
                # Count anomalies by severity
                severity_counts = await db.execute(
                    select(
                        BrainAnomaly.severity,
                        func.count(BrainAnomaly.id).label('count')
                    )
                    .where(BrainAnomaly.timestamp >= since)
                    .group_by(BrainAnomaly.severity)
                )
                
                severity_data = {row.severity: row.count for row in severity_counts}
                
                # Get active anomalies
                active_anomalies = await db.execute(
                    select(BrainAnomaly)
                    .where(and_(
                        BrainAnomaly.timestamp >= since,
                        BrainAnomaly.status == "active"
                    ))
                    .order_by(BrainAnomaly.timestamp.desc())
                    .limit(10)
                )
                
                active_data = [
                    {
                        "id": a.id,
                        "timestamp": a.timestamp.isoformat(),
                        "metric_name": a.metric_name,
                        "change_pct": a.change_pct,
                        "severity": a.severity,
                        "details": a.details
                    }
                    for a in active_anomalies.scalars().all()
                ]
                
                return {
                    "period_hours": hours,
                    "severity_counts": severity_data,
                    "active_anomalies": active_data,
                    "total_anomalies": sum(severity_data.values())
                }
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to get anomaly summary: {e}")
            return {"period_hours": hours, "severity_counts": {}, "active_anomalies": [], "total_anomalies": 0}
    
    async def get_business_metrics_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get business metrics trends."""
        try:
            async with self.session_maker() as db:
                since = datetime.now(timezone.utc) - timedelta(hours=hours)
                
                result = await db.execute(
                    select(BrainBusinessMetrics)
                    .where(BrainBusinessMetrics.timestamp >= since)
                    .order_by(BrainBusinessMetrics.timestamp.desc())
                )
                
                metrics = result.scalars().all()
                
                return [
                    {
                        "id": m.id,
                        "timestamp": m.timestamp.isoformat(),
                        "total_recommendations": m.total_recommendations,
                        "recommendation_hit_rate": m.recommendation_hit_rate,
                        "average_ev": m.average_ev,
                        "clv_trend": m.clv_trend,
                        "prop_volume": m.prop_volume,
                        "user_confidence_score": m.user_confidence_score,
                        "api_response_time_ms": m.api_response_time_ms,
                        "error_rate": m.error_rate,
                        "throughput": m.throughput,
                        "cpu_usage": m.cpu_usage,
                        "memory_usage": m.memory_usage,
                        "disk_usage": m.disk_usage
                    }
                    for m in metrics
                ]
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to get business metrics trends: {e}")
            return []
    
    async def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old data based on retention policies."""
        if not self._cleanup_enabled:
            return {"status": "disabled", "cleaned": 0}
        
        cleanup_results = {}
        total_cleaned = 0
        
        try:
            async with self.session_maker() as db:
                now = datetime.now(timezone.utc)
                
                # Clean up old decisions
                cutoff = now - timedelta(days=self._retention_days["decisions"])
                result = await db.execute(
                    delete(BrainDecision).where(BrainDecision.timestamp < cutoff)
                )
                decisions_cleaned = result.rowcount
                cleanup_results["decisions"] = decisions_cleaned
                total_cleaned += decisions_cleaned
                
                # Clean up old health checks
                cutoff = now - timedelta(days=self._retention_days["health_checks"])
                result = await db.execute(
                    delete(BrainHealthCheck).where(BrainHealthCheck.timestamp < cutoff)
                )
                health_cleaned = result.rowcount
                cleanup_results["health_checks"] = health_cleaned
                total_cleaned += health_cleaned
                
                # Clean up old healing actions
                cutoff = now - timedelta(days=self._retention_days["healing_actions"])
                result = await db.execute(
                    delete(BrainHealingAction).where(BrainHealingAction.timestamp < cutoff)
                )
                healing_cleaned = result.rowcount
                cleanup_results["healing_actions"] = healing_cleaned
                total_cleaned += healing_cleaned
                
                # Clean up old anomalies (keep resolved ones longer)
                cutoff = now - timedelta(days=self._retention_days["anomalies"])
                result = await db.execute(
                    delete(BrainAnomaly).where(
                        and_(
                            BrainAnomaly.timestamp < cutoff,
                            BrainAnomaly.status != "active"
                        )
                    )
                )
                anomalies_cleaned = result.rowcount
                cleanup_results["anomalies"] = anomalies_cleaned
                total_cleaned += anomalies_cleaned
                
                # Clean up old correlations
                cutoff = now - timedelta(days=self._retention_days["correlations"])
                result = await db.execute(
                    delete(BrainCorrelation).where(BrainCorrelation.started_at < cutoff)
                )
                correlations_cleaned = result.rowcount
                cleanup_results["correlations"] = correlations_cleaned
                total_cleaned += correlations_cleaned
                
                # Clean up very old business metrics (keep 1 year)
                cutoff = now - timedelta(days=self._retention_days["metrics"])
                result = await db.execute(
                    delete(BrainBusinessMetrics).where(BrainBusinessMetrics.timestamp < cutoff)
                )
                metrics_cleaned = result.rowcount
                cleanup_results["business_metrics"] = metrics_cleaned
                total_cleaned += metrics_cleaned
                
                await db.commit()
                
                logger.info(f"[BRAIN:PERSIST] Cleanup completed: {total_cleaned} records removed")
                cleanup_results["total_cleaned"] = total_cleaned
                cleanup_results["status"] = "success"
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Cleanup failed: {e}")
            cleanup_results["status"] = "error"
            cleanup_results["error"] = str(e)
        
        return cleanup_results
    
    async def get_system_state_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system state history."""
        try:
            async with self.session_maker() as db:
                result = await db.execute(
                    select(BrainSystemState)
                    .order_by(BrainSystemState.timestamp.desc())
                    .limit(limit)
                )
                
                states = result.scalars().all()
                
                return [
                    {
                        "id": s.id,
                        "timestamp": s.timestamp.isoformat(),
                        "cycle_count": s.cycle_count,
                        "overall_status": s.overall_status,
                        "heals_attempted": s.heals_attempted,
                        "heals_succeeded": s.heals_succeeded,
                        "consecutive_failures": s.consecutive_failures,
                        "sport_priority": s.sport_priority,
                        "quota_budget": s.quota_budget,
                        "auto_commit_enabled": s.auto_commit_enabled,
                        "git_commits_made": s.git_commits_made,
                        "betting_opportunities_found": s.betting_opportunities_found,
                        "strong_bets_identified": s.strong_bets_identified,
                        "last_betting_scan": s.last_betting_scan.isoformat() if s.last_betting_scan else None,
                        "top_betting_opportunities": s.top_betting_opportunities,
                        "last_cycle_duration_ms": s.last_cycle_duration_ms,
                        "uptime_hours": s.uptime_hours
                    }
                    for s in states
                ]
                
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Failed to get system state history: {e}")
            return []


# Global persistence service instance
brain_persistence = BrainPersistenceService()
