import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
os.environ["DEVELOPMENT_MODE"] = "1"

from db.session import engine
from sqlalchemy import text

def check_names():
    print(f"Checking names in DB: {engine.url}")
    with engine.connect() as conn:
        try:
            res = conn.execute(text("SELECT DISTINCT player_name FROM proplines WHERE player_name LIKE '%Hart%'"))
            names = [row[0] for row in res]
            print(f"Found Hart names in proplines: {names}")
            
            res = conn.execute(text("SELECT COUNT(*) FROM proplines"))
            print(f"Total proplines: {res.scalar()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_names()
