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

middle_service = MiddleService()
