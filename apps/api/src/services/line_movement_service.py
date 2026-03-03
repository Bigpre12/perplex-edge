import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class LineMovementService:
    def __init__(self):
        self.history: Dict[str, List[Dict[str, Any]]] = {}
        self.sharp_threshold = 30 # odds points (e.g. -110 to -140)
    
    def record_movement(self, market_id: str, odds: int, sportsbook: str):
        """Record a snapshot of the current odds for a market"""
        if market_id not in self.history:
            self.history[market_id] = []
        
        self.history[market_id].append({
            "odds": odds,
            "book": sportsbook,
            "timestamp": datetime.now(timezone.utc)
        })
        
        # Keep only last 24h
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        self.history[market_id] = [h for h in self.history[market_id] if h['timestamp'] > cutoff]

    def get_velocity(self, market_id: str) -> float:
        """Calculate movement velocity (odds change per hour)"""
        hits = self.history.get(market_id, [])
        if len(hits) < 2:
            return 0.0
        
        latest = hits[-1]
        earliest = hits[0]
        
        time_diff = (latest['timestamp'] - earliest['timestamp']).total_seconds() / 3600.0
        if time_diff == 0: return 0.0
        
        odds_diff = latest['odds'] - earliest['odds']
        return round(odds_diff / time_diff, 2)

    def detect_steam(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Identify if a move is 'Sharp' / 'Steam'"""
        hits = self.history.get(market_id, [])
        if len(hits) < 2: return None
        
        latest = hits[-1]
        # Look back 1 hour
        window = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_hits = [h for h in hits if h['timestamp'] > window]
        
        if len(recent_hits) < 2: return None
        
        diff = recent_hits[-1]['odds'] - recent_hits[0]['odds']
        if abs(diff) >= self.sharp_threshold:
            return {
                "market_id": market_id,
                "move": diff,
                "velocity": self.get_velocity(market_id),
                "severity": "High" if abs(diff) >= 50 else "Medium"
            }
        return None

line_movement_service = LineMovementService()
