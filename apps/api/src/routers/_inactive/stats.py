from fastapi import APIRouter, Query
from typing import Optional
from services.props_service import fetch_scores, fetch_active_sports
from config.sports_config import ALL_SPORTS, SPORT_DISPLAY
import asyncio

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("/scores")
async def get_scores(sport: Optional[str] = Query(None), days: int = Query(1)):
    active = await fetch_active_sports()
    target = [sport] if sport else [s for s in ALL_SPORTS if s in active]

    all_scores = []
    results = await asyncio.gather(*[fetch_scores(s, days_from=days) for s in target])

    for sport_key, games in zip(target, results):
        for g in games:
            scores = {s["name"]: s["score"] for s in (g.get("scores") or [])}
            all_scores.append({
                "id": g["id"],
                "sport": SPORT_DISPLAY.get(sport_key, sport_key),
                "home_team": g["home_team"],
                "away_team": g["away_team"],
                "home_score": scores.get(g["home_team"]),
                "away_score": scores.get(g["away_team"]),
                "completed": g.get("completed"),
                "commence_time": g.get("commence_time"),
            })

    return {"count": len(all_scores), "scores": all_scores}

@router.get("/active-sports")
async def active_sports():
    active = await fetch_active_sports()
    return {
        "sports": [
            {"key": s, "display": SPORT_DISPLAY.get(s, s)}
            for s in active if s in ALL_SPORTS
        ]
    }
