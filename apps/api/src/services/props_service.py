# apps/api/src/services/props_service.py
import logging
from typing import Optional, List, Dict
from sqlalchemy import select
from database import async_session_maker
from models.unified import UnifiedOdds
from services.cache import cache
from config.sports_config import SPORT_DISPLAY

logger = logging.getLogger(__name__)

class PropsService:
    async def get_all_props(self, sport_filter: Optional[str] = None) -> List[Dict]:
        """
        Query UnifiedOdds for player props.
        Groups by (player_name, market_key) to find best lines.
        """
        async with async_session_maker() as session:
            # Query non-game lines
            stmt = select(UnifiedOdds).where(
                UnifiedOdds.market_key.notin_(['h2h', 'spreads', 'totals'])
            )
            if sport_filter:
                stmt = stmt.where(UnifiedOdds.sport == sport_filter)
            
            result = await session.execute(stmt)
            odds = result.scalars().all()
            
            if not odds: return []

            # Grouping: (eid, player, mkey) -> outcome -> book -> (line, price)
            grouped = {}
            for o in odds:
                key = (o.event_id, o.player_name, o.market_key)
                if key not in grouped:
                    grouped[key] = {
                        "event_id": o.event_id,
                        "sport": SPORT_DISPLAY.get(o.sport, o.sport),
                        "sport_key": o.sport,
                        "home_team": o.home_team,
                        "away_team": o.away_team,
                        "commence_time": o.game_time.isoformat() if o.game_time else None,
                        "player_name": o.player_name,
                        "market_key": o.market_key,
                        "stat_type": o.market_key.replace("player_", "").replace("_", " ").title(),
                        "over": [],
                        "under": []
                    }
                
                if o.outcome_key in ['over', 'under']:
                    grouped[key][o.outcome_key].append({
                        "line": float(o.line) if o.line else 0.0,
                        "odds": int(o.price),
                        "book": o.bookmaker
                    })

            # Finalize: Find best over/under
            final_props = []
            for item in grouped.values():
                if item["over"]:
                    item["best_over"] = max(item["over"], key=lambda x: (x["line"], x["odds"]))
                if item["under"]:
                    item["best_under"] = min(item["under"], key=lambda x: (x["line"], -x["odds"]))
                
                if "best_over" in item or "best_under" in item:
                    final_props.append(item)
            
            return final_props

    async def get_team_props(self, sport_filter: Optional[str] = None) -> List[Dict]:
        """Query UnifiedOdds for h2h/spreads/totals."""
        async with async_session_maker() as session:
            stmt = select(UnifiedOdds).where(
                UnifiedOdds.market_key.in_(['h2h', 'spreads', 'totals'])
            )
            if sport_filter:
                stmt = stmt.where(UnifiedOdds.sport == sport_filter)
            
            result = await session.execute(stmt)
            odds = result.scalars().all()
            
            # Simple grouping by event_id
            events = {}
            for o in odds:
                if o.event_id not in events:
                    events[o.event_id] = {
                        "event_id": o.event_id,
                        "sport": SPORT_DISPLAY.get(o.sport, o.sport),
                        "sport_key": o.sport,
                        "home_team": o.home_team,
                        "away_team": o.away_team,
                        "commence_time": o.game_time.isoformat() if o.game_time else None,
                        "markets": {}
                    }
                
                m_key = o.market_key
                if m_key not in events[o.event_id]["markets"]:
                    events[o.event_id]["markets"][m_key] = []
                
                events[o.event_id]["markets"][m_key].append({
                    "outcome": o.outcome_key,
                    "bookmaker": o.bookmaker,
                    "price": int(o.price),
                    "line": float(o.line) if o.line else None
                })
            
            return list(events.values())

props_service = PropsService()
get_all_props = props_service.get_all_props
get_team_props = props_service.get_team_props
