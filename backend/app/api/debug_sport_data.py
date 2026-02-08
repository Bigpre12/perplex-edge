"""
Debug sport data integrity.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix = " / api / debug - sport - data", tags = ["debug - sport - data"])

@router.get(" / check - games")
async def check_games_by_sport(sport_id: int = Query(53),
 db: AsyncSession = Depends(get_db)):
 """Check what games exist for a sport."""
 try:
 # Check games table
 games_sql = text(f"""
 SELECT g.id, g.start_time, g.sport_id, s.name as sport_name
 FROM games g
 JOIN sports s ON g.sport_id = s.id
 WHERE g.sport_id = {sport_id}
 ORDER BY g.start_time DESC
 LIMIT 10
 """)

 games_result = await db.execute(games_sql)
 games_rows = games_result.fetchall()

 # Check ModelPicks with actual sport_id
 picks_sql = text(f"""
 SELECT mp.id, mp.sport_id, p.name as player_name, g.start_time, s.name as sport_name
 FROM model_picks mp
 JOIN players p ON mp.player_id = p.id
 JOIN games g ON mp.game_id = g.id
 JOIN sports s ON g.sport_id = s.id
 WHERE mp.sport_id = {sport_id}
 ORDER BY mp.generated_at DESC
 LIMIT 5
 """)

 picks_result = await db.execute(picks_sql)
 picks_rows = picks_result.fetchall()

 return {
 "sport_id": sport_id,
 "games": [
 {
 "game_id": row[0],
 "start_time": row[1].isoformat(),
 "game_sport_id": row[2],
 "sport_name": row[3]
 }
 for row in games_rows
 ],
 "model_picks": [
 {
 "pick_id": row[0],
 "pick_sport_id": row[1],
 "player_name": row[2],
 "game_start": row[3].isoformat(),
 "sport_name": row[4]
 }
 for row in picks_rows
 ]
 }

 except Exception as e:
 return {
 "error": str(e),
 "sport_id": sport_id
 }

@router.get(" / check - nhl - players")
async def check_nhl_players(db: AsyncSession = Depends(get_db)):
 """Check for actual NHL players."""
 try:
 # Check players with NHL teams
 nhl_sql = text("""
 SELECT p.name, t.name as team_name, s.name as sport_name
 FROM players p
 JOIN teams t ON p.team_id = t.id
 JOIN sports s ON t.sport_id = s.id
 WHERE s.name = 'NHL'
 LIMIT 10
 """)

 result = await db.execute(nhl_sql)
 rows = result.fetchall()

 return {
 "nhl_players": [
 {
 "player_name": row[0],
 "team_name": row[1],
 "sport_name": row[2]
 }
 for row in rows
 ]
 }

 except Exception as e:
 return {
 "error": str(e)
 }
