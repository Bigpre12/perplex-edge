"""
Waterfall Router — /api/waterfall/*

Exposes the full priority-waterfall data pipeline as a first-class REST API.
Providers cascade in order: Odds API → ESPN → TheSportsDB → TheRundown → BallDontLie → MySportsFeeds → SportsGameOdds

Endpoints:
  GET  /api/waterfall/status          — live provider health probe
  GET  /api/waterfall/providers       — full registry: rate limits, capabilities, configured chains
  GET  /api/waterfall/sports          — all sports + their stats/odds provider chains
  GET  /api/waterfall/games           — games via waterfall with per-provider trace annotation
  GET  /api/waterfall/odds            — team-market odds (h2h, spreads, totals) via odds chain
  GET  /api/waterfall/props           — player props for a specific game via Odds API
  POST /api/waterfall/refresh         — force-bust cache + re-fetch a sport from scratch
"""

import os
import asyncio
import logging
import httpx
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from core.waterfall_config import all_registry_sport_keys
from real_data_connector import real_data_connector, SPORT_KEY_TO_ID
from services.waterfall_router import waterfall_router
from services.cache import cache

logger = logging.getLogger(__name__)
router = APIRouter(tags=["waterfall"])

# ---------------------------------------------------------------------------
# Provider registry metadata
# ---------------------------------------------------------------------------

PROVIDER_META = {
    "the_odds_api": {
        "name": "The Odds API",
        "url": "https://the-odds-api.com",
        "quota": "500 credits/month",
        "key_env": "THE_ODDS_API_KEY",
        "capabilities": ["h2h", "spreads", "totals", "player_props", "all_major_sports"],
        "probe_url": "https://api.the-odds-api.com/v4/sports?apiKey={key}",
    },
    "betstack": {
        "name": "BetStack (free API)",
        "url": "https://api.betstack.dev",
        "quota": "Free tier rate limits",
        "key_env": "BETSTACK_API_KEY",
        "capabilities": ["consensus_lines", "events"],
        "probe_url": None,
    },
    "espn": {
        "name": "ESPN Free API",
        "url": "https://site.api.espn.com",
        "quota": "Unlimited (no key required)",
        "key_env": None,
        "capabilities": ["games", "scores", "schedules", "all_sports"],
        "probe_url": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    },
    "thesportsdb": {
        "name": "TheSportsDB",
        "url": "https://www.thesportsdb.com",
        "quota": "Free tier — $0 key",
        "key_env": "THESPORTSDB_API_KEY",
        "capabilities": ["games", "scores", "schedules", "mma", "all_sports"],
        "probe_url": "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={today}&s=Basketball",
    },
    "therundown": {
        "name": "TheRundown",
        "url": "https://therundown.io",
        "quota": "20k data points/day",
        "key_env": "THERUNDOWN_API_KEY",
        "capabilities": ["games", "odds", "3_books", "nfl_nba_mlb_nhl"],
        "probe_url": None,
    },
    "balldontlie": {
        "name": "BallDontLie",
        "url": "https://api.balldontlie.io",
        "quota": "Free forever",
        "key_env": "BALLDONTLIE_API_KEY",
        "capabilities": ["nba_games", "nba_stats", "nfl_games", "mlb_games", "nhl_games", "ncaab_games"],
        "probe_url": "https://api.balldontlie.io/v1/games",
    },
    "mysportsfeeds": {
        "name": "MySportsFeeds",
        "url": "https://api.mysportsfeeds.com",
        "quota": "Free personal tier",
        "key_env": "MYSPORTSFEEDS_API_KEY",
        "capabilities": ["nfl_stats", "nba_stats", "mlb_stats", "nhl_stats", "deep_player_stats"],
        "probe_url": None,
    },
    "sportsgameodds": {
        "name": "SportsGameOdds",
        "url": "https://sportsgameodds.com",
        "quota": "1k objects/month",
        "key_env": "SPORTSGAMEODDS_API_KEY",
        "capabilities": ["ufc_odds", "alt_lines", "all_sports"],
        "probe_url": None,
    },
    "api_sports": {
        "name": "API-Sports",
        "url": "https://api-sports.io",
        "quota": "100 requests/day (Free)",
        "key_env": "API_SPORTS_KEY",
        "capabilities": ["live_scores", "fixtures", "all_major_sports"],
        "probe_url": "https://v3.football.api-sports.io/status",
    },
    "sportmonks": {
        "name": "Sportmonks",
        "url": "https://sportmonks.com",
        "quota": "V3 Free tier",
        "key_env": "SPORTMONKS_API_KEY",
        "capabilities": ["football_v3", "basketball", "odds"],
        "probe_url": "https://api.sportmonks.com/v3/my/profile",
    },
    "isports_api": {
        "name": "iSports API",
        "url": "https://isportsapi.com",
        "quota": "Trial tier",
        "key_env": "ISPORTS_ACCOUNT / ISPORTS_SECRET",
        "capabilities": ["schedules", "scores", "odds"],
        "probe_url": "https://api.isportsapi.com/sport/football/schedule",
    },
    "isports": {
        "name": "iSports API",
        "url": "https://isportsapi.com",
        "quota": "Trial tier",
        "key_env": "ISPORTS_ACCOUNT / ISPORTS_SECRET",
        "capabilities": ["schedules", "scores", "odds"],
        "probe_url": "https://api.isportsapi.com/sport/football/schedule",
    },
}

# Ordered waterfall chain (default)
WATERFALL_ORDER = [
    "the_odds_api",
    "betstack",
    "api_sports",
    "sportmonks",
    "isports_api",
    "isports",
    "espn",
    "thesportsdb",
    "therundown",
    "balldontlie",
    "mysportsfeeds",
    "sportsgameodds",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def _probe_espn() -> dict:
    """Quick probe to ESPN with a 5 s timeout."""
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            return {"healthy": r.status_code < 400, "status_code": r.status_code}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def _probe_odds_api() -> dict:
    """Probe The Odds API sports list (very cheap — 0 credits used)."""
    from core.config import settings
    keys = settings.ODDS_API_KEYS
    if not keys:
        return {"healthy": False, "error": "No Odds API keys configured"}
    key = keys[0]
    url = f"https://api.the-odds-api.com/v4/sports?apiKey={key}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            return {
                "healthy": r.status_code == 200,
                "status_code": r.status_code,
                "remaining_requests": r.headers.get("x-requests-remaining"),
                "used_requests": r.headers.get("x-requests-used"),
            }
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def _probe_thesportsdb() -> dict:
    """Probe TheSportsDB free events endpoint."""
    today = _today_str()
    url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={today}&s=Basketball"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            return {"healthy": r.status_code < 400, "status_code": r.status_code}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def _probe_balldontlie() -> dict:
    """Probe BallDontLie top-level games list."""
    from core.config import settings
    key = settings.BALLDONTLIE_API_KEY if hasattr(settings, 'BALLDONTLIE_API_KEY') else os.getenv("BALLDONTLIE_API_KEY", "")
    headers = {"Authorization": key} if key else {}
    url = "https://api.balldontlie.io/v1/games"
    try:
        async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
            r = await client.get(url, params={"per_page": 1})
            return {"healthy": r.status_code == 200, "status_code": r.status_code}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def _probe_api_sports() -> dict:
    """Probe API-Sports status endpoint."""
    from core.config import settings
    key = settings.API_SPORTS_KEY
    if not key:
        return {"healthy": False, "error": "API_SPORTS_KEY not set"}
    url = "https://v3.football.api-sports.io/status"
    try:
        async with httpx.AsyncClient(timeout=5.0, headers={"x-apisports-key": key}) as client:
            r = await client.get(url)
            return {"healthy": r.status_code == 200, "status_code": r.status_code}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def _probe_sportmonks() -> dict:
    """Probe Sportmonks profile endpoint."""
    from core.config import settings
    key = getattr(settings, 'SPORTMONKS_KEY', None) or os.getenv("SPORTMONKS_API_KEY", "")
    if not key:
        return {"healthy": False, "error": "SPORTMONKS_KEY not set"}
    url = f"https://api.sportmonks.com/v3/my/profile?api_token={key}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            return {"healthy": r.status_code == 200, "status_code": r.status_code}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def _probe_isports_api() -> dict:
    """Probe iSports API with a simple schedule call."""
    from core.config import settings
    # iSports V3 uses account + secret auth
    account = os.getenv("ISPORTS_ACCOUNT", "")
    secret = os.getenv("ISPORTS_SECRET", "")
    if not account or not secret:
        return {"healthy": False, "error": "ISPORTS credentials not set"}
    url = f"https://api.isportsapi.com/sport/football/schedule?account={account}&secret={secret}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            return {"healthy": r.status_code == 200, "status_code": r.status_code}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def _probe_unprobed(provider_key: str) -> dict:
    """Placeholder for providers with no safe probe endpoint."""
    return {"healthy": None, "note": "no probe endpoint — provider assumed available if key is set"}


PROBE_FNS = {
    "the_odds_api": _probe_odds_api,
    "espn": _probe_espn,
    "thesportsdb": _probe_thesportsdb,
    "balldontlie": _probe_balldontlie,
    "api_sports": _probe_api_sports,
    "sportmonks": _probe_sportmonks,
    "isports_api": _probe_isports_api,
    "isports": _probe_isports_api,
    "betstack": lambda: _probe_unprobed("betstack"),
    "therundown":    lambda: _probe_unprobed("therundown"),
    "mysportsfeeds": lambda: _probe_unprobed("mysportsfeeds"),
    "sportsgameodds": lambda: _probe_unprobed("sportsgameodds"),
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/providers")
async def list_providers():
    """
    Full provider registry.
    Returns metadata on all 7 waterfall providers: name, quota, env key, capabilities.
    """
    return {
        "total": len(PROVIDER_META),
        "waterfall_order": WATERFALL_ORDER,
        "providers": PROVIDER_META,
        "timestamp": _now_iso(),
        "error": None,
    }


@router.get("/sports")
async def list_sports():
    """
    All configured sports with their stats and odds provider chains.
    Useful for the frontend to render provider badges and capability matrices.
    """
    sports = {}
    all_keys = set(all_registry_sport_keys()) | set(SPORT_KEY_TO_ID.keys())

    for sport_key in sorted(all_keys):
        display = sport_key.replace("_", " ").title()
        sports[sport_key] = {
            "sport_key": sport_key,
            "display_name": display,
            "sport_id": SPORT_KEY_TO_ID.get(sport_key),
            "stats_providers": real_data_connector.get_waterfall_chain(sport_key, data_type="stats"),
            "odds_providers": real_data_connector.get_waterfall_chain(sport_key, data_type="odds"),
        }

    return {
        "total": len(sports),
        "items": list(sports.values()),
        "timestamp": _now_iso(),
        "error": None,
    }


@router.get("/status")
async def provider_status():
    """
    Live health probe of all waterfall providers.
    Runs probes in parallel to minimize latency. Non-probeable providers
    are returned with healthy=null and a note explaining why.
    """
    cached = await cache.get_json("waterfall:status")
    if cached:
        cached["from_cache"] = True
        return cached

    probe_tasks = {key: fn() for key, fn in PROBE_FNS.items()}
    results_raw = await asyncio.gather(*probe_tasks.values(), return_exceptions=True)

    statuses = {}
    all_healthy = True
    for key, result in zip(probe_tasks.keys(), results_raw):
        if isinstance(result, Exception):
            statuses[key] = {"healthy": False, "error": str(result)}
            all_healthy = False
        else:
            statuses[key] = result
            if result.get("healthy") is False:
                all_healthy = False

    payload = {
        "overall": "healthy" if all_healthy else "degraded",
        "providers": {
            key: {
                "name": PROVIDER_META[key]["name"],
                **statuses.get(key, {"healthy": None}),
            }
            for key in WATERFALL_ORDER
        },
        "timestamp": _now_iso(),
        "from_cache": False,
        "error": None,
    }

    # Cache for 60 s to avoid hammering providers on every frontend refresh
    await cache.set_json("waterfall:status", payload, ttl=60)
    return payload


@router.get("/games")
async def waterfall_games(
    sport: str = Query("basketball_nba", description="Sport key, e.g. basketball_nba"),
):
    """
    Fetch live games via the full waterfall provider chain and return which
    provider actually served the data (source annotation per game).
    """
    try:
        games = await real_data_connector.fetch_games_by_sport(sport)
        source = games[0].get("source", "unknown") if games else "none"
        return {
            "sport": sport,
            "count": len(games),
            "serving_provider": source,
            "items": games,
            "timestamp": _now_iso(),
            "error": None,
        }
    except Exception as e:
        logger.error(f"[waterfall/games] {sport}: {e}")
        return {
            "sport": sport,
            "count": 0,
            "serving_provider": "none",
            "items": [],
            "timestamp": _now_iso(),
            "error": str(e),
        }


@router.get("/odds")
async def waterfall_odds(
    sport: str = Query("basketball_nba", description="Sport key"),
    markets: str = Query("h2h,spreads,totals", description="Comma-separated market keys"),
):
    """
    Pull team-level odds for a sport through the odds waterfall chain.
    Falls back through TheRundown and SportsGameOdds if Odds API is exhausted.
    Markets: h2h (moneyline), spreads, totals.
    """
    try:
        items = await waterfall_router.get_data(sport, data_type="odds", markets=markets)
        if items:
            prov = items[0].get("source_provider", "unknown")
            return {
                "sport": sport,
                "markets_requested": markets,
                "count": len(items),
                "serving_provider": prov,
                "items": items,
                "timestamp": _now_iso(),
                "error": None,
            }
    except Exception as e:
        logger.warning(f"[waterfall/odds] Waterfall router failed for {sport}: {e}")

    return {
        "sport": sport,
        "markets_requested": markets,
        "count": 0,
        "serving_provider": "none",
        "items": [],
        "timestamp": _now_iso(),
        "error": "All odds providers exhausted",
    }


@router.get("/props")
async def waterfall_props(
    sport: str = Query("basketball_nba", description="Sport key"),
    game_id: str = Query(..., description="Odds API event ID for the game"),
    market: str = Query("player_points", description="Market key, e.g. player_points, player_rebounds"),
):
    """
    Fetch player props for a specific game via The Odds API.
    Supported markets: player_points, player_rebounds, player_assists,
    player_threes, player_blocks, player_steals, player_turnovers.
    """
    try:
        props = await real_data_connector.fetch_player_props(sport, game_id, market)
        return {
            "sport": sport,
            "game_id": game_id,
            "market": market,
            "count": len(props),
            "items": props,
            "timestamp": _now_iso(),
            "error": None,
        }
    except Exception as e:
        logger.error(f"[waterfall/props] {sport}/{game_id}/{market}: {e}")
        return {
            "sport": sport,
            "game_id": game_id,
            "market": market,
            "count": 0,
            "items": [],
            "timestamp": _now_iso(),
            "error": str(e),
        }


@router.post("/refresh")
async def waterfall_refresh(
    sport: str = Query("basketball_nba", description="Sport key to refresh"),
):
    """
    Force-bust the in-memory and Redis cache for a sport, then immediately
    re-fetch from the top of the waterfall chain.
    Returns new data plus which provider served it.
    """
    # Purge any known cache keys for this sport
    cache_keys_to_delete = [
        f"waterfall:{sport}:games",
        f"odds_api:{sport}:live",
        f"espn:{sport}:scoreboard",
        f"thesportsdb:{sport}:events",
        f"therundown:{sport}:games",
        f"balldontlie:nba:games",
        f"msf:{sport}:daily",
        f"sgo:{sport}:events",
        "waterfall:status",
    ]
    deleted = 0
    for key in cache_keys_to_delete:
        try:
            await cache.delete(key)
            deleted += 1
        except Exception:
            pass

    logger.info(f"[waterfall/refresh] Busted {deleted} cache keys for {sport}")

    # Re-fetch fresh
    try:
        games = await real_data_connector.fetch_games_by_sport(sport)
        source = games[0].get("source", "unknown") if games else "none"
        return {
            "status": "refreshed",
            "sport": sport,
            "cache_keys_cleared": deleted,
            "count": len(games),
            "serving_provider": source,
            "items": games,
            "timestamp": _now_iso(),
            "error": None,
        }
    except Exception as e:
        logger.error(f"[waterfall/refresh] Re-fetch failed for {sport}: {e}")
        return {
            "status": "refresh_error",
            "sport": sport,
            "cache_keys_cleared": deleted,
            "count": 0,
            "serving_provider": "none",
            "items": [],
            "timestamp": _now_iso(),
            "error": str(e),
        }
