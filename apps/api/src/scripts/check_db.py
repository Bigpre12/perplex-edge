import asyncio, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from database import SessionLocal
from models.props import PropLine
from sqlalchemy import func

def check():
    db = SessionLocal()
    try:
        count = db.query(func.count(PropLine.id)).scalar()
        latest = db.query(func.max(PropLine.start_time)).scalar()
        print(f"PropLine Count: {count}")
        print(f"PropLine Latest: {latest}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
