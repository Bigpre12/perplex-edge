"""
Sentry integration for error monitoring.

Provides automatic error tracking and performance monitoring.
"""
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_sentry_initialized = False


def init_sentry() -> bool:
    """
    Initialize Sentry error monitoring.
    
    Only initializes if SENTRY_DSN is configured.
    
    Returns:
        True if Sentry was initialized, False otherwise
    """
    global _sentry_initialized
    
    if _sentry_initialized:
        return True
    
    settings = get_settings()
    
    if not settings.sentry_dsn:
        logger.info("sentry_disabled", reason="SENTRY_DSN not configured")
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.httpx import HttpxIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            
            # Performance monitoring
            traces_sample_rate=0.1 if settings.is_production else 1.0,
            profiles_sample_rate=0.1 if settings.is_production else 1.0,
            
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                HttpxIntegration(),
                LoggingIntegration(
                    level=None,  # Don't capture log messages as breadcrumbs
                    event_level=None,  # Don't send log messages as events
                ),
            ],
            
            # Don't send personally identifiable information
            send_default_pii=False,
            
            # Before send hook to filter/modify events
            before_send=_before_send,
            
            # Release tracking (if available)
            release=f"perplex-engine@0.1.0",
        )
        
        _sentry_initialized = True
        logger.info(
            "sentry_initialized",
            environment=settings.environment,
            traces_sample_rate=0.1 if settings.is_production else 1.0,
        )
        return True
        
    except ImportError:
        logger.warning("sentry_import_failed", reason="sentry-sdk not installed")
        return False
    except Exception as e:
        logger.error("sentry_init_failed", error=str(e)[:200])
        return False


def _before_send(event: dict, hint: dict) -> Optional[dict]:
    """
    Filter/modify Sentry events before sending.
    
    Use this to:
    - Drop non-essential errors
    - Sanitize sensitive data
    - Add custom context
    """
    # Don't send 404 errors
    if event.get("exception"):
        values = event["exception"].get("values", [])
        for value in values:
            if "404" in str(value.get("value", "")):
                return None
    
    # Don't send rate limit errors (expected behavior)
    if "rate limit" in str(event).lower():
        return None
    
    return event


def capture_exception(error: Exception, **extra_context) -> Optional[str]:
    """
    Manually capture an exception to Sentry.
    
    Args:
        error: The exception to capture
        **extra_context: Additional context to include
    
    Returns:
        The Sentry event ID if captured, None otherwise
    """
    if not _sentry_initialized:
        return None
    
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            for key, value in extra_context.items():
                scope.set_extra(key, value)
            
            return sentry_sdk.capture_exception(error)
    except Exception:
        return None


def capture_message(message: str, level: str = "info", **extra_context) -> Optional[str]:
    """
    Manually send a message to Sentry.
    
    Args:
        message: The message to send
        level: Severity level (debug, info, warning, error, fatal)
        **extra_context: Additional context to include
    
    Returns:
        The Sentry event ID if captured, None otherwise
    """
    if not _sentry_initialized:
        return None
    
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            for key, value in extra_context.items():
                scope.set_extra(key, value)
            
            return sentry_sdk.capture_message(message, level=level)
    except Exception:
        return None


def set_user(user_id: str, **user_data) -> None:
    """Set user context for Sentry events."""
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        sentry_sdk.set_user({"id": user_id, **user_data})
    except Exception:
        pass


def add_breadcrumb(message: str, category: str = "custom", **data) -> None:
    """Add a breadcrumb for debugging context."""
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            data=data,
        )
    except Exception:
        pass
