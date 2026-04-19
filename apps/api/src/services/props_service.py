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

    async def get_canonical_props(self, sport: str, min_ev: float = None, only_ev: bool = False) -> Dict[str, Any]:
        """
        Returns the canonical props structure requested by the new UI.
        Shape matches EXACTLY what is expected by the frontend.
        """
        from models import UnifiedEVSignal, UnifiedOdds
        from sqlalchemy import text
        from datetime import datetime, timezone
        import uuid
        from services.props_live_query import (
            props_live_game_time_window,
            props_live_window_params,
            props_live_window_sql_clause,
        )

        try:
            async with async_session_maker() as session:
                t_lo, t_hi = props_live_window_params()
                # Optimized query: fetch all UnifiedOdds joined with UnifiedEVSignal
                sql = """
                SELECT 
                    o.id as odds_id,
                    o.event_id, 
                    o.sport,
                    o.league,
                    o.home_team,
                    o.away_team,
                    o.game_time,
                    o.player_name,
                    o.market_key,
                    o.outcome_key,
                    o.line,
                    o.price,
                    o.bookmaker,
                    o.implied_prob,
                    o.created_at as updated_at,
                    e.true_prob,
                    e.edge_percent
                FROM unified_odds o
                LEFT JOIN ev_signals e ON 
                    o.event_id = e.event_id AND 
                    o.sport = e.sport AND 
                    o.player_name = e.player_name AND
                    o.market_key = e.market_key AND 
                    o.outcome_key = e.outcome_key AND 
                    o.bookmaker = e.bookmaker
                WHERE o.sport = :sport
                  AND o.market_key NOT IN ('h2h', 'spreads', 'totals')
                """ + props_live_window_sql_clause(
                    "o.game_time"
                )
                
                # Check DB dialect
                engine_url = str(session.bind.url)
                if "sqlite" in engine_url:
                    # SQLite fallback query without left join on ev table schema matching strict PG rules
                    # This builds a basic ORM query
                    stmt = select(UnifiedOdds, UnifiedEVSignal).select_from(
                        UnifiedOdds.__table__.outerjoin(
                            UnifiedEVSignal.__table__, 
                            and_(
                                UnifiedOdds.sport == UnifiedEVSignal.sport,
                                UnifiedOdds.event_id == UnifiedEVSignal.event_id,
                                UnifiedOdds.market_key == UnifiedEVSignal.market_key,
                                UnifiedOdds.outcome_key == UnifiedEVSignal.outcome_key,
                                UnifiedOdds.bookmaker == UnifiedEVSignal.bookmaker
                            )
                        )
                    ).where(UnifiedOdds.sport == sport).where(
                        UnifiedOdds.market_key.notin_(['h2h', 'spreads', 'totals']),
                        props_live_game_time_window(UnifiedOdds.game_time),
                    )
                    result = await session.execute(stmt)
                    raw_rows = []
                    for o, e in result.all():
                        raw_rows.append({
                            'odds_id': o.id,
                            'event_id': o.event_id,
                            'sport': o.sport,
                            'league': o.league,
                            'home_team': o.home_team,
                            'away_team': o.away_team,
                            'game_time': o.game_time,
                            'player_name': o.player_name,
                            'market_key': o.market_key,
                            'outcome_key': o.outcome_key,
                            'line': float(o.line) if o.line else 0.0,
                            'price': o.price,
                            'bookmaker': o.bookmaker,
                            'implied_prob': float(o.implied_prob) if o.implied_prob else 0.0,
                            'updated_at': o.updated_at,
                            'true_prob': float(e.true_prob) if e else None,
                            'edge_percent': float(e.edge_percent) if e else None
                        })
                else:
                    from sqlalchemy import text
                    result = await session.execute(
                        text(sql),
                        {"sport": sport, "t_lo": t_lo, "t_hi": t_hi},
                    )
                    raw_rows = [dict(r._mapping) for r in result.all()]
                
                # Group by Unique Prop Entity: Event + Player + Market + Line
                grouped = {}
                global_updated = None
                
                for row_dict in raw_rows:
                    if row_dict.get('line') is None: continue # Ignore NULL lines only
                    r = row_dict
                    player = r.get('player_name') or r.get('home_team') or "Matchup"
                    key = (r['event_id'], player, r['market_key'], float(r['line'] or 0.0))
                    
                    if key not in grouped:
                        grouped[key] = {
                            "id": f"{r['event_id']}_{(r.get('player_name') or r.get('home_team') or 'Matchup').replace(' ','')}_{r['market_key']}_{float(r['line'] or 0.0)}",
                            "game_id": r['event_id'],
                            "sport": (r['sport'] or "").upper().replace("BASKETBALL_",""),
                            "league": (r['league'] or "").upper().replace("BASKETBALL_",""),
                            "player_name": r['player_name'] or r['home_team'] or "Matchup",
                            "team": r['home_team'], # Approximated, full metadata needed for exact team
                            "opponent": r['away_team'], # Approximated
                            "start_time": r['game_time'].isoformat() + "Z" if r.get('game_time') else None,
                            "stat_type": r['market_key'].replace("player_", "").replace("_", " ").title(),
                            "line": float(r['line']),
                            "over_odds": None,
                            "under_odds": None,
                            "best_book": None,
                            "books": [],
                            "implied_probability": 0.0,
                            "model_probability": 0.0,
                            "ev_percentage": 0.0,
                            "confidence": 0.0,
                            "steam_signal": False,
                            "whale_signal": False,
                            "sharp_conflict": False,
                            "last_updated": r['updated_at'].isoformat() + "Z" if r.get('updated_at') else datetime.utcnow().isoformat() + "Z",
                            
                            # Helpers for calculating best odds
                            "_max_over": -10000,
                            "_max_under": -10000,
                            "_max_ev": -999.0,
                            "_max_ev_side": "over",
                        }
                    
                    group = grouped[key]
                    
                    # Track global updated
                    if r.get("updated_at"):
                        if not global_updated or r["updated_at"] > global_updated:
                            global_updated = r["updated_at"]
                            
                    # Add to books array
                    group["books"].append({
                        "book": r["bookmaker"],
                        "side": r["outcome_key"],
                        "odds": int(r["price"] or 0)
                    })
                    
                    # Update Over/Under best odds
                    if r["outcome_key"] == "over" and r.get("price"):
                        price = int(r["price"])
                        if price > group["_max_over"]:
                            group["_max_over"] = price
                            group["over_odds"] = price
                            # Approximate best book if it's the over
                            if group["_max_ev"] <= 0:
                                group["best_book"] = r["bookmaker"]
                                
                    if r["outcome_key"] == "under" and r.get("price"):
                        price = int(r["price"])
                        if price > group["_max_under"]:
                            group["_max_under"] = price
                            group["under_odds"] = price
                            
                    # Update EV metrics
                    if r.get("edge_percent") and float(r["edge_percent"]) > group["_max_ev"]:
                        group["_max_ev"] = float(r["edge_percent"])
                        group["ev_percentage"] = round(float(r["edge_percent"]), 2)
                        group["model_probability"] = round(float(r["true_prob"]), 3) if r.get("true_prob") else 0.0
                        group["implied_probability"] = round(float(r["implied_prob"]), 3) if r.get("implied_prob") else 0.0
                        group["best_book"] = r["bookmaker"]
                        # Set confidence based loosely on Ev or hardcoded for now
                        group["confidence"] = min(100.0, max(50.0, 50.0 + (float(r["edge_percent"]) * 3)))
                        # Ensure we capture what side the primary edge exists on for advisory logic
                        group["_max_ev_side"] = r.get("outcome_key", "over")
                
                # Final filtering and cleanup
                final_props = []
                for g in grouped.values():
                    # Extract side before deleting helpers
                    best_ev_side = g.get("_max_ev_side", "over")
                    
                    # Cleanup internal Helpers
                    del g["_max_over"]
                    del g["_max_under"]
                    del g["_max_ev"]
                    if "_max_ev_side" in g:
                        del g["_max_ev_side"]
                    
                    # Apply Filters
                    if only_ev and g["ev_percentage"] <= 0:
                        continue
                    if min_ev is not None and g["ev_percentage"] < min_ev:
                        continue
                        
                    # Default values for missing fields to avoid frontend crashes
                    g["team"] = g["team"] or "UNK"
                    g["opponent"] = g["opponent"] or "UNK"
                    g["over_odds"] = g["over_odds"] or -110
                    g["under_odds"] = g["under_odds"] or -110
                    g["best_book"] = g["best_book"] or "Average"
                    
                    # Restore Recommendation Advisory Payload
                    ev_val = g.get("ev_percentage", 0.0)
                    tier = "S" if ev_val >= 5 else "A" if ev_val >= 3 else "B" if ev_val >= 1 else "C"
                    
                    if ev_val > 0.5:
                        reason = f"{g['player_name']} {best_ev_side} {g['line']} shows a {ev_val}% edge vs market average."
                    else:
                        reason = "No significant market edge detected. Watch for late sharp movement."
                        tier = "C"

                    g["recommendation"] = {
                        "side": best_ev_side,
                        "tier": tier,
                        "ev": ev_val,
                        "reason": reason
                    }
                    
                    final_props.append(g)
                
                # Sort if only_ev
                if only_ev:
                    final_props.sort(key=lambda x: x["ev_percentage"], reverse=True)
                
                now_str = datetime.utcnow().isoformat() + "Z"
                
                # If no player props found, fall back to team markets (spreads/totals)
                if not final_props:
                    logger.info(f"No player props found for {sport}, falling back to team markets")
                    team_data = await self._get_team_canonical(sport, session, min_ev, only_ev)
                    return {
                        "props": team_data,
                        "count": len(team_data),
                        "updated": now_str,
                        "fallback": "team_markets"
                    }
                
                return {
                    "props": final_props,
                    "count": len(final_props),
                    "updated": global_updated.isoformat() + "Z" if global_updated else now_str
                }
                
        except Exception as e:
            logger.error(f"Error in get_canonical_props: {e}")
            now_str = datetime.utcnow().isoformat() + "Z"
            return {"props": [], "count": 0, "updated": now_str}

    async def _get_team_canonical(self, sport, session, min_ev=None, only_ev=False):
        """Fallback: return team markets (spreads/totals) in canonical shape when no player props exist."""
        from models import UnifiedOdds
        from datetime import datetime
        
        stmt = select(UnifiedOdds).where(
            UnifiedOdds.sport == sport,
            UnifiedOdds.market_key.in_(['spreads', 'totals'])
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()
        
        grouped = {}
        for o in rows:
            team = o.home_team or "Matchup"
            key = (o.event_id, team, o.market_key, float(o.line) if o.line else 0.0)
            
            if key not in grouped:
                grouped[key] = {
                    "id": f"{o.event_id}_{team.replace(' ','')}_{o.market_key}_{float(o.line or 0.0)}",
                    "game_id": o.event_id,
                    "sport": (o.sport or "").upper().replace("BASKETBALL_",""),
                    "league": (o.league or "").upper().replace("BASKETBALL_",""),
                    "player_name": team,
                    "team": o.home_team or "UNK",
                    "opponent": o.away_team or "UNK",
                    "start_time": o.game_time.isoformat() + "Z" if o.game_time else None,
                    "stat_type": o.market_key.replace("_", " ").title(),
                    "line": float(o.line) if o.line else 0.0,
                    "over_odds": -110,
                    "under_odds": -110,
                    "best_book": o.bookmaker or "Average",
                    "books": [],
                    "implied_probability": 0.0,
                    "model_probability": 0.0,
                    "ev_percentage": 0.0,
                    "confidence": 0.0,
                    "steam_signal": False,
                    "whale_signal": False,
                    "sharp_conflict": False,
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "recommendation": {
                        "side": "over",
                        "tier": "C",
                        "ev": 0.0,
                        "reason": "Team market data. No specific player edge."
                    }
                }
            
            g = grouped[key]
            g["books"].append({"book": o.bookmaker, "side": o.outcome_key, "odds": int(o.price or 0)})
            
            if o.outcome_key == "over" and o.price:
                price = int(o.price)
                if price > g.get("over_odds", -10000):
                    g["over_odds"] = price
            if o.outcome_key == "under" and o.price:
                price = int(o.price)
                if price > g.get("under_odds", -10000):
                    g["under_odds"] = price
        
        return list(grouped.values())

props_service = PropsService()
get_all_props = props_service.get_all_props
get_team_props = props_service.get_team_props
get_canonical_props = props_service.get_canonical_props
