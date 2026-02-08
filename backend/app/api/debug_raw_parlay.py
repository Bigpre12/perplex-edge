"""
Debug raw parlay service step by step.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix = " / api / debug - raw - parlay", tags = ["debug - raw - parlay"])

@router.get(" / test - raw - sql")
async def test_raw_sql_parlay(sport_id: int = Query(30),
 min_grade: str = Query("C"),
 db: AsyncSession = Depends(get_db)):
 """Test raw SQL parlay service step by step."""
 try:
 now = datetime.now(timezone.utc)
 six_hours_ago = now - timedelta(hours = 6)
 game_window_start = now - timedelta(hours = 2)
 game_window_end = now + timedelta(hours = 36)

 # Step 1: Test the exact raw SQL query from parlay service
 sql = text(f"""
 SELECT
 mp.id, mp.expected_value, mp.line_value, mp.generated_at,
 p.name as player_name, g.start_time as game_start,
 m.stat_type as stat_type
 FROM model_picks mp
 JOIN players p ON mp.player_id = p.id
 JOIN games g ON mp.game_id = g.id
 JOIN markets m ON mp.market_id = m.id
 WHERE g.sport_id = {sport_id}
 AND mp.generated_at > NOW() - INTERVAL '6 hours'
 AND mp.line_value IS NOT NULL AND mp.line_value > 0
 AND g.start_time > NOW() - INTERVAL '24 hours'
 AND g.start_time < NOW() + INTERVAL '48 hours'
 ORDER BY mp.expected_value DESC
 LIMIT 1000
 """)

 result = await db.execute(sql)
 rows = result.fetchall()

 step1_data = []
 for row in rows:
 pick_id, expected_value, line_value, generated_at, player_name, game_start, stat_type = row

 # Calculate grade
 edge = expected_value
 if edge > = 0.05:
 grade = "A"
 elif edge > = 0.03:
 grade = "B"
 elif edge > = 0.01:
 grade = "C"
 elif edge > = 0.00:
 grade = "D"
 else:
 grade = "F"

 grade_numeric = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}.get(grade, 0)

 step1_data.append({
 "pick_id": pick_id,
 "player_name": player_name,
 "game_start": game_start.isoformat(),
 "generated_at": generated_at.isoformat(),
 "expected_value": expected_value,
 "line_value": line_value,
 "grade": grade,
 "grade_numeric": grade_numeric,
 "stat_type": stat_type
 })

 # Step 2: Check grade filtering
 min_grade_numeric = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}[min_grade]

 step2_data = []
 for data in step1_data:
 passes_grade = data["grade_numeric"] > = min_grade_numeric
 step2_data.append({
 *  * data,
 "passes_grade_filter": passes_grade,
 "min_grade_numeric": min_grade_numeric,
 "reason": "Passes" if passes_grade else f"Fail: {data['grade_numeric']} < {min_grade_numeric}"
 })

 # Step 3: Check line value filtering
 step3_data = []
 for data in step2_data:
 if data["passes_grade_filter"]:
 has_valid_line = data["line_value"] is not None and data["line_value"] > 0
 step3_data.append({
 *  * data,
 "has_valid_line": has_valid_line,
 "reason": "Passes" if has_valid_line else f"Fail: line_value = {data['line_value']}"
 })

 return {
 "query_info": {
 "sport_id": sport_id,
 "now": now.isoformat(),
 "six_hours_ago": six_hours_ago.isoformat(),
 "game_window_start": game_window_start.isoformat(),
 "game_window_end": game_window_end.isoformat(),
 "min_grade": min_grade,
 "min_grade_numeric": min_grade_numeric
 },
 "step1_raw_sql": {
 "total": len(step1_data),
 "data": step1_data[:5]
 },
 "step2_grade_filter": {
 "total": len(step2_data),
 "data": step2_data[:5]
 },
 "step3_line_filter": {
 "total": len(step3_data),
 "data": step3_data[:5]
 },
 "final_candidates": len(step3_data)
 }

 except Exception as e:
 return {
 "error": str(e),
 "sport_id": sport_id
 }
