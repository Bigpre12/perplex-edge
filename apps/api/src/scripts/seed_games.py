import os
import sys
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
from db.session import SessionLocal
from models.prop import GameLine

def seed_games():
    db = SessionLocal()
    try:
        # Purge existing
        db.query(GameLine).delete()
        
        games = [
            GameLine(
                game_id="live_game_1",
                sport_key="basketball_nba",
                home_team="Golden State Warriors",
                away_team="Los Angeles Lakers",
                commence_time=datetime.now(timezone.utc) - timedelta(hours=1),
                market_key="h2h"
            ),
            GameLine(
                game_id="live_game_2",
                sport_key="basketball_nba",
                home_team="Phoenix Suns",
                away_team="Milwaukee Bucks",
                commence_time=datetime.now(timezone.utc) - timedelta(minutes=30),
                market_key="h2h"
            ),
            GameLine(
                game_id="live_game_3",
                sport_key="americanfootball_nfl",
                home_team="Kansas City Chiefs",
                away_team="Philadelphia Eagles",
                commence_time=datetime.now(timezone.utc) + timedelta(hours=24),
                market_key="h2h"
            )
        ]
        
        for g in games:
            db.add(g)
        
        db.commit()
        print(f"✅ Seeded {len(games)} GameLines")
    finally:
        db.close()

if __name__ == "__main__":
    seed_games()
