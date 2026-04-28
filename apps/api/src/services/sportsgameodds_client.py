"""
SportsGameOdds Client — Free Tier (1,000 objects/month, 10 req/min)

The only free API that covers UFC/MMA odds + alternate lines.
Used sparingly for: UFC odds, alt lines on high-confidence props.

Docs: https://sportsgameodds.com/docs/v1/
"""
import os
import httpx
from services.api_telemetry import InstrumentedAsyncClient
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

SPORT_SLUG = {
    "mma_mixed_martial_arts": "UFC",
    "basketball_nba": "NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "tennis_atp": "ATP",
    "basketball_ncaab": "NCAAB",
    "americanfootball_ncaaf": "NCAAF",
    "soccer_epl": "EPL",
}


class SportsGameOddsClient:
    BASE_URL = "https://api.sportsgameodds.com/v2"

    def __init__(self):
        self.api_key = os.getenv("SPORTSGAMEODDS_KEY", "")
        self._cache: Dict[str, dict] = {}
        self.default_ttl = 1800  # 30 min — conserve the 1k/mo quota
        self.timeout = 10.0

    def _get_cached(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and time.time() < entry["expires_at"]:
            return entry["data"]
        return None

    def _set_cache(self, key: str, data: Any, ttl: int = None):
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + (ttl or self.default_ttl),
        }

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def get_events(self, sport_key: str = "basketball_nba", odds_available: bool = True) -> List[Dict]:
        """Fetch upcoming events for a league via v2 API."""
        if not self.available:
            return []

        league_id = SPORT_SLUG.get(sport_key, sport_key) # Fallback to key itself
        
        cache_key = f"sgo_events_v2_{league_id}_{odds_available}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/events"
        params = {
            "leagueID": league_id,
            "oddsAvailable": "true" if odds_available else "false"
        }
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                raw = resp.json()

            # v2 response usually puts data in a 'data' or top-level list
            events = self._normalize_events(raw, sport_key)
            self._set_cache(cache_key, events)
            logger.info(f"SportsGameOdds V2: {len(events)} events for {league_id}")
            return events

        except Exception as e:
            logger.error(f"SportsGameOdds V2 error for {league_id}: {e}")
            return []

    def _normalize_events(self, raw: Any, sport_key: str) -> List[Dict]:
        """Convert SGO v2 response to our format."""
        items = []
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict):
            items = raw.get("data", raw.get("events", []))
            
        games = []
        for event in items:
            try:
                # v2 structure often has teams or homeTeam/awayTeam directly
                home_name = event.get("homeTeam") or event.get("teams", {}).get("home", {}).get("name", "Home")
                away_name = event.get("awayTeam") or event.get("teams", {}).get("away", {}).get("name", "Away")
                
                start_str = event.get("startTime") or event.get("eventDate", "")
                try:
                    start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                except Exception:
                    start_time = datetime.now(timezone.utc)

                games.append({
                    "id": str(event.get("id") or event.get("eventID", "")),
                    "sport_key": sport_key,
                    "start_time": start_time,
                    "home_team_name": home_name,
                    "away_team_name": away_name,
                    "home_score": event.get("homeScore"),
                    "away_score": event.get("awayScore"),
                    "status": event.get("status", "upcoming"),
                    "source": "sportsgameodds",
                })
            except Exception as e:
                logger.debug(f"SportsGameOdds V2: Skipping event: {e}")
                continue

        return games

    async def get_odds(self, event_id: str, include_alt_lines: bool = False) -> Optional[Dict]:
        """Get odds for a specific event via v2."""
        if not self.available:
            return None

        cache_key = f"sgo_odds_v2_{event_id}_{include_alt_lines}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # v2 often uses /events/{id} or /odds/{id}
        url = f"{self.BASE_URL}/events/{event_id}"
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            self._set_cache(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"SportsGameOdds v2 odds error: {e}")
            return None

    async def get_teams(self, league_id: str = "NBA") -> List[Dict]:
        """Fetch teams for a specific league via v2 /teams endpoint."""
        if not self.available:
            return []

        cache_key = f"sgo_teams_v2_{league_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/teams"
        params = {"leagueID": league_id}
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            
            # Normalize to a simple list of teams
            teams = data.get("data", data if isinstance(data, list) else [])
            self._set_cache(cache_key, teams)
            return teams
        except Exception as e:
            logger.error(f"SportsGameOdds v2 teams error: {e}")
            return []

    async def get_players(self, league_id: str = "NBA", team_id: Optional[str] = None) -> List[Dict]:
        """Fetch players for a league or team via v2 /players endpoint."""
        if not self.available:
            return []

        cache_key = f"sgo_players_v2_{league_id}_{team_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/players"
        params = {"leagueID": league_id}
        if team_id:
            params["teamID"] = team_id
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            # Normalize to a simple list of players
            players = data.get("data", data if isinstance(data, list) else [])
            self._set_cache(cache_key, players)
            return players
        except Exception as e:
            logger.error(f"SportsGameOdds v2 players error: {e}")
            return []

    async def get_sports(self) -> List[Dict]:
        """Fetch list of all available sports/leagues via v2 /sports endpoint."""
        if not self.available:
            return []

        cache_key = "sgo_sports_v2"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/sports"
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            # Normalize to a simple list of sports
            sports = data.get("data", data if isinstance(data, list) else [])
            self._set_cache(cache_key, sports)
            return sports
        except Exception as e:
            logger.error(f"SportsGameOdds v2 sports error: {e}")
            return []

    async def get_leagues(self) -> List[Dict]:
        """Fetch list of all available leagues via v2 /leagues endpoint."""
        if not self.available:
            return []

        cache_key = "sgo_leagues_v2"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/leagues"
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            # Normalize to a simple list of leagues
            leagues = data.get("data", data if isinstance(data, list) else [])
            self._set_cache(cache_key, leagues)
            return leagues
        except Exception as e:
            logger.error(f"SportsGameOdds v2 leagues error: {e}")
            return []

    async def get_stats(self, event_id: Optional[str] = None, player_id: Optional[str] = None) -> List[Dict]:
        """Fetch stats for an event or player via v2 /stats endpoint."""
        if not self.available:
            return []

        cache_key = f"sgo_stats_v2_{event_id}_{player_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/stats"
        params = {}
        if event_id:
            params["eventID"] = event_id
        if player_id:
            params["playerID"] = player_id
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            # Normalize to a simple list of stats
            stats = data.get("data", data if isinstance(data, list) else [])
            self._set_cache(cache_key, stats)
            return stats
        except Exception as e:
            logger.error(f"SportsGameOdds v2 stats error: {e}")
            return []

    async def get_markets(self, league_id: Optional[str] = None) -> List[Dict]:
        """Fetch available markets via v2 /markets endpoint."""
        if not self.available:
            return []

        cache_key = f"sgo_markets_v2_{league_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/markets"
        params = {}
        if league_id:
            params["leagueID"] = league_id
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            # Normalize to a simple list of markets
            markets = data.get("data", data if isinstance(data, list) else [])
            self._set_cache(cache_key, markets)
            return markets
        except Exception as e:
            logger.error(f"SportsGameOdds v2 markets error: {e}")
            return []

    async def get_account_usage(self) -> Optional[Dict]:
        """Fetch API usage and credit info via v2 /account/usage endpoint."""
        if not self.available:
            return None

        url = f"{self.BASE_URL}/account/usage"
        headers = {"x-api-key": self.api_key}

        try:
            async with InstrumentedAsyncClient(provider="sportsgameodds", timeout=self.timeout) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"SportsGameOdds v2 usage error: {e}")
            return None

    def parse_odd_id(self, odd_id: str):
        """Parse an oddID into its components."""
        from services.sgo_market_service import SGOMarketService
        
        try:
            # First, use the SGO Market Service for deep resolution
            parsed = SGOMarketService.parse_odd_id(odd_id)
            return {
                "oddID": odd_id,
                "stat": parsed["stat_display"],
                "statID": parsed["stat_id"],
                "entity": parsed["entity_display"],
                "entityID": parsed["entity_id"],
                "period": parsed["period_display"],
                "periodID": parsed["period_id"],
                "betType": parsed["bet_type_display"],
                "betTypeID": parsed["bet_type_id"],
                "side": parsed["side_display"],
                "sideID": parsed["side_id"],
                "description": SGOMarketService.get_market_description(odd_id)
            }
        except Exception:
            # Fallback to simple split if service fails
            parts = odd_id.split("-")
            if len(parts) >= 5:
                return {
                    "stat": parts[0],
                    "entity": parts[1],
                    "period": parts[2],
                    "betType": parts[3],
                    "side": parts[4]
                }
            return {"raw": odd_id}


# Singleton
sportsgameodds_client = SportsGameOddsClient()
