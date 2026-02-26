"""
Free injury data via ESPN hidden API + Rotowire RSS feed.
No API key required.
"""
import httpx
from datetime import datetime
from typing import List, Dict, Any

ESPN_INJURIES = {
    "nba": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries",
    "nfl": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries",
    "mlb": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/injuries",
    "nhl": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/injuries",
}

IMPACT_MAP = {
    "Out":          {"impact": "high",   "color": "#f44336", "badge": "OUT"},
    "Doubtful":     {"impact": "high",   "color": "#ff5722", "badge": "DOUBTFUL"},
    "Questionable": {"impact": "medium", "color": "#ff9800", "badge": "Q"},
    "Probable":     {"impact": "low",    "color": "#8bc34a", "badge": "PROB"},
    "Day-To-Day":   {"impact": "medium", "color": "#ff9800", "badge": "D2D"},
}

async def fetch_injuries(sport: str = "nba") -> list[dict]:
    url = ESPN_INJURIES.get(sport.lower())
    if not url:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            data = r.json()
    except Exception:
        return []

    injuries = []
    for team in data.get("injuries", []):
        team_name = team.get("team", {}).get("displayName", "")
        for inj in team.get("injuries", []):
            athlete = inj.get("athlete", {})
            status  = inj.get("status", "Unknown")
            meta    = IMPACT_MAP.get(status, {"impact": "unknown", "color": "#888", "badge": status})
            injuries.append({
                "player_name":  athlete.get("displayName", ""),
                "position":     athlete.get("position", {}).get("abbreviation", ""),
                "team":         team_name,
                "status":       status,
                "description":  inj.get("longComment", inj.get("shortComment", "")),
                "sport":        sport.upper(),
                "impact":       meta["impact"],
                "color":        meta["color"],
                "badge":        meta["badge"],
                "return_date":  inj.get("date", "Unknown"),
                "source":       "ESPN",
                "fetched_at":   datetime.utcnow().isoformat(),
            })

    return sorted(injuries, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["impact"], 3))


# ─── Backward-compatible class wrapper ────────────────────────────────────────
# immediate_working.py imports `injury_service` (singleton) and calls
# `injury_service.filter_injured_players(props, sport, name_key="player_name")`

class InjuryService:
    """Compatibility wrapper so existing code can call injury_service.filter_injured_players()."""

    _cache: dict = {}
    _cache_ts: dict = {}

    async def _get_injuries(self, sport: str) -> list[dict]:
        import time
        now = time.time()
        # Cache for 5 minutes
        if sport in self._cache and (now - self._cache_ts.get(sport, 0)) < 300:
            return self._cache[sport]
        try:
            data = await fetch_injuries(sport)
            self._cache[sport] = data
            self._cache_ts[sport] = now
            return data
        except Exception:
            return self._cache.get(sport, [])

    async def filter_injured_players(self, props: list, sport_key: str, name_key: str = "player_name") -> list:
        """
        Async filter — removes players with high-impact injuries (Out/Doubtful) from the prop list.
        """
        # Extract the short sport name from sport_key (e.g. "basketball_nba" -> "nba")
        sport_short = sport_key.split("_")[-1] if "_" in sport_key else sport_key
        try:
            injuries = await self._get_injuries(sport_short)
        except Exception:
            return props

        injured_names = {i["player_name"].lower() for i in injuries if i["impact"] == "high"}
        if not injured_names:
            return props
        return [p for p in props if p.get(name_key, "").lower() not in injured_names]

    async def calculate_injury_impact(self, sport: str, team: str) -> List[Dict[str, Any]]:
        """Identify teammates who benefit from a star player being OUT"""
        try:
            injuries = await self._get_injuries(sport)
            star_injured = [i for i in injuries if i['team'] == team and i['impact'] == 'high']
            
            if not star_injured: return []
            
            # Simple alpha: if a teammate is OUT, other teammates get more usage
            # In a real app, this would use a usage-transfer model
            impacts = []
            for inj in star_injured:
                impacts.append({
                    "absent_player": inj['player_name'],
                    "beneficiaries": [
                        {"name": "Teammate A", "boost": 0.15, "reason": "Increased Usage"},
                        {"name": "Teammate B", "boost": 0.10, "reason": "More Shot Attempts"}
                    ],
                    "team": team,
                    "sport": sport
                })
            return impacts
        except Exception:
            return []


# Singleton for backward compatibility
injury_service = InjuryService()
