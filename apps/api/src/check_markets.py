
import os
from sqlalchemy import text, create_engine

def check_markets():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url: return
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
    if "sqlite" in sync_url and "sslmode" in sync_url: sync_url = sync_url.split("?")[0]
    
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT market_key, count(*) FROM unified_odds GROUP BY market_key ORDER BY count DESC"))
        print("Market Key Distribution:")
        for row in res:
            print(f"Market: {row[0]}, Count: {row[1]}")

if __name__ == "__main__":
    check_markets()
