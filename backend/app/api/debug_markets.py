"""
Debug markets join issues in parlay generation.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/api/debug-markets", tags=["debug-markets"])

@router.get("/check-markets-data")
async def check_markets_data(
    sport_id: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Check markets data and relationships."""
    try:
        results = {}
        
        # Check if markets table exists and has data
        markets_count_sql = text("SELECT COUNT(*) as count FROM markets")
        result = await db.execute(markets_count_sql)
        results["total_markets"] = result.fetchone()[0]
        
        # Check market types
        market_types_sql = text("SELECT DISTINCT stat_type, COUNT(*) as count FROM markets GROUP BY stat_type ORDER BY count DESC")
        result = await db.execute(market_types_sql)
        results["market_types"] = [{"stat_type": row[0], "count": row[1]} for row in result.fetchall()]
        
        # Check model_picks market_id values
        picks_market_sql = text(f"""
            SELECT 
                COUNT(*) as total_picks,
                COUNT(DISTINCT mp.market_id) as unique_market_ids,
                COUNT(CASE WHEN mp.market_id IS NULL THEN 1 END) as null_market_ids
            FROM model_picks mp
            JOIN games g ON mp.game_id = g.id
            WHERE g.sport_id = {sport_id}
        """)
        
        result = await db.execute(picks_market_sql)
        row = result.fetchone()
        results["picks_market_analysis"] = {
            "total_picks": row[0],
            "unique_market_ids": row[1],
            "null_market_ids": row[2]
        }
        
        # Check if market_ids in model_picks exist in markets
        market_join_sql = text(f"""
            SELECT 
                COUNT(*) as valid_joins,
                COUNT(DISTINCT mp.market_id) as valid_market_ids
            FROM model_picks mp
            JOIN games g ON mp.game_id = g.id
            JOIN markets m ON mp.market_id = m.id
            WHERE g.sport_id = {sport_id}
        """)
        
        result = await db.execute(market_join_sql)
        row = result.fetchone()
        results["market_join_analysis"] = {
            "valid_joins": row[0],
            "valid_market_ids": row[1]
        }
        
        # Check sample picks with market info
        sample_picks_sql = text(f"""
            SELECT 
                mp.id,
                mp.market_id,
                m.stat_type as market_stat_type,
                p.name as player_name,
                g.start_time
            FROM model_picks mp
            JOIN players p ON mp.player_id = p.id
            JOIN games g ON mp.game_id = g.id
            LEFT JOIN markets m ON mp.market_id = m.id
            WHERE g.sport_id = {sport_id}
            AND mp.generated_at > NOW() - INTERVAL '6 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
            ORDER BY mp.expected_value DESC
            LIMIT 10
        """)
        
        result = await db.execute(sample_picks_sql)
        results["sample_picks"] = [
            {
                "pick_id": row[0],
                "market_id": row[1],
                "market_stat_type": row[2],
                "player_name": row[3],
                "game_start": row[4].isoformat() if row[4] else None
            }
            for row in result.fetchall()
        ]
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "results": results
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "sport_id": sport_id
        }

@router.get("/test-without-markets")
async def test_without_markets_join(
    sport_id: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Test parlay query without markets join."""
    try:
        # Test without markets join
        sql = text(f"""
            SELECT 
                mp.id, mp.expected_value, mp.line_value, mp.generated_at,
                p.name as player_name, p.id as player_id, g.start_time as game_start,
                'UNKNOWN' as stat_type
            FROM model_picks mp
            JOIN players p ON mp.player_id = p.id
            JOIN games g ON mp.game_id = g.id
            WHERE g.sport_id = {sport_id}
            AND mp.generated_at > NOW() - INTERVAL '6 hours'
            AND mp.line_value IS NOT NULL AND mp.line_value > 0
            AND g.start_time > NOW() - INTERVAL '24 hours'
            AND g.start_time < NOW() + INTERVAL '48 hours'
            ORDER BY mp.expected_value DESC
            LIMIT 10
        """)
        
        result = await db.execute(sql)
        rows = result.fetchall()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sport_id": sport_id,
            "total_results": len(rows),
            "sample_results": [
                {
                    "pick_id": row[0],
                    "expected_value": row[1],
                    "line_value": row[2],
                    "player_name": row[4],
                    "player_id": row[5],
                    "game_start": row[6].isoformat(),
                    "stat_type": row[7]
                }
                for row in rows[:5]
            ]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "sport_id": sport_id
        }
