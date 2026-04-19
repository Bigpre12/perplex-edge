import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from core.waterfall_config import (
    CONSENSUS_LINES,
    ODDS_LIVE,
    ODDS_PREGAME,
    PLAYER_PROPS,
    SCHEDULE,
    canonical_sport_key,
    get_provider_chain,
    resolve_data_type,
)
from services.balldontlie_client import balldontlie_client
from services.api_sports_client import api_sports_client
from services.sportmonks_client import sportmonks_client
from services.isports_client import isports_client
from services.statsbomb_client import statsbomb_client
from services.odds_api_client import odds_api
from services.thesportsdb_client import thesportsdb_client
from services.espn_client import espn_client
from services.therundown_client import therundown_client
from services.sportsgameodds_client import sportsgameodds_client
from services.betstack_client import betstack_client
from services.mysportsfeeds_client import mysportsfeeds_client
from services.cache import cache
from services.commence_time import event_commence_utc, reject_absurd_future, parse_commence_to_utc

logger = logging.getLogger(__name__)

class ProviderUnavailableError(Exception):
    """Custom exception for unified error handling in waterfall."""
    pass

class WaterfallRouter:
    """
    Branched Waterfall Orchestrator.
    Routes requests based on sport type and data type.
    """
    
    # TTL Definitions
    TTL_LIVE = 60
    TTL_STATS = 900 # 15 minutes
    TTL_SCHEDULE = 86400 # 24 hours

    async def get_data(
        self,
        sport: str,
        data_type: str = "stats",
        *,
        markets: Optional[str] = None,
        skip_cache: bool = False,
    ) -> Any:
        """Entry point for all waterfall data requests.

        ``skip_cache`` — when True, bypass Redis read/write (used by scheduled ingest so odds
        are not served from a stale snapshot while the router still walks the provider chain).
        """
        sport_lower = sport.lower()
        if resolve_data_type(data_type) == PLAYER_PROPS:
            logger.info("Waterfall: player_props requires event context; use Odds API props endpoint")
            return []
        chain = get_provider_chain(sport_lower, data_type)
        return await self._execute_waterfall(
            sport_lower, data_type, chain, markets=markets, skip_cache=skip_cache
        )

    def _is_odds_like(self, data_type: str) -> bool:
        r = resolve_data_type(data_type)
        return r in (ODDS_PREGAME, ODDS_LIVE, CONSENSUS_LINES)

    def _normalize_to_odds_events(self, rows: List[Dict], sport_key: str) -> List[Dict]:
        """Coerce schedule-shaped rows into Odds-API-like events for downstream mappers."""
        out: List[Dict] = []
        sk = canonical_sport_key(sport_key)
        for g in rows:
            if not isinstance(g, dict):
                continue
            if g.get("bookmakers") is not None and (
                g.get("commence_time") is not None or g.get("commenceTime") is not None
            ):
                out.append(g)
                continue
            ht = g.get("home_team") or g.get("home_team_name") or ""
            at = g.get("away_team") or g.get("away_team_name") or ""
            st = g.get("commence_time") or g.get("start_time")
            if isinstance(st, datetime):
                parsed = reject_absurd_future(parse_commence_to_utc(st))
            elif st:
                parsed = reject_absurd_future(event_commence_utc({"commence_time": st}))
            else:
                parsed = None
            commence = (
                parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
                if parsed
                else ""
            )
            eid = str(g.get("id") or g.get("event_id") or "")
            out.append(
                {
                    "id": eid,
                    "sport_key": sk,
                    "home_team": ht,
                    "away_team": at,
                    "commence_time": commence,
                    "bookmakers": g.get("bookmakers") or [],
                }
            )
        return out

    async def _execute_waterfall(
        self,
        sport: str,
        data_type: str,
        chain: List[str],
        *,
        markets: Optional[str] = None,
        skip_cache: bool = False,
    ) -> Any:
        """Executes the provider chain with try/except and caching logic."""
        canonical = canonical_sport_key(sport)
        resolved = resolve_data_type(data_type)
        cache_key = f"wf:{resolved}:{canonical}:{markets or ''}"
        
        # 1. Check Redis Cache
        if not skip_cache:
            cached = await cache.get_json(cache_key)
            if cached:
                return cached

        # 2. Iterate through providers
        for provider_key in chain:
            try:
                data = await self._call_provider(
                    provider_key, sport, data_type, markets=markets
                )
                if data:
                    if isinstance(data, dict):
                        if data.get("error"):
                            continue
                        logger.warning(
                            "Waterfall: %s returned non-list payload for %s %s; skipping",
                            provider_key,
                            sport,
                            data_type,
                        )
                        continue
                    if not isinstance(data, list):
                        continue
                    # 3. Label source and cache
                    for item in data:
                        if isinstance(item, dict):
                            item["source_provider"] = provider_key
                            
                    # 4. Apply dynamic TTL
                    ttl = self.TTL_LIVE if resolved == ODDS_LIVE else self.TTL_STATS
                    if resolved == SCHEDULE: ttl = self.TTL_SCHEDULE
                    
                    if not skip_cache:
                        await cache.set_json(cache_key, data, ttl=ttl)
                    logger.info(f"✅ Waterfall: {provider_key} served {sport} {data_type}")
                    return data
            except Exception as e:
                logger.warning(f"⚠️ Waterfall: {provider_key} failed for {sport}: {e}")
                continue

        logger.error(f"❌ Waterfall: All providers exhausted for {sport} {data_type}")
        return []

    async def _call_provider(
        self,
        provider: str,
        sport: str,
        data_type: str,
        *,
        markets: Optional[str] = None,
    ) -> Any:
        """Bridges generic waterfall request to specific provider client."""
        sk = canonical_sport_key(sport)
        odds_like = self._is_odds_like(data_type)

        if provider == "balldontlie":
            raw = await balldontlie_client.get_games(sk)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "api_sports":
            raw = await api_sports_client.get_games(sport)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "sportmonks":
            return await sportmonks_client.get_fixtures()
        elif provider == "isports":
            raw = await isports_client.get_games(sport)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "the_odds_api":
            return await odds_api.get_live_odds(sk, markets=markets)
        elif provider == "thesportsdb":
            raw = await thesportsdb_client.get_events_by_day(sk)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "espn":
            raw = await espn_client.get_scoreboard(sk)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "therundown":
            raw = await therundown_client.get_games(sk)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "sportsgameodds":
            raw = await sportsgameodds_client.get_events(sk)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "betstack":
            if not betstack_client.available:
                return None
            raw = await betstack_client.get_odds(sk)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "oddspapi":
            # Roadmap: thin client + legal keys — placeholder keeps chain order explicit
            logger.debug("OddsPapi: no client wired; skipping provider slot")
            return None
        elif provider == "mysportsfeeds":
            if not mysportsfeeds_client.available:
                return None
            raw = await mysportsfeeds_client.get_daily_games(sk)
            if odds_like and raw:
                return self._normalize_to_odds_events(raw, sk)
            return raw
        elif provider == "kalshi":
            logger.debug("Kalshi: waterfall batch fetch not used for this data_type")
            return None
        return None

    async def get_historical_soccer(self, match_id: int) -> Any:
        """Special bypass handler for StatsBomb."""
        # StatsBomb is NOT in the live waterfall branch per instructions
        # Always serve from Supabase permanently
        return await statsbomb_client.get_events(match_id)

waterfall_router = WaterfallRouter()
