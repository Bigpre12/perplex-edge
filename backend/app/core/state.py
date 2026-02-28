# backend/core/state.py
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SystemState:
    """Manages the internal state of the Lucrix Engine Brain."""
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.cycle_count = 0
        self.last_sync = None
        self.active_tasks = []
        self.health_metrics = {
            "api_status": "healthy",
            "db_status": "healthy",
            "ai_status": "healthy"
        }

    def get_uptime(self) -> float:
        delta = datetime.now(timezone.utc) - self.start_time
        return delta.total_seconds() / 3600.0

    def get_summary(self) -> Dict[str, Any]:
        return {
            "uptime_hours": round(self.get_uptime(), 2),
            "cycle_count": self.cycle_count,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "health": self.health_metrics
        }

# Global state singleton
state = SystemState()
