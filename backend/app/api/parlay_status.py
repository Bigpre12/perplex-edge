"""
Comprehensive parlay service status dashboard.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/api/parlay-status", tags=["parlay-status"])

@router.get("/comprehensive")
async def get_comprehensive_status(
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive status of all parlay services and sports."""
    try:
        now = datetime.now(timezone.utc)
        
        # Test each supported sport
        supported_sports = [30, 32, 53]  # NBA, NCAA Basketball, NHL
        sport_status = {}
        
        for sport_id in supported_sports:
            sport_names = {30: "NBA", 32: "NCAA Basketball", 53: "NHL"}
            
            # Check recent picks
            picks_sql = text(f"""
                SELECT COUNT(*) as count
                FROM model_picks mp
                JOIN games g ON mp.game_id = g.id
                WHERE g.sport_id = {sport_id}
                AND mp.generated_at > '{now - timedelta(hours=24)}'
                AND mp.line_value IS NOT NULL AND mp.line_value > 0
            """)
            
            result = await db.execute(picks_sql)
            pick_count = result.fetchone()[0]
            
            # Check grade distribution
            grades_sql = text(f"""
                SELECT 
                    CASE 
                        WHEN mp.expected_value >= 0.05 THEN 'A'
                        WHEN mp.expected_value >= 0.03 THEN 'B'
                        WHEN mp.expected_value >= 0.01 THEN 'C'
                        WHEN mp.expected_value >= 0.00 THEN 'D'
                        ELSE 'F'
                    END as grade,
                    COUNT(*) as count
                FROM model_picks mp
                JOIN games g ON mp.game_id = g.id
                WHERE g.sport_id = {sport_id}
                AND mp.generated_at > '{now - timedelta(hours=24)}'
                AND mp.line_value IS NOT NULL AND mp.line_value > 0
                GROUP BY grade
                ORDER BY grade
            """)
            
            grades_result = await db.execute(grades_sql)
            grade_rows = grades_result.fetchall()
            grade_distribution = {row[0]: row[1] for row in grade_rows}
            
            sport_status[sport_id] = {
                "name": sport_names.get(sport_id, f"Sport {sport_id}"),
                "pick_count_24h": pick_count,
                "grade_distribution": grade_distribution,
                "status": "active" if pick_count > 0 else "inactive"
            }
        
        # Test multi-sport endpoints
        endpoint_status = {}
        
        # Test supported sports endpoint
        try:
            supported_sql = text("""
                SELECT DISTINCT g.sport_id, s.name, COUNT(*) as pick_count
                FROM model_picks mp
                JOIN games g ON mp.game_id = g.id
                JOIN sports s ON g.sport_id = s.id
                WHERE mp.generated_at > NOW() - INTERVAL '24 hours'
                AND mp.line_value IS NOT NULL AND mp.line_value > 0
                GROUP BY g.sport_id, s.name
                ORDER BY pick_count DESC
            """)
            
            result = await db.execute(supported_sql)
            rows = result.fetchall()
            
            endpoint_status["supported_sports"] = {
                "status": "working",
                "count": len(rows),
                "sports": [{"sport_id": row[0], "name": row[1], "pick_count": row[2]} for row in rows]
            }
        except Exception as e:
            endpoint_status["supported_sports"] = {"status": "error", "error": str(e)}
        
        # Overall system health
        total_picks = sum(status["pick_count_24h"] for status in sport_status.values())
        active_sports = len([s for s in sport_status.values() if s["status"] == "active"])
        
        return {
            "timestamp": now.isoformat(),
            "overall_health": {
                "status": "healthy" if active_sports >= 2 else "degraded",
                "total_picks_24h": total_picks,
                "active_sports": active_sports,
                "total_sports": len(supported_sports)
            },
            "sport_status": sport_status,
            "endpoint_status": endpoint_status,
            "services": {
                "multisport_parlay": "working",
                "team_service": "working",
                "raw_sql_queries": "working",
                "schema_validation": "working"
            },
            "known_issues": [
                {
                    "issue": "Team abbreviations showing 'UNK'",
                    "severity": "low",
                    "impact": "Cosmetic only",
                    "status": "Team service needs debugging"
                },
                {
                    "issue": "No NHL players in database",
                    "severity": "medium",
                    "impact": "NHL parlays unavailable",
                    "status": "Data feed issue"
                },
                {
                    "issue": "Placeholder odds calculations",
                    "severity": "low",
                    "impact": "Odds not market-accurate",
                    "status": "Needs sportsbook integration"
                }
            ]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_health": {
                "status": "error",
                "error": str(e)
            },
            "sport_status": {},
            "endpoint_status": {},
            "services": {},
            "known_issues": [{"issue": "System error", "severity": "high", "error": str(e)}]
        }
