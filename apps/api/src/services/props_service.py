import asyncio
import os
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from config.sports_config import (
    ALL_SPORTS, PROP_MARKETS, SPORT_DISPLAY
)

TEAM_PROP_MARKETS = ["h2h", "spreads", "totals"]
from app.services.odds_api_client import odds_api
from services.cache import cache
from services.cache_service import CACHE_TTL

from sqlalchemy import select
from database import async_session_maker
# from models.props import PropLine, PropOdds, GameLine, GameLineOdds

logger = logging.getLogger(__name__)

def get_player_image(name: str) -> str:
    """Returns a deterministic placeholder headshot from ESPN CDN."""
    name_hash = int(sum(ord(c) for c in str(name)))
    generic_espn_ids = [1966, 6583, 3136993, 3992, 4683020, 4277905, 4395628, 4065648, 3136193, 3975, 6478, 4277956, 3155526]
    espn_id = generic_espn_ids[name_hash % len(generic_espn_ids)]
    return f"https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/{espn_id}.png&w=150&h=150"

class PropsService:
    async def fetch_active_sports(self) -> List[str]:
        """Dynamically fetch which sports are currently in-season."""
        sports = await odds_api.get_active_sports()
        return [s["key"] for s in sports if s.get("active")]

    async def fetch_events(self, sport: str) -> List[Dict]:
        """Fetch events for a sport using the waterfall connector."""
        from real_data_connector import real_data_connector
        return await real_data_connector.fetch_games_by_sport(sport)

    async def fetch_player_props(self, sport: str, event_id: str, markets: List[str]) -> Dict:
        """Fetch player props using the waterfall connector."""
        from real_data_connector import real_data_connector
        market_str = markets[0] if markets else "player_points"
        props = await real_data_connector.fetch_player_props(sport, event_id, market_str)
        # Wrap list in bookmakers dict to maintain compatibility with existing grouping logic
        return {"bookmakers": [{"key": "merged", "title": "Merged Odds", "markets": [{"key": market_str, "outcomes": []}]}]} if not props else {"bookmakers": self._format_props_for_compatibility(props, market_str)}

    def _format_props_for_compatibility(self, props: List[Dict], market: str) -> List[Dict]:
        """Internal helper to format flat props list into nested structure expected by grouping logic."""
        # This is a bit of a shim to avoid rewriting the entire grouped logic in get_all_props
        # real_data_connector returns: [{"player_name": "...", "line": 2.5, "over_odds": -110, "under_odds": -110, "sportsbook": "FanDuel"}]
        # Existing logic expects: {"bookmakers": [{"title": "...", "markets": [{"key": "...", "outcomes": [{"name": "Over", "description": "Player", "point": 2.5, "price": -110}]}]}]}
        
        books = {}
        for p in props:
            book = p.get("sportsbook", "Unknown")
            if book not in books:
                books[book] = {"key": p.get("sportsbook_key", book.lower()), "title": book, "markets": []}
            
            # Find or create market
            mkt = next((m for m in books[book]["markets"] if m["key"] == market), None)
            if not mkt:
                mkt = {"key": market, "outcomes": []}
                books[book]["markets"].append(mkt)
            
            # Add Over/Under outcomes
            player = p.get("player_name")
            mkt["outcomes"].append({
                "name": "Over",
                "description": player,
                "point": p.get("line"),
                "price": p.get("over_odds")
            })
            mkt["outcomes"].append({
                "name": "Under",
                "description": player,
                "point": p.get("line"),
                "price": p.get("under_odds")
            })
        
        return list(books.values())

    async def fetch_game_odds(self, sport: str) -> List[Dict]:
        """Fetch game odds using the managed client."""
        markets = ",".join(TEAM_PROP_MARKETS[:5])
        return await odds_api.get_live_odds(sport, markets=markets)

    async def fetch_scores(self, sport: str, days_from: int = 1) -> List[Dict]:
        """Fetch scores using the managed client."""
        params = {"daysFrom": days_from}
        return await odds_api._request(f"/sports/{sport}/scores", params=params) or []

    async def get_all_props(self, sport_filter: Optional[str] = None) -> list[dict]:
        """Pull player props for all active sports or a single sport, grouping by market."""
        cache_key = f"player_props_grouped:{sport_filter or 'all'}"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached

        active = await self.fetch_active_sports()
        target_sports = [sport_filter] if sport_filter else [s for s in ALL_SPORTS if s in active]

        all_markets = []

        async def process_sport(sport: str):
            try:
                events = await self.fetch_events(sport)
                if not events:
                    return
                
                markets_string = PROP_MARKETS.get(sport, "player_points")
                markets = markets_string.split(",")
                
                # 🔓 LOCK REMOVAL: Parallel fetch more events in dev mode
                from config import settings
                max_events = len(events) if settings.DEVELOPMENT_MODE else 3
                tasks = [self.fetch_player_props(sport, event["id"], markets) for event in events[:max_events]]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, data in enumerate(results):
                    if isinstance(data, Exception) or not data or "bookmakers" not in data:
                        continue
                    
                    event = events[i]
                    event_id = event["id"]
                    
                    # Group by (player_name, market_key)
                    grouped = {}
                    
                    for book in data.get("bookmakers", []):
                        for market in book.get("markets", []):
                            m_key = market["key"]
                            for outcome in market.get("outcomes", []):
                                player = outcome.get("description", outcome.get("name"))
                                key = (player, m_key)
                                
                                if key not in grouped:
                                    grouped[key] = {
                                        "player_name": player,
                                        "market_key": m_key,
                                        "stat_type": m_key.replace("player_", "").replace("_", " ").title(),
                                        "over": [],
                                        "under": []
                                    }
                                
                                side = outcome["name"].lower()
                                if side in ["over", "under"]:
                                    grouped[key][side].append({
                                        "line": outcome.get("point"),
                                        "odds": outcome.get("price"),
                                        "book": book["title"],
                                        "book_key": book["key"]
                                    })
                    
                    for (player, m_key), details in grouped.items():
                        best_over = max(details["over"], key=lambda x: (x["line"] or 0, x["odds"])) if details["over"] else None
                        best_under = min(details["under"], key=lambda x: (x["line"] or 999, -x["odds"])) if details["under"] else None
                        
                        if best_over or best_under:
                            all_markets.append({
                                "event_id": event_id,
                                "sport": SPORT_DISPLAY.get(sport, sport),
                                "sport_key": sport,
                                "home_team": event.get("home_team"),
                                "away_team": event.get("away_team"),
                                "commence_time": event.get("commence_time"),
                                "player_name": player,
                                "market_key": m_key,
                                "stat_type": details["stat_type"],
                                "best_over": best_over,
                                "best_under": best_under,
                                "all_books": {
                                    "over": details["over"],
                                    "under": details["under"]
                                }
                            })
            except Exception as e:
                logger.error(f"Error processing sport {sport}: {e}")

        await asyncio.gather(*[process_sport(s) for s in target_sports])
        
        if all_markets:
            await cache.set_json(cache_key, all_markets, CACHE_TTL["player_props"])
        
        # If no props, database fallback
        if not all_markets:
            all_markets = await self._db_fallback(sport_filter)

        return all_markets

    async def _db_fallback(self, sport_filter: Optional[str]) -> list[dict]:
        logger.info(f"Checking database fallback for {sport_filter}...")
        results = []
        async with async_session_maker() as session:
            from models.props import PropLine, PropOdds
            stmt = select(PropLine)
            if sport_filter:
                stmt = stmt.where(PropLine.sport_key == sport_filter)
            
            from config import settings
            db_limit = 1000 if settings.DEVELOPMENT_MODE else 200
            stmt = stmt.order_by(PropLine.created_at.desc()).limit(db_limit)
            result = await session.execute(stmt)
            lines = result.scalars().all()
            
            for line in lines:
                odds_stmt = select(PropOdds).where(PropOdds.prop_line_id == line.id)
                odds_res = await session.execute(odds_stmt)
                odds_list = odds_res.scalars().all()
                
                best_over = None
                best_under = None
                if odds_list:
                    overs = [o.over_odds for o in odds_list if o.over_odds is not None]
                    unders = [o.under_odds for o in odds_list if o.under_odds is not None]
                    if overs:
                        best_over = {"line": line.line, "odds": max(overs), "book": "Mixed"}
                    if unders:
                        best_under = {"line": line.line, "odds": max(unders), "book": "Mixed"}

                results.append({
                    "event_id": line.game_id,
                    "sport": SPORT_DISPLAY.get(line.sport_key, line.sport_key),
                    "sport_key": line.sport_key,
                    "home_team": line.team,
                    "away_team": line.opponent,
                    "commence_time": line.start_time.isoformat() if line.start_time else None,
                    "player_name": line.player_name,
                    "market_key": line.stat_type,
                    "stat_type": line.stat_type.replace("player_", "").replace("_", " ").title(),
                    "best_over": best_over,
                    "best_under": best_under,
                    "source": "database_fallback",
                    "sharp_money": line.sharp_money,
                    "steam_score": line.steam_score
                })
        return results

    async def enrich_props(self, props: List[Dict], sport: str) -> List[Dict]:
        """Apply advanced enrichment: Injuries, DVP, Monte Carlo, and Sharp Signals."""
        if not props:
            return []

        from services.injury_service import injury_service
        from services.dvp_service import get_dvp_rating
        from services.monte_carlo_service import monte_carlo_service, american_to_implied
        from services.player_stats_service import player_stats_service
        
        # 1. Filter Injuries
        props = await injury_service.filter_injured_players(props, sport, name_key="player_name")

        async def enrich_single(p):
            try:
                player_name = p.get('player_name', 'Unknown')
                stat_type = p.get('stat_type', 'Prop')
                line = float(p.get('best_over', {}).get('line') or p.get('best_under', {}).get('line') or 0.0)
                
                # Fetch DVP/Matchup context
                # Use a dummy DB session or context if needed, but get_dvp_rating handles it usually
                dvp = await get_dvp_rating(p.get('away_team', 'TBD'), "N/A", stat_type)
                matchup_rank = dvp.get("rank", 15)
                
                # Confidence / Edge Calculation
                model_prob = 0.55 # Baseline
                impl_prob = american_to_implied(p.get('best_over', {}).get('odds', -110))
                
                # Simple steam-based edge if available
                steam = p.get('steam_score', 0.0)
                edge = model_prob - impl_prob + (steam * 0.01)
                
                unique_id = hashlib.md5(f"{player_name}_{stat_type}_{line}_{sport}".encode()).hexdigest()

                return {
                    **p,
                    'id': unique_id,
                    'player': {'name': player_name, 'team': p.get('home_team')},
                    'player_image': get_player_image(player_name),
                    'market': {'stat_type': stat_type, 'description': 'Over/Under'},
                    'side': 'over',
                    'line_value': line,
                    'odds': p.get('best_over', {}).get('odds', -110),
                    'edge': edge,
                    'confidence_score': model_prob,
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'matchup': {
                        'opp_rank': matchup_rank,
                        'opponent': p.get('away_team'),
                        'def_rank_vs_pos': matchup_rank
                    }
                }
            except Exception as e:
                logger.error(f"Error enriching prop {p.get('player_name')}: {e}")
                return p

        return await asyncio.gather(*[enrich_single(p) for p in props])

    async def get_team_props(self, sport_filter: Optional[str] = None) -> list[dict]:
        """Pull game-level (team/spread/total) odds for all sports."""
        cache_key = f"team_props:{sport_filter or 'all'}"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached

        active = await self.fetch_active_sports()
        target_sports = [sport_filter] if sport_filter else [s for s in ALL_SPORTS if s in active]

        all_games = []
        for sport in target_sports:
            try:
                games = await self.fetch_game_odds(sport)
                if not isinstance(games, list):
                    continue
                for g in games:
                    all_games.append({
                        "event_id": g.get("id"),
                        "sport": SPORT_DISPLAY.get(sport, sport),
                        "sport_key": sport,
                        "home_team": g.get("home_team"),
                        "away_team": g.get("away_team"),
                        "commence_time": g.get("commence_time"),
                        "bookmakers": g.get("bookmakers", []),
                    })
            except Exception as e:
                logger.error(f"Error processing team props for {sport}: {e}")
        
        if not all_games:
            logger.info(f"API returned no team props for {sport_filter}, checking database fallback...")
            async with async_session_maker() as session:
                from models.props import GameLine
                stmt = select(GameLine)
                if sport_filter:
                    stmt = stmt.where(GameLine.sport_key == sport_filter)
                from config import settings
                game_limit = 500 if settings.DEVELOPMENT_MODE else 50
                stmt = stmt.order_by(GameLine.commence_time.desc()).limit(game_limit)
                result = await session.execute(stmt)
                games = result.scalars().all()
                
                for g in games:
                    all_games.append({
                        "event_id": g.game_id,
                        "sport": SPORT_DISPLAY.get(g.sport_key, g.sport_key),
                        "sport_key": g.sport_key,
                        "home_team": g.home_team,
                        "away_team": g.away_team,
                        "commence_time": g.commence_time.isoformat() if g.commence_time else None,
                        "bookmakers": [],
                        "source": "database_fallback"
                    })

        await cache.set_json(cache_key, all_games, CACHE_TTL["team_props"])
        return all_games

props_service = PropsService()

# Export for backward compatibility if needed (but class is preferred)
get_all_props = props_service.get_all_props
get_team_props = props_service.get_team_props
fetch_scores = props_service.fetch_scores
fetch_active_sports = props_service.fetch_active_sports
fetch_events = props_service.fetch_events
fetch_player_props = props_service.fetch_player_props
fetch_game_odds = props_service.fetch_game_odds
