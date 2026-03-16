import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from database import engine
from sqlalchemy import text

def check():
    print(f"DEBUG: Using DB URL: {engine.url}")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT sport, count(*), max(ingested_ts) FROM odds GROUP BY sport"))
        for row in res:
            print(f"SPORT: {row[0]}, COUNT: {row[1]}, MAX_TS: {row[2]}")

if __name__ == "__main__":
    check()
