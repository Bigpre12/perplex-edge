"""
Resilience utilities for external API calls.

Provides retry logic with exponential backoff and circuit breakers.
Falls back to simple implementations if dependencies are not installed.
"""
import asyncio
import functools
import logging
from typing import Any, Callable, Optional, TypeVar

# Try to import tenacity, provide fallback if not available
try:
    from tenacity import (
        AsyncRetrying,
        RetryError,
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
        wait_random_exponential,
        before_sleep_log,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

# Try to import pybreaker, provide fallback if not available
try:
    from pybreaker import CircuitBreaker, CircuitBreakerError
    PYBREAKER_AVAILABLE = True
except ImportError:
    PYBREAKER_AVAILABLE = False
    
    # Simple fallback CircuitBreakerError
    class CircuitBreakerError(Exception):
        pass

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


# =============================================================================
# Retry Configuration
# =============================================================================

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        min_wait_seconds: float = 1.0,
        max_wait_seconds: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.min_wait_seconds = min_wait_seconds
        self.max_wait_seconds = max_wait_seconds
        self.exponential_base = exponential_base
        self.jitter = jitter


# Default retry configuration for external APIs
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    min_wait_seconds=1.0,
    max_wait_seconds=30.0,
    jitter=True,
)

# More aggressive retry for critical paths
AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    min_wait_seconds=0.5,
    max_wait_seconds=60.0,
    jitter=True,
)


# =============================================================================
# Retry Decorators
# =============================================================================

def with_retry(
    config: RetryConfig = DEFAULT_RETRY_CONFIG,
    retry_on: tuple = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """
    Decorator to add retry logic with exponential backoff.
    
    Usage:
        @with_retry()
        async def fetch_data():
            ...
        
        @with_retry(config=AGGRESSIVE_RETRY_CONFIG)
        async def critical_fetch():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            attempt = 0
            last_exception = None
            
            while attempt < config.max_attempts:
                attempt += 1
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    
                    if attempt >= config.max_attempts:
                        logger.error(
                            "retry_exhausted",
                            function=func.__name__,
                            attempts=attempt,
                            error=str(e)[:200],
                        )
                        raise
                    
                    # Calculate wait time with exponential backoff
                    wait_time = min(
                        config.min_wait_seconds * (config.exponential_base ** (attempt - 1)),
                        config.max_wait_seconds,
                    )
                    
                    # Add jitter if enabled
                    if config.jitter:
                        import random
                        wait_time = wait_time * (0.5 + random.random())
                    
                    logger.warning(
                        "retry_attempt",
                        function=func.__name__,
                        attempt=attempt,
                        max_attempts=config.max_attempts,
                        wait_seconds=round(wait_time, 2),
                        error=str(e)[:100],
                    )
                    
                    if on_retry:
                        on_retry(attempt, e)
                    
                    await asyncio.sleep(wait_time)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            return None  # type: ignore
        
        return wrapper
    return decorator


def retry_on_http_errors(
    max_attempts: int = 3,
    retry_statuses: tuple = (429, 500, 502, 503, 504),
):
    """
    Decorator for retrying HTTP requests on specific status codes.
    
    Usage:
        @retry_on_http_errors()
        async def fetch_from_api():
            response = await client.get(url)
            response.raise_for_status()
            return response
    """
    import httpx
    
    def should_retry(exc: BaseException) -> bool:
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code in retry_statuses
        if isinstance(exc, (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError)):
            return True
        return False
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            attempt = 0
            while attempt < max_attempts:
                attempt += 1
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if not should_retry(e) or attempt >= max_attempts:
                        raise
                    
                    # Special handling for 429 - use Retry-After header if available
                    wait_time = 1.0 * (2 ** (attempt - 1))
                    if hasattr(e, 'response') and hasattr(e.response, 'headers'):
                        retry_after = e.response.headers.get('Retry-After')
                        if retry_after:
                            try:
                                wait_time = float(retry_after)
                            except ValueError:
                                pass
                    
                    logger.warning(
                        "http_retry",
                        function=func.__name__,
                        attempt=attempt,
                        wait_seconds=round(wait_time, 2),
                        error=str(e)[:100],
                    )
                    
                    await asyncio.sleep(wait_time)
            
            return None  # type: ignore
        
        return wrapper
    return decorator


# =============================================================================
# Circuit Breakers
# =============================================================================

class DummyCircuitBreaker:
    """Fallback circuit breaker when pybreaker is not installed."""
    
    def __init__(self, fail_max: int = 5, reset_timeout: int = 60, name: str = ""):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.name = name
        self.fail_counter = 0
        self.current_state = "closed"
    
    async def call_async(self, func, *args, **kwargs):
        """Just call the function directly."""
        return await func(*args, **kwargs)


class CircuitBreakerRegistry:
    """Registry for circuit breakers by service name."""
    
    _breakers: dict[str, Any] = {}
    
    @classmethod
    def get_or_create(
        cls,
        name: str,
        fail_max: int = 5,
        reset_timeout: int = 60,
    ) -> Any:
        """Get or create a circuit breaker for a service."""
        if name not in cls._breakers:
            if PYBREAKER_AVAILABLE:
                cls._breakers[name] = CircuitBreaker(
                    fail_max=fail_max,
                    reset_timeout=reset_timeout,
                    name=name,
                )
            else:
                cls._breakers[name] = DummyCircuitBreaker(
                    fail_max=fail_max,
                    reset_timeout=reset_timeout,
                    name=name,
                )
            logger.info(
                "circuit_breaker_created",
                name=name,
                fail_max=fail_max,
                reset_timeout=reset_timeout,
            )
        return cls._breakers[name]
    
    @classmethod
    def get_status(cls) -> dict[str, dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {
            name: {
                "state": getattr(breaker, 'current_state', 'unknown'),
                "fail_counter": getattr(breaker, 'fail_counter', 0),
                "fail_max": getattr(breaker, 'fail_max', 5),
                "reset_timeout": getattr(breaker, 'reset_timeout', 60),
            }
            for name, breaker in cls._breakers.items()
        }


def with_circuit_breaker(
    service_name: str,
    fail_max: int = 5,
    reset_timeout: int = 60,
    fallback: Optional[Callable[..., T]] = None,
):
    """
    Decorator to wrap a function with a circuit breaker.
    
    Usage:
        @with_circuit_breaker("odds_api")
        async def fetch_odds():
            ...
        
        @with_circuit_breaker("stats_api", fallback=lambda: [])
        async def fetch_stats():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        breaker = CircuitBreakerRegistry.get_or_create(
            service_name, fail_max, reset_timeout
        )
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                # Check if circuit is open before calling
                if breaker.current_state == "open":
                    logger.warning(
                        "circuit_breaker_open",
                        service=service_name,
                        function=func.__name__,
                    )
                    if fallback:
                        return fallback(*args, **kwargs)
                    raise CircuitBreakerError(breaker)
                
                # Call the function
                result = await breaker.call_async(func, *args, **kwargs)
                return result
                
            except CircuitBreakerError:
                logger.error(
                    "circuit_breaker_tripped",
                    service=service_name,
                    function=func.__name__,
                )
                if fallback:
                    return fallback(*args, **kwargs)
                raise
        
        return wrapper
    return decorator


# =============================================================================
# Combined Resilience Pattern
# =============================================================================

def resilient_call(
    service_name: str,
    retry_config: RetryConfig = DEFAULT_RETRY_CONFIG,
    circuit_fail_max: int = 5,
    circuit_reset_timeout: int = 60,
    fallback: Optional[Callable[..., T]] = None,
):
    """
    Combined decorator for retry + circuit breaker.
    
    Applies retry logic first, then circuit breaker.
    
    Usage:
        @resilient_call("odds_api")
        async def fetch_odds():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Apply retry first
        retried_func = with_retry(config=retry_config)(func)
        # Then circuit breaker
        protected_func = with_circuit_breaker(
            service_name,
            fail_max=circuit_fail_max,
            reset_timeout=circuit_reset_timeout,
            fallback=fallback,
        )(retried_func)
        return protected_func
    
    return decorator
