import asyncio
import logging
import time
import httpx
from typing import Optional, Dict, Any, Callable
from core.config import settings

logger = logging.getLogger(__name__)

class ResilientBaseClient:
    """
    Base client with:
    - Exponential Backoff & Retries
    - Circuit Breaker logic
    - Connection Pooling (via httpx.AsyncClient)
    - Quota/Usage Logging
    """
    
    def __init__(
        self, 
        name: str, 
        base_url: str, 
        timeout: int = 15,
        max_retries: int = 3,
        circuit_fail_threshold: int = 5,
        circuit_reset_timeout: int = 60
    ):
        self.name = name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Circuit Breaker state
        self.fail_count = 0
        self.fail_threshold = circuit_fail_threshold
        self.reset_timeout = circuit_reset_timeout
        self.last_fail_time = 0
        self.is_open = False
        
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )

    async def request(
        self, 
        method: str, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Any:
        """
        Execute an async HTTP request with resilience.
        """
        if self._is_circuit_open():
            logger.warning(f"[{self.name}] Circuit is OPEN. Skipping request to {path}")
            raise Exception(f"Circuit breaker for {self.name} is open.")

        try:
            start_time = time.time()
            response = await self.client.request(
                method, 
                path, 
                params=params, 
                json=json_data, 
                headers=headers
            )
            latency = (time.time() - start_time) * 1000
            
            # Quota Check (Custom per client usually, but base can log)
            self._log_usage(response, latency)

            if response.status_code == 429: # Rate Limited
                return await self._handle_retry(method, path, params, json_data, headers, retry_count, wait=5)

            response.raise_for_status()
            self._on_success()
            return response.json()

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            self._on_failure()
            
            resp_content = ""
            if isinstance(e, httpx.HTTPStatusError):
                resp_content = f" | Response: {e.response.text}"
            
            if retry_count < self.max_retries:
                wait_time = (2 ** retry_count) # Exponential
                logger.warning(f"[{self.name}] Request failed: {str(e)}{resp_content}. Retrying in {wait_time}s...")
                return await self._handle_retry(method, path, params, json_data, headers, retry_count, wait=wait_time)
            
            logger.error(f"[{self.name}] Max retries reached for {path}. Error: {str(e)}{resp_content}")
            raise e

    def _is_circuit_open(self) -> bool:
        if self.is_open:
            if time.time() - self.last_fail_time > self.reset_timeout:
                logger.info(f"[{self.name}] Circuit half-opened. Testing next request.")
                return False
            return True
        return False

    def _on_success(self):
        self.fail_count = 0
        self.is_open = False

    def _on_failure(self):
        self.fail_count += 1
        self.last_fail_time = time.time()
        if self.fail_count >= self.fail_threshold:
            logger.error(f"[{self.name}] Failure threshold reached. TRIPPING CIRCUIT BREAKER.")
            self.is_open = True

    async def _handle_retry(self, method, path, params, json_data, headers, retry_count, wait=1):
        await asyncio.sleep(wait)
        return await self.request(method, path, params, json_data, headers, retry_count + 1)

    def _log_usage(self, response: httpx.Response, latency: float):
        """Hook for quota tracking"""
        pass

    async def close(self):
        await self.client.aclose()
