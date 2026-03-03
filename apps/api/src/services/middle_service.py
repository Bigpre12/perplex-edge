import logging
from typing import List, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MiddleService:
    async def scan_for_middles(self, games_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans a list of games and their bookmaker data for middle opportunities.
        A middle occurs when Book A's Over line is significantly lower than Book B's Under line.
        """
        middles = []
        
        for game in games_data:
            bookmakers = game.get("bookmakers", [])
            if len(bookmakers) < 2:
                continue
                
            # Dictionary to track best lines per market
            # market_id -> { 'over': {'book': name, 'line': val, 'odds': odds}, 'under': ... }
            market_map = {}
            
            for bm in bookmakers:
                bm_name = bm.get("title")
                for market in bm.get("markets", []):
                    market_key = market.get("key")
                    outcomes = market.get("outcomes", [])
                    
                    if market_key not in market_map:
                        market_map[market_key] = {"over": None, "under": None}
                        
                    for outcome in outcomes:
                        name = outcome.get("name", "").lower()
                        line = outcome.get("point")
                        odds = outcome.get("price")
                        
                        if line is None: continue
                        
                        if "over" in name:
                            current = market_map[market_key]["over"]
                            if current is None or line < current["line"]:
                                market_map[market_key]["over"] = {
                                    "book": bm_name, "line": line, "odds": odds
                                }
                        elif "under" in name:
                            current = market_map[market_key]["under"]
                            if current is None or line > current["line"]:
                                market_map[market_key]["under"] = {
                                    "book": bm_name, "line": line, "odds": odds
                                }
            
            # Check for windows in each market
            for m_key, best in market_map.items():
                if best["over"] and best["under"]:
                    over_line = best["over"]["line"]
                    under_line = best["under"]["line"]
                    
                    if under_line > over_line:
                        # Profit window found
                        middles.append({
                            "game": f"{game.get('away_team')} @ {game.get('home_team')}",
                            "market": m_key.replace("player_", "").replace("_", " ").upper(),
                            "window": f"{over_line} - {under_line}",
                            "width": round(under_line - over_line, 1),
                            "over_side": best["over"],
                            "under_side": best["under"],
                            "profit_potential": "High" if (under_line - over_line) >= 2 else "Medium",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
        return middles

    async def scan_for_prop_middles(self, sport_key: str) -> List[Dict[str, Any]]:
        """
        Scans the PropLine/PropOdds database for middle/arbitrage windows.
        """
        from database import SessionLocal
        from models.props import PropLine, PropOdds
        from sqlalchemy import select
        from services.monte_carlo_service import american_to_implied
        
        db = SessionLocal()
        middles = []
        try:
            stmt = select(PropLine).where(PropLine.sport_key == sport_key).limit(500)
            res = db.execute(stmt)
            props = res.scalars().all()
            
            for p in props:
                odds_stmt = select(PropOdds).where(PropOdds.prop_line_id == p.id)
                o_res = db.execute(odds_stmt)
                book_odds = o_res.scalars().all()
                
                if len(book_odds) < 2: continue
                
                for i, b1 in enumerate(book_odds):
                    for j, b2 in enumerate(book_odds):
                        if i == j: continue
                        p1, p2 = american_to_implied(b1.over_odds), american_to_implied(b2.under_odds)
                        if (p1 + p2) < 0.99:
                            middles.append({
                                "game": f"{p.team} @ {p.opponent}",
                                "market": f"{p.player_name} {p.stat_type.upper().replace('_', ' ')}",
                                "window": f"Line: {p.line}",
                                "width": round(1.0 - (p1 + p2), 3),
                                "over_side": {"book": b1.sportsbook, "odds": b1.over_odds},
                                "under_side": {"book": b2.sportsbook, "odds": b2.under_odds},
                                "profit_potential": "High" if (p1 + p2) < 0.95 else "Medium",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "is_arb": True 
                            })
            return middles
        finally:
            db.close()

middle_service = MiddleService()
