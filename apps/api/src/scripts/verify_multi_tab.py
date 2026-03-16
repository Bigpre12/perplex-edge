import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
os.environ["DEVELOPMENT_MODE"] = "1"

from db.session import engine
from sqlalchemy import text

def verify():
    tables = ["whale_moves", "steam_events", "player_hit_rates", "gamelines"]
    with engine.connect() as conn:
        for table in tables:
            try:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res.scalar()
                print(f"Table {table}: {count} rows")
                if count > 0:
                    res = conn.execute(text(f"SELECT * FROM {table} LIMIT 1"))
                    print(f"  Sample: {res.fetchone()}")
            except Exception as e:
                print(f"Table {table}: Error {e}")

if __name__ == "__main__":
    verify()
