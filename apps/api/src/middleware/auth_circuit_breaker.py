import time
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class AuthCircuitBreaker:
    def __init__(self, threshold=50, cooldown=60):
        self.threshold = threshold
        self.cooldown = cooldown
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.threshold:
            self.state = "OPEN"
            logger.error(f"Circuit Breaker TRIPPED: {self.failures} failures. State: OPEN")

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"
        logger.info("Circuit Breaker CLOSED (Success in Half-Open state).")

    def can_proceed(self):
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.cooldown:
                self.state = "HALF_OPEN"
                logger.info("Circuit Breaker HALF-OPEN: Allowing test request.")
                return True
            return False
        
        if self.state == "HALF_OPEN":
            # In simple implementation, we only allow one at a time.
            # But for FastAPI middleware, multiple might hit at once.
            return True
            
        return False

    def reset(self):
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0
        logger.info("Circuit Breaker RESET manually.")

# Global instance
auth_breaker = AuthCircuitBreaker(threshold=50, cooldown=60)

class AuthCircuitBreakerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip circuit breaker for internal admin reset
        if request.url.path == "/api/admin/reset-circuit-breaker":
            return await call_next(request)

        if not auth_breaker.can_proceed():
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                    "error": "Circuit breaker open: Too many authentication errors"
                }
            )

        try:
            response = await call_next(request)
            
            # We specifically look for 401/403 to trigger the breaker
            if response.status_code in [401, 403]:
                auth_breaker.record_failure()
            elif response.status_code < 400:
                if auth_breaker.state == "HALF_OPEN":
                    auth_breaker.record_success()
            
            return response
        except Exception as e:
            # If a request crashes, we don't necessarily count it as an auth failure 
            # unless it's an HTTPException with 401/403
            if isinstance(e, HTTPException) and e.status_code in [401, 403]:
                auth_breaker.record_failure()
            raise e
