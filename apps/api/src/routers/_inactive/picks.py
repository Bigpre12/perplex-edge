import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from api_utils.auth_supabase import get_current_user_supabase
from api_utils.validation import validate_sport, validate_limit
from database import get_db_connection

router = APIRouter(prefix="/api/picks", tags=["picks"])

class PickCreate(BaseModel):
    player_name: str
    team: str
    opponent: str
    sport: str
    stat_type: str
    line: float
    model_projection: float
    pick: str  # "over" | "under"
    confidence: str  # "HIGH" | "MEDIUM" | "LOW"
    ev_percentage: float
    odds: int
    game_time: str
    event_id: Optional[str] = None

class PickSettle(BaseModel):
    pick_id: str
    actual_value: float

@router.get("")
async def get_picks(
    sport: Optional[str] = None, 
    settled: Optional[bool] = None,
    user: dict = Depends(get_current_user_supabase)
):
    sport = validate_sport(sport)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM picks WHERE user_id = ?"
    params = [user.id]
    if sport:
        query += " AND sport = ?"
        params.append(sport)
    if settled is True:
        query += " AND hit IS NOT NULL"
    elif settled is False:
        query += " AND hit IS NULL"
    query += " ORDER BY game_time DESC LIMIT 500"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return {"count": len(rows), "picks": [dict(r) for r in rows]}

@router.post("")
async def create_pick(
    pick: PickCreate,
    user: dict = Depends(get_current_user_supabase)
):
    validate_sport(pick.sport)
    conn = get_db_connection()
    cursor = conn.cursor()
    pick_id = str(uuid.uuid4())
    
    cursor.execute("""
        INSERT INTO picks (id, user_id, player_name, team, opponent, sport, stat_type,
                          line, model_projection, pick, confidence, ev_percentage,
                          odds, game_time, event_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pick_id, user.id, pick.player_name, pick.team, pick.opponent, pick.sport,
        pick.stat_type, pick.line, pick.model_projection, pick.pick,
        pick.confidence, pick.ev_percentage, pick.odds, pick.game_time,
        pick.event_id, datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    return {"id": pick_id, "status": "created"}

@router.post("/settle")
async def settle_pick(
    data: PickSettle,
    user: dict = Depends(get_current_user_supabase)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM picks WHERE id = ? AND user_id = ?", (data.pick_id, user.id))
    pick = cursor.fetchone()
    if not pick:
        conn.close()
        raise HTTPException(status_code=404, detail="Pick not found")
    
    hit = None
    if pick["pick"].lower() == "over":
        hit = data.actual_value > pick["line"]
    elif pick["pick"].lower() == "under":
        hit = data.actual_value < pick["line"]
    
    result = "win" if hit else "loss"
    
    # Update pick
    cursor.execute("""
        UPDATE picks SET hit = ?, actual_value = ?, result = ?, settled_at = ?
        WHERE id = ?
    """, (hit, data.actual_value, result, datetime.utcnow().isoformat(), data.pick_id))
    
    # Update player hit rate
    cursor.execute("""
        SELECT COUNT(*) as total, SUM(CASE WHEN hit = 1 THEN 1 ELSE 0 END) as hits
        FROM picks
        WHERE player_name = ? AND stat_type = ? AND hit IS NOT NULL
    """, (pick["player_name"], pick["stat_type"]))
    stats = cursor.fetchone()
    
    if stats and stats["total"] > 0:
        hit_rate = round((stats["hits"] / stats["total"]) * 100, 1)
        # Handle conflict for both sqlite and postgres
        try:
            # Try PostgreSQL syntax first if possible, or use UPSERT for SQLite
            cursor.execute("""
                INSERT INTO player_hit_rates (player_name, stat_type, hit_rate, total_picks, hits, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_name, stat_type) DO UPDATE SET
                    hit_rate = excluded.hit_rate,
                    total_picks = excluded.total_picks,
                    hits = excluded.hits,
                    updated_at = excluded.updated_at
            """, (pick["player_name"], pick["stat_type"], hit_rate,
                  stats["total"], stats["hits"], datetime.utcnow().isoformat()))
        except:
            # Fallback for older SQLite versions or different DBs
            cursor.execute("DELETE FROM player_hit_rates WHERE player_name = ? AND stat_type = ?", (pick["player_name"], pick["stat_type"]))
            cursor.execute("""
                INSERT INTO player_hit_rates (player_name, stat_type, hit_rate, total_picks, hits, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pick["player_name"], pick["stat_type"], hit_rate,
                  stats["total"], stats["hits"], datetime.utcnow().isoformat()))
    
    conn.commit()
    conn.close()
    return {"id": data.pick_id, "hit": hit, "result": result, "actual_value": data.actual_value}

@router.get("/hit-rates")
async def get_hit_rates(
    sport: Optional[str] = None, 
    min_picks: int = 5,
    user: dict = Depends(get_current_user_supabase)
):
    sport = validate_sport(sport)
    min_picks = validate_limit(min_picks, 50)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT player_name, sport, stat_type,
               COUNT(*) as total_picks,
               SUM(CASE WHEN hit = 1 THEN 1 ELSE 0 END) as hits,
               ROUND(AVG(CASE WHEN hit = 1 THEN 100.0 ELSE 0 END), 1) as hit_rate,
               ROUND(AVG(ev_percentage), 2) as avg_ev,
               ROUND(AVG(odds), 0) as avg_odds
        FROM picks
        WHERE user_id = ? AND hit IS NOT NULL
    """
    params = [user.id]
    if sport:
        query += " AND sport = ?"
        params.append(sport)
    query += " GROUP BY player_name, sport, stat_type HAVING total_picks >= ?"
    params.append(min_picks)
    query += " ORDER BY hit_rate DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return {"count": len(rows), "hit_rates": [dict(r) for r in rows]}
