"""
Debug parlay service step by step.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.core.database import get_db
from app.models import ModelPick, Player, Game, Team, Market
from app.services.parlay_service import build_parlay_legs, calculate_grade, grade_to_numeric

router = APIRouter(prefix = " / api / debug - parlay", tags = ["debug - parlay"])

@router.get(" / step - by - step")
async def debug_parlay_step_by_step(sport_id: int = Query(30),
 min_grade: str = Query("C"),
 db: AsyncSession = Depends(get_db)):
 """Debug parlay service step by step."""
 try:
 now = datetime.now(timezone.utc)
 six_hours_ago = now - timedelta(hours = 6)

 # Step 1: Check ModelPick data
 model_picks_result = await db.execute(select(ModelPick, Player, Game)
 .join(Player, ModelPick.player_id =  = Player.id)
 .join(Game, ModelPick.game_id =  = Game.id)
 .where(and_(Game.sport_id =  = sport_id,
 ModelPick.generated_at > six_hours_ago))
 .limit(10))
 model_picks = model_picks_result.all()

 step1_data = []
 for pick, player, game in model_picks:
 step1_data.append({
 "pick_id": pick.id,
 "player_name": player.name,
 "game_start": game.start_time.isoformat(),
 "generated_at": pick.generated_at.isoformat(),
 "expected_value": pick.expected_value,
 "line_value": pick.line_value,
 "grade": calculate_grade(pick.expected_value),
 "grade_numeric": grade_to_numeric(calculate_grade(pick.expected_value))
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

 # Step 4: Check freshness filtering
 step4_data = []
 for data in step3_data:
 # Use timezone - aware datetime comparison
 pick_age = now - data["generated_at"]
 is_fresh = pick_age.total_seconds() < = 21600 # 6 hours
 step4_data.append({
 *  * data,
 "is_fresh": is_fresh,
 "pick_age_hours": pick_age.total_seconds() / 3600,
 "reason": "Passes" if is_fresh else f"Fail: {pick_age.total_seconds() / 3600:.1f} hours old"
 })

 return {
 "step1_model_picks": {
 "total": len(step1_data),
 "data": step1_data[:5]
 },
 "step2_grade_filter": {
 "total": len(step2_data),
 "data": step2_data[:5],
 "min_grade": min_grade,
 "min_grade_numeric": min_grade_numeric
 },
 "step3_line_filter": {
 "total": len(step3_data),
 "data": step3_data[:5]
 },
 "step4_freshness_filter": {
 "total": len(step4_data),
 "data": step4_data[:5]
 },
 "final_candidates": len(step4_data)
 }

 except Exception as e:
 return {
 "error": str(e),
 "sport_id": sport_id
 }
