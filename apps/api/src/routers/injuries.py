# apps/api/src/routers/injuries.py
# Uses ESPN's free public API — no key required, real-time injury data

from fastapi import APIRouter, Query
import httpx
import logging

from services.intel_service import intel_service

router = APIRouter(tags=["injuries"])
logger = logging.getLogger(__name__)

ESPN_INJURY_URLS = {
    "NBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries",
    "NFL": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries",
    "MLB": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/injuries",
    "NHL": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/injuries",
    "WNBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/injuries",
}

# Cache in memory
_injury_cache: dict[str, set[str]] = {}

async def fetch_injured_players(sport: str = "NBA") -> set[str]:
    """Internal helper to get set of injured player names for filtering."""
    url = ESPN_INJURY_URLS.get(sport.upper())
    if not url:
        return set()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
        if r.status_code != 200:
            return set()
        data = r.json()
        injured = set()
        
        # ESPN structure: team_entry.injuries[] -> athlete.displayName
        for team_entry in data.get("injuries", []):
            for inj in team_entry.get("injuries", []):
                status = inj.get("status", "").lower()
                # Only include significant injuries that would mean they aren't playing
                critical_statuses = ("out", "injured reserve", "doubtful", "suspension", "not with team", "day-to-day" if "ruled out" in inj.get("shortComment", "").lower() else "out")
                if any(s in status for s in critical_statuses) or status == "out":
                    athlete = inj.get("athlete", {})
                    name = athlete.get("displayName", "")
                    if name:
                        injured.add(name.lower())
        
        _injury_cache[sport.upper()] = injured
        return injured
    except Exception as e:
        logger.error(f"[INJURY] ESPN fetch failed for {sport}: {e}")
        return _injury_cache.get(sport.upper(), set())

@router.get("/injuries")
async def get_injuries(sport: str = Query("NBA", description="NBA, NFL, MLB, NHL, WNBA")):
    """Public endpoint for injury reports."""
    url = ESPN_INJURY_URLS.get(sport.upper())
    if not url:
        return {"injuries": [], "error": "Invalid sport"}
        
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
        if r.status_code != 200:
            return {"injuries": [], "error": f"ESPN returned {r.status_code}"}
        
        data = r.json()
        result = []
        for team_entry in data.get("injuries", []):
            team = team_entry.get("team", {})
            team_name = team.get("displayName", "")
            for inj in team_entry.get("injuries", []):
                athlete = inj.get("athlete", {})
                display_name = athlete.get("displayName", "")
                status = inj.get("status", "")
                position = athlete.get("position", {}).get("abbreviation", "")
                
                # Improved heuristic for "Impact Analysis"
                stat_impact = "High Variance"
                teammate_boost = "Next Man Up"
                direction = "neutral"
                
                # NFL Positions
                if position == "QB":
                    stat_impact = "-4.5 Spread"
                    teammate_boost = "Backup QB"
                    direction = "negative"
                elif position == "RB":
                    stat_impact = "+12.5 Rush Yds"
                    teammate_boost = "RB2 Boost"
                    direction = "positive"
                elif position == "WR":
                    stat_impact = "+8.5 Targets"
                    teammate_boost = "WR2 Boost"
                    direction = "positive"
                # NBA Positions
                elif position in ("PG", "SG"):
                    stat_impact = "+2.4 Ast"
                    teammate_boost = "Guard Boost"
                    direction = "positive"
                elif position in ("SF", "PF"):
                    stat_impact = "+3.6 Pts"
                    teammate_boost = "Wing Boost"
                    direction = "positive"
                elif position == "C":
                    stat_impact = "+4.2 Reb"
                    teammate_boost = "Post Boost"
                    direction = "positive"
                
                if "out" in status.lower() or "injured reserve" in status.lower():
                    # direction is already set or modified above
                    pass
                else:
                    direction = "neutral"

                result.append({
                    "player": display_name,
                    "position": position,
                    "team": team_name,
                    "status": status,
                    "detail": inj.get("details", {}).get("detail", "N/A"),
                    "return_date": inj.get("details", {}).get("returnDate", None),
                    "short_comment": inj.get("shortComment", ""),
                    "stat_impact": stat_impact,
                    "teammate_boost": teammate_boost,
                    "direction": direction,
                    "body_part": inj.get("details", {}).get("type", "General") if isinstance(inj.get("details"), dict) else "General"
                })
        return {"injuries": result, "count": len(result), "sport": sport.upper()}
    except Exception as e:
        logger.error(f"[INJURY] API error: {e}")
        return {"injuries": [], "error": str(e)}

@router.get("/check/{player_name}")
async def check_player_injured(player_name: str, sport: str = "NBA"):
    """Check if a specific player is currently on the injury report."""
    injured_set = await fetch_injured_players(sport)
    is_injured = player_name.lower() in injured_set
    return {"player": player_name, "injured": is_injured, "sport": sport}

@router.get("/recent-intel")
async def recent_intel(sport: str = "basketball_nba"):
    """Fetch recent AI-curated market intelligence."""
    return await intel_service.get_daily_intel(sport)
