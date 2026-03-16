class AsyncSession: pass
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import insert
from services.odds_api_client import odds_api
from models.prop import PropLine

logger = logging.getLogger(__name__)

class SteamService:
    def __init__(self):
        self.line_history = {} # In-memory cache for delta comparison

    def _snapshot_key(self, player: str, stat: str, side: str) -> str:
        return f"{player.lower()}:{stat.lower()}:{side.lower()}"

    async def detect_and_persist_steam(self, sport: str, db: AsyncSession) -> List[Dict]:
        """
        Detects steam moves (unusual line/odds movement across multiple books)
        and persists them to the steam_events table.
        """
        alerts = []
        try:
            events = await odds_api.get_events(sport)
            if not events:
                return []

            # Sample the biggest upcoming games
            for event in events[:10]:
                event_id = event["id"]
                home = event.get("home_team", "")
                away = event.get("away_team", "")
                
                # Fetch props using the client
                data = await odds_api.get_player_props(sport, event_id, "player_points,player_rebounds,player_assists", regions="us")
                if not data:
                    continue
                
                current_snapshot = self._extract_snapshot(data)
                
                for key, current in current_snapshot.items():
                    if key in self.line_history:
                        prev = self.line_history[key]
                        alert = await self._analyze_movement(current, prev, home, away, sport, db)
                        if alert:
                            alerts.append(alert)
                    
                    self.line_history[key] = current
            
            return alerts
        except Exception as e:
            logger.error(f"Steam detection error for {sport}: {e}")
            return []

    def _extract_snapshot(self, data: Dict) -> Dict:
        """Flattens nested bookmaker data into a searchable snapshot."""
        snapshot = {}
        bookmakers = data.get("bookmakers", [])
        for bm in bookmakers:
            book_name = bm["title"]
            for market in bm.get("markets", []):
                stat = market["key"]
                for outcome in market.get("outcomes", []):
                    player = outcome.get("description", "Unknown")
                    side = outcome.get("name", "over").lower()
                    key = self._snapshot_key(player, stat, side)
                    
                    if key not in snapshot:
                        snapshot[key] = {
                            "player": player,
                            "stat": stat,
                            "side": side,
                            "line": outcome.get("point", 0.0),
                            "odds": {},
                            "ts": datetime.now(timezone.utc)
                        }
                    snapshot[key]["odds"][book_name] = outcome.get("price", -110)
        return snapshot

    async def _analyze_movement(self, curr: Dict, prev: Dict, home: str, away: str, sport: str, db: AsyncSession) -> Optional[Dict]:
        """Detects if lines moved significantly across 3+ books."""
        books_moved = []
        total_delta = 0
        
        # We only look at price moves for the SAME line point
        if curr["line"] != prev["line"]:
            return None # Handle point moves elsewhere or later

        for book, curr_price in curr["odds"].items():
            if book in prev["odds"]:
                prev_price = prev["odds"][book]
                delta = curr_price - prev_price # e.g. -110 to -125 is -15
                
                if abs(delta) >= 10: # Significant move
                    books_moved.append(book)
                    total_delta += delta
        
        if len(books_moved) >= 3:
            avg_move = total_delta / len(books_moved)
            severity = min(10.0, len(books_moved) * 1.5 + abs(avg_move) / 10.0)
            
            alert_data = {
                "sport": sport,
                "player_name": curr["player"],
                "stat_type": curr["stat"],
                "side": curr["side"],
                "line": curr["line"],
                "movement": round(avg_move, 1),
                "book_count": len(books_moved),
                "severity": round(severity, 1),
                "description": f"STEAM detected: {len(books_moved)} books pushed {curr['side']} odds on {curr['player']}"
            }
            
            # Persist to steam_events
            from models.analytical import SteamEvent
            stmt = insert(SteamEvent).values(**alert_data)
            await db.execute(stmt)
            await db.commit()
            
            return alert_data
        
        return None

steam_service = SteamService()
detect_and_persist_steam = steam_service.detect_and_persist_steam
