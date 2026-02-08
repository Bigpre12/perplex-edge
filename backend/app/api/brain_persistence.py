"""
Brain Persistence API Endpoints - REST API for brain persistence data.

Provides endpoints to access brain decisions, health checks, healing actions,
and analytics data stored in PostgreSQL.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.brain_persistence import brain_persistence
from app.services.brain_persistence_integration import(get_brain_analytics,
 monitor_brain_performance,
 periodic_cleanup)

logger = logging.getLogger(__name__)

router = APIRouter(prefix = " / api / brain", tags = ["brain - persistence"])

@router.get(" / decisions")
async def get_brain_decisions(limit: int = Query(50, ge = 1, le = 500),
 category: Optional[str] = Query(None),
 hours: int = Query(24, ge = 1, le = 168) # 1 week max) - > Dict[str, Any]:
 """Get recent brain decisions with optional filtering."""
 try:
 decisions = await brain_persistence.get_recent_decisions(limit = limit, category = category)

 # Filter by time if specified
 if hours < 168: # Only filter if less than max
 cutoff = datetime.now(timezone.utc) - timedelta(hours = hours)
 decisions = [
 d for d in decisions
 if datetime.fromisoformat(d["timestamp"].replace('Z', ' + 00:00')) > = cutoff
 ]

 return {
 "status": "success",
 "decisions": decisions,
 "count": len(decisions),
 "filters": {"limit": limit, "category": category, "hours": hours}
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get decisions: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get brain decisions: {str(e)}")

@router.get(" / health - trends")
async def get_health_trends(component: Optional[str] = Query(None),
 hours: int = Query(24, ge = 1, le = 168)) - > Dict[str, Any]:
 """Get health check trends for analysis."""
 try:
 trends = await brain_persistence.get_health_trends(component = component, hours = hours)

 return {
 "status": "success",
 "trends": trends,
 "count": len(trends),
 "filters": {"component": component, "hours": hours}
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get health trends: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get health trends: {str(e)}")

@router.get(" / anomalies")
async def get_anomaly_summary(hours: int = Query(24, ge = 1, le = 168)) - > Dict[str, Any]:
 """Get anomaly summary for the specified time period."""
 try:
 summary = await brain_persistence.get_anomaly_summary(hours = hours)

 return {
 "status": "success",
 "summary": summary
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get anomaly summary: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get anomaly summary: {str(e)}")

@router.get(" / business - metrics")
async def get_business_metrics_trends(hours: int = Query(24, ge = 1, le = 168)) - > Dict[str, Any]:
 """Get business metrics trends."""
 try:
 trends = await brain_persistence.get_business_metrics_trends(hours = hours)

 return {
 "status": "success",
 "trends": trends,
 "count": len(trends),
 "filters": {"hours": hours}
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get business metrics: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get business metrics: {str(e)}")

@router.get(" / system - state")
async def get_system_state_history(limit: int = Query(10, ge = 1, le = 100)) - > Dict[str, Any]:
 """Get recent system state history."""
 try:
 history = await brain_persistence.get_system_state_history(limit = limit)

 return {
 "status": "success",
 "history": history,
 "count": len(history)
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get system state history: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get system state history: {str(e)}")

@router.get(" / analytics")
async def get_brain_analytics_endpoint(hours: int = Query(24, ge = 1, le = 168)) - > Dict[str, Any]:
 """Get comprehensive brain analytics."""
 try:
 analytics = await get_brain_analytics(hours = hours)

 return {
 "status": "success",
 "analytics": analytics
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get brain analytics: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get brain analytics: {str(e)}")

@router.get(" / performance")
async def get_brain_performance() - > Dict[str, Any]:
 """Monitor brain performance metrics."""
 try:
 performance = await monitor_brain_performance()

 return {
 "status": "success",
 "performance": performance
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get brain performance: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get brain performance: {str(e)}")

@router.post(" / cleanup")
async def trigger_cleanup() - > Dict[str, Any]:
 """Trigger manual cleanup of old brain data."""
 try:
 results = await brain_persistence.cleanup_old_data()

 return {
 "status": "success",
 "cleanup_results": results,
 "triggered_at": datetime.now(timezone.utc).isoformat()
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to trigger cleanup: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to trigger cleanup: {str(e)}")

@router.get(" / correlations")
async def get_correlation_summary() - > Dict[str, Any]:
 """Get summary of recent correlations."""
 try:
 # This would need to be implemented in brain_persistence
 # For now, return a placeholder
 return {
 "status": "success",
 "message": "Correlation summary not yet implemented",
 "placeholder": True
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get correlation summary: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get correlation summary: {str(e)}")

@router.get(" / learning")
async def get_learning_data(hours: int = Query(24, ge = 1, le = 168)) - > Dict[str, Any]:
 """Get brain learning data."""
 try:
 # This would need to be implemented in brain_persistence
 # For now, return a placeholder
 return {
 "status": "success",
 "message": "Learning data not yet implemented",
 "placeholder": True,
 "filters": {"hours": hours}
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get learning data: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get learning data: {str(e)}")

@router.get(" / dashboard")
async def get_brain_dashboard(hours: int = Query(24, ge = 1, le = 168)) - > Dict[str, Any]:
 """Get comprehensive brain dashboard data."""
 try:
 # Get all the data needed for a dashboard
 analytics = await get_brain_analytics(hours = hours)
 performance = await monitor_brain_performance()
 anomalies = await brain_persistence.get_anomaly_summary(hours = hours)
 recent_decisions = await brain_persistence.get_recent_decisions(limit = 20)
 health_trends = await brain_persistence.get_health_trends(hours = hours)

 return {
 "status": "success",
 "dashboard": {
 "analytics": analytics,
 "performance": performance,
 "anomaly_summary": anomalies,
 "recent_decisions": recent_decisions[:10], # Top 10
 "health_summary": {
 "total_checks": len(health_trends),
 "healthy": len([h for h in health_trends if h.get("status") =  = "healthy"]),
 "degraded": len([h for h in health_trends if h.get("status") =  = "degraded"]),
 "critical": len([h for h in health_trends if h.get("status") =  = "critical"])
 },
 "generated_at": datetime.now(timezone.utc).isoformat()
 }
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get brain dashboard: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get brain dashboard: {str(e)}")

@router.get(" / export")
async def export_brain_data(data_type: str = Query(..., pattern = "^(decisions|health|anomalies|metrics|state)$"),
 hours: int = Query(24, ge = 1, le = 168),
 format: str = Query("json", pattern = "^(json|csv)$")) - > Dict[str, Any]:
 """Export brain data in specified format."""
 try:
 # Get data based on type
 if data_type =  = "decisions":
 data = await brain_persistence.get_recent_decisions(limit = 1000)
 elif data_type =  = "health":
 data = await brain_persistence.get_health_trends(hours = hours)
 elif data_type =  = "anomalies":
 summary = await brain_persistence.get_anomaly_summary(hours = hours)
 data = summary.get("active_anomalies", [])
 elif data_type =  = "metrics":
 data = await brain_persistence.get_business_metrics_trends(hours = hours)
 elif data_type =  = "state":
 data = await brain_persistence.get_system_state_history(limit = 100)
 else:
 raise HTTPException(status_code = 400, detail = f"Invalid data_type: {data_type}")

 # Format data(JSON for now, CSV could be added later)
 if format =  = "json":
 return {
 "status": "success",
 "export": {
 "data_type": data_type,
 "format": format,
 "count": len(data),
 "data": data,
 "exported_at": datetime.now(timezone.utc).isoformat(),
 "filters": {"hours": hours}
 }
 }
 else:
 # CSV format would need additional implementation
 raise HTTPException(status_code = 400, detail = "CSV format not yet implemented")

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to export brain data: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to export brain data: {str(e)}")

@router.post(" / decision")
async def log_manual_decision(category: str,
 action: str,
 reasoning: str,
 outcome: str,
 details: Optional[Dict[str, Any]] = None,
 duration_ms: int = 0) - > Dict[str, Any]:
 """Manually log a brain decision."""
 try:
 decision_id = await brain_persistence.log_decision(category = category,
 action = action,
 reasoning = reasoning,
 outcome = outcome,
 details = details,
 duration_ms = duration_ms)

 return {
 "status": "success",
 "decision_id": decision_id,
 "logged_at": datetime.now(timezone.utc).isoformat()
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to log manual decision: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to log manual decision: {str(e)}")

@router.post(" / health - check")
async def log_manual_health_check(component: str,
 status: str,
 message: str,
 details: Optional[Dict[str, Any]] = None,
 response_time_ms: int = 0,
 error_count: int = 0) - > Dict[str, Any]:
 """Manually log a health check."""
 try:
 check_id = await brain_persistence.log_health_check(component = component,
 status = status,
 message = message,
 details = details,
 response_time_ms = response_time_ms,
 error_count = error_count)

 return {
 "status": "success",
 "check_id": check_id,
 "logged_at": datetime.now(timezone.utc).isoformat()
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to log manual health check: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to log manual health check: {str(e)}")

@router.get(" / stats")
async def get_brain_statistics(hours: int = Query(24, ge = 1, le = 168)) - > Dict[str, Any]:
 """Get brain statistics summary."""
 try:
 # Get all the data for statistics
 decisions = await brain_persistence.get_recent_decisions(limit = 1000)
 health_trends = await brain_persistence.get_health_trends(hours = hours)
 anomalies = await brain_persistence.get_anomaly_summary(hours = hours)
 metrics = await brain_persistence.get_business_metrics_trends(hours = hours)

 # Calculate statistics
 decision_stats = {
 "total": len(decisions),
 "by_category": {},
 "by_outcome": {},
 "success_rate": 0
 }

 for decision in decisions:
 category = decision.get("category", "unknown")
 outcome = decision.get("outcome", "unknown")

 decision_stats["by_category"][category] = decision_stats["by_category"].get(category, 0) + 1
 decision_stats["by_outcome"][outcome] = decision_stats["by_outcome"].get(outcome, 0) + 1

 if decisions:
 decision_stats["success_rate"] = decision_stats["by_outcome"].get("success", 0) / len(decisions)

 health_stats = {
 "total_checks": len(health_trends),
 "by_status": {},
 "by_component": {},
 "avg_response_time": 0
 }

 response_times = []
 for health in health_trends:
 status = health.get("status", "unknown")
 component = health.get("component", "unknown")
 response_time = health.get("response_time_ms", 0)

 health_stats["by_status"][status] = health_stats["by_status"].get(status, 0) + 1
 health_stats["by_component"][component] = health_stats["by_component"].get(component, 0) + 1
 response_times.append(response_time)

 if response_times:
 health_stats["avg_response_time"] = sum(response_times) / len(response_times)

 return {
 "status": "success",
 "statistics": {
 "period_hours": hours,
 "decisions": decision_stats,
 "health_checks": health_stats,
 "anomalies": {
 "total_anomalies": anomalies.get("total_anomalies", 0),
 "severity_counts": anomalies.get("severity_counts", {}),
 "active_count": len(anomalies.get("active_anomalies", []))
 },
 "business_metrics": {
 "data_points": len(metrics),
 "avg_hit_rate": sum(m.get("recommendation_hit_rate", 0) for m in metrics) / len(metrics) if metrics else 0,
 "avg_ev": sum(m.get("average_ev", 0) for m in metrics) / len(metrics) if metrics else 0
 }
 },
 "generated_at": datetime.now(timezone.utc).isoformat()
 }

 except Exception as e:
 logger.error(f"[API:BRAIN] Failed to get brain statistics: {e}")
 raise HTTPException(status_code = 500, detail = f"Failed to get brain statistics: {str(e)}")
