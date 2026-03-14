# apps/api/src/routers/edges.py
from fastapi import APIRouter, Query
from typing import Optional
from services.props_service import get_all_props
from services.ev_service import grade_prop
from database import get_db_connection

router = APIRouter(prefix="/api/edges", tags=["edges"])

@router.get("/top")
async def top_edges(
    sport: Optional[str] = Query(None),
    min_ev: float = Query(2.0),
    min_hit_rate: float = Query(55.0),
    confidence: Optional[str] = Query(None),
    limit: int = Query(100),
):
    props = await get_all_props(sport_filter=sport)

    # Get hit rates from DB - offload to executor to avoid blocking
    def _fetch_hit_rates():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT player_name, stat_type, hit_rate FROM player_hit_rates")
            return {
                f"{r['player_name']}|{r['stat_type']}": r["hit_rate"]
                for r in cursor.fetchall()
            }
        finally:
            conn.close()

    import asyncio
    loop = asyncio.get_running_loop()
    hit_rate_map = await loop.run_in_executor(None, _fetch_hit_rates)

    # Group over/under by player+stat+line to get both sides for vig removal
    grouped: dict = {}
    for prop in props:
        key = f"{prop['player_name']}|{prop['stat_type']}|{prop['line']}"
        if key not in grouped:
            grouped[key] = {"over": None, "under": None, "meta": prop}
        if prop["pick"].lower() == "over" and (
            grouped[key]["over"] is None or prop["odds"] > grouped[key]["over"]["odds"]
        ):
            grouped[key]["over"] = prop
        elif prop["pick"].lower() == "under" and (
            grouped[key]["under"] is None or prop["odds"] > grouped[key]["under"]["odds"]
        ):
            grouped[key]["under"] = prop

    results = []
    for key, data in grouped.items():
        if not data["over"] or not data["under"]:
            continue

        meta = data["meta"]
        over_odds = data["over"]["odds"]
        under_odds = data["under"]["odds"]
        
        hr_key = f"{meta['player_name']}|{meta['stat_type']}"
        hit_rate = hit_rate_map.get(hr_key)

        for pick_side, pick_odds, pick_book in [
            ("over", over_odds, data["over"]["book"]),
            ("under", under_odds, data["under"]["book"]),
        ]:
            graded = grade_prop(
                pick=pick_side,
                over_odds=over_odds,
                under_odds=under_odds,
                hit_rate=hit_rate,
            )

            if graded["ev_percentage"] < min_ev:
                continue
            if hit_rate and hit_rate < min_hit_rate:
                continue
            if confidence and graded["confidence"] != confidence:
                continue

            results.append({
                "player_name": meta["player_name"],
                "sport": meta["sport"],
                "team": meta.get("home_team", ""),
                "opponent": meta.get("away_team", ""),
                "stat_type": meta["stat_type"],
                "line": meta["line"],
                "pick": pick_side,
                "odds": pick_odds,
                "book": pick_book,
                "game_time": meta.get("commence_time", ""),
                "hit_rate": hit_rate,
                **graded,
            })

    results.sort(key=lambda x: x["ev_percentage"], reverse=True)
    return {"count": len(results[:limit]), "props": results[:limit]}
