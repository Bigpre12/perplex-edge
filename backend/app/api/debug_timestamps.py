"""
Debug timestamp issues in parlay generation.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/api/debug-timestamps", tags=["debug-timestamps"])


@router.get("/check-data")
async def check_data_timestamps(
    sport_id: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Check actual timestamps in the database."""
    try:
        now = datetime.now(timezone.utc)
        
        # Check recent model picks
        picks_sql = text(f"""
            SELECT 
                mp.id,
                mp.expected_value,
                mp.line_value,
                mp.generated_at,
                p.name as player_name,
                g.start_time as game_start,
                g.sport_id
            FROM model_picks mp
            JOIN players p ON mp.player_id = p.id
            JOIN games g ON mp.game_id = g.id
            WHERE g.sport_id = {sport_id}
            ORDER BY mp.generated_at DESC
            LIMIT 10
        """)
        
        result = await db.execute(picks_sql)
        picks_rows = result.fetchall()
        
        # Check database current time
        db_time_sql = text("SELECT NOW() as db_time, CURRENT_TIMESTAMP as current_timestamp")
        db_result = await db.execute(db_time_sql)
        db_time_row = db_result.fetchone()
        
        # Check games in time window
        games_sql = text(f"""
            SELECT 
                g.id,
                g.start_time,
                g.sport_id,
                NOW() - INTERVAL '6 hours' as six_hours_ago,
                NOW() - INTERVAL '2 hours' as two_hours_ago,
                NOW() + INTERVAL '36 hours' as thirty_six_hours_future
            FROM games g
            WHERE g.sport_id = {sport_id}
            AND g.start_time > NOW() - INTERVAL '2 hours'
            AND g.start_time < NOW() + INTERVAL '36 hours'
            ORDER BY g.start_time
            LIMIT 10
        """)
        
        games_result = await db.execute(games_sql)
        games_rows = games_result.fetchall()
        
        # Check picks in time window
        picks_window_sql = text(f"""
            SELECT 
                COUNT(*) as total_picks,
                mp.generated_at,
                NOW() - INTERVAL '6 hours' as six_hours_ago
            FROM model_picks mp
            JOIN games g ON mp.game_id = g.id
            WHERE g.sport_id = {sport_id}
            AND mp.generated_at > NOW() - INTERVAL '6 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
            GROUP BY mp.generated_at, NOW() - INTERVAL '6 hours'
            LIMIT 5
        """)
        
        picks_window_result = await db.execute(picks_window_sql)
        picks_window_rows = picks_window_result.fetchall()
        
        return {
            "timestamp": now.isoformat(),
            "database_time": {
                "now": db_time_row[0].isoformat(),
                "current_timestamp": db_time_row[1].isoformat()
            },
            "recent_picks": [
                {
                    "pick_id": row[0],
                    "expected_value": row[1],
                    "line_value": row[2],
                    "generated_at": row[3].isoformat(),
                    "player_name": row[4],
                    "game_start": row[5].isoformat(),
                    "sport_id": row[6]
                }
                for row in picks_rows
            ],
            "games_in_window": [
                {
                    "game_id": row[0],
                    "start_time": row[1].isoformat(),
                    "sport_id": row[2],
                    "six_hours_ago": row[3].isoformat(),
                    "two_hours_ago": row[4].isoformat(),
                    "thirty_six_hours_future": row[5].isoformat()
                }
                for row in games_rows
            ],
            "picks_in_window": [
                {
                    "total_picks": row[0],
                    "generated_at": row[1].isoformat(),
                    "six_hours_ago": row[2].isoformat()
                }
                for row in picks_window_rows
            ]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "sport_id": sport_id
        }


@router.get("/test-sql-variations")
async def test_sql_variations(
    sport_id: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Test different SQL variations to find the issue."""
    try:
        results = {}
        
        # Test 1: Basic query without time filters
        basic_sql = text(f"""
            SELECT COUNT(*) as count
            FROM model_picks mp
            JOIN games g ON mp.game_id = g.id
            WHERE g.sport_id = {sport_id}
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
        """)
        
        result = await db.execute(basic_sql)
        results["basic_query"] = result.fetchone()[0]
        
        # Test 2: With generated_at filter
        generated_sql = text(f"""
            SELECT COUNT(*) as count
            FROM model_picks mp
            JOIN games g ON mp.game_id = g.id
            WHERE g.sport_id = {sport_id}
            AND mp.generated_at > NOW() - INTERVAL '6 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
        """)
        
        result = await db.execute(generated_sql)
        results["with_generated_at_filter"] = result.fetchone()[0]
        
        # Test 3: With game time filter
        game_sql = text(f"""
            SELECT COUNT(*) as count
            FROM model_picks mp
            JOIN games g ON mp.game_id = g.id
            WHERE g.sport_id = {sport_id}
            AND g.start_time > NOW() - INTERVAL '2 hours'
            AND g.start_time < NOW() + INTERVAL '36 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
        """)
        
        result = await db.execute(game_sql)
        results["with_game_time_filter"] = result.fetchone()[0]
        
        # Test 4: With both time filters
        both_sql = text(f"""
            SELECT COUNT(*) as count
            FROM model_picks mp
            JOIN games g ON mp.game_id = g.id
            WHERE g.sport_id = {sport_id}
            AND mp.generated_at > NOW() - INTERVAL '6 hours'
            AND g.start_time > NOW() - INTERVAL '2 hours'
            AND g.start_time < NOW() + INTERVAL '36 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
        """)
        
        result = await db.execute(both_sql)
        results["with_both_time_filters"] = result.fetchone()[0]
        
        # Test 5: With markets join
        markets_sql = text(f"""
            SELECT COUNT(*) as count
            FROM model_picks mp
            JOIN players p ON mp.player_id = p.id
            JOIN games g ON mp.game_id = g.id
            JOIN markets m ON mp.market_id = m.id
            WHERE g.sport_id = {sport_id}
            AND mp.generated_at > NOW() - INTERVAL '6 hours'
            AND g.start_time > NOW() - INTERVAL '2 hours'
            AND g.start_time < NOW() + INTERVAL '36 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
        """)
        
        result = await db.execute(markets_sql)
        results["with_markets_join"] = result.fetchone()[0]
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "test_results": results
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "sport_id": sport_id
        }
