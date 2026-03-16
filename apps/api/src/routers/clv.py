from common_deps import get_current_user_supabase
from api_utils.validation import validate_sport
from fastapi import APIRouter, Query, Depends, Security
from common_deps import require_pro, require_elite
from typing import Optional
import os, httpx, asyncio
from core.sports_config import ALL_SPORTS, SPORT_DISPLAY
from db.session import get_db_connection, SessionLocal

router = APIRouter(tags=["clv"])
from services.odds_api_client import odds_api

async def fetch_historical_odds(sport: str, event_id: str) -> dict:
    """Fetch historical odds using the managed client."""
    res = await odds_api.get_player_props(sport, event_id, markets="h2h,spreads,totals", regions="us,us2")
    return res if isinstance(res, dict) else {"bookmakers": res}

@router.get("/")
@router.get("/track")
async def track_clv(sport: str = Query("basketball_nba")):
    """
    Returns live CLV tracking data from local DB (fallback to Supabase).
    """
    try:
        from db.session import SessionLocal
        from models.analytical import CLVRecord
        from sqlalchemy import desc
        
        db = SessionLocal()
        # Look for local records first
        records = db.query(CLVRecord).order_by(desc(CLVRecord.created_at)).limit(50).all()
        db.close()
        
        if records:
            return [{
                "player": r.player_name,
                "stat_type": r.stat_type,
                "open_line": r.opening_line,
                "current_line": r.closing_line,
                "close_line": r.closing_line,
                "clv_value": r.clv,
                "sportsbook": "Lucrix Edge",
                "recorded_at": r.created_at.isoformat()
            } for r in records]

        # FALLBACK: Supabase
        import httpx
        import os
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            return []

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        async with httpx.AsyncClient() as client:
            url = f"{SUPABASE_URL}/rest/v1/clv_snapshots?sport=eq.{sport}&limit=50&order=recorded_at.desc"
            r = await client.get(url, headers=headers)
            snapshots = r.json() if r.status_code == 200 else []
            
            return [{
                "player": s.get("player"),
                "stat_type": s.get("stat_type"),
                "open_line": s.get("open_line"),
                "current_line": s.get("current_line"),
                "close_line": s.get("close_line"),
                "clv_value": s.get("clv_value"),
                "sportsbook": s.get("sportsbook"),
                "recorded_at": s.get("recorded_at")
            } for s in snapshots]
    except Exception as e:
        print(f"CLV fetch error: {e}")
        return []

@router.get("/summary")
async def get_clv(
    sport: Optional[str] = Query(None),
    user: dict = Depends(get_current_user_supabase)
):
    sport = validate_sport(sport)
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT id, player_name, sport, stat_type, line,
               pick, odds as open_odds, game_time,
               hit, result, event_id
        FROM picks
        WHERE user_id = ? AND open_odds IS NOT NULL
    """
    params = [user["id"]]
    if sport:
        query += " AND sport = ?"
        params.append(sport)
    query += " ORDER BY game_time DESC LIMIT 200"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    clv_entries = []
    for row in rows:
        # Calculate CLV: compare open odds to close odds
        # Note: In a real implementation, you'd fetch the actual close odds from API or DB
        open_odds = row["open_odds"]
        close_odds = row["open_odds"] # fallback if can't fetch
        
        def american_to_implied(odds: float) -> float:
            if odds > 0:
                return 100 / (odds + 100)
            return abs(odds) / (abs(odds) + 100)

        open_implied = american_to_implied(open_odds)
        close_implied = american_to_implied(close_odds)
        clv = round((close_implied - open_implied) * 100, 2)

        # Remove vig for true EV at close
        vig_factor = 0.955
        ev_at_close = round((close_implied * vig_factor - (1 - close_implied)) * 100, 2)

        clv_entries.append({
            "id": row["id"],
            "player_name": row["player_name"],
            "sport": row["sport"],
            "stat_type": row["stat_type"],
            "line": row["line"],
            "pick": row["pick"],
            "open_odds": open_odds,
            "close_odds": close_odds,
            "clv": clv,
            "ev_at_close": ev_at_close,
            "result": row["result"],
            "game_time": row["game_time"],
        })

    return {"count": len(clv_entries), "clv": clv_entries}

@router.get("/leaderboard", dependencies=[Depends(require_pro)])
async def get_clv_leaderboard(
    limit: int = Query(20, description="Number of picks to return"),
    sport: Optional[str] = Query(None, description="Filter by sport")
):
    """Top picks ranked by CLV percentage."""
    # This logic is adapted from legacy analysis.py _generate_sample_clv_picks
    from services.clv_service import clv_service
    from db.session import async_session_maker
    from models.prop import PropLine, PropHistory
    from sqlalchemy import select
    
    async with async_session_maker() as db:
        stmt = select(PropLine).join(PropHistory).distinct().limit(50)
        if sport:
            stmt = stmt.where(PropLine.sport_key == sport)
            
        result = await db.execute(stmt)
        lines = result.scalars().all()
        
        picks = []
        for line in lines:
            hist_stmt = select(PropHistory).where(PropHistory.prop_line_id == line.id).order_by(PropHistory.created_at)
            hist_res = await db.execute(hist_stmt)
            history = hist_res.scalars().all()
            
            if not history: continue
            
            hist_data = [
                {"line_value": h.old_line, "timestamp": h.created_at.isoformat()},
                {"line_value": h.new_line, "timestamp": h.created_at.isoformat()}
            ]
            
            clv_res = clv_service.compute_for_pick(
                pick_data={"odds": -110}, 
                odds_history=hist_data
            )
            
            picks.append({
                "id": line.id,
                "player_name": line.player_name,
                "stat_type": line.stat_type,
                "sport": line.sport_key.split("_")[-1].upper() if "_" in line.sport_key else line.sport_key.upper(),
                "line": line.line,
                "odds": -110,
                **clv_res
            })
            
        # Sort by CLV descending
        ranked = sorted(
            [p for p in picks if p.get("clv_percentage") is not None],
            key=lambda p: p["clv_percentage"],
            reverse=True,
        )
        
        return {"leaderboard": ranked[:limit], "total": len(ranked)}
