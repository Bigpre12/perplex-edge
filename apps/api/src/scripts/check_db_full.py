import asyncio, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from db.session import SessionLocal
from models.prop import PropLine, GameLine
from models.brain import ModelPick
from sqlalchemy import func

def check():
    db = SessionLocal()
    try:
        tables = [
            ("PropLine", PropLine, "start_time"),
            ("GameLine", GameLine, "commence_time"),
            ("ModelPick", ModelPick, "created_at")
        ]
        for name, model, date_col in tables:
            count = db.query(func.count(model.id)).scalar()
            latest = db.query(func.max(getattr(model, date_col))).scalar()
            print(f"{name:10} | Count: {count:5} | Latest: {latest}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
