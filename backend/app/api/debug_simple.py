"""
Simple debug endpoint using raw SQL to avoid timezone issues.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix = " / api / debug - simple", tags = ["debug - simple"])

@router.get(" / test - sql")
async def test_raw_sql(sport_id: int = Query(30),
 hours_back: int = Query(24),
 db: AsyncSession = Depends(get_db)):
 """Test using raw SQL to avoid timezone issues."""
 try:
 now = datetime.now(timezone.utc)
 hours_ago = now - timedelta(hours = hours_back)

 # Use raw SQL to avoid timezone issues
 sql = text(f"""
 SELECT COUNT( * ) as count
 FROM model_picks mp
 JOIN games g ON mp.game_id = g.id
 WHERE g.sport_id = {sport_id}
 AND mp.generated_at > '{hours_ago.isoformat()}'
 """)

 result = await db.execute(sql)
 count = result.scalar()

 return {
 "sport_id": sport_id,
 "hours_back": hours_back,
 "count": count,
 "now": now.isoformat(),
 "hours_ago": hours_ago.isoformat(),
 "sql": str(sql)
 }

 except Exception as e:
 return {
 "error": str(e),
 "sport_id": sport_id
 }

@router.get(" / test - recent - picks")
async def test_recent_picks(sport_id: int = Query(30),
 db: AsyncSession = Depends(get_db)):
 """Test recent picks with simpler query."""
 try:
 # Use raw SQL with proper timezone handling
 sql = text(f"""
 SELECT mp.id, mp.expected_value, mp.line_value, mp.generated_at,
 p.name as player_name, g.start_time as game_start
 FROM model_picks mp
 JOIN players p ON mp.player_id = p.id
 JOIN games g ON mp.game_id = g.id
 WHERE g.sport_id = {sport_id}
 ORDER BY mp.generated_at DESC
 LIMIT 5
 """)

 result = await db.execute(sql)
 rows = result.fetchall()

 picks = []
 for row in rows:
 picks.append({
 "pick_id": row[0],
 "expected_value": float(row[1]),
 "line_value": float(row[2]) if row[2] else None,
 "generated_at": row[3].isoformat(),
 "player_name": row[4],
 "game_start": row[5].isoformat(),
 "grade": "A" if float(row[1]) > = 0.05 else "B" if float(row[1]) > = 0.03 else "C" if float(row[1]) > = 0.01 else "D" if float(row[1]) > = 0.0 else "F"
 })

 return {
 "sport_id": sport_id,
 "picks": picks,
 "count": len(picks)
 }

 except Exception as e:
 return {
 "error": str(e),
 "sport_id": sport_id
 }
