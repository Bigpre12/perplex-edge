"""
Fix NHL data corruption by removing NBA players from NHL games.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix = " / api / fix - nhl - data", tags = ["fix - nhl - data"])

@router.post(" / identify - corruption")
async def identify_nhl_corruption(db: AsyncSession = Depends(get_db)):
 """Identify NHL data corruption issues."""
 try:
 # Check for NBA players in NHL games
 corruption_sql = text("""
 SELECT COUNT( * ) as corrupted_count
 FROM model_picks mp
 JOIN players p ON mp.player_id = p.id
 JOIN games g ON mp.game_id = g.id
 JOIN teams t ON p.team_id = t.id
 WHERE g.sport_id = 53 -  - NHL
 AND t.sport_id ! = 53 -  - Team is not NHL
 """)

 result = await db.execute(corruption_sql)
 corrupted_count = result.fetchone()[0]

 # Get sample corrupted records
 sample_sql = text("""
 SELECT mp.id, p.name as player_name, t.name as team_name,
 t.sport_id as team_sport_id, g.sport_id as game_sport_id
 FROM model_picks mp
 JOIN players p ON mp.player_id = p.id
 JOIN games g ON mp.game_id = g.id
 JOIN teams t ON p.team_id = t.id
 WHERE g.sport_id = 53 -  - NHL
 AND t.sport_id ! = 53 -  - Team is not NHL
 LIMIT 10
 """)

 sample_result = await db.execute(sample_sql)
 sample_rows = sample_result.fetchall()

 return {
 "corrupted_count": corrupted_count,
 "sample_corruption": [
 {
 "pick_id": row[0],
 "player_name": row[1],
 "team_name": row[2],
 "team_sport_id": row[3],
 "game_sport_id": row[4]
 }
 for row in sample_rows
 ]
 }

 except Exception as e:
 return {
 "error": str(e),
 "corrupted_count": 0,
 "sample_corruption": []
 }

@router.post(" / clean - corruption")
async def clean_nhl_corruption(db: AsyncSession = Depends(get_db)):
 """Clean NHL data corruption by removing invalid picks."""
 try:
 # Delete NBA players from NHL games
 clean_sql = text("""
 DELETE FROM model_picks
 WHERE id IN(SELECT mp.id
 FROM model_picks mp
 JOIN players p ON mp.player_id = p.id
 JOIN games g ON mp.game_id = g.id
 JOIN teams t ON p.team_id = t.id
 WHERE g.sport_id = 53 -  - NHL
 AND t.sport_id ! = 53 -  - Team is not NHL)
 """)

 result = await db.execute(clean_sql)
 deleted_count = result.rowcount
 await db.commit()

 return {
 "deleted_count": deleted_count,
 "status": "success",
 "message": f"Removed {deleted_count} corrupted NHL picks"
 }

 except Exception as e:
 await db.rollback()
 return {
 "error": str(e),
 "deleted_count": 0,
 "status": "failed"
 }

@router.post(" / verify - nhl - players")
async def verify_nhl_players_exist(db: AsyncSession = Depends(get_db)):
 """Verify actual NHL players exist in the database."""
 try:
 # Check for real NHL players
 nhl_players_sql = text("""
 SELECT COUNT( * ) as nhl_player_count
 FROM players p
 JOIN teams t ON p.team_id = t.id
 WHERE t.sport_id = 53 -  - NHL
 """)

 result = await db.execute(nhl_players_sql)
 nhl_player_count = result.fetchone()[0]

 # Get sample NHL players
 sample_nhl_sql = text("""
 SELECT p.name, t.name as team_name
 FROM players p
 JOIN teams t ON p.team_id = t.id
 WHERE t.sport_id = 53 -  - NHL
 LIMIT 10
 """)

 sample_result = await db.execute(sample_nhl_sql)
 sample_rows = sample_result.fetchall()

 return {
 "nhl_player_count": nhl_player_count,
 "sample_nhl_players": [
 {
 "player_name": row[0],
 "team_name": row[1]
 }
 for row in sample_rows
 ]
 }

 except Exception as e:
 return {
 "error": str(e),
 "nhl_player_count": 0,
 "sample_nhl_players": []
 }
