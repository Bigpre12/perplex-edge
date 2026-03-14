import sys
import os
import random
from datetime import datetime, timezone

# Add current dir to sys.path to import database and models
sys.path.append(os.getcwd())

from database import SessionLocal
from models.props import PropLine
from sqlalchemy import select

def settle_demo_props():
    db = SessionLocal()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Get all sports
    from sqlalchemy import func
    sports = db.query(PropLine.sport_key).distinct().all()
    
    total_settled = 0
    for (sport_key,) in sports:
        # Get props in the past for this sport that are not settled
        stmt = select(PropLine).where(
            PropLine.start_time < now, 
            PropLine.is_settled == False,
            PropLine.sport_key == sport_key
        ).limit(100) # Settle up to 100 per sport
        
        props = db.execute(stmt).scalars().all()
        print(f"Settling {len(props)} props for {sport_key}...")
        
        for prop in props:
            is_hit = random.random() > 0.48
            actual = prop.line + (random.uniform(0.5, 5.5) if is_hit else -random.uniform(0.5, 5.5))
            
            prop.is_settled = True
            prop.hit = is_hit
            prop.actual_value = round(max(0, actual), 1)
            total_settled += 1
            
    db.commit()
    print(f"Total settled: {total_settled} props across all sports.")
    db.close()

if __name__ == "__main__":
    settle_demo_props()
