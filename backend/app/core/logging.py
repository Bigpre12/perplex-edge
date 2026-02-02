"""
Structured logging configuration for Perplex Engine.

Provides JSON-formatted logs with correlation IDs for request tracing.
Falls back to standard logging if structlog is not installed.
"""
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Optional

# Try to import structlog, fall back to standard logging if not available
try:
    import structlog
    from structlog.types import EventDict, WrappedLogger
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None
    EventDict = dict
    WrappedLogger = Any

# Context variable for request correlation ID
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """Get current correlation ID or generate a new one."""
    cid = correlation_id_ctx.get()
    if cid is None:
        cid = str(uuid.uuid4())[:8]
        correlation_id_ctx.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_ctx.set(cid)


def add_correlation_id(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Processor to add correlation ID to all log entries."""
    cid = correlation_id_ctx.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


def add_service_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Processor to add service context to all log entries."""
    event_dict["service"] = "perplex-engine"
    return event_dict


def configure_logging(json_logs: bool = True, log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        json_logs: If True, output JSON formatted logs (for production).
                   If False, output human-readable logs (for development).
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    if STRUCTLOG_AVAILABLE:
        # Shared processors for all logging
        shared_processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            add_correlation_id,
            add_service_context,
        ]
        
        if json_logs:
            # Production: JSON output
            shared_processors.append(structlog.processors.format_exc_info)
            shared_processors.append(structlog.processors.JSONRenderer())
        else:
            # Development: colored console output
            shared_processors.append(structlog.dev.ConsoleRenderer(colors=True))
        
        # Configure structlog
        structlog.configure(
            processors=shared_processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure standard library logging to use structlog
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level.upper()),
        )
    else:
        # Fallback to standard logging
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level.upper()),
        )
        logging.warning("structlog not installed, using standard logging")
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str = __name__) -> Any:
    """
    Get a structured logger instance.
    
    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Processing request", user_id=123, action="login")
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


# Convenience function for logging with extra context
def log_with_context(
    logger: Any,
    level: str,
    message: str,
    **kwargs: Any
) -> None:
    """
    Log a message with additional context.
    
    Args:
        logger: Logger instance
        level: Log level (info, warning, error, debug)
        message: Log message
        **kwargs: Additional context to include in log
    """
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, **kwargs)


# Metrics tracking (simple in-memory for now)
class RequestMetrics:
    """Simple in-memory request metrics tracker."""
    
    def __init__(self):
        self._request_count = 0
        self._error_count = 0
        self._total_duration_ms = 0.0
        self._endpoint_counts: dict[str, int] = {}
        self._endpoint_errors: dict[str, int] = {}
        self._endpoint_durations: dict[str, float] = {}
    
    def record_request(
        self,
        path: str,
        method: str,
        status_code: int,
        duration_ms: float
    ) -> None:
        """Record a request for metrics."""
        self._request_count += 1
        self._total_duration_ms += duration_ms
        
        endpoint_key = f"{method}:{path}"
        self._endpoint_counts[endpoint_key] = self._endpoint_counts.get(endpoint_key, 0) + 1
        self._endpoint_durations[endpoint_key] = (
            self._endpoint_durations.get(endpoint_key, 0) + duration_ms
        )
        
        if status_code >= 400:
            self._error_count += 1
            self._endpoint_errors[endpoint_key] = self._endpoint_errors.get(endpoint_key, 0) + 1
    
    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics summary."""
        avg_duration = (
            self._total_duration_ms / self._request_count
            if self._request_count > 0
            else 0
        )
        error_rate = (
            self._error_count / self._request_count * 100
            if self._request_count > 0
            else 0
        )
        
        # Top 10 slowest endpoints
        sorted_by_duration = sorted(
            self._endpoint_durations.items(),
            key=lambda x: x[1] / max(self._endpoint_counts.get(x[0], 1), 1),
            reverse=True
        )[:10]
        
        return {
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "error_rate_pct": round(error_rate, 2),
            "avg_duration_ms": round(avg_duration, 2),
            "endpoints": {
                k: {
                    "count": self._endpoint_counts.get(k, 0),
                    "errors": self._endpoint_errors.get(k, 0),
                    "avg_duration_ms": round(
                        self._endpoint_durations.get(k, 0) / max(self._endpoint_counts.get(k, 1), 1),
                        2
                    ),
                }
                for k, _ in sorted_by_duration
            },
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._request_count = 0
        self._error_count = 0
        self._total_duration_ms = 0.0
        self._endpoint_counts.clear()
        self._endpoint_errors.clear()
        self._endpoint_durations.clear()


# Global metrics instance
request_metrics = RequestMetrics()
