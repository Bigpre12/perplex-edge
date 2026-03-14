import time
from typing import Any, Optional

class TTLCache:
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expires_at = self._store[key]
            if time.time() < expires_at:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        self._store[key] = (value, time.time() + ttl_seconds)

    def invalidate(self, key: str):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()

# TTL strategy per data type (seconds)
CACHE_TTL = {
    "player_props": 55,       # 55 sec — per task requirement
    "team_props": 55,         # 55 sec
    "live_games": 30,         # 30 sec — live scores
    "scores": 300,            # 5 min — completed scores
    "slate": 300,             # 5 min — today's games
    "injuries": 300,          # 5 min
    "news": 180,              # 3 min
    "active_sports": 3600,    # 1 hour — rarely changes
    "hit_rates": 600,         # 10 min — DB data
}

cache = TTLCache()
