import time
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class AuthCircuitBreaker:
    def __init__(self, threshold=10, cooldown=60):
        self.threshold = threshold
        self.cooldown = cooldown
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
        self._half_open_probe_in_flight = False

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        self._half_open_probe_in_flight = False
        if self.failures >= self.threshold:
            self.state = "OPEN"
            logger.error(f"Circuit Breaker TRIPPED: {self.failures} failures. State: OPEN")

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"
        self._half_open_probe_in_flight = False
        logger.info("Circuit Breaker CLOSED (Success in Half-Open state).")

    def can_proceed(self):
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.cooldown:
                self.state = "HALF_OPEN"
                self._half_open_probe_in_flight = False
                logger.info("Circuit Breaker HALF-OPEN: Allowing test request.")
                return True
            return False
        
        if self.state == "HALF_OPEN":
            if self._half_open_probe_in_flight:
                return False
            self._half_open_probe_in_flight = True
            return True
            
        return False

    def reset(self):
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0
        self._half_open_probe_in_flight = False
        logger.info("Circuit Breaker RESET manually.")

    def reset_at(self):
        if self.state != "OPEN":
            return None
        return self.last_failure_time + self.cooldown

# Global instance
auth_breaker = AuthCircuitBreaker(threshold=10, cooldown=60)

class AuthCircuitBreakerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip circuit breaker for internal admin reset
        if request.url.path == "/api/admin/reset-circuit-breaker":
            return await call_next(request)

        if not auth_breaker.can_proceed():
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Service temporarily unavailable",
                    "error": "Auth circuit breaker open: too many authentication failures",
                }
            )

        try:
            response = await call_next(request)
            
            # We specifically look for 401/403 to trigger the breaker
            if response.status_code in [401, 403]:
                auth_breaker.record_failure()
            elif response.status_code == 503:
                # Infrastructure failures should not be treated as auth failures.
                if auth_breaker.state == "HALF_OPEN":
                    auth_breaker._half_open_probe_in_flight = False
            elif response.status_code < 400:
                if auth_breaker.state == "HALF_OPEN":
                    auth_breaker.record_success()
            
            return response
        except Exception as e:
            # If a request crashes, we don't necessarily count it as an auth failure 
            # unless it's an HTTPException with 401/403
            if isinstance(e, HTTPException) and e.status_code in [401, 403]:
                auth_breaker.record_failure()
            elif isinstance(e, HTTPException) and e.status_code == 503 and auth_breaker.state == "HALF_OPEN":
                auth_breaker._half_open_probe_in_flight = False
            raise e
