"""
Base classes and types for the data layer.

This module provides:
- BaseProvider: Abstract base for all API providers
- Common error types
- DataResponse: Standard response envelope with provenance
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, TypeVar, Generic

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Error Types
# =============================================================================

class ProviderError(Exception):
    """Base exception for provider errors."""
    
    def __init__(self, message: str, provider: str = "unknown", status_code: int = None):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")


class RateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""
    
    def __init__(self, provider: str, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after}s" if retry_after else "Rate limit exceeded",
            provider=provider,
            status_code=429,
        )


class AuthenticationError(ProviderError):
    """Raised when API authentication fails."""
    
    def __init__(self, provider: str):
        super().__init__("Authentication failed - check API key", provider=provider, status_code=401)


class NotFoundError(ProviderError):
    """Raised when requested resource is not found."""
    
    def __init__(self, provider: str, resource: str):
        super().__init__(f"Resource not found: {resource}", provider=provider, status_code=404)


# =============================================================================
# Response Types
# =============================================================================

class CacheType(Enum):
    """Type of cache the data came from."""
    LIVE = "live"           # Short TTL (5-10 min) for odds
    HISTORICAL = "historical"  # Long TTL (24h) for stats/baselines
    REFERENCE = "reference"    # Very long TTL (1 week) for static data
    NONE = "none"           # Not cached


T = TypeVar("T")


@dataclass
class DataResponse(Generic[T]):
    """
    Standard response envelope with provenance information.
    
    Every response from the data layer includes:
    - data: The actual payload
    - source: Where the data came from ("oddsapi", "espn", "cache", "stub")
    - last_updated: When the data was fetched/cached
    - season: Current season label ("2025-26" or "2025")
    - stale: True if data is from cache after provider failure
    - cache_type: Which cache the data came from
    """
    data: T
    source: str
    last_updated: datetime
    season: str
    stale: bool = False
    cache_type: CacheType = CacheType.NONE
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "data": self.data,
            "source": self.source,
            "last_updated": self.last_updated.isoformat(),
            "season": self.season,
            "stale": self.stale,
            "cache_type": self.cache_type.value,
        }
    
    @classmethod
    def fresh(cls, data: T, source: str, season: str) -> "DataResponse[T]":
        """Create a fresh (non-cached) response."""
        return cls(
            data=data,
            source=source,
            last_updated=datetime.now(timezone.utc),
            season=season,
            stale=False,
            cache_type=CacheType.NONE,
        )
    
    @classmethod
    def from_cache(
        cls,
        data: T,
        source: str,
        season: str,
        last_updated: datetime,
        cache_type: CacheType,
        stale: bool = False,
    ) -> "DataResponse[T]":
        """Create a response from cached data."""
        return cls(
            data=data,
            source=source,
            last_updated=last_updated,
            season=season,
            stale=stale,
            cache_type=cache_type,
        )


# =============================================================================
# Base Provider
# =============================================================================

@dataclass
class RateLimitState:
    """Track rate limit state for a provider."""
    remaining: Optional[int] = None
    limit: Optional[int] = None
    reset_at: Optional[datetime] = None
    
    def is_exhausted(self) -> bool:
        """Check if rate limit is exhausted."""
        if self.remaining is None:
            return False
        return self.remaining <= 0
    
    def update_from_headers(self, headers: httpx.Headers):
        """Update state from response headers."""
        # Common header patterns
        if "x-requests-remaining" in headers:
            self.remaining = int(headers["x-requests-remaining"])
        if "x-ratelimit-remaining" in headers:
            self.remaining = int(headers["x-ratelimit-remaining"])
        if "x-ratelimit-limit" in headers:
            self.limit = int(headers["x-ratelimit-limit"])


class BaseProvider(ABC):
    """
    Abstract base class for all external API providers.
    
    Features:
    - Consistent HTTP request handling
    - Automatic retry with exponential backoff
    - Rate limit tracking
    - Standardized error handling
    - Health check support
    
    Subclasses must implement:
    - name: Provider name for logging/provenance
    - base_url: API base URL
    - health_check(): Check if provider is available
    """
    
    # Override in subclasses
    name: str = "base"
    base_url: str = ""
    
    # Configuration
    timeout: int = 30
    max_retries: int = 3
    base_retry_delay: float = 1.0
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None
        self.rate_limit = RateLimitState()
        self._last_request_at: Optional[datetime] = None
    
    async def __aenter__(self):
        """Context manager entry - create HTTP client."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client, creating if needed."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (appended to base_url)
            params: Query parameters
            headers: Additional headers
            json_body: JSON body for POST/PUT
        
        Returns:
            Parsed JSON response
        
        Raises:
            ProviderError: On non-retryable errors
            RateLimitError: When rate limit exceeded
            AuthenticationError: When API key invalid
        """
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        
        # Add authentication if needed
        if self.api_key:
            headers = self._add_auth(headers, params or {})
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Check rate limit before request
                if self.rate_limit.is_exhausted():
                    raise RateLimitError(self.name)
                
                # Make request
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    json=json_body,
                )
                
                # Track rate limits from headers
                self.rate_limit.update_from_headers(response.headers)
                self._last_request_at = datetime.now(timezone.utc)
                
                # Handle response status
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError(self.name)
                elif response.status_code == 404:
                    raise NotFoundError(self.name, endpoint)
                elif response.status_code == 422:
                    # Validation error - don't retry
                    logger.warning(f"[{self.name}] Validation error: {response.text}")
                    return {}
                elif response.status_code == 429:
                    retry_after = response.headers.get("retry-after")
                    raise RateLimitError(self.name, int(retry_after) if retry_after else None)
                elif response.status_code >= 500:
                    # Server error - retry
                    last_error = ProviderError(
                        f"Server error: {response.status_code}",
                        provider=self.name,
                        status_code=response.status_code,
                    )
                else:
                    raise ProviderError(
                        f"Unexpected status: {response.status_code}",
                        provider=self.name,
                        status_code=response.status_code,
                    )
                    
            except httpx.TimeoutException:
                last_error = ProviderError("Request timeout", provider=self.name)
            except httpx.RequestError as e:
                last_error = ProviderError(f"Request failed: {e}", provider=self.name)
            except (RateLimitError, AuthenticationError, NotFoundError):
                raise  # Don't retry these
            except Exception as e:
                last_error = ProviderError(str(e), provider=self.name)
            
            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                delay = self.base_retry_delay * (2 ** attempt)
                logger.warning(
                    f"[{self.name}] Request failed, retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})"
                )
                await asyncio.sleep(delay)
        
        # All retries exhausted
        raise last_error or ProviderError("All retries exhausted", provider=self.name)
    
    def _add_auth(self, headers: dict, params: dict) -> dict:
        """
        Add authentication to request.
        
        Override in subclasses for different auth methods.
        Default: Add API key as query parameter.
        """
        return headers
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is available.
        
        Returns:
            True if provider is healthy and responding
        """
        pass
    
    def get_rate_limit_status(self) -> dict[str, Any]:
        """Get current rate limit status."""
        return {
            "remaining": self.rate_limit.remaining,
            "limit": self.rate_limit.limit,
            "exhausted": self.rate_limit.is_exhausted(),
            "last_request": self._last_request_at.isoformat() if self._last_request_at else None,
        }
