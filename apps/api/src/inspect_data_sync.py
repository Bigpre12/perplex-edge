
import os
from sqlalchemy import text, create_engine

def check_data():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL NOT SET")
        return
        
    # Standardize URL for sync driver
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
    
    # Remove sslmode from query params if sqlite
    if "sqlite" in sync_url and "sslmode" in sync_url:
        sync_url = sync_url.split("?")[0]
        
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        # Check overall counts
        total = conn.execute(text("SELECT count(*) FROM unified_odds")).scalar()
        print(f"Total UnifiedOdds: {total}")
        
        # Check by sport
        res = conn.execute(text("SELECT sport, count(*) FROM unified_odds GROUP BY sport"))
        for row in res:
            print(f"Sport: {row[0]}, Count: {row[1]}")
            
        # Check sample rows
        res = conn.execute(text("SELECT sport, market_key, player_name, outcome_key, line FROM unified_odds LIMIT 10"))
        print("\nSample Rows:")
        for row in res:
            print(row)

if __name__ == "__main__":
    check_data()
