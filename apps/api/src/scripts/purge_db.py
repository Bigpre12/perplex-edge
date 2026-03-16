import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

# Load .env from apps/api/.env
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

from db.session import SessionLocal, engine
from models.prop import PropLine, PropOdds
from models.history import PropHistory
from models.brain import ModelPick

def purge():
    print("🧹 Purging ALL sports data (cleansing for real data)...")
    with SessionLocal() as s:
        # Delete picks 
        s.query(ModelPick).delete()
        s.query(PropHistory).delete()
        s.query(PropOdds).delete()
        s.query(PropLine).delete()
        
        s.commit()
    print("✅ Purge complete. Database is clean.")

if __name__ == "__main__":
    purge()
