"""
Alternate lines ladder — like Props.cash's ladder feature.
Given a player + stat, return the hit rates at multiple line values
so bettors can find the most +EV line across books.
"""
from fastapi import APIRouter, Query
from services.player_splits_service import search_player, get_player_stats, compute_hit_rate, STAT_KEY_MAP
from datetime import datetime

router = APIRouter(prefix="/alt-lines", tags=["alt-lines"])

@router.get("/ladder")
async def line_ladder(
    player_name: str = Query(...),
    stat_type:   str = Query("points"),
    base_line:   float = Query(..., description="The standard line, e.g. 25.5"),
    step:        float = Query(0.5, description="Step size between ladder rungs"),
    rungs:       int   = Query(7, description="How many alt lines to show above/below"),
    last_n:      int   = Query(15, description="Games to analyze"),
):
    player = await search_player(player_name)
    if not player:
        return {"error": f"Player '{player_name}' not found"}

    stat_key = STAT_KEY_MAP.get(stat_type.lower(), stat_type.lower())
    stats    = await get_player_stats(player["id"], last_n=last_n)

    lines = [round(base_line + (i - rungs // 2) * step, 1) for i in range(rungs)]

    ladder = []
    for l in lines:
        result = compute_hit_rate(stats, stat_key, l)
        hr = result["hit_rate"]
        # Traffic light rating
        if hr is None:
            rating = "unknown"
        elif hr >= 0.70:
            rating = "strong"
        elif hr >= 0.55:
            rating = "lean"
        elif hr >= 0.40:
            rating = "weak"
        else:
            rating = "avoid"

        ladder.append({
            "line":      l,
            "hit_rate":  hr,
            "hits":      result.get("hits"),
            "sample":    result["sample"],
            "avg":       result.get("avg"),
            "rating":    rating,
            "is_base":   l == base_line,
        })

    return {
        "player_name": player_name,
        "stat_type":   stat_type,
        "base_line":   base_line,
        "ladder":      ladder,
        "games_used":  last_n,
        "timestamp":   datetime.utcnow().isoformat(),
    }
