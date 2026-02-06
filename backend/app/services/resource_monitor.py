"""
Resource Monitor - Track resource usage and optimize for Railway credit usage.

This module provides:
- Real-time resource usage monitoring
- Credit usage estimation and alerts
- Performance baseline tracking
- Resource optimization recommendations
- Cost control and budget management
"""

import logging
import asyncio
import time
import psutil
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class ResourceMetrics:
    """Resource usage metrics."""
    timestamp: str
    memory_usage_mb: float
    memory_percent: float
    cpu_percent: float
    disk_usage_mb: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    thread_count: int
    open_files: int
    gc_collections: int
    gc_uncollectable: int

@dataclass
class CreditEstimate:
    """Railway credit usage estimate."""
    monthly_budget: float = 5.0  # $5/month
    daily_budget: float = 0.167   # $5/30 days
    hourly_budget: float = 0.007  # $5/30/24 hours
    current_usage: float = 0.0
    projected_usage: float = 0.0
    remaining_budget: float = 5.0
    days_remaining: int = 30
    cost_per_hour: float = 0.007
    within_budget: bool = True

class ResourceMonitor:
    """Monitor and optimize resource usage for Railway credit management."""
    
    def __init__(self):
        self.metrics_history: List[ResourceMetrics] = []
        self.baseline_metrics: Optional[ResourceMetrics] = None
        self.credit_estimate = CreditEstimate()
        self.monitoring_active = False
        self.start_time = datetime.now(timezone.utc)
        self.last_network_check = 0
        
    def get_current_metrics(self) -> ResourceMetrics:
        """Get current system resource metrics."""
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage_mb = memory.used / 1024 / 1024
            memory_percent = memory.percent
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_mb = disk.used / 1024 / 1024
            disk_percent = disk.percent
            
            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # Process metrics
            process = psutil.Process()
            process_count = len(psutil.pids())
            thread_count = process.num_threads()
            open_files = process.num_fds() if hasattr(process, 'num_fds') else 0
            
            # Garbage collection metrics
            import gc
            gc_stats = gc.get_stats()
            gc_collections = sum(stat.get('collections', 0) for stat in gc_stats)
            gc_uncollectable = sum(stat.get('uncollectable', 0) for stat in gc_stats)
            
            return ResourceMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                memory_usage_mb=memory_usage_mb,
                memory_percent=memory_percent,
                cpu_percent=cpu_percent,
                disk_usage_mb=disk_usage_mb,
                disk_percent=disk_percent,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                process_count=process_count,
                thread_count=thread_count,
                open_files=open_files,
                gc_collections=gc_collections,
                gc_uncollectable=gc_uncollectable
            )
            
        except Exception as e:
            logger.error(f"Failed to get resource metrics: {e}")
            return ResourceMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                memory_usage_mb=0.0,
                memory_percent=0.0,
                cpu_percent=0.0,
                disk_usage_mb=0.0,
                disk_percent=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                process_count=0,
                thread_count=0,
                open_files=0,
                gc_collections=0,
                gc_uncollectable=0
            )
    
    def estimate_credit_usage(self) -> CreditEstimate:
        """Estimate Railway credit usage based on resource consumption."""
        try:
            # Railway pricing (approximate)
            # Hobby tier: $5/month for 512MB RAM, 0.25 CPU
            # Production tier: ~$0.01/hour per 512MB RAM
            
            current_metrics = self.get_current_metrics()
            
            # Calculate hourly cost based on memory usage
            memory_mb = current_metrics.memory_usage_mb
            if memory_mb <= 512:
                hourly_cost = 0.007  # $5/month / 720 hours
            elif memory_mb <= 1024:
                hourly_cost = 0.014  # Double for 1GB
            else:
                hourly_cost = 0.021  # Triple for >1GB
            
            # Calculate usage since start
            hours_running = (datetime.now(timezone.utc) - self.start_time).total_seconds() / 3600
            current_usage = hours_running * hourly_cost
            
            # Project monthly usage
            daily_usage = hourly_cost * 24
            projected_usage = daily_usage * 30
            
            # Calculate remaining budget
            remaining_budget = self.credit_estimate.monthly_budget - current_usage
            
            # Check if within budget
            within_budget = remaining_budget > 0 and projected_usage <= self.credit_estimate.monthly_budget
            
            self.credit_estimate = CreditEstimate(
                monthly_budget=self.credit_estimate.monthly_budget,
                daily_budget=self.credit_estimate.daily_budget,
                hourly_budget=self.credit_estimate.hourly_budget,
                current_usage=current_usage,
                projected_usage=projected_usage,
                remaining_budget=remaining_budget,
                days_remaining=int(remaining_budget / daily_usage) if daily_usage > 0 else 30,
                cost_per_hour=hourly_cost,
                within_budget=within_budget
            )
            
            return self.credit_estimate
            
        except Exception as e:
            logger.error(f"Failed to estimate credit usage: {e}")
            return self.credit_estimate
    
    def optimize_resource_usage(self) -> Dict[str, Any]:
        """Provide resource optimization recommendations."""
        try:
            current_metrics = self.get_current_metrics()
            recommendations = []
            
            # Memory optimization
            if current_metrics.memory_usage_mb > 400:
                recommendations.append({
                    "type": "memory",
                    "severity": "warning",
                    "message": f"High memory usage: {current_metrics.memory_usage_mb:.1f}MB",
                    "action": "Consider enabling aggressive garbage collection"
                })
            
            if current_metrics.memory_usage_mb > 500:
                recommendations.append({
                    "type": "memory",
                    "severity": "critical",
                    "message": f"Critical memory usage: {current_metrics.memory_usage_mb:.1f}MB",
                    "action": "Immediate memory cleanup required"
                })
            
            # CPU optimization
            if current_metrics.cpu_percent > 80:
                recommendations.append({
                    "type": "cpu",
                    "severity": "warning",
                    "message": f"High CPU usage: {current_metrics.cpu_percent:.1f}%",
                    "action": "Consider optimizing background tasks"
                })
            
            # Process optimization
            if current_metrics.process_count > 50:
                recommendations.append({
                    "type": "process",
                    "severity": "info",
                    "message": f"High process count: {current_metrics.process_count}",
                    "action": "Review process cleanup"
                })
            
            # GC optimization
            if current_metrics.gc_uncollectable > 100:
                recommendations.append({
                    "type": "memory_leak",
                    "severity": "critical",
                    "message": f"High uncollectable objects: {current_metrics.gc_uncollectable}",
                    "action": "Investigate memory leaks"
                })
            
            # Credit optimization
            credit_estimate = self.estimate_credit_usage()
            if not credit_estimate.within_budget:
                recommendations.append({
                    "type": "credit",
                    "severity": "critical",
                    "message": f"Over budget: ${credit_estimate.projected_usage:.2f} projected vs ${credit_estimate.monthly_budget:.2f} budget",
                    "action": "Reduce resource usage or upgrade plan"
                })
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "current_metrics": asdict(current_metrics),
                "credit_estimate": asdict(credit_estimate),
                "recommendations": recommendations,
                "optimization_score": self._calculate_optimization_score(current_metrics, credit_estimate)
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize resource usage: {e}")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "recommendations": []
            }
    
    def _calculate_optimization_score(self, metrics: ResourceMetrics, credit: CreditEstimate) -> float:
        """Calculate resource optimization score (0-100)."""
        try:
            score = 100.0
            
            # Memory score (40% weight)
            if metrics.memory_usage_mb <= 256:
                memory_score = 100.0
            elif metrics.memory_usage_mb <= 384:
                memory_score = 80.0
            elif metrics.memory_usage_mb <= 512:
                memory_score = 60.0
            else:
                memory_score = max(0, 40.0 - (metrics.memory_usage_mb - 512) / 10)
            
            # CPU score (30% weight)
            if metrics.cpu_percent <= 25:
                cpu_score = 100.0
            elif metrics.cpu_percent <= 50:
                cpu_score = 80.0
            elif metrics.cpu_percent <= 75:
                cpu_score = 60.0
            else:
                cpu_score = max(0, 40.0 - (metrics.cpu_percent - 75) / 2)
            
            # Credit score (30% weight)
            credit_score = 100.0 if credit.within_budget else max(0, 50.0 - credit.projected_usage * 10)
            
            # Weighted average
            total_score = (memory_score * 0.4) + (cpu_score * 0.3) + (credit_score * 0.3)
            
            return round(total_score, 1)
            
        except Exception as e:
            logger.error(f"Failed to calculate optimization score: {e}")
            return 0.0
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous resource monitoring."""
        try:
            self.monitoring_active = True
            logger.info(f"[RESOURCE] Starting resource monitoring with {interval_seconds}s interval")
            
            # Set baseline
            self.baseline_metrics = self.get_current_metrics()
            logger.info(f"[RESOURCE] Baseline metrics: {self.baseline_metrics.memory_usage_mb:.1f}MB RAM, {self.baseline_metrics.cpu_percent:.1f}% CPU")
            
            while self.monitoring_active:
                try:
                    # Get current metrics
                    current_metrics = self.get_current_metrics()
                    self.metrics_history.append(current_metrics)
                    
                    # Keep only last 1000 metrics
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                    
                    # Check for alerts
                    await self._check_resource_alerts(current_metrics)
                    
                    # Update credit estimate
                    self.estimate_credit_usage()
                    
                    # Log if significant changes
                    if self.baseline_metrics:
                        memory_change = current_metrics.memory_usage_mb - self.baseline_metrics.memory_usage_mb
                        cpu_change = current_metrics.cpu_percent - self.baseline_metrics.cpu_percent
                        
                        if abs(memory_change) > 50 or abs(cpu_change) > 20:
                            logger.info(f"[RESOURCE] Significant change: RAM {memory_change:+.1f}MB, CPU {cpu_change:+.1f}%")
                    
                    await asyncio.sleep(interval_seconds)
                    
                except Exception as e:
                    logger.error(f"[RESOURCE] Monitoring loop error: {e}")
                    await asyncio.sleep(interval_seconds)
                    
        except Exception as e:
            logger.error(f"[RESOURCE] Failed to start monitoring: {e}")
            self.monitoring_active = False
    
    async def _check_resource_alerts(self, metrics: ResourceMetrics):
        """Check for resource usage alerts."""
        try:
            # Memory alerts
            if metrics.memory_usage_mb > 500:
                logger.warning(f"[RESOURCE] High memory usage: {metrics.memory_usage_mb:.1f}MB")
            
            if metrics.memory_usage_mb > 600:
                logger.critical(f"[RESOURCE] Critical memory usage: {metrics.memory_usage_mb:.1f}MB")
            
            # CPU alerts
            if metrics.cpu_percent > 80:
                logger.warning(f"[RESOURCE] High CPU usage: {metrics.cpu_percent:.1f}%")
            
            # GC alerts
            if metrics.gc_uncollectable > 100:
                logger.warning(f"[RESOURCE] High uncollectable objects: {metrics.gc_uncollectable}")
            
            # Credit alerts
            if not self.credit_estimate.within_budget:
                logger.warning(f"[RESOURCE] Over budget: ${self.credit_estimate.projected_usage:.2f} projected")
            
        except Exception as e:
            logger.error(f"[RESOURCE] Alert check failed: {e}")
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring_active = False
        logger.info("[RESOURCE] Resource monitoring stopped")
    
    def get_performance_baseline(self) -> Dict[str, Any]:
        """Get performance baseline statistics."""
        try:
            if not self.metrics_history:
                return {"error": "No metrics history available"}
            
            # Calculate statistics
            memory_values = [m.memory_usage_mb for m in self.metrics_history]
            cpu_values = [m.cpu_percent for m in self.metrics_history]
            
            baseline = {
                "baseline_metrics": asdict(self.baseline_metrics) if self.baseline_metrics else None,
                "current_metrics": asdict(self.metrics_history[-1]) if self.metrics_history else None,
                "statistics": {
                    "memory": {
                        "min": min(memory_values),
                        "max": max(memory_values),
                        "avg": sum(memory_values) / len(memory_values),
                        "current": memory_values[-1] if memory_values else 0
                    },
                    "cpu": {
                        "min": min(cpu_values),
                        "max": max(cpu_values),
                        "avg": sum(cpu_values) / len(cpu_values),
                        "current": cpu_values[-1] if cpu_values else 0
                    }
                },
                "credit_estimate": asdict(self.credit_estimate),
                "monitoring_duration": str(datetime.now(timezone.utc) - self.start_time),
                "total_samples": len(self.metrics_history)
            }
            
            return baseline
            
        except Exception as e:
            logger.error(f"Failed to get performance baseline: {e}")
            return {"error": str(e)}
    
    def export_metrics(self) -> str:
        """Export metrics history as JSON."""
        try:
            export_data = {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "baseline": asdict(self.baseline_metrics) if self.baseline_metrics else None,
                "credit_estimate": asdict(self.credit_estimate),
                "metrics_history": [asdict(m) for m in self.metrics_history],
                "monitoring_duration": str(datetime.now(timezone.utc) - self.start_time)
            }
            
            return json.dumps(export_data, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return json.dumps({"error": str(e)})

# Global resource monitor instance
resource_monitor = ResourceMonitor()
