"""
BetStack free sports API client (api.betstack.dev).

Docs: https://api.betstack.dev/docs — GET /api/v1/events?league=...&include_lines=true
Auth: X-API-Key header. Enterprise stack (api.betstack.io/bc, /be) is separate.
"""
from __future__ import annotations

import asyncio
import os
import httpx
from services.api_telemetry import InstrumentedAsyncClient
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

from api_utils.http import build_headers
from core.config import settings
from services.commence_time import reject_absurd_future

logger = logging.getLogger(__name__)

# Free-tier spacing: default 60s between Betstack HTTP attempts (per process).
# Interval check + stamp run under _betstack_http_lock (stamp before I/O); HTTP runs outside the
# lock so waiters are not blocked for the full round-trip. Multiple replicas still share one
# key's quota unless each worker uses its own key or a higher tier.
_betstack_last_request_monotonic: float = 0.0
_betstack_http_lock = asyncio.Lock()

# Lucrix sport_key -> BetStack `league` query param (see /docs Events section)
LUCRIX_TO_BETSTACK_LEAGUE: Dict[str, str] = {
    "basketball_nba": "basketball_nba",
    "americanfootball_nfl": "americanfootball_nfl",
    "baseball_mlb": "baseball_mlb",
    "icehockey_nhl": "icehockey_nhl",
    "basketball_ncaab": "basketball_ncaab",
    "americanfootball_ncaaf": "americanfootball_ncaaf",
    "basketball_wnba": "basketball_wnba",
    "soccer_epl": "soccer_epl",
    "soccer_usa_mls": "soccer_usa_mls",
    "mma_mixed_martial_arts": "mma_mixed_martial_arts",
}

# Short aliases passed from older callers
SHORT_SPORT_TO_LEAGUE = {
    "nba": "basketball_nba",
    "nfl": "americanfootball_nfl",
    "mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
    "ncaab": "basketball_ncaab",
    "ncaaf": "americanfootball_ncaaf",
}


def resolve_betstack_league_key(sport: str) -> str:
    s = (sport or "").strip().lower()
    if s in LUCRIX_TO_BETSTACK_LEAGUE:
        return LUCRIX_TO_BETSTACK_LEAGUE[s]
    if s in SHORT_SPORT_TO_LEAGUE:
        return SHORT_SPORT_TO_LEAGUE[s]
    if "_" in s:
        return s
    return "basketball_nba"


class BetstackClient:
    def __init__(self):
        self.api_key = settings.BETSTACK_API_KEY
        self.base_url = (settings.BETSTACK_BASE_URL or "").strip().rstrip("/")
        self.timeout = 25.0
        self._missing_key_logged = False
        self._missing_url_logged = False
        self._warned_remote = False
        self._remote_disabled = False
        if not self.base_url:
            logger.warning("Betstack: BETSTACK_BASE_URL missing; Betstack client will stay disabled.")

    @property
    def available(self) -> bool:
        return bool(self.api_key) and bool(self.base_url) and not self._remote_disabled

    def _disable_remote(self, reason: str) -> None:
        if not self._remote_disabled:
            self._remote_disabled = True
            logger.warning(
                "Betstack: disabling client for this process (%s). Set BETSTACK_BASE_URL and paths correctly to re-enable.",
                reason,
            )

    async def _get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        global _betstack_last_request_monotonic
        if not self.api_key:
            if not self._missing_key_logged:
                logger.warning("Betstack API missing credentials: BETSTACK_API_KEY not set")
                self._missing_key_logged = True
            return None
        if not self.base_url:
            if not self._missing_url_logged:
                logger.warning(
                    "Betstack: BETSTACK_BASE_URL is not set — use https://api.betstack.dev/api/v1 for the free API."
                )
                self._missing_url_logged = True
            return None
        if self._remote_disabled:
            return None

        min_iv = float(os.getenv("BETSTACK_MIN_INTERVAL_SECONDS", "60"))

        headers = build_headers(
            {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            }
        )
        rel = path.lstrip("/")
        url = urljoin(f"{self.base_url}/", rel)

        async with _betstack_http_lock:
            now_m = time.monotonic()
            elapsed = now_m - _betstack_last_request_monotonic
            if min_iv > 0 and _betstack_last_request_monotonic > 0 and elapsed < min_iv:
                logger.info(
                    "Betstack: skipping request (spacing %.1fs < %.0fs); set BETSTACK_MIN_INTERVAL_SECONDS to adjust",
                    elapsed,
                    min_iv,
                )
                return None
            if min_iv > 0:
                _betstack_last_request_monotonic = time.monotonic()

        async with InstrumentedAsyncClient(provider="betstack", purpose="polling", timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers, params=params or {}, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                code = e.response.status_code
                if code == 429:
                    logger.warning(
                        "Betstack rate limit (429): free tier allows ~1 req/60s per key. Skipping this call."
                    )
                    return None
                if code == 404:
                    parsed = urlsplit(str(e.response.url))
                    sanitized_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))
                    logger.warning(
                        "Betstack 404 at: %s — check base URL and path config",
                        sanitized_url,
                    )
                    return None
                if code in (401, 403):
                    if not self._warned_remote:
                        logger.warning(
                            "Betstack API HTTP %s for %s — check API key and BETSTACK_BASE_URL.",
                            code,
                            url,
                        )
                        self._warned_remote = True
                    self._disable_remote(f"HTTP {code}")
                else:
                    logger.error("Betstack API error %s: %s", code, e.response.text[:500])
                return None
            except Exception as e:
                logger.error("Betstack request failed: %s", e)
                return None

    async def list_events(
        self,
        league_key: str,
        *,
        include_lines: bool = True,
        completed: Optional[bool] = False,
    ) -> List[Dict[str, Any]]:
        """GET /events — consensus events with optional embedded lines."""
        params: Dict[str, Any] = {"league": league_key, "include_lines": str(include_lines).lower()}
        if completed is not None:
            params["completed"] = str(completed).lower()
        data = await self._get_json("events", params=params)
        if data is None:
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            inner = data.get("events") or data.get("data") or data.get("items")
            if isinstance(inner, list):
                return inner
        return []

    async def get_lines_for_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """GET /lines?event_id= — when events do not embed lines."""
        data = await self._get_json("lines", params={"event_id": event_id})
        if data is None:
            return None
        if isinstance(data, dict) and "event_id" in data:
            return data
        if isinstance(data, list) and data:
            for row in data:
                if isinstance(row, dict) and row.get("event_id") == event_id:
                    return row
            return data[0] if isinstance(data[0], dict) else None
        return None

    @staticmethod
    def _pick_line_obj(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        lines = event.get("lines")
        if isinstance(lines, dict):
            return lines
        if isinstance(lines, list) and lines:
            last = lines[-1]
            return last if isinstance(last, dict) else None
        return None

    async def events_to_prop_dicts(self, lucrix_sport_key: str, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map BetStack events + consensus lines into dicts compatible with PropRecord / unified_ingestion."""
        logger.debug("Betstack: mapping %s events for sport %s", len(events), lucrix_sport_key)
        out: List[Dict[str, Any]] = []
        for ev in events:
            if not isinstance(ev, dict):
                continue
            eid = ev.get("id")
            if eid is None:
                continue
            game_id = str(eid)
            home = ev.get("home_team") or ""
            away = ev.get("away_team") or ""
            commence = ev.get("commence_time")
            gtime = None
            if isinstance(commence, str):
                try:
                    gtime = datetime.fromisoformat(commence.replace("Z", "+00:00"))
                    gtime = reject_absurd_future(gtime)
                except ValueError:
                    gtime = None

            line_obj = self._pick_line_obj(ev)
            if line_obj is None:
                line_obj = await self.get_lines_for_event(int(eid)) if str(eid).isdigit() else None
            if not isinstance(line_obj, dict):
                continue

            # Totals (game-level; no player)
            total_num = line_obj.get("total_number")
            over_j = line_obj.get("over_line")
            under_j = line_obj.get("under_line")
            if total_num is not None and over_j is not None and under_j is not None:
                out.append(
                    {
                        "game_id": game_id,
                        "player_name": None,
                        "market_key": "totals",
                        "line": float(total_num),
                        "odds_over": float(over_j),
                        "odds_under": float(under_j),
                        "home_team": home,
                        "away_team": away,
                        "game_start_time": gtime,
                    }
                )

            # Point spread (home line number + prices)
            ps_h = line_obj.get("point_spread_home")
            ps_a = line_obj.get("point_spread_away")
            pj_h = line_obj.get("point_spread_home_line")
            pj_a = line_obj.get("point_spread_away_line")
            if ps_h is not None and pj_h is not None and pj_a is not None:
                out.append(
                    {
                        "game_id": game_id,
                        "player_name": None,
                        "market_key": "spreads",
                        "line": float(ps_h),
                        "odds_over": float(pj_h),
                        "odds_under": float(pj_a),
                        "home_team": home,
                        "away_team": away,
                        "game_start_time": gtime,
                    }
                )

            # Moneyline (store home / away prices as over/under fields for compatibility)
            ml_h = line_obj.get("money_line_home")
            ml_a = line_obj.get("money_line_away")
            if ml_h is not None and ml_a is not None:
                out.append(
                    {
                        "game_id": game_id,
                        "player_name": None,
                        "market_key": "h2h",
                        "line": 0.0,
                        "odds_over": float(ml_h),
                        "odds_under": float(ml_a),
                        "home_team": home,
                        "away_team": away,
                        "game_start_time": gtime,
                    }
                )

        return out

    async def get_player_props(self, sport: str = "basketball_nba") -> List[Dict[str, Any]]:
        """
        BetStack free API has no player-props endpoint; return team markets (totals, spreads, h2h) as prop-shaped dicts.
        `sport` may be a Lucrix key (basketball_nba) or short alias (nba).
        """
        league = resolve_betstack_league_key(sport)
        events = await self.list_events(league, include_lines=True, completed=False)
        return await self.events_to_prop_dicts(league, events)

    async def get_odds(self, sport: str = "nba") -> List[Dict[str, Any]]:
        """Return raw event objects for the league (for callers expecting a list)."""
        league = resolve_betstack_league_key(sport)
        return await self.list_events(league, include_lines=True, completed=False)


betstack_client = BetstackClient()


def get_betstack_client() -> Optional[BetstackClient]:
    if not betstack_client.available:
        logger.debug("Betstack API client requested but credentials not set.")
        return None
    return betstack_client
