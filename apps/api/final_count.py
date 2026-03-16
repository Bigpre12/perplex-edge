import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from database import engine
from sqlalchemy import text

def count():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT count(*) FROM odds"))
        print(f"FINAL_ODDS_COUNT: {res.scalar()}")

if __name__ == "__main__":
    count()
