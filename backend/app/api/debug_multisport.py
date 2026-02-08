"""
Debug multisport parlay endpoint specifically.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/api/debug-multisport", tags=["debug-multisport"])


@router.get("/test-multisport-sql")
async def test_multisport_sql(
    sport_id: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Test the exact SQL used in multisport parlay endpoint."""
    try:
        # Use the exact SQL from multisport parlay
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
            AND mp.generated_at > NOW() - INTERVAL '6 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
            AND g.start_time > NOW() - INTERVAL '24 hours'
            AND g.start_time < NOW() + INTERVAL '48 hours'
            ORDER BY mp.expected_value DESC
            LIMIT 1000
        """)
        
        result = await db.execute(sql)
        rows = result.fetchall()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "sql_results": {
                "total_rows": len(rows),
                "sample_rows": [
                    {
                        "pick_id": row[0],
                        "expected_value": row[1],
                        "line_value": row[2],
                        "generated_at": row[3].isoformat(),
                        "player_name": row[4],
                        "player_id": row[5],
                        "game_start": row[6].isoformat(),
                        "stat_type": row[7]
                    }
                    for row in rows[:5]
                ]
            }
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "sport_id": sport_id
        }


@router.get("/test-multisport-processing")
async def test_multisport_processing(
    sport_id: int = 30,
    min_leg_grade: str = "C",
    db: AsyncSession = Depends(get_db)
):
    """Test the processing logic from multisport parlay endpoint."""
    try:
        # Get the data
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
            AND mp.generated_at > NOW() - INTERVAL '6 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
            AND g.start_time > NOW() - INTERVAL '24 hours'
            AND g.start_time < NOW() + INTERVAL '48 hours'
            ORDER BY mp.expected_value DESC
            LIMIT 1000
        """)
        
        result = await db.execute(sql)
        rows = result.fetchall()
        
        # Process legs with working logic
        min_grade_numeric = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}[min_leg_grade.upper()]
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
            
            # Create leg with all required fields
            leg = {
                "pick_id": pick_id,
                "player_name": player_name,
                "player_id": player_id,
                "team_abbr": "UNK",
                "game_id": None,
                "stat_type": stat_type,
                "line": line_value,
                "side": "OVER",
                "odds": -110,
                "grade": grade,
                "win_prob": 0.5,
                "edge": edge,
                "hit_rate_5g": 0.0,
                "is_100_last_5": False,
                "confidence_score": 0.0,
                "hit_rate_30d": 0.0,
                "hit_rate_10g": 0.0,
                "hit_rate_3g": 0.0,
            }
            
            legs.append(leg)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "processing_results": {
                "total_rows": len(rows),
                "legs_created": len(legs),
                "sample_legs": legs[:3],
                "grade_filtering": {
                    "min_grade": min_leg_grade,
                    "min_grade_numeric": min_grade_numeric,
                    "legs_passed_filter": len(legs)
                }
            }
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "sport_id": sport_id
        }


@router.get("/compare-endpoints")
async def compare_endpoints(
    sport_id: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Compare debug vs multisport endpoint results."""
    try:
        # Test debug raw parlay
        debug_sql = text(f"""
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
        
        debug_result = await db.execute(debug_sql)
        debug_rows = debug_result.fetchall()
        
        # Test multisport SQL
        multisport_sql = text(f"""
            SELECT 
                mp.id, mp.expected_value, mp.line_value, mp.generated_at,
                p.name as player_name, p.id as player_id, g.start_time as game_start,
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
        
        multisport_result = await db.execute(multisport_sql)
        multisport_rows = multisport_result.fetchall()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "comparison": {
                "debug_endpoint": {
                    "total_rows": len(debug_rows),
                    "sample_data": [
                        {
                            "pick_id": row[0],
                            "expected_value": row[1],
                            "player_name": row[4],
                            "stat_type": row[6]
                        }
                        for row in debug_rows[:3]
                    ]
                },
                "multisport_endpoint": {
                    "total_rows": len(multisport_rows),
                    "sample_data": [
                        {
                            "pick_id": row[0],
                            "expected_value": row[1],
                            "player_name": row[4],
                            "stat_type": row[7]
                        }
                        for row in multisport_rows[:3]
                    ]
                },
                "difference": len(debug_rows) - len(multisport_rows)
            }
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "sport_id": sport_id
        }
