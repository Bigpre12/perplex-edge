"""
The Unified Odds API REST Client

Standardized production-grade client for The Odds API (V4).
Consolidates logic from legacy clients and ensures:
1. Robust Key Rotation across multiple API keys.
2. Daily Call Capping to protect quotas (~100k/mo).
3. Intelligent Caching (Redis + Memory fallback).
4. Consistent Interface for all ingestion and analytic services.

Methods:
    - get_active_sports(): List of in-season sports.
    - get_events(sport): Game schedule only (cheap, no odds).
    - get_live_odds(sport, markets): Real-time odds for games.
    - get_player_props(sport, event_id, markets): Deep player markets.
"""
import os
import time
import httpx # type: ignore
from services.api_telemetry import InstrumentedAsyncClient  # type: ignore
import logging
import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timezone, timedelta

from core.config import settings # type: ignore
from clients.base_client import ResilientBaseClient # type: ignore
from services.cache import cache # type: ignore
from api_utils.http import build_headers # type: ignore
from services.external_api_gateway import external_api_gateway

logger = logging.getLogger(__name__)

class OddsApiClient(ResilientBaseClient):
    """
    Client for TheOddsAPI (Live Odds, Historical, Scores).
    
    [ARCHITECTURAL RULE]
    This client is the SOLE authorized path for TheOddsAPI data.
    The frontend MUST NOT call TheOddsAPI directly. All requests must
    be routed through this backend service to ensure:
    1. API Key Security (Never exposed to browser)
    2. Response Caching (Lower latency & cost)
    3. Tier-Based Gating (Elite/Pro restrictions)
    """
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    TEAM_MARKETS = ["h2h", "spreads", "totals"]

    PLAYER_PROP_MARKETS = [
        "player_points", "player_rebounds", "player_assists",
        "player_threes", "player_blocks", "player_steals",
        "player_points_rebounds_assists", "player_points_rebounds",
        "player_points_assists", "player_first_touchdown_scorer",
        "player_anytime_touchdown_scorer", "player_pass_yds",
        "player_pass_tds", "player_rush_yds", "player_reception_yds",
        "player_receptions", "batter_hits", "batter_home_runs",
        "batter_rbis", "pitcher_strikeouts"
    ]

    @classmethod
    def get_markets_for_sport(cls, sport: str) -> str:
        """Returns only the valid team markets for the specified sport. Player props are fetched separately."""
        return ",".join(cls.TEAM_MARKETS)
    
    def __init__(self):
        # Load keys from centralized settings, then merge backup / legacy vars (deduped)
        key_list = [k for k in (settings.ODDS_API_KEYS or []) if k and str(k).strip()]
        for extra_var in ("ODDS_API_KEY_BACKUP", "THE_ODDS_API_KEY"):
            extra = (os.getenv(extra_var) or "").strip()
            if extra and extra not in key_list:
                key_list.append(extra)
        self.api_keys = key_list
        self.current_key_idx = 0
        # Last x-requests-remaining from The Odds API (used to skip expensive per-event prop calls)
        self._last_requests_remaining: Optional[int] = None
        # Auth/config failures: long cooldown (legacy env ODDS_API_KEY_COOLDOWN_SECONDS)
        self.dead_key_cooldown_auth = int(
            os.getenv(
                "ODDS_API_KEY_AUTH_COOLDOWN_SECONDS",
                os.getenv("ODDS_API_KEY_COOLDOWN_SECONDS", "3600"),
            )
        )
        # 429: short backoff so keys are not shelved for an hour on quota spikes
        self.dead_key_cooldown_429 = int(os.getenv("ODDS_API_KEY_RATE_LIMIT_COOLDOWN_SECONDS", "90"))

        # key_index -> unix time until this key is skipped
        self._dead_until: Dict[int, float] = {}

        # 404/EventNotFound Cache: (sport, event_id) -> unix timestamp until skipped
        # This prevents repeated calls for events that the API says don't exist.
        self._dead_events: Dict[Tuple[str, str], float] = {}
        self.dead_event_ttl = 3600  # 1 hour

        self.default_ttl = 300  # 5 min — standard odds
        self.long_ttl = 3600    # 1 hour — sports/metadata
        self.timeout = 15.0
        self.event_ids_ttl_seconds = int(os.getenv("THE_ODDS_API_EVENT_IDS_TTL_SECONDS", "300"))
        self._event_ids_cache: Dict[str, Tuple[float, Set[str]]] = {}
        self._last_all_dead_warn_ts: float = 0.0
        self._all_dead_warn_interval_seconds = int(
            os.getenv("ODDS_API_ALL_KEYS_DEAD_WARN_INTERVAL_SECONDS", "60")
        )
        self._all_keys_dead_until: Optional[datetime] = None

        # Limit per day (approx 100k/mo tier)
        self.max_daily_calls = int(os.getenv("THE_ODDS_API_MAX_CALLS_PER_DAY", 10000))
        # Optional hard cap on successful calls per calendar month (Redis counter).
        self.max_monthly_calls = int(
            os.getenv("THE_ODDS_API_MAX_CALLS_PER_MONTH")
            or os.getenv("ODDS_API_MONTHLY_LIMIT", "0")
        )
        # If >0 and remaining header falls below this, skip further get_player_props in ingest
        self.min_remaining_before_stop = int(os.getenv("THE_ODDS_API_MIN_REMAINING_BEFORE_STOP", "0"))

        if not self.api_keys:
            logger.warning(
                "OddsApiClient: no keys configured — The Odds API disabled "
                "(set ODDS_API_KEYS, THE_ODDS_API_KEY, ODDS_API_KEY, or THE_ODDS_API_KEY_0..N)"
            )
        else:
            safe_keys = [f"{k[:4]}****" for k in self.api_keys if k]
            logger.info(
                "OddsApiClient: %s key(s) configured (prefixes): %s",
                len(self.api_keys),
                ", ".join(safe_keys),
            )

    def _is_event_dead(self, sport: str, event_id: str) -> bool:
        """Checks if an event has recently returned a 404 or EVENT_NOT_FOUND."""
        until = self._dead_events.get((sport, event_id))
        if not until:
            return False
        if time.time() > until:
            del self._dead_events[(sport, event_id)]
            return False
        return True

    def _mark_event_dead(self, sport: str, event_id: str):
        """Shelves an event ID for an hour after it returns 404."""
        self._dead_events[(sport, event_id)] = time.time() + self.dead_event_ttl
        logger.info(f"Odds API: Shelving event {event_id} for {sport} (returned 404/Not Found)")

    def _is_key_dead(self, idx: int) -> bool:
        """True if key index is in cooldown until _dead_until[idx]."""
        until = self._dead_until.get(idx)
        if until is None:
            return False
        now = time.time()
        if now >= until:
            del self._dead_until[idx]
            logger.info("Odds API key index %s cooldown expired, retrying.", idx)
            return False
        return True

    def _mark_key_dead(self, idx: int, reason: str, *, status_code: Optional[int] = None):
        """Block key index until now + cooldown (shorter for 429 than for 401/403)."""
        # If 429 daily limit reached, cooldown for 24 hours (roughly until next reset)
        if status_code == 429 and "daily limit" in reason.lower():
            cooldown = 86400 # 24 hours
        else:
            cooldown = self.dead_key_cooldown_429 if status_code == 429 else self.dead_key_cooldown_auth
            
        self._dead_until[idx] = time.time() + cooldown
        logger.warning(
            "Odds API key index %s cooling %ss (%s): %s",
            idx,
            cooldown,
            "rate_limit" if status_code == 429 else "auth_or_config",
            reason,
        )

    def _all_keys_dead(self) -> bool:
        """Returns True if every key is currently marked dead."""
        if not self.api_keys:
            return True
        return all(self._is_key_dead(i) for i in range(len(self.api_keys)))

    def _in_global_dead_window(self) -> bool:
        if not self._all_keys_dead_until:
            return False
        if datetime.now(timezone.utc) >= self._all_keys_dead_until:
            self._all_keys_dead_until = None
            return False
        return True

    def _log_all_keys_dead_throttled(self) -> None:
        now = time.time()
        if now - self._last_all_dead_warn_ts >= self._all_dead_warn_interval_seconds:
            logger.warning("🚨 All Odds API keys are dead/cooling down. Skipping request.")
            self._last_all_dead_warn_ts = now

    def _enter_global_dead_window(self) -> None:
        now = datetime.now(timezone.utc)
        if not self._all_keys_dead_until or now >= self._all_keys_dead_until:
            self._all_keys_dead_until = now + timedelta(minutes=5)
            logger.warning("🚨 All Odds API keys are dead/cooling down. Entering 5-minute global backoff window.")

    def all_keys_unavailable(self) -> bool:
        """
        True when The Odds API cannot be called (no keys configured, or all keys in cooldown).
        Used to skip doomed per-event prop fetches without log spam.
        """
        if not self.api_keys:
            return True
        return self._in_global_dead_window() or self._all_keys_dead()

    def all_keys_dead(self) -> bool:
        return self.all_keys_unavailable()

    def key_health(self) -> Dict[str, Any]:
        total = len(self.api_keys)
        dead = sum(1 for i in range(total) if self._is_key_dead(i))
        alive = max(0, total - dead)
        return {
            "keys_alive": alive,
            "keys_dead": dead,
            "cooling_until": self._all_keys_dead_until.isoformat() if self._all_keys_dead_until else None,
        }

    @property
    def is_configured(self) -> bool:
        """Returns True if at least one API key is available."""
        return bool(self.api_keys and any(self.api_keys))

    def _get_api_key(self) -> str:
        if not self.is_configured:
            return ""
        return self.api_keys[self.current_key_idx % len(self.api_keys)]

    def _rotate_key(self) -> bool:
        if len(self.api_keys) <= 1:
            return False
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        logger.warning(f"🔄 Rotated to Odds API key index {self.current_key_idx}")
        return True

    async def _get_today_count(self) -> int:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key = f"odds_api_usage:{today}"
        count = await cache.get(key)
        return int(count) if count else 0

    async def _increment_count(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key = f"odds_api_usage:{today}"
        count = await self._get_today_count()
        await cache.set(key, str(count + 1), ttl=86400)

    async def _get_month_count(self) -> int:
        if self.max_monthly_calls <= 0:
            return 0
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        key = f"odds_api_usage_month:{month}"
        raw = await cache.get(key)
        return int(raw) if raw else 0

    async def _increment_month_count(self) -> None:
        if self.max_monthly_calls <= 0:
            return
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        key = f"odds_api_usage_month:{month}"
        n = await self._get_month_count()
        await cache.set(key, str(n + 1), ttl=2678400)

    def _capture_quota_headers(self, resp: Any) -> None:
        rem = resp.headers.get("x-requests-remaining") or resp.headers.get(
            "X-Requests-Remaining"
        )
        if rem is None:
            return
        try:
            self._last_requests_remaining = int(rem)
        except (TypeError, ValueError):
            pass

    def quota_conserve_player_props(self) -> bool:
        """
        True when ingest should stop issuing further TOA per-event player prop requests.
        Uses last x-requests-remaining vs THE_ODDS_API_MIN_REMAINING_BEFORE_STOP (0 = off).
        """
        if self.min_remaining_before_stop <= 0:
            return False
        r = self._last_requests_remaining
        return r is not None and r < self.min_remaining_before_stop

    @staticmethod
    def is_valid_event_id(event_id: str) -> bool:
        return isinstance(event_id, str) and len(event_id) == 32

    async def get_valid_event_ids(self, sport: str, force_refresh: bool = False) -> Set[str]:
        now = time.time()
        cached = self._event_ids_cache.get(sport)
        if not force_refresh and cached and now < cached[0]:
            return cached[1]

        events = await self.get_events(sport, use_cache=False, ttl=self.event_ids_ttl_seconds)
        valid_ids: Set[str] = set()
        for event in events:
            if not isinstance(event, dict):
                continue
            eid = event.get("id")
            if self.is_valid_event_id(eid):
                valid_ids.add(eid)

        self._event_ids_cache[sport] = (now + self.event_ids_ttl_seconds, valid_ids)
        return valid_ids

    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        ttl: Optional[int] = None,
        quota_sport: Optional[str] = None,
        quota_market: Optional[str] = None,
    ) -> Any:
        # 1. Configuration & Global Gating
        if not self.is_configured:
            logger.warning("Odds API missing credentials: ODDS_API_KEYS not set or empty")
            return None

        # Check if we are in a 5-minute global backoff (all keys recently failed)
        if self._in_global_dead_window():
            self._log_all_keys_dead_throttled()
            return None

        # Check if an event ID was passed and if it's already marked as dead (404)
        if quota_sport and "/events/" in endpoint:
            # Extract event_id from endpoint if possible
            eid = endpoint.split("/events/")[1].split("/")[0] if "/events/" in endpoint else None
            if eid and self._is_event_dead(quota_sport, eid):
                logger.debug(f"Odds API: Skipping request for dead event {eid}")
                return None

        # 2. Daily & Monthly Quota Checks
        count = await self._get_today_count()
        if count >= self.max_daily_calls and not settings.DEVELOPMENT_MODE:
            logger.warning(f"🚨 Odds API daily limit ({self.max_daily_calls}) reached. Aborting.")
            self._enter_global_dead_window() # Backoff for 5 mins to stop the flood
            return None

        if self.max_monthly_calls > 0 and not settings.DEVELOPMENT_MODE:
            mcount = await self._get_month_count()
            if mcount >= self.max_monthly_calls:
                logger.warning(
                    "🚨 Odds API monthly limit (%s) reached (%s). Aborting.",
                    self.max_monthly_calls,
                    mcount,
                )
                self._enter_global_dead_window()
                return None

        params = params.copy() if params else {}
        ttl = ttl if ttl is not None else self.default_ttl
        
        # 3. Cache Check
        cache_key = f"odds_api_v4:{endpoint}:{str(sorted(params.items()))}"
        if use_cache:
            cached = await cache.get_json(cache_key)
            if cached:
                return cached

        # 4. DB-backed monthly quota / hard stop
        try:
            from db.session import async_session_maker
            from services.odds_quota_store import raise_if_quota_blocked

            async with async_session_maker() as _qs:
                blocked, reason = await raise_if_quota_blocked(_qs)
            if blocked:
                logger.warning("QUOTA BLOCKED before HTTP (%s): monthly quota exhausted.", reason)
                self._enter_global_dead_window()
                return None
        except Exception as e:
            logger.warning("Odds quota pre-check failed — BLOCKING request (fail-closed): %s", e)
            return None

        # 5. Execute Request with Waterfall Rotation
        for _ in range(len(self.api_keys) or 1):
            # If current key is dead, rotate. If we can't rotate to a live key, we're done.
            if self._is_key_dead(self.current_key_idx):
                if not self._rotate_key() or self._all_keys_dead():
                    self._enter_global_dead_window()
                    return None
                continue

            key = self._get_api_key()
            if not key:
                break

            p = params.copy()
            p["apiKey"] = key
            url = f"{self.BASE_URL}{endpoint}"
            
            try:
                data_class = "pregame_odds"
                if endpoint.endswith("/sports"):
                    data_class = "sports"
                elif endpoint.endswith("/events"):
                    data_class = "events"
                elif "/events/" in endpoint and "/odds" in endpoint:
                    data_class = "player_props"
                
                gw = await external_api_gateway.request(
                    provider="theoddsapi",
                    endpoint=endpoint,
                    url=url,
                    params=p,
                    method=method.upper(),
                    timeout_s=self.timeout,
                    data_class=data_class,
                    sport=quota_sport,
                    markets=(quota_market or str(params.get("markets") or ""))[:256] if params else quota_market,
                    regions=str(params.get("regions") or "us") if params else "us",
                    force_refresh=not use_cache,
                )
                
                if not gw:
                    return None
                
                self._capture_quota_headers(type("RespShim", (), {"headers": gw.headers})())

                if gw.status_code == 200:
                    data = gw.data or {}
                    await self._increment_count()
                    await self._increment_month_count()
                    
                    try:
                        from db.session import async_session_maker
                        from services.odds_quota_store import apply_quota_headers
                        async with async_session_maker() as _qs:
                            await apply_quota_headers(
                                _qs,
                                remaining_header=gw.headers.get("x-requests-remaining") or gw.headers.get("X-Requests-Remaining"),
                                used_header=gw.headers.get("x-requests-used") or gw.headers.get("X-Requests-Used"),
                                sport=quota_sport,
                                market=quota_market,
                                endpoint_path=endpoint,
                            )
                    except Exception as e:
                        logger.warning("Odds quota header persist failed: %s", e)
                    
                    await cache.set_json(cache_key, data, ttl=ttl)
                    return data

                elif gw.status_code in (401, 403):
                    self._mark_key_dead(self.current_key_idx, f"Auth Failure ({gw.status_code})", status_code=gw.status_code)
                    if not self._rotate_key():
                        self._enter_global_dead_window()
                        break
                    continue
                
                elif gw.status_code == 429:
                    # Mark current key dead (24h if daily limit, else short)
                    reason = str(gw.data).lower()
                    self._mark_key_dead(self.current_key_idx, f"Rate Limit: {reason[:100]}", status_code=429)
                    if not self._rotate_key():
                        self._enter_global_dead_window()
                        break
                    continue

                elif gw.status_code in (404, 422):
                    # 404: Not Found, 422: Unprocessable (often means invalid event_id for the sport)
                    if quota_sport and "/events/" in endpoint:
                        eid = endpoint.split("/events/")[1].split("/")[0]
                        self._mark_event_dead(quota_sport, eid)
                    return None
                
                else:
                    logger.error(f"❌ Odds API error {gw.status_code} for {endpoint}")
                    return None
                    
            except Exception as e:
                logger.error(f"Odds API connection error: {e}")
                return None
        
        return None

    # --- Core API Methods ---

    async def get_active_sports(self, use_cache: bool = True, ttl: Optional[int] = None) -> List[Dict]:
        """Fetch all currently active sports."""
        return (
            await self._make_request(
                "/sports",
                use_cache=use_cache,
                ttl=ttl or self.long_ttl,
                quota_market="sports_list",
            )
            or []
        )

    async def get_events(self, sport: str, use_cache: bool = True, ttl: Optional[int] = None) -> List[Dict]:
        """Fetch game schedules (cheap, no odds results)."""
        return (
            await self._make_request(
                f"/sports/{sport}/events",
                use_cache=use_cache,
                ttl=ttl,
                quota_sport=sport,
                quota_market="events",
            )
            or []
        )

    async def get_live_odds(self, sport: str, regions: str = "us", markets: Optional[str] = None, use_cache: bool = True, ttl: Optional[int] = None) -> List[Dict]:
        """Fetch real-time odds for games."""
        if os.getenv("ODDS_API_FORCE_US_ONLY", "true").strip().lower() in {"1", "true", "yes", "on"}:
            regions = "us"
        if os.getenv("ODDS_API_FORCE_CORE_MARKETS", "false").strip().lower() in {"1", "true", "yes", "on"}:
            markets = "h2h"
        params = {
            "regions": regions,
            "markets": markets or self.get_markets_for_sport(sport),
            "bookmakers": "pinnacle,draftkings,fanduel,betmgm,caesars,bet365",
            "oddsFormat": "american",
            "dateFormat": "iso"
        }
        return (
            await self._make_request(
                f"/sports/{sport}/odds",
                params=params,
                use_cache=use_cache,
                ttl=ttl,
                quota_sport=sport,
                quota_market=str(params.get("markets") or "")[:256] or "team_odds",
            )
            or []
        )

    async def get_player_props(self, sport: str, event_id: str, markets: str, regions: str = "us", use_cache: bool = True, ttl: Optional[int] = None) -> Dict:
        """Fetch specific player props for an event."""
        if os.getenv("ODDS_API_FORCE_US_ONLY", "true").strip().lower() in {"1", "true", "yes", "on"}:
            regions = "us"
        if not self.is_valid_event_id(event_id):
            logger.warning("Skipping TheOddsAPI request: invalid event_id '%s'", event_id)
            return {}
        valid_ids = await self.get_valid_event_ids(sport)
        if valid_ids and event_id not in valid_ids:
            logger.warning(
                "Skipping TheOddsAPI request: stale/unknown event_id '%s' for sport '%s'",
                event_id,
                sport,
            )
            return {}

        params = {
            "regions": regions,
            "markets": markets,
            "bookmakers": "pinnacle,draftkings,fanduel,betmgm,caesars,bet365",
            "oddsFormat": "american",
            "dateFormat": "iso"
        }
        # Note: endpoint returns a dict for single event ID if passed as path param
        return (
            await self._make_request(
                f"/sports/{sport}/events/{event_id}/odds",
                params=params,
                use_cache=use_cache,
                ttl=ttl,
                quota_sport=sport,
                quota_market=(markets or "")[:256] or "player_props",
            )
            or {}
        )

    # --- Compatibility Aliases ---
    async def get_odds(self, sport: str, regions: str = "us", markets: Optional[str] = None) -> List[Dict]:
        return await self.get_live_odds(sport, regions, markets)

    async def get_event_odds(self, sport: str, event_id: str, regions: str = "us", markets: Optional[str] = None) -> Dict:
        """Fetch odds for a specific event ID."""
        if not self.is_valid_event_id(event_id):
            logger.warning("Skipping TheOddsAPI request: invalid event_id '%s'", event_id)
            return {}
        valid_ids = await self.get_valid_event_ids(sport)
        if valid_ids and event_id not in valid_ids:
            logger.warning(
                "Skipping TheOddsAPI request: stale/unknown event_id '%s' for sport '%s'",
                event_id,
                sport,
            )
            return {}

        params = {
            "regions": regions,
            "markets": markets or self.get_markets_for_sport(sport),
            "oddsFormat": "american",
            "dateFormat": "iso"
        }
        return (
            await self._make_request(
                f"/sports/{sport}/events/{event_id}/odds",
                params=params,
                quota_sport=sport,
                quota_market=str(params.get("markets") or "")[:256] or "event_odds",
            )
            or {}
        )

    async def fetch_odds(self, sport: str, regions: str = "us", markets: Optional[str] = None) -> List[Dict]:
        return await self.get_live_odds(sport, regions, markets)

    async def fetch_events(self, sport: str) -> List[Dict]:
        return await self.get_events(sport)

    async def fetch_player_props(self, sport: str, event_id: str, markets: str, regions: str = "us") -> Dict:
        return await self.get_player_props(sport, event_id, markets, regions)

# --- Global Singletons ---
odds_api_client = OddsApiClient()
odds_api = odds_api_client
