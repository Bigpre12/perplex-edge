"""
API Call Monitoring and Logging.

Tracks every external API call with:
- Endpoint, method, status code
- Latency (ms)
- Response counts (games, props, etc.)
- Error tracking (429s, 5xx, timeouts)

Provides metrics for:
- Error rate monitoring
- Latency trends
- Sudden count drops
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from collections import deque
from functools import wraps

logger = logging.getLogger(__name__)


# =============================================================================
# API Call Record
# =============================================================================

@dataclass
class APICallRecord:
    """Record of a single API call."""
    timestamp: datetime
    provider: str  # "odds_api", "espn", "balldontlie", etc.
    endpoint: str
    method: str
    status_code: int
    latency_ms: int
    success: bool
    response_count: int  # Number of items returned (games, props, etc.)
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "response_count": self.response_count,
            "error_message": self.error_message,
        }


# =============================================================================
# API Monitor (Singleton)
# =============================================================================

class APIMonitor:
    """
    Singleton monitor for tracking API calls across the application.
    
    Maintains a rolling window of recent calls for analysis.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Rolling window of recent calls (last 1000)
        self._calls: deque[APICallRecord] = deque(maxlen=1000)
        
        # Per-provider error counts (last hour)
        self._error_counts: dict[str, deque] = {}
        
        # Per-provider response counts for drop detection
        self._response_counts: dict[str, deque] = {}
        
        self._initialized = True
    
    def record_call(
        self,
        provider: str,
        endpoint: str,
        method: str,
        status_code: int,
        latency_ms: int,
        response_count: int = 0,
        error_message: Optional[str] = None,
    ) -> APICallRecord:
        """
        Record an API call.
        
        Automatically logs and tracks the call.
        """
        success = 200 <= status_code < 400
        
        record = APICallRecord(
            timestamp=datetime.now(timezone.utc),
            provider=provider,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            success=success,
            response_count=response_count,
            error_message=error_message,
        )
        
        # Add to rolling window
        self._calls.append(record)
        
        # Track errors per provider
        if provider not in self._error_counts:
            self._error_counts[provider] = deque(maxlen=100)
        if not success:
            self._error_counts[provider].append(record.timestamp)
        
        # Track response counts per provider
        if provider not in self._response_counts:
            self._response_counts[provider] = deque(maxlen=100)
        self._response_counts[provider].append((record.timestamp, response_count))
        
        # Log the call
        log_level = logging.INFO if success else logging.WARNING
        log_msg = (
            f"API {method} {provider}{endpoint} -> "
            f"{status_code} ({latency_ms}ms, {response_count} items)"
        )
        if error_message:
            log_msg += f" [{error_message}]"
        
        logger.log(log_level, log_msg)
        
        return record
    
    def get_recent_calls(
        self,
        provider: Optional[str] = None,
        minutes: int = 60,
    ) -> list[APICallRecord]:
        """Get recent API calls, optionally filtered by provider."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        calls = [c for c in self._calls if c.timestamp >= cutoff]
        
        if provider:
            calls = [c for c in calls if c.provider == provider]
        
        return calls
    
    def get_error_rate(
        self,
        provider: Optional[str] = None,
        minutes: int = 60,
    ) -> float:
        """Calculate error rate for recent calls."""
        calls = self.get_recent_calls(provider, minutes)
        
        if not calls:
            return 0.0
        
        errors = sum(1 for c in calls if not c.success)
        return errors / len(calls)
    
    def get_429_count(
        self,
        provider: Optional[str] = None,
        minutes: int = 60,
    ) -> int:
        """Count rate limit (429) errors."""
        calls = self.get_recent_calls(provider, minutes)
        return sum(1 for c in calls if c.status_code == 429)
    
    def get_avg_latency(
        self,
        provider: Optional[str] = None,
        minutes: int = 60,
    ) -> float:
        """Calculate average latency in ms."""
        calls = self.get_recent_calls(provider, minutes)
        
        if not calls:
            return 0.0
        
        return sum(c.latency_ms for c in calls) / len(calls)
    
    def check_count_drop(
        self,
        provider: str,
        current_count: int,
        threshold_pct: float = 0.5,
    ) -> Optional[dict]:
        """
        Check if current response count is significantly lower than recent average.
        
        Returns alert info if drop detected, None otherwise.
        """
        if provider not in self._response_counts:
            return None
        
        recent = list(self._response_counts[provider])
        if len(recent) < 3:
            return None
        
        # Get average of previous calls (excluding current)
        prev_counts = [count for _, count in recent[:-1] if count > 0]
        if not prev_counts:
            return None
        
        avg_count = sum(prev_counts) / len(prev_counts)
        
        if avg_count > 0 and current_count < avg_count * threshold_pct:
            drop_pct = (1 - current_count / avg_count) * 100
            return {
                "provider": provider,
                "current_count": current_count,
                "average_count": avg_count,
                "drop_percent": drop_pct,
            }
        
        return None
    
    def get_metrics(self, minutes: int = 60) -> dict[str, Any]:
        """Get comprehensive metrics summary."""
        calls = self.get_recent_calls(minutes=minutes)
        
        # Group by provider
        by_provider = {}
        for call in calls:
            if call.provider not in by_provider:
                by_provider[call.provider] = []
            by_provider[call.provider].append(call)
        
        provider_metrics = {}
        for provider, provider_calls in by_provider.items():
            total = len(provider_calls)
            errors = sum(1 for c in provider_calls if not c.success)
            rate_limits = sum(1 for c in provider_calls if c.status_code == 429)
            
            provider_metrics[provider] = {
                "total_calls": total,
                "errors": errors,
                "error_rate": errors / total if total > 0 else 0,
                "rate_limits_429": rate_limits,
                "avg_latency_ms": sum(c.latency_ms for c in provider_calls) / total if total > 0 else 0,
                "total_items_returned": sum(c.response_count for c in provider_calls),
            }
        
        return {
            "time_window_minutes": minutes,
            "total_calls": len(calls),
            "overall_error_rate": self.get_error_rate(minutes=minutes),
            "overall_avg_latency_ms": self.get_avg_latency(minutes=minutes),
            "by_provider": provider_metrics,
        }
    
    def get_alerts(self) -> list[dict[str, Any]]:
        """Check for alert conditions."""
        alerts = []
        
        # Check each provider
        providers = set(c.provider for c in self._calls)
        
        for provider in providers:
            # High error rate (>10%)
            error_rate = self.get_error_rate(provider, minutes=30)
            if error_rate > 0.1:
                alerts.append({
                    "type": "high_error_rate",
                    "provider": provider,
                    "error_rate": error_rate,
                    "severity": "error" if error_rate > 0.25 else "warning",
                    "message": f"{provider}: {error_rate:.1%} error rate in last 30 min",
                })
            
            # Rate limiting
            rate_limits = self.get_429_count(provider, minutes=30)
            if rate_limits > 0:
                alerts.append({
                    "type": "rate_limited",
                    "provider": provider,
                    "count": rate_limits,
                    "severity": "warning" if rate_limits < 5 else "error",
                    "message": f"{provider}: {rate_limits} rate limit (429) responses",
                })
            
            # High latency (>5s average)
            avg_latency = self.get_avg_latency(provider, minutes=30)
            if avg_latency > 5000:
                alerts.append({
                    "type": "high_latency",
                    "provider": provider,
                    "avg_latency_ms": avg_latency,
                    "severity": "warning",
                    "message": f"{provider}: {avg_latency:.0f}ms average latency",
                })
        
        return alerts


# Global monitor instance
_monitor = APIMonitor()


def get_api_monitor() -> APIMonitor:
    """Get the global API monitor instance."""
    return _monitor


# =============================================================================
# Decorator for Automatic Call Tracking
# =============================================================================

def track_api_call(provider: str):
    """
    Decorator to automatically track API calls.
    
    Usage:
        @track_api_call("odds_api")
        async def fetch_games(endpoint: str) -> list:
            response = await client.get(endpoint)
            return response.json()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract endpoint from args/kwargs
            endpoint = kwargs.get("endpoint", args[0] if args else "/unknown")
            method = kwargs.get("method", "GET")
            
            start_time = time.time()
            status_code = 0
            response_count = 0
            error_message = None
            
            try:
                result = await func(*args, **kwargs)
                status_code = 200
                
                # Try to get count from result
                if isinstance(result, list):
                    response_count = len(result)
                elif isinstance(result, dict):
                    # Common patterns
                    if "data" in result and isinstance(result["data"], list):
                        response_count = len(result["data"])
                    elif "games" in result:
                        response_count = len(result["games"])
                    elif "events" in result:
                        response_count = len(result["events"])
                
                return result
                
            except Exception as e:
                error_message = str(e)[:100]
                
                # Try to extract status code from exception
                if hasattr(e, "response") and hasattr(e.response, "status_code"):
                    status_code = e.response.status_code
                elif "timeout" in str(e).lower():
                    status_code = 408
                elif "connection" in str(e).lower():
                    status_code = 503
                else:
                    status_code = 500
                
                raise
                
            finally:
                latency_ms = int((time.time() - start_time) * 1000)
                _monitor.record_call(
                    provider=provider,
                    endpoint=str(endpoint),
                    method=method,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    response_count=response_count,
                    error_message=error_message,
                )
        
        return wrapper
    return decorator


# =============================================================================
# Manual Logging Helper
# =============================================================================

def log_api_call(
    provider: str,
    endpoint: str,
    status_code: int,
    latency_ms: int,
    response_count: int = 0,
    method: str = "GET",
    error: Optional[str] = None,
) -> APICallRecord:
    """
    Manually log an API call.
    
    Use this when the decorator approach isn't suitable.
    
    Example:
        start = time.time()
        response = await client.get(url)
        log_api_call(
            provider="odds_api",
            endpoint="/sports/basketball_nba/odds",
            status_code=response.status_code,
            latency_ms=int((time.time() - start) * 1000),
            response_count=len(response.json()),
        )
    """
    return _monitor.record_call(
        provider=provider,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        latency_ms=latency_ms,
        response_count=response_count,
        error_message=error,
    )
