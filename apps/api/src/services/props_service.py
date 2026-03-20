# apps/api/src/services/props_service.py
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_
from db.session import async_session_maker
from models import UnifiedOdds
from services.cache import cache
from core.sports_config import SPORT_DISPLAY

logger = logging.getLogger(__name__)

class PropsService:
    async def get_all_props(self, sport_filter: Optional[str] = None) -> List[Dict]:
        """
        Query UnifiedOdds joined with UnifiedEVSignal for player props.
        Groups by (player_name, market_key) to find best lines and attaches EV recommendations.
        """
        from models import UnifiedEVSignal
        from sqlalchemy import outerjoin

        try:
            async with async_session_maker() as session:
                # Query UnifiedOdds joined with UnifiedEVSignal
                stmt = select(UnifiedOdds, UnifiedEVSignal).select_from(
                    outerjoin(UnifiedOdds, UnifiedEVSignal, 
                        and_(
                            UnifiedOdds.sport == UnifiedEVSignal.sport,
                            UnifiedOdds.event_id == UnifiedEVSignal.event_id,
                            UnifiedOdds.market_key == UnifiedEVSignal.market_key,
                            UnifiedOdds.outcome_key == UnifiedEVSignal.outcome_key,
                            UnifiedOdds.bookmaker == UnifiedEVSignal.bookmaker
                        )
                    )
                ).where(
                    UnifiedOdds.market_key.notin_(['h2h', 'spreads', 'totals'])
                )
                
                if sport_filter:
                    stmt = stmt.where(UnifiedOdds.sport == sport_filter)
                
                result = await session.execute(stmt)
                # Fetch all rows (pairs of UnifiedOdds, UnifiedEVSignal)
                rows = result.all()
                
                if not rows: return []

                # Grouping: (eid, player, mkey) -> outcome -> book -> (line, price, ev)
                grouped: Dict[tuple, Dict[str, Any]] = {}
                for odds_item, signal in rows:
                    o = odds_item
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
                            "under": [],
                            "max_edge": 0.0,
                            "recommendation": None
                        }
                    
                    ev_val = float(signal.edge_percent) if signal else 0.0
                    
                    if o.outcome_key in ['over', 'under']:
                        grouped[key][o.outcome_key].append({
                            "line": float(o.line) if o.line else 0.0,
                            "odds": int(o.price),
                            "book": o.bookmaker,
                            "ev": ev_val
                        })
                        
                        # Update best recommendation for this prop group
                        if ev_val > grouped[key]["max_edge"]:
                            grouped[key]["max_edge"] = ev_val
                            tier = "S" if ev_val >= 5 else "A" if ev_val >= 3 else "B" if ev_val >= 1 else "C"
                            grouped[key]["recommendation"] = {
                                "side": o.outcome_key,
                                "tier": tier,
                                "ev": ev_val,
                                "reason": f"{o.player_name} {o.outcome_key} {o.line} shows a {ev_val}% edge vs market average."
                            }

                # Finalize: Find best over/under lines for display
                final_props = []
                for item in grouped.values():
                    if item["over"]:
                        item["best_over"] = max(item["over"], key=lambda x: (x["line"], x["odds"]))
                    if item["under"]:
                        item["best_under"] = min(item["under"], key=lambda x: (x["line"], -x["odds"]))
                    
                    if "best_over" in item or "best_under" in item:
                        # Provide an empty recommendation if none was found
                        if not item["recommendation"]:
                            item["recommendation"] = {
                                "side": "over",
                                "tier": "C",
                                "ev": 0.0,
                                "reason": "No significant market edge detected."
                            }
                        final_props.append(item)
                
                # Sort by max edge (hottest props first)
                final_props.sort(key=lambda x: x.get("max_edge", 0), reverse=True)
                return final_props
        except Exception as e:
            logger.error(f"Error in get_all_props: {e}")
            return []
        return [] # Fallback

    async def get_team_props(self, sport_filter: Optional[str] = None) -> List[Dict]:
        """Query UnifiedOdds for h2h/spreads/totals."""
        try:
            async with async_session_maker() as session:
                stmt = select(UnifiedOdds).where(
                    UnifiedOdds.market_key.in_(['h2h', 'spreads', 'totals'])
                )
                if sport_filter:
                    stmt = stmt.where(UnifiedOdds.sport == sport_filter)
                
                result = await session.execute(stmt)
                odds = result.scalars().all()
                
                # Simple grouping by event_id
                events: Dict[str, Dict[str, Any]] = {}
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
        except Exception as e:
            logger.error(f"Error in get_team_props: {e}")
            return []
        return [] # Fallback

props_service = PropsService()
get_all_props = props_service.get_all_props
get_team_props = props_service.get_team_props
