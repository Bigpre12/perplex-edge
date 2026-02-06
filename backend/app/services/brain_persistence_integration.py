"""
Brain Persistence Integration - Additional functions for brain persistence.

Provides additional persistence functions that can be integrated into the brain loop
without modifying the existing brain.py file extensively.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from app.services.brain_persistence import brain_persistence

logger = logging.getLogger(__name__)


async def persist_health_checks(checks: list) -> bool:
    """Persist health checks to PostgreSQL."""
    try:
        for check in checks:
            await brain_persistence.log_health_check(
                component=check.component,
                status=check.status,
                message=check.message,
                details=check.details,
                response_time_ms=getattr(check, 'response_time_ms', 0),
                error_count=getattr(check, 'error_count', 0)
            )
        return True
    except Exception as e:
        logger.warning(f"[BRAIN:PERSIST] Failed to persist health checks: {e}")
        return False


async def persist_healing_action(
    action: str,
    target: str,
    reason: str,
    result: str,
    duration_ms: int = 0,
    details: Optional[Dict[str, Any]] = None
) -> bool:
    """Persist a healing action to PostgreSQL."""
    try:
        await brain_persistence.log_healing_action(
            action=action,
            target=target,
            reason=reason,
            result=result,
            duration_ms=duration_ms,
            details=details or {}
        )
        return True
    except Exception as e:
        logger.warning(f"[BRAIN:PERSIST] Failed to persist healing action: {e}")
        return False


async def persist_business_metrics(metrics: Dict[str, Any]) -> bool:
    """Persist business metrics to PostgreSQL."""
    try:
        await brain_persistence.log_business_metrics(metrics)
        return True
    except Exception as e:
        logger.warning(f"[BRAIN:PERSIST] Failed to persist business metrics: {e}")
        return False


async def persist_system_state(state_data: Dict[str, Any]) -> bool:
    """Persist system state to PostgreSQL."""
    try:
        await brain_persistence.save_system_state(state_data)
        return True
    except Exception as e:
        logger.warning(f"[BRAIN:PERSIST] Failed to persist system state: {e}")
        return False


async def persist_anomaly(
    metric_name: str,
    baseline_value: float,
    current_value: float,
    change_pct: float,
    severity: str,
    details: Optional[Dict[str, Any]] = None
) -> bool:
    """Persist an anomaly to PostgreSQL."""
    try:
        await brain_persistence.log_anomaly(
            metric_name=metric_name,
            baseline_value=baseline_value,
            current_value=current_value,
            change_pct=change_pct,
            severity=severity,
            details=details or {}
        )
        return True
    except Exception as e:
        logger.warning(f"[BRAIN:PERSIST] Failed to persist anomaly: {e}")
        return False


async def load_previous_system_state() -> Optional[Dict[str, Any]]:
    """Load previous system state from PostgreSQL."""
    try:
        state_history = await brain_persistence.get_system_state_history(limit=1)
        if state_history:
            return state_history[0]
        return None
    except Exception as e:
        logger.warning(f"[BRAIN:PERSIST] Could not load previous state: {e}")
        return None


async def periodic_cleanup(interval_hours: int = 24) -> None:
    """Run periodic cleanup of old brain data."""
    while True:
        try:
            await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
            
            logger.info("[BRAIN:PERSIST] Starting periodic cleanup...")
            cleanup_results = await brain_persistence.cleanup_old_data()
            
            if cleanup_results.get("status") == "success":
                total_cleaned = cleanup_results.get("total_cleaned", 0)
                logger.info(f"[BRAIN:PERSIST] Cleanup completed: {total_cleaned} records removed")
                
                # Log cleanup as a decision
                try:
                    await brain_persistence.log_decision(
                        category="maintenance",
                        action="periodic_cleanup",
                        reasoning=f"Routine cleanup of old brain data",
                        outcome="success",
                        details=cleanup_results
                    )
                except Exception as e:
                    logger.warning(f"[BRAIN:PERSIST] Failed to log cleanup decision: {e}")
            else:
                logger.error(f"[BRAIN:PERSIST] Cleanup failed: {cleanup_results.get('error', 'Unknown error')}")
                
        except asyncio.CancelledError:
            logger.info("[BRAIN:PERSIST] Cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"[BRAIN:PERSIST] Cleanup task error: {e}")
            # Continue running even if cleanup fails


# Integration helper functions
def create_persistence_enabled_brain_state():
    """Create a brain state that automatically persists decisions."""
    from app.services.brain import BrainState
    
    class PersistentBrainState(BrainState):
        def log_decision(
            self,
            category: str,
            action: str,
            reasoning: str,
            outcome: str,
            details: dict | None = None,
        ):
            # Call parent method
            super().log_decision(category, action, reasoning, outcome, details)
            
            # Persist to PostgreSQL asynchronously
            try:
                asyncio.create_task(
                    brain_persistence.log_decision(
                        category=category,
                        action=action,
                        reasoning=reasoning,
                        outcome=outcome,
                        details=details or {}
                    )
                )
            except Exception as e:
                logger.warning(f"[BRAIN:PERSIST] Failed to persist decision: {e}")
    
    return PersistentBrainState()


# Brain analytics functions
async def get_brain_analytics(hours: int = 24) -> Dict[str, Any]:
    """Get comprehensive brain analytics for the specified time period."""
    try:
        # Get recent decisions
        decisions = await brain_persistence.get_recent_decisions(limit=100)
        
        # Get health trends
        health_trends = await brain_persistence.get_health_trends(hours=hours)
        
        # Get anomaly summary
        anomaly_summary = await brain_persistence.get_anomaly_summary(hours=hours)
        
        # Get business metrics trends
        metrics_trends = await brain_persistence.get_business_metrics_trends(hours=hours)
        
        # Get system state history
        state_history = await brain_persistence.get_system_state_history(limit=10)
        
        # Analyze decision patterns
        decision_categories = {}
        decision_outcomes = {}
        for decision in decisions:
            category = decision.get("category", "unknown")
            outcome = decision.get("outcome", "unknown")
            
            decision_categories[category] = decision_categories.get(category, 0) + 1
            decision_outcomes[outcome] = decision_outcomes.get(outcome, 0) + 1
        
        # Analyze health patterns
        health_status_counts = {}
        component_health = {}
        for health in health_trends:
            status = health.get("status", "unknown")
            component = health.get("component", "unknown")
            
            health_status_counts[status] = health_status_counts.get(status, 0) + 1
            
            if component not in component_health:
                component_health[component] = {"healthy": 0, "degraded": 0, "critical": 0}
            component_health[component][status] = component_health[component].get(status, 0) + 1
        
        return {
            "period_hours": hours,
            "decision_summary": {
                "total_decisions": len(decisions),
                "categories": decision_categories,
                "outcomes": decision_outcomes,
                "success_rate": decision_outcomes.get("success", 0) / len(decisions) if decisions else 0
            },
            "health_summary": {
                "total_checks": len(health_trends),
                "status_distribution": health_status_counts,
                "component_health": component_health,
                "overall_health_score": health_status_counts.get("healthy", 0) / len(health_trends) if health_trends else 0
            },
            "anomaly_summary": anomaly_summary,
            "metrics_trends": {
                "latest_metrics": metrics_trends[0] if metrics_trends else None,
                "trend_count": len(metrics_trends),
                "avg_hit_rate": sum(m.get("recommendation_hit_rate", 0) for m in metrics_trends) / len(metrics_trends) if metrics_trends else 0,
                "avg_ev": sum(m.get("average_ev", 0) for m in metrics_trends) / len(metrics_trends) if metrics_trends else 0
            },
            "system_state_history": state_history,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"[BRAIN:PERSIST] Failed to generate analytics: {e}")
        return {
            "period_hours": hours,
            "error": str(e),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }


# Brain performance monitoring
async def monitor_brain_performance() -> Dict[str, Any]:
    """Monitor brain performance and return metrics."""
    try:
        # Get recent system states
        recent_states = await brain_persistence.get_system_state_history(limit=10)
        
        if not recent_states:
            return {"status": "no_data", "message": "No system state data available"}
        
        # Calculate performance metrics
        latest_state = recent_states[0]
        
        # Cycle performance
        cycle_durations = [s.get("last_cycle_duration_ms", 0) for s in recent_states if s.get("last_cycle_duration_ms")]
        avg_cycle_duration = sum(cycle_durations) / len(cycle_durations) if cycle_durations else 0
        
        # Healing effectiveness
        healing_rates = []
        for state in recent_states:
            attempted = state.get("heals_attempted", 0)
            succeeded = state.get("heals_succeeded", 0)
            if attempted > 0:
                healing_rates.append(succeeded / attempted)
        
        avg_healing_rate = sum(healing_rates) / len(healing_rates) if healing_rates else 0
        
        # System stability
        status_changes = []
        for i in range(1, len(recent_states)):
            if recent_states[i].get("overall_status") != recent_states[i-1].get("overall_status"):
                status_changes.append(recent_states[i].get("overall_status"))
        
        stability_score = 1.0 - (len(status_changes) / len(recent_states)) if recent_states else 0
        
        return {
            "status": "healthy",
            "uptime_hours": latest_state.get("uptime_hours", 0),
            "total_cycles": latest_state.get("cycle_count", 0),
            "current_status": latest_state.get("overall_status", "unknown"),
            "performance_metrics": {
                "avg_cycle_duration_ms": round(avg_cycle_duration, 2),
                "avg_healing_rate": round(avg_healing_rate, 3),
                "stability_score": round(stability_score, 3),
                "total_heals_attempted": latest_state.get("heals_attempted", 0),
                "total_heals_succeeded": latest_state.get("heals_succeeded", 0),
                "git_commits_made": latest_state.get("git_commits_made", 0)
            },
            "recent_activity": {
                "status_changes": len(status_changes),
                "last_cycle_at": latest_state.get("timestamp"),
                "betting_opportunities": latest_state.get("betting_opportunities_found", 0),
                "strong_bets": latest_state.get("strong_bets_identified", 0)
            },
            "monitored_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"[BRAIN:PERSIST] Failed to monitor brain performance: {e}")
        return {
            "status": "error",
            "error": str(e),
            "monitored_at": datetime.now(timezone.utc).isoformat()
        }
