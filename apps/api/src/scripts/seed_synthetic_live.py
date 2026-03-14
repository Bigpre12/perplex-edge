import asyncio
from sqlalchemy import update
from database import SessionLocal
from models.props import PropLine
from datetime import datetime, timezone, timedelta

async def create_synthetic_today_data():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=20, minute=0, second=0, microsecond=0) # Late today
        tomorrow_start = today_start + timedelta(days=1)
        
        # Update first 50 NBA props to be 'today'
        # We need to make sure they share game_ids so they group into games
        
        # Get some unique game_ids
        from sqlalchemy import select
        stmt = select(PropLine.game_id).where(PropLine.sport_key == 'basketball_nba').distinct().limit(5)
        res = db.execute(stmt)
        game_ids = [r[0] for r in res.all() if r[0]]
        
        if not game_ids:
            print("No NBA game_ids found to update.")
            return

        print(f"Updating games {game_ids} to start today/tomorrow...")
        
        for i, gid in enumerate(game_ids):
            target_time = today_start if i < 3 else tomorrow_start
            stmt_upd = update(PropLine).where(PropLine.game_id == gid).values(start_time=target_time)
            db.execute(stmt_upd)
        
        db.commit()
        print("Successfully created synthetic 'live' data for today/tomorrow.")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_synthetic_today_data())
