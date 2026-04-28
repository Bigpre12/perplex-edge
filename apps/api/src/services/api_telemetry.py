"""
Centralized Outbound API Observability Layer

Instruments all outbound HTTP calls with:
- Structured JSON logging (provider, latency, status, usage headers)
- Quota threshold warnings (25% / 10% / 5%)
- Per-provider error streak detection (429, 401/403, 404, timeout)
- Rolling N-request summary logs with p95 latency
- URL sanitization (strip API keys from logs)

Usage:
    async with InstrumentedAsyncClient(provider="theoddsapi", purpose="polling") as client:
        resp = await client.get("https://api.the-odds-api.com/v4/sports")
"""

import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

logger = logging.getLogger("api_telemetry")

# ---------------------------------------------------------------------------
# URL Sanitization
# ---------------------------------------------------------------------------

_DEFAULT_STRIP_PARAMS = {"apikey", "api_key", "token", "key", "secret", "password"}


def sanitize_url(
    url: str,
    strip_params: Optional[List[str]] = None,
) -> str:
    """Remove secret-bearing query parameters from a URL for safe logging.

    >>> sanitize_url("https://api.example.com/v1?apiKey=abc123&sport=nba")
    'https://api.example.com/v1?sport=nba'
    """
    try:
        params_to_strip = {p.lower() for p in (strip_params or _DEFAULT_STRIP_PARAMS)}
        parsed = urlparse(url)
        qs = parse_qs(parsed.query, keep_blank_values=True)
        filtered = {k: v for k, v in qs.items() if k.lower() not in params_to_strip}
        clean_query = urlencode(filtered, doseq=True)
        return urlunparse(parsed._replace(query=clean_query))
    except Exception:
        # Never crash on logging helpers
        return url


def mask_key(key: str) -> str:
    """Mask an API key for safe logging: first 4 + '...' + last 4."""
    if not key or len(key) < 10:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


# ---------------------------------------------------------------------------
# Usage Header Extraction
# ---------------------------------------------------------------------------

# Canonical header names (case-insensitive matching)
_USAGE_HEADER_MAP = {
    # TheOddsAPI
    "x-requests-used": "used",
    "x-requests-remaining": "remaining",
    "x-requests-last": "last_cost",
    # Generic rate-limit
    "x-ratelimit-limit": "limit",
    "x-ratelimit-remaining": "remaining",
    "x-ratelimit-reset": "reset",
    "ratelimit-limit": "limit",
    "ratelimit-remaining": "remaining",
    "ratelimit-reset": "reset",
    "retry-after": "retry_after",
    # Groq token-level
    "x-ratelimit-reset-requests": "reset",
    "x-ratelimit-reset-tokens": "tokens_reset",
    "x-ratelimit-limit-requests": "limit",
    "x-ratelimit-remaining-requests": "remaining",
    "x-ratelimit-limit-tokens": "tokens_limit",
    "x-ratelimit-remaining-tokens": "tokens_remaining",
}


def extract_usage_headers(headers: httpx.Headers) -> dict:
    """Normalize usage / rate-limit headers into a standard dict.

    Never raises — always returns a dict.
    """
    result: Dict[str, Any] = {
        "used": None,
        "remaining": None,
        "limit": None,
        "reset": None,
        "retry_after": None,
        "last_cost": None,
        "tokens_limit": None,
        "tokens_remaining": None,
        "tokens_reset": None,
        "headers_present": False,
        "raw": {},
    }

    try:
        for header_name, canonical in _USAGE_HEADER_MAP.items():
            value = headers.get(header_name)
            if value is not None:
                result["headers_present"] = True
                result["raw"][header_name] = value

                # Parse numeric values
                if canonical in ("used", "remaining", "limit", "last_cost",
                                 "retry_after", "tokens_limit", "tokens_remaining"):
                    try:
                        result[canonical] = int(value)
                    except (ValueError, TypeError):
                        try:
                            result[canonical] = float(value)
                        except (ValueError, TypeError):
                            result[canonical] = value
                else:
                    # String values (reset timestamps)
                    result[canonical] = value
    except Exception:
        pass  # Never crash

    return result


# ---------------------------------------------------------------------------
# Structured Log Emitter
# ---------------------------------------------------------------------------


def log_api_request(
    provider: str,
    method: str,
    url: str,
    status_code: int,
    latency_ms: float,
    usage: dict,
    job: Optional[str] = None,
    purpose: Optional[str] = None,
    sport: Optional[str] = None,
    market: Optional[str] = None,
    event_id: Optional[str] = None,
    player_id: Optional[str] = None,
    attempt: int = 1,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    session_id: Optional[str] = None,
    extra: Optional[dict] = None,
) -> None:
    """Emit a single structured log entry for an outbound API request."""

    parsed = urlparse(url)
    safe_url = sanitize_url(url)

    success = 200 <= status_code < 400

    entry = {
        "event": "external_api_request",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "method": method.upper(),
        "host": parsed.hostname or "",
        "endpoint": parsed.path or "/",
        "url": safe_url,
        "status": status_code,
        "success": success,
        "latency_ms": round(latency_ms, 1),
        "attempt": attempt,
    }

    # Optional context fields (only include if set)
    if job:
        entry["job"] = job
    if purpose:
        entry["purpose"] = purpose
    if sport:
        entry["sport"] = sport
    if market:
        entry["market"] = market
    if event_id:
        entry["event_id"] = event_id
    if player_id:
        entry["player_id"] = player_id
    if session_id:
        entry["session_id"] = session_id
    if error_type:
        entry["error_type"] = error_type
    if error_message:
        entry["error_message"] = error_message[:500]
    if extra:
        entry["extra"] = extra

    # Usage headers
    entry["usage_headers_present"] = usage.get("headers_present", False)
    if usage.get("headers_present"):
        entry["usage"] = {
            k: v for k, v in usage.items()
            if k not in ("headers_present", "raw") and v is not None
        }

    # Log level based on status
    if success:
        logger.info("external_api_request | %s %s %s %dms",
                     provider, method.upper(), parsed.path, round(latency_ms), extra={"structured": entry})
    elif 400 <= status_code < 500:
        logger.warning("external_api_request | %s %s %s HTTP %d %dms",
                       provider, method.upper(), parsed.path, status_code, round(latency_ms),
                       extra={"structured": entry})
    else:
        logger.error("external_api_request | %s %s %s HTTP %d %dms",
                     provider, method.upper(), parsed.path, status_code, round(latency_ms),
                     extra={"structured": entry})


# ---------------------------------------------------------------------------
# Per-Provider Error Streak Tracker
# ---------------------------------------------------------------------------


class _ProviderErrorTracker:
    """Lightweight in-memory per-provider streak counter for error patterns."""

    def __init__(self):
        self._streaks: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"429": 0, "auth": 0, "404": 0, "timeout": 0}
        )

    def record_success(self, provider: str) -> None:
        """Reset all streaks for a provider on success."""
        if provider in self._streaks:
            for k in self._streaks[provider]:
                self._streaks[provider][k] = 0

    def record_error(self, provider: str, status_code: int, is_timeout: bool = False) -> None:
        """Increment the relevant streak and emit warnings at threshold (3)."""
        s = self._streaks[provider]

        if is_timeout:
            s["timeout"] += 1
            if s["timeout"] >= 3:
                logger.warning(
                    "Repeated timeouts from %s (%d consecutive) — provider may be unstable",
                    provider, s["timeout"],
                )
        elif status_code == 429:
            s["429"] += 1
            if s["429"] >= 3:
                logger.warning(
                    "Repeated rate limiting from %s (%d consecutive 429s) — consider adding backoff",
                    provider, s["429"],
                )
        elif status_code in (401, 403):
            s["auth"] += 1
            if s["auth"] >= 3:
                logger.error(
                    "Repeated auth failures from %s (%d consecutive %ds) — check API key config",
                    provider, s["auth"], status_code,
                )
        elif status_code == 404:
            s["404"] += 1
            if s["404"] >= 3:
                logger.warning(
                    "Repeated 404s from %s (%d consecutive) — check for stale IDs",
                    provider, s["404"],
                )


_error_tracker = _ProviderErrorTracker()


# ---------------------------------------------------------------------------
# Rolling Per-Provider Summary Accumulator
# ---------------------------------------------------------------------------


class _ProviderSummaryAccumulator:
    """Thread-safe (asyncio.Lock) rolling summary that emits every N requests."""

    def __init__(self, window_size: int = 25):
        self.window_size = window_size
        self._lock = asyncio.Lock()
        self._data: Dict[str, Dict[str, Any]] = {}

    def _empty_bucket(self) -> Dict[str, Any]:
        return {
            "count": 0,
            "success": 0,
            "error_4xx": 0,
            "rate_limit_429": 0,
            "error_5xx": 0,
            "timeout": 0,
            "latencies": [],
            "latest_usage_remaining": None,
            "latest_usage_limit": None,
            "latest_reset": None,
        }

    async def record(
        self,
        provider: str,
        status_code: int,
        latency_ms: float,
        usage: dict,
        is_timeout: bool = False,
    ) -> None:
        async with self._lock:
            if provider not in self._data:
                self._data[provider] = self._empty_bucket()

            b = self._data[provider]
            b["count"] += 1
            b["latencies"].append(latency_ms)

            if is_timeout:
                b["timeout"] += 1
            elif 200 <= status_code < 400:
                b["success"] += 1
            elif status_code == 429:
                b["rate_limit_429"] += 1
                b["error_4xx"] += 1
            elif 400 <= status_code < 500:
                b["error_4xx"] += 1
            elif status_code >= 500:
                b["error_5xx"] += 1

            # Track latest usage
            if usage.get("remaining") is not None:
                b["latest_usage_remaining"] = usage["remaining"]
            if usage.get("limit") is not None:
                b["latest_usage_limit"] = usage["limit"]
            if usage.get("reset") is not None:
                b["latest_reset"] = usage["reset"]

            # Emit summary when window is full
            if b["count"] >= self.window_size:
                self._emit_summary(provider, b)
                self._data[provider] = self._empty_bucket()

    def _emit_summary(self, provider: str, b: Dict[str, Any]) -> None:
        latencies = sorted(b["latencies"])
        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        p95_idx = max(0, int(len(latencies) * 0.95) - 1)
        p95_lat = latencies[p95_idx] if latencies else 0

        summary = {
            "event": "api_usage_summary",
            "provider": provider,
            "window_requests": b["count"],
            "success_count": b["success"],
            "error_4xx_count": b["error_4xx"],
            "rate_limit_429_count": b["rate_limit_429"],
            "error_5xx_count": b["error_5xx"],
            "timeout_count": b["timeout"],
            "avg_latency_ms": round(avg_lat, 1),
            "p95_latency_ms": round(p95_lat, 1),
            "latest_usage_remaining": b["latest_usage_remaining"],
            "latest_usage_limit": b["latest_usage_limit"],
            "latest_reset": b["latest_reset"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "api_usage_summary | %s | %d req | %d ok | %d 4xx | %d 5xx | avg %.0fms | p95 %.0fms",
            provider, b["count"], b["success"], b["error_4xx"], b["error_5xx"],
            avg_lat, p95_lat,
            extra={"structured": summary},
        )


_summary = _ProviderSummaryAccumulator(window_size=25)


# ---------------------------------------------------------------------------
# Quota Threshold Checker
# ---------------------------------------------------------------------------


def _check_quota_thresholds(provider: str, usage: dict) -> None:
    """Emit warnings when API quota drops below 25% / 10% / 5%."""
    remaining = usage.get("remaining")
    limit = usage.get("limit")

    if remaining is None or limit is None or limit <= 0:
        return

    try:
        ratio = remaining / limit
    except (TypeError, ZeroDivisionError):
        return

    if ratio <= 0.05:
        logger.error(
            "API quota CRITICAL — %s below 5%% (%s/%s remaining)",
            provider, remaining, limit,
        )
    elif ratio <= 0.10:
        logger.warning(
            "API quota below 10%% — %s (%s/%s remaining)",
            provider, remaining, limit,
        )
    elif ratio <= 0.25:
        logger.warning(
            "API quota below 25%% — %s (%s/%s remaining)",
            provider, remaining, limit,
        )


# ---------------------------------------------------------------------------
# Instrumented Async Client (Drop-in httpx.AsyncClient wrapper)
# ---------------------------------------------------------------------------


class InstrumentedAsyncClient:
    """Drop-in replacement for ``httpx.AsyncClient`` that auto-logs every
    request with structured telemetry, quota warnings, and error tracking.

    Usage::

        async with InstrumentedAsyncClient(provider="theoddsapi") as client:
            resp = await client.get("/v4/sports", params={"apiKey": key})
    """

    def __init__(
        self,
        provider: str,
        base_url: str = "",
        job: Optional[str] = None,
        purpose: Optional[str] = None,
        **httpx_kwargs: Any,
    ):
        self.provider = provider
        self.job = job
        self.purpose = purpose
        self._httpx_kwargs = httpx_kwargs
        if base_url:
            self._httpx_kwargs["base_url"] = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "InstrumentedAsyncClient":
        self._client = httpx.AsyncClient(**self._httpx_kwargs)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[override]
        if self._client:
            await self._client.aclose()
            self._client = None

    # -- Core request method --

    async def request(
        self,
        method: str,
        url: str,
        *,
        sport: Optional[str] = None,
        market: Optional[str] = None,
        event_id: Optional[str] = None,
        player_id: Optional[str] = None,
        attempt: int = 1,
        telemetry_purpose: Optional[str] = None,
        telemetry_job: Optional[str] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute an HTTP request with full telemetry instrumentation.

        All extra ``kwargs`` are forwarded to ``httpx.AsyncClient.request``.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(**self._httpx_kwargs)

        is_timeout = False
        status_code = 0
        latency_ms = 0.0
        usage: dict = {"headers_present": False}
        response: Optional[httpx.Response] = None

        start = time.perf_counter()
        try:
            response = await self._client.request(method, url, **kwargs)
            latency_ms = (time.perf_counter() - start) * 1000
            status_code = response.status_code
            usage = extract_usage_headers(response.headers)
        except httpx.TimeoutException:
            latency_ms = (time.perf_counter() - start) * 1000
            is_timeout = True
            status_code = 0
            _error_tracker.record_error(self.provider, 0, is_timeout=True)
            log_api_request(
                provider=self.provider,
                method=method,
                url=str(self._client.base_url) + str(url) if not str(url).startswith("http") else str(url),
                status_code=0,
                latency_ms=latency_ms,
                usage=usage,
                job=telemetry_job or self.job,
                purpose=telemetry_purpose or self.purpose,
                sport=sport,
                market=market,
                event_id=event_id,
                player_id=player_id,
                attempt=attempt,
                error_type="timeout",
                error_message="Request timed out",
            )
            asyncio.ensure_future(
                _summary.record(self.provider, 0, latency_ms, usage, is_timeout=True)
            )
            raise
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            log_api_request(
                provider=self.provider,
                method=method,
                url=str(self._client.base_url) + str(url) if not str(url).startswith("http") else str(url),
                status_code=0,
                latency_ms=latency_ms,
                usage=usage,
                job=telemetry_job or self.job,
                purpose=telemetry_purpose or self.purpose,
                sport=sport,
                attempt=attempt,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            raise

        # Resolve the full URL for logging
        full_url = str(response.url) if response else str(url)

        # Log the request
        log_api_request(
            provider=self.provider,
            method=method,
            url=full_url,
            status_code=status_code,
            latency_ms=latency_ms,
            usage=usage,
            job=telemetry_job or self.job,
            purpose=telemetry_purpose or self.purpose,
            sport=sport,
            market=market,
            event_id=event_id,
            player_id=player_id,
            attempt=attempt,
        )

        # Error streak tracking
        if 200 <= status_code < 400:
            _error_tracker.record_success(self.provider)
        else:
            _error_tracker.record_error(self.provider, status_code)

        # Quota threshold warnings
        _check_quota_thresholds(self.provider, usage)

        # Rolling summary
        asyncio.ensure_future(
            _summary.record(self.provider, status_code, latency_ms, usage)
        )

        return response

    # -- Convenience HTTP methods (match httpx.AsyncClient interface) --

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)
