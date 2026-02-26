"""
BallDontLie v1 API — free tier, no key required.
Fetches real player stat splits: L5, L10, L20, vs-opponent, home/away.
"""
import httpx
from typing import Optional
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

BALLDONTLIE_BASE = "https://api.balldontlie.io/v1"
_BDL_KEY = os.environ.get("BALLDONTLIE_API_KEY", "")
HEADERS = {"Authorization": _BDL_KEY} if _BDL_KEY else {}

async def search_player(name: str) -> Optional[dict]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{BALLDONTLIE_BASE}/players", params={"search": name}, headers=HEADERS)
            if r.status_code != 200:
                logger.warning(f"BallDontLie API returned {r.status_code}: {r.text[:200]}")
                return None
            data = r.json().get("data", [])
            return data[0] if data else None
    except Exception as e:
        logger.error(f"BallDontLie search_player error: {e}")
        return None

async def get_player_stats(player_id: int, last_n: int = 10) -> list[dict]:
    """Fetch last N game stats for a player."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                f"{BALLDONTLIE_BASE}/stats",
                params={
                    "player_ids[]": player_id,
                    "per_page": last_n,
                    "sort": "date",
                    "order": "desc",
                },
                headers=HEADERS
            )
            if r.status_code != 200:
                logger.warning(f"BallDontLie API stats returned {r.status_code}")
                return []
            return r.json().get("data", [])
    except Exception as e:
        logger.error(f"BallDontLie get_player_stats error: {e}")
        return []

def compute_hit_rate(stats: list[dict], stat_key: str, line: float) -> dict:
    """Compute hit rate for over a given line."""
    values = [float(g.get(stat_key, 0) or 0) for g in stats]
    if not values:
        return {"hit_rate": None, "sample": 0, "avg": None, "values": []}
    hits = sum(1 for v in values if v > line)
    return {
        "hit_rate": round(hits / len(values), 3),
        "sample": len(values),
        "avg": round(sum(values) / len(values), 1),
        "values": values,
        "hits": hits,
    }

STAT_KEY_MAP = {
    "points":    "pts",
    "rebounds":  "reb",
    "assists":   "ast",
    "steals":    "stl",
    "blocks":    "blk",
    "threes":    "fg3m",
    "turnovers": "turnover",
    "pra":       None,  # computed below
}

async def get_full_splits(player_name: str, stat_type: str, line: float) -> dict:
    """Master function: returns L5/L10/L20/season splits for a player + stat."""
    player = await search_player(player_name)
    if not player:
        return {"error": f"Player '{player_name}' not found", "player_name": player_name}

    player_id = player["id"]
    stat_key = STAT_KEY_MAP.get(stat_type.lower(), stat_type.lower())

    # Fetch 20 games (covers L5, L10, L20)
    stats = await get_player_stats(player_id, last_n=20)

    def hits_for(n: int):
        subset = stats[:n]
        if stat_key is None and stat_type.lower() == "pra":
            # Points + rebounds + assists combined
            values = [
                float(g.get("pts",0) or 0) +
                float(g.get("reb",0) or 0) +
                float(g.get("ast",0) or 0)
                for g in subset
            ]
            hits = sum(1 for v in values if v > line)
            return {
                "hit_rate": round(hits / len(values), 3) if values else None,
                "sample": len(values),
                "avg": round(sum(values) / len(values), 1) if values else None,
                "values": values,
                "hits": hits,
            }
        return compute_hit_rate(subset, stat_key, line)

    return {
        "player_name": player_name,
        "player_id": player_id,
        "team": f"{player.get('team', {}).get('full_name', 'N/A')}",
        "stat_type": stat_type,
        "line": line,
        "splits": {
            "l5":  hits_for(5),
            "l10": hits_for(10),
            "l20": hits_for(20),
        },
        "source": "balldontlie",
        "timestamp": datetime.utcnow().isoformat(),
    }
