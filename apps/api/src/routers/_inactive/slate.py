# apps/api/src/routers/slate.py
from fastapi import APIRouter, Query
from typing import Optional
from services.props_service import get_all_props, fetch_active_sports
from services.ev_service import grade_prop
from config.sports_config import ALL_SPORTS, SPORT_DISPLAY
from datetime import datetime, timezone

router = APIRouter(prefix="/api/slate", tags=["slate"])

@router.get("/today")
async def today_slate(sport: Optional[str] = Query(None)):
    props = await get_all_props(sport_filter=sport)
    today = datetime.now(timezone.utc).date()

    # Group by event
    events: dict = {}
    for prop in props:
        commence = prop.get("commence_time", "")
        if not commence: continue
        try:
            game_date = datetime.fromisoformat(commence.replace("Z", "+00:00")).date()
        except Exception:
            continue
        if game_date != today:
            continue

        eid = prop["event_id"]
        if eid not in events:
            events[eid] = {
                "event_id": eid,
                "sport": prop["sport"],
                "home_team": prop["home_team"],
                "away_team": prop["away_team"],
                "commence_time": commence,
                "all_props": [],
            }
        events[eid]["all_props"].append(prop)

    games = []
    for eid, event in events.items():
        # Grade and pick top 5 props per game
        graded_props = []
        grouped: dict = {}
        for p in event["all_props"]:
            key = f"{p['player_name']}|{p['stat_type']}|{p['line']}"
            if key not in grouped:
                grouped[key] = {"over": None, "under": None}
            side = p["pick"].lower()
            if side in ("over", "under"):
                if grouped[key][side] is None or p["odds"] > grouped[key][side]["odds"]:
                    grouped[key][side] = p

        for key, sides in grouped.items():
            if not sides["over"] or not sides["under"]:
                continue
            for side in ["over", "under"]:
                p = sides[side]
                graded = grade_prop(
                    pick=side,
                    over_odds=sides["over"]["odds"],
                    under_odds=sides["under"]["odds"],
                )
                graded_props.append({
                    "player_name": p["player_name"],
                    "stat_type": p["stat_type"],
                    "line": p["line"],
                    "pick": side,
                    "odds": p["odds"],
                    "book": p["book"],
                    **graded,
                })

        graded_props.sort(key=lambda x: x["ev_percentage"], reverse=True)
        event["top_props"] = graded_props[:5]
        del event["all_props"]
        games.append(event)

    games.sort(key=lambda x: x["commence_time"])
    return {"count": len(games), "games": games}
