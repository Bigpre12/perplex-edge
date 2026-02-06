"""
Debug raw SQL service with detailed logging.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/api/debug-raw-service", tags=["debug-raw-service"])


@router.get("/detailed-debug")
async def debug_raw_service_detailed(
    sport_id: int = Query(30),
    min_grade: str = Query("C"),
    db: AsyncSession = Depends(get_db)
):
    """Debug raw SQL service with detailed logging."""
    try:
        now = datetime.now(timezone.utc)
        six_hours_ago = now - timedelta(hours=6)
        game_window_start = now - timedelta(hours=2)
        game_window_end = now + timedelta(hours=36)
        
        # Step 1: Test the exact raw SQL query
        sql = text(f"""
            SELECT 
                mp.id, mp.expected_value, mp.line_value, mp.generated_at,
                p.name as player_name, p.id as player_id, g.start_time as game_start,
                m.stat_type as stat_type
            FROM model_picks mp
            JOIN players p ON mp.player_id = p.id
            JOIN games g ON mp.game_id = g.id
            JOIN markets m ON mp.market_id = m.id
            WHERE g.sport_id = {sport_id}
            AND mp.generated_at > '{six_hours_ago.isoformat()}'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
            AND g.start_time > '{game_window_start.isoformat()}'
            AND g.start_time < '{game_window_end.isoformat()}'
            ORDER BY mp.expected_value DESC
            LIMIT 1000
        """)
        
        result = await db.execute(sql)
        rows = result.fetchall()
        
        debug_info = {
            "query_info": {
                "sport_id": sport_id,
                "now": now.isoformat(),
                "six_hours_ago": six_hours_ago.isoformat(),
                "game_window_start": game_window_start.isoformat(),
                "game_window_end": game_window_end.isoformat(),
                "min_grade": min_grade
            },
            "step1_sql_results": {
                "total_rows": len(rows),
                "sample_rows": []
            },
            "step2_grade_filtering": {
                "total": 0,
                "sample": []
            },
            "step3_leg_creation": {
                "total": 0,
                "sample": []
            }
        }
        
        # Step 1: Show sample SQL results
        for i, row in enumerate(rows[:5]):
            pick_id, expected_value, line_value, generated_at, player_name, player_id, game_start, stat_type = row
            
            debug_info["step1_sql_results"]["sample_rows"].append({
                "pick_id": pick_id,
                "player_name": player_name,
                "player_id": player_id,
                "expected_value": expected_value,
                "line_value": line_value,
                "generated_at": generated_at.isoformat(),
                "game_start": game_start.isoformat(),
                "stat_type": stat_type
            })
        
        # Step 2: Test grade filtering
        min_grade_numeric = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}[min_grade]
        grade_filtered = []
        
        for row in rows:
            pick_id, expected_value, line_value, generated_at, player_name, player_id, game_start, stat_type = row
            
            # Calculate grade
            edge = expected_value
            if edge >= 0.05:
                grade = "A"
            elif edge >= 0.03:
                grade = "B"
            elif edge >= 0.01:
                grade = "C"
            elif edge >= 0.00:
                grade = "D"
            else:
                grade = "F"
            
            grade_numeric = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}.get(grade, 0)
            
            passes_grade = grade_numeric >= min_grade_numeric
            if passes_grade:
                grade_filtered.append({
                    "pick_id": pick_id,
                    "player_name": player_name,
                    "expected_value": expected_value,
                    "grade": grade,
                    "grade_numeric": grade_numeric,
                    "passes_grade": passes_grade
                })
        
        debug_info["step2_grade_filtering"]["total"] = len(grade_filtered)
        debug_info["step2_grade_filtering"]["sample"] = grade_filtered[:5]
        
        # Step 3: Test leg creation
        legs = []
        for row in rows:
            pick_id, expected_value, line_value, generated_at, player_name, player_id, game_start, stat_type = row
            
            # Calculate grade
            edge = expected_value
            if edge >= 0.05:
                grade = "A"
            elif edge >= 0.03:
                grade = "B"
            elif edge >= 0.01:
                grade = "C"
            elif edge >= 0.00:
                grade = "D"
            else:
                grade = "F"
            
            grade_numeric = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}.get(grade, 0)
            
            # Skip if below minimum grade
            if grade_numeric < min_grade_numeric:
                continue
            
            # Create leg dictionary
            leg = {
                "pick_id": pick_id,
                "player_name": player_name,
                "game_start": game_start.isoformat(),
                "generated_at": generated_at.isoformat(),
                "stat_type": stat_type,
                "line_value": line_value,
                "expected_value": expected_value,
                "grade": grade,
                "edge": edge,
                "grade_numeric": grade_numeric,
                "confidence_score": 0.0,
                "hit_rate_30d": 0.0,
                "hit_rate_10g": 0.0,
                "hit_rate_5g": 0.0,
                "hit_rate_3g": 0.0,
            }
            
            legs.append(leg)
        
        debug_info["step3_leg_creation"]["total"] = len(legs)
        debug_info["step3_leg_creation"]["sample"] = legs[:5]
        
        return debug_info
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id
        }
