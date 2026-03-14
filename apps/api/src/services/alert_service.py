import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from app.services.odds_api_client import odds_api

logger = logging.getLogger(__name__)

# In-memory history for line movement: {prop_key: [(timestamp, line), ...]}
_line_history: Dict[str, List[tuple]] = {}

class AlertService:
    def __init__(self):
        self.steam_threshold_points = 1.5
        self.steam_window_minutes = 10
        self.max_history_age_minutes = 60

    def _get_prop_key(self, player: str, stat: str, side: str) -> str:
        return f"{player.lower()}:{stat.lower()}:{side.lower()}"

    def record_movement(self, player: str, stat: str, side: str, line: float):
        """Record a line snapshot."""
        key = self._get_prop_key(player, stat, side)
        if key not in _line_history:
            _line_history[key] = []
        
        now = datetime.now(timezone.utc)
        _line_history[key].append((now, line))
        
        # Cleanup old history
        cutoff = now - timedelta(minutes=self.max_history_age_minutes)
        _line_history[key] = [h for h in _line_history[key] if h[0] > cutoff]

    async def get_steam_alerts(self, sport: str) -> List[Dict[str, Any]]:
        """
        Detect steam moves: > 1.5 points movement in < 10 minutes.
        This requires external polling/snapshots to be populated.
        """
        alerts = []
        now = datetime.now(timezone.utc)
        target_time = now - timedelta(minutes=self.steam_window_minutes)
        
        for key, history in _line_history.items():
            if len(history) < 2:
                continue
            
            latest_time, latest_line = history[-1]
            # Find earliest point in the window
            earliest_in_window = next((h for h in history if h[0] >= target_time), history[0])
            earliest_time, earliest_line = earliest_in_window
            
            diff = abs(latest_line - earliest_line)
            
            if diff >= self.steam_threshold_points:
                player, stat, side = key.split(":")
                alerts.append({
                    "id": f"steam_{key}_{latest_time.timestamp()}",
                    "type": "STEAM",
                    "player": player.title(),
                    "stat": stat.title(),
                    "side": side.upper(),
                    "old_line": earliest_line,
                    "new_line": latest_line,
                    "movement": diff,
                    "timestamp": latest_time.isoformat(),
                    "severity": "HIGH" if diff >= 3.0 else "MEDIUM",
                    "description": f"Rapid Steam: {player.title()} {stat.title()} moved {diff} points in under 10m"
                })
        
        return sorted(alerts, key=lambda x: x["movement"], reverse=True)

alert_service = AlertService()
