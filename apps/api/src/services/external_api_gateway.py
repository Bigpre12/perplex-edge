from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Dict, Optional, Tuple

import httpx
from sqlalchemy import text

from db.session import async_session_maker
from services.cache import cache

logger = logging.getLogger(__name__)


@dataclass
class GatewayResult:
    status_code: int
    data: Any
    headers: Dict[str, str]
    cache_hit: bool
    started_at: datetime
    completed_at: datetime


class ExternalApiGateway:
    """Canonical paid API gateway with TTL cache, coalescing, budgets, and logging."""

    TTL_POLICY_SECONDS: Dict[str, int] = {
        "sports": 24 * 3600,
        "events": 10 * 60,
        "pregame_odds": 180,
        "player_props": 300,
        "live_odds": 30,
        "historical": 0,  # admin/manual only
    }

    def __init__(self) -> None:
        self._inflight: Dict[str, asyncio.Future] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    def _request_key(self, provider: str, endpoint: str, params: Dict[str, Any]) -> str:
        payload = json.dumps({"p": provider, "e": endpoint, "q": sorted(params.items())}, default=str)
        return f"ext:{provider}:{sha256(payload.encode()).hexdigest()}"

    def _ttl_for_class(self, data_class: str) -> int:
        return int(self.TTL_POLICY_SECONDS.get(data_class, 120))

    async def _budget_state(self, provider: str) -> Dict[str, Any]:
        hour_limit = int(__import__("os").getenv("EXT_API_HOURLY_BUDGET", "1200"))
        day_limit = int(__import__("os").getenv("EXT_API_DAILY_BUDGET", "12000"))
        reserve_limit = int(__import__("os").getenv("EXT_API_LIVE_RESERVE_BUDGET", "250"))

        now = datetime.now(timezone.utc)
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        used_hour = 0
        used_day = 0
        try:
            async with async_session_maker() as session:
                res_h = await session.execute(
                    text(
                        "SELECT COUNT(*) FROM external_api_call_log "
                        "WHERE provider=:p AND started_at >= :hs AND cache_hit = FALSE"
                    ),
                    {"p": provider, "hs": hour_start},
                )
                used_hour = int(res_h.scalar() or 0)
                res_d = await session.execute(
                    text(
                        "SELECT COUNT(*) FROM external_api_call_log "
                        "WHERE provider=:p AND started_at >= :ds AND cache_hit = FALSE"
                    ),
                    {"p": provider, "ds": day_start},
                )
                used_day = int(res_d.scalar() or 0)
        except Exception as e:
            logger.debug("gateway budget lookup failed: %s", e)

        def pct(used: int, limit: int) -> float:
            return (used / limit) if limit > 0 else 0.0

        hourly_pct = pct(used_hour, hour_limit)
        if hourly_pct >= 0.95:
            mode = "emergency_freeze"
        elif hourly_pct >= 0.90:
            mode = "protection"
        elif hourly_pct >= 0.75:
            mode = "conservative"
        else:
            mode = "normal"

        return {
            "mode": mode,
            "used_hour": used_hour,
            "used_day": used_day,
            "hour_limit": hour_limit,
            "day_limit": day_limit,
            "reserve_limit": reserve_limit,
        }

    async def _persist_call(
        self,
        *,
        provider: str,
        endpoint: str,
        sport: Optional[str],
        markets: Optional[str],
        regions: Optional[str],
        event_count: Optional[int],
        status_code: int,
        headers: Dict[str, str],
        cache_hit: bool,
        started_at: datetime,
        completed_at: datetime,
        request_key: str,
    ) -> None:
        try:
            xr = headers.get("x-requests-remaining") or headers.get("X-Requests-Remaining")
            xu = headers.get("x-requests-used") or headers.get("X-Requests-Used")
            xl = headers.get("x-requests-last") or headers.get("X-Requests-Last")
            async with async_session_maker() as session:
                await session.execute(
                    text(
                        """
                        INSERT INTO external_api_call_log
                        (provider, endpoint, sport, markets, regions, event_count, status_code,
                         x_requests_remaining, x_requests_used, x_requests_last, cache_hit,
                         started_at, completed_at, request_key)
                        VALUES
                        (:provider, :endpoint, :sport, :markets, :regions, :event_count, :status_code,
                         :x_requests_remaining, :x_requests_used, :x_requests_last, :cache_hit,
                         :started_at, :completed_at, :request_key)
                        """
                    ),
                    {
                        "provider": provider,
                        "endpoint": endpoint,
                        "sport": sport,
                        "markets": markets,
                        "regions": regions,
                        "event_count": event_count,
                        "status_code": status_code,
                        "x_requests_remaining": int(xr) if xr and str(xr).isdigit() else None,
                        "x_requests_used": int(xu) if xu and str(xu).isdigit() else None,
                        "x_requests_last": int(xl) if xl and str(xl).isdigit() else None,
                        "cache_hit": cache_hit,
                        "started_at": started_at,
                        "completed_at": completed_at,
                        "request_key": request_key,
                    },
                )
                await session.commit()
        except Exception as e:
            logger.debug("gateway call logging failed: %s", e)

    async def request(
        self,
        *,
        provider: str,
        endpoint: str,
        url: str,
        params: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        timeout_s: float = 15.0,
        data_class: str = "pregame_odds",
        sport: Optional[str] = None,
        markets: Optional[str] = None,
        regions: Optional[str] = None,
        force_refresh: bool = False,
        admin_override: bool = False,
        live_essential: bool = False,
    ) -> Optional[GatewayResult]:
        started = datetime.now(timezone.utc)
        req_key = self._request_key(provider, endpoint, params)
        ttl = self._ttl_for_class(data_class)
        if data_class == "historical" and not admin_override:
            return None

        budget = await self._budget_state(provider)
        if budget["mode"] == "emergency_freeze" and not admin_override:
            return None
        if budget["mode"] == "protection" and not (admin_override or live_essential):
            if data_class in {"historical", "player_props"}:
                return None

        if not force_refresh and ttl > 0:
            cached = await cache.get_json(req_key)
            if cached is not None:
                done = datetime.now(timezone.utc)
                result = GatewayResult(200, cached, {}, True, started, done)
                await self._persist_call(
                    provider=provider,
                    endpoint=endpoint,
                    sport=sport,
                    markets=markets,
                    regions=regions,
                    event_count=len(cached) if isinstance(cached, list) else None,
                    status_code=200,
                    headers={},
                    cache_hit=True,
                    started_at=started,
                    completed_at=done,
                    request_key=req_key,
                )
                return result

        lock = self._locks.setdefault(req_key, asyncio.Lock())
        async with lock:
            if req_key in self._inflight:
                return await self._inflight[req_key]
            dist_lock_key = f"lock:{req_key}"
            got_dist_lock = await cache.acquire_lock(dist_lock_key, ttl=max(5, ttl))
            if not got_dist_lock:
                # Another worker/node is refreshing this key. Serve current cache if present.
                cached = await cache.get_json(req_key)
                if cached is not None:
                    done = datetime.now(timezone.utc)
                    return GatewayResult(200, cached, {}, True, started, done)

            fut: asyncio.Future = asyncio.get_running_loop().create_future()
            self._inflight[req_key] = fut
            try:
                async with httpx.AsyncClient(timeout=timeout_s) as client:
                    if method.upper() == "GET":
                        resp = await client.get(url, params=params, headers=headers)
                    else:
                        resp = await client.request(method.upper(), url, params=params, headers=headers)
                done = datetime.now(timezone.utc)
                body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else None
                if resp.status_code == 200 and ttl > 0 and body is not None:
                    await cache.set_json(req_key, body, ttl=ttl)
                result = GatewayResult(resp.status_code, body, dict(resp.headers), False, started, done)
                await self._persist_call(
                    provider=provider,
                    endpoint=endpoint,
                    sport=sport,
                    markets=markets,
                    regions=regions,
                    event_count=len(body) if isinstance(body, list) else None,
                    status_code=resp.status_code,
                    headers=dict(resp.headers),
                    cache_hit=False,
                    started_at=started,
                    completed_at=done,
                    request_key=req_key,
                )
                fut.set_result(result)
                return result
            except Exception as e:
                fut.set_result(None)
                logger.error("external gateway request failed %s %s: %s", provider, endpoint, e)
                return None
            finally:
                self._inflight.pop(req_key, None)
                if got_dist_lock:
                    await cache.release_lock(dist_lock_key)

    async def quota_status(self, provider: str) -> Dict[str, Any]:
        return await self._budget_state(provider)


external_api_gateway = ExternalApiGateway()
