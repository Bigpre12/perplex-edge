"""
Brain Metrics API - Expose brain business metrics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from datetime import datetime, timezone, timedelta
import asyncio
from brain_metrics_service import get_current_metrics, get_metrics_summary, metrics_service

router = APIRouter()

@router.get("/brain-metrics")
async def get_brain_metrics():
    """Get current brain business metrics"""
    try:
        metrics = await get_current_metrics()
        
        if not metrics:
            return {
                "error": "No metrics available",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Format for display
        return {
            "timestamp": metrics.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "total_recommendations": metrics.get("total_recommendations", 0),
            "recommendation_hit_rate": metrics.get("recommendation_hit_rate", 0.0),
            "average_ev": metrics.get("average_ev", 0.0),
            "clv_trend": metrics.get("clv_trend", 0.0),
            "prop_volume": metrics.get("prop_volume", 0),
            "user_confidence_score": metrics.get("user_confidence_score", 0.0),
            "api_response_time_ms": metrics.get("api_response_time_ms", 0),
            "error_rate": metrics.get("error_rate", 0.0),
            "throughput": metrics.get("throughput", 0.0),
            "system_metrics": {
                "cpu_usage": metrics.get("cpu_usage", 0.0),
                "memory_usage": metrics.get("memory_usage", 0.0),
                "disk_usage": metrics.get("disk_usage", 0.0)
            }
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
        summary = await get_metrics_summary(hours)
        
        if not summary:
            return {
                "error": "No metrics available",
                "period_hours": hours,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "period_hours": summary["period_hours"],
            "total_records": summary["total_records"],
            "total_recommendations": summary["total_recommendations"],
            "average_hit_rate": summary["average_hit_rate"],
            "average_ev": summary["average_ev"],
            "max_hit_rate": summary["max_hit_rate"],
            "min_hit_rate": summary["min_hit_rate"],
            "latest_metrics": {
                "timestamp": summary["latest_metrics"].get("timestamp"),
                "total_recommendations": summary["latest_metrics"].get("total_recommendations"),
                "hit_rate": summary["latest_metrics"].get("recommendation_hit_rate"),
                "average_ev": summary["latest_metrics"].get("average_ev"),
                "clv_trend": summary["latest_metrics"].get("clv_trend"),
                "prop_volume": summary["latest_metrics"].get("prop_volume"),
                "user_confidence": summary["latest_metrics"].get("user_confidence_score"),
                "api_response_time": summary["latest_metrics"].get("api_response_time_ms"),
                "error_rate": summary["latest_metrics"].get("error_rate"),
                "throughput": summary["latest_metrics"].get("throughput")
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "period_hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-dashboard")
async def get_brain_dashboard():
    """Get comprehensive brain dashboard data"""
    try:
        # Get current metrics
        current = await get_current_metrics()
        
        # Get summaries for different time periods
        summary_24h = await get_metrics_summary(24)
        summary_7d = await get_metrics_summary(168)  # 7 days
        
        return {
            "current_metrics": {
                "timestamp": current.get("timestamp"),
                "total_recommendations": current.get("total_recommendations", 0),
                "hit_rate": current.get("recommendation_hit_rate", 0.0),
                "average_ev": current.get("average_ev", 0.0),
                "clv_trend": current.get("clv_trend", 0.0),
                "prop_volume": current.get("prop_volume", 0),
                "user_confidence": current.get("user_confidence_score", 0.0),
                "api_response_time": current.get("api_response_time_ms", 0),
                "error_rate": current.get("error_rate", 0.0),
                "throughput": current.get("throughput", 0.0),
                "system": {
                    "cpu_usage": current.get("cpu_usage", 0.0),
                    "memory_usage": current.get("memory_usage", 0.0),
                    "disk_usage": current.get("disk_usage", 0.0)
                }
            },
            "summaries": {
                "last_24_hours": {
                    "total_recommendations": summary_24h.get("total_recommendations", 0),
                    "average_hit_rate": summary_24h.get("average_hit_rate", 0.0),
                    "average_ev": summary_24h.get("average_ev", 0.0),
                    "max_hit_rate": summary_24h.get("max_hit_rate", 0.0),
                    "min_hit_rate": summary_24h.get("min_hit_rate", 0.0)
                },
                "last_7_days": {
                    "total_recommendations": summary_7d.get("total_recommendations", 0),
                    "average_hit_rate": summary_7d.get("average_hit_rate", 0.0),
                    "average_ev": summary_7d.get("average_ev", 0.0),
                    "max_hit_rate": summary_7d.get("max_hit_rate", 0.0),
                    "min_hit_rate": summary_7d.get("min_hit_rate", 0.0)
                }
            },
            "status": "healthy" if current else "no_data",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-metrics/start")
async def start_metrics_collection():
    """Start continuous metrics collection"""
    try:
        if not metrics_service.running:
            # Start in background
            asyncio.create_task(metrics_service.start_metrics_collection(300))  # Every 5 minutes
            return {
                "status": "started",
                "message": "Metrics collection started",
                "interval_seconds": 300,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "status": "already_running",
                "message": "Metrics collection is already running",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/brain-metrics/stop")
async def stop_metrics_collection():
    """Stop continuous metrics collection"""
    try:
        metrics_service.stop()
        return {
            "status": "stopped",
            "message": "Metrics collection stopped",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
