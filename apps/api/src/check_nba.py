
import os
from sqlalchemy import text, create_engine

def check_nba():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url: return
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
    if "sqlite" in sync_url and "sslmode" in sync_url: sync_url = sync_url.split("?")[0]
    
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT sport, market_key, player_name, outcome_key, line, price FROM unified_odds WHERE sport = 'basketball_nba' LIMIT 10"))
        print("NBA Sample Data:")
        for row in res:
            print(row)

if __name__ == "__main__":
    check_nba()
