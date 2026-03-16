import asyncio, os, sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv; load_dotenv()
from datetime import datetime, timezone, timedelta
from db.session import engine, SessionLocal
from models.analytical import CLVRecord

def seed_clv():
    db = SessionLocal()
    try:
        # Clear existing
        db.query(CLVRecord).delete()
        
        players = [
            ("Luka Doncic", "player_points", 32.5),
            ("LeBron James", "player_rebounds", 7.5),
            ("Stephen Curry", "player_threes", 4.5),
            ("Nikola Jokic", "player_assists", 9.5),
            ("Kevin Durant", "player_points", 27.5),
            ("Giannis Antetokounmpo", "player_rebounds", 11.5),
            ("Jayson Tatum", "player_points", 26.5),
            ("Joel Embiid", "player_points", 33.5),
            ("Shai Gilgeous-Alexander", "player_assists", 6.5),
            ("Anthony Edwards", "player_threes", 3.5),
        ]
        
        records = []
        for i in range(20):
            p_name, stat, open_line = random.choice(players)
            # Create a movement
            move = random.uniform(-1.5, 2.5)
            close_line = open_line + move
            clv_val = round(((close_line - open_line) / open_line) * 100, 2)
            
            records.append(CLVRecord(
                player_name=p_name,
                stat_type=stat,
                opening_line=open_line,
                closing_line=close_line,
                clv=clv_val,
                clv_label='GREAT' if clv_val > 5 else 'GOOD' if clv_val > 2 else 'NEUTRAL',
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))
            ))
            
        db.add_all(records)
        db.commit()
        print(f"✅ Seeded {len(records)} CLV records")
    finally:
        db.close()

if __name__ == "__main__":
    seed_clv()
