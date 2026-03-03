from fastapi import APIRouter, Query
from services.injury_service import fetch_injuries

router = APIRouter(prefix="/injuries", tags=["injuries"])

@router.get("/report")
async def injury_report(
    sport: str = Query("nba", description="nba, nfl, mlb, nhl"),
    impact: str = Query("all", description="all, high, medium, low"),
):
    injuries = await fetch_injuries(sport)
    if impact != "all":
        injuries = [i for i in injuries if i["impact"] == impact]
    return {
        "sport": sport.upper(),
        "total": len(injuries),
        "high_impact": sum(1 for i in injuries if i["impact"] == "high"),
        "injuries": injuries,
    }

@router.get("/player/{player_name}")
async def player_injury_status(player_name: str, sport: str = Query("nba")):
    injuries = await fetch_injuries(sport)
    matches = [i for i in injuries if player_name.lower() in i["player_name"].lower()]
    return {
        "player_name": player_name,
        "status": matches[0] if matches else {"status": "Active", "impact": "none", "badge": "ACTIVE", "color": "#00e676"},
    }
