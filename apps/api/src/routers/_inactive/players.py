from fastapi import APIRouter, Depends, Security
from api_utils.auth_supabase import get_current_user_supabase
from api_utils.validation import validate_sport
from database import get_db_connection
from services.props_service import get_all_props
from services.ev_service import grade_prop
from urllib.parse import unquote

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/{player_name}")
async def get_player_profile(
    player_name: str,
    user: dict = Depends(get_current_user_supabase)
):
    name = unquote(player_name)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Hit rates
    cursor.execute("""
        SELECT stat_type,
               ROUND(AVG(CASE WHEN hit = 1 THEN 100.0 ELSE 0 END), 1) as hit_rate,
               COUNT(*) as total_picks,
               SUM(CASE WHEN hit = 1 THEN 1 ELSE 0 END) as hits,
               ROUND(AVG(ev_percentage), 2) as avg_ev
        FROM picks
        WHERE player_name = ? AND user_id = ? AND hit IS NOT NULL
        GROUP BY stat_type
        ORDER BY total_picks DESC
    """, (name, user["id"]))
    hit_rates = [dict(r) for r in cursor.fetchall()]

    # Recent stats from picks (actual values)
    cursor.execute("""
        SELECT game_time as game_date, opponent, stat_type, actual_value as value
        FROM picks
        WHERE player_name = ? AND user_id = ? AND actual_value IS NOT NULL
        ORDER BY game_time DESC LIMIT 20
    """, (name, user["id"]))
    stats = [dict(r) for r in cursor.fetchall()]

    # Get sport and team from most recent pick
    cursor.execute("SELECT sport, team FROM picks WHERE player_name = ? AND user_id = ? ORDER BY game_time DESC LIMIT 1", (name, user["id"]))
    meta = cursor.fetchone()
    conn.close()

    # Today's props from live API
    all_props = await get_all_props()
    player_props_raw = [p for p in all_props if p["player_name"].lower() == name.lower()]

    # Group and grade
    grouped: dict = {}
    for p in player_props_raw:
        key = f"{p['stat_type']}|{p['line']}"
        side = p["pick"].lower()
        if key not in grouped:
            grouped[key] = {"over": None, "under": None, "meta": p}
        if side in ("over", "under") and (grouped[key][side] is None or p["odds"] > grouped[key][side]["odds"]):
            grouped[key][side] = p

    graded_props = []
    for key, sides in grouped.items():
        if not sides["over"] or not sides["under"]:
            continue
        for side in ["over", "under"]:
            p = sides[side]
            graded = grade_prop(pick=side, over_odds=sides["over"]["odds"], under_odds=sides["under"]["odds"])
            graded_props.append({
                "stat_type": p["stat_type"],
                "line": p["line"],
                "pick": side,
                "odds": p["odds"],
                "book": p["book"],
                **graded,
            })

    graded_props.sort(key=lambda x: x["ev_percentage"], reverse=True)

    return {
        "player_name": name,
        "team": meta["team"] if meta else "",
        "sport": meta["sport"] if meta else "",
        "position": "",
        "injury_status": None,
        "hit_rates": hit_rates,
        "stats": stats,
        "props": graded_props,
    }
