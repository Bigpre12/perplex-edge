import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
os.environ["DEVELOPMENT_MODE"] = "1"

from database import engine
from sqlalchemy import text

def check():
    print(f"Checking DB: {engine.url}")
    with engine.connect() as conn:
        try:
            res = conn.execute(text("SELECT COUNT(*) FROM model_picks"))
            count = res.scalar()
            print(f"model_picks count: {count}")
        except Exception as e:
            print(f"Error checking model_picks: {e}")

        # Check proplines
        try:
            res = conn.execute(text("SELECT COUNT(*) FROM proplines"))
            count = res.scalar()
            print(f"proplines count: {count}")
        except Exception as e:
            print(f"Error checking proplines: {e}")
            
        # Check propodds
        try:
            res = conn.execute(text("SELECT COUNT(*) FROM propodds"))
            count = res.scalar()
            print(f"propodds count: {count}")
        except Exception as e:
            print(f"Error checking propodds: {e}")

if __name__ == "__main__":
    check()
