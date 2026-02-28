import asyncio
from sqlalchemy import text
from database import async_session_maker

async def seed_markets():
    # MLB Stat Types to seed
    mlb_stats = [
        ("hits", "Player Hits", "player_prop"),
        ("total_bases", "Total Bases", "player_prop"),
        ("strikeouts", "Pitcher Strikeouts", "player_prop"),
        ("runs_batted_in", "Runs Batted In", "player_prop"),
        ("walks", "Walks", "player_prop"),
        ("home_runs", "Home Runs", "player_prop"),
        ("pitcher_strikeouts", "Pitcher Strikeouts (Alt)", "player_prop"),
        ("earned_runs", "Earned Runs", "player_prop")
    ]
    
    async with async_session_maker() as session:
        async with session.begin():
            print("Seeding MLB markets (Sport ID 40)...")
            for stat_type, desc, m_type in mlb_stats:
                # Check if exists
                stmt = text("SELECT id FROM markets WHERE stat_type = :stat AND sport_id = 40")
                res = await session.execute(stmt, {"stat": stat_type})
                if not res.first():
                    insert_stmt = text("""
                        INSERT INTO markets (sport_id, market_type, stat_type, description, created_at)
                        VALUES (40, :m_type, :stat, :desc, datetime('now'))
                    """)
                    await session.execute(insert_stmt, {
                        "m_type": m_type,
                        "stat": stat_type,
                        "desc": desc
                    })
                    print(f"  Added {stat_type}")
                else:
                    print(f"  {stat_type} already exists")
            
            print("Seeding complete.")

if __name__ == "__main__":
    try:
        asyncio.run(seed_markets())
    except Exception as e:
        print(f"Error during seeding: {e}")
