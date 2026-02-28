import asyncio
from sqlalchemy import text
from database import async_session_maker

async def seed_basketball_markets():
    # Sport IDs: 39 (NCAAB), 53 (WNBA)
    sports = [39, 53]
    
    # Basketball Stat Types to seed
    stats = [
        ("player_points", "Over/Under Points", "player_prop"),
        ("player_rebounds", "Over/Under Rebounds", "player_prop"),
        ("player_assists", "Over/Under Assists", "player_prop"),
        ("player_steals", "Over/Under Steals", "player_prop"),
        ("player_blocks", "Over/Under Blocks", "player_prop"),
        ("player_three_pointers_made", "Over/Under 3-Pointers Made", "player_prop")
    ]
    
    async with async_session_maker() as session:
        async with session.begin():
            for sport_id in sports:
                print(f"Seeding markets for Sport ID {sport_id}...")
                for stat_type, desc, m_type in stats:
                    # Check if exists
                    stmt = text("SELECT id FROM markets WHERE stat_type = :stat AND sport_id = :sid")
                    res = await session.execute(stmt, {"stat": stat_type, "sid": sport_id})
                    if not res.first():
                        insert_stmt = text("""
                            INSERT INTO markets (sport_id, market_type, stat_type, description, created_at)
                            VALUES (:sid, :m_type, :stat, :desc, datetime('now'))
                        """)
                        await session.execute(insert_stmt, {
                            "sid": sport_id,
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
        asyncio.run(seed_basketball_markets())
    except Exception as e:
        print(f"Error during seeding: {e}")
