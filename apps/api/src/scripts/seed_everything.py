import asyncio
import os
import sys
import random
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
os.environ["DEVELOPMENT_MODE"] = "1"

from db.session import async_session_maker
from models import WhaleMove, SteamEvent, HitRateModel
from models.prop import PropLine, GameLine, GameLineOdds
from sqlalchemy import select, delete, update

async def run_seed():
    print("🧹 Starting fresh seed...")
    async with async_session_maker() as session:
        # 1. Purge
        print("Purging existing data...")
        await session.execute(delete(WhaleMove))
        await session.execute(delete(SteamEvent))
        await session.execute(delete(HitRateModel))
        await session.execute(delete(GameLine))
        
        # 2. Add Whale Moves
        print("Adding Whale Moves...")
        whales = [
            WhaleMove(
                sport="basketball_nba",
                player_name="Victor Wembanyama",
                stat_type="player_points",
                line=23.5,
                move_type="WHALE_MOVE",
                side="over",
                severity="High",
                books_involved="FanDuel, DraftKings",
                whale_label="WHALE"
            ),
            WhaleMove(
                sport="basketball_nba",
                player_name="Tobias Harris",
                stat_type="player_points",
                line=13.5,
                move_type="SHARP_SPLIT",
                side="under",
                severity="Moderate",
                books_involved="BetMGM",
                whale_label="SHARP"
            )
        ]
        for w in whales:
            session.sync_session.add(w)
            
        # 3. Add Steam Events
        print("Adding Steam Events...")
        steams = [
            SteamEvent(
                sport="basketball_nba",
                player_name="Cade Cunningham",
                stat_type="player_assists",
                side="over",
                line=8.5,
                movement=1.5,
                book_count=5,
                severity=4.5,
                description="Rapid line movement across 5 books in 2 minutes."
            )
        ]
        for s in steams:
            session.sync_session.add(s)
            
        # 4. Add Hit Rates
        print("Adding Hit Rates...")
        hit_rates = [
            HitRateModel(player_name="Victor Wembanyama", stat_type="player_points", l5_hit_rate=80.0, l10_hit_rate=70.0, l20_hit_rate=65.0),
            HitRateModel(player_name="Tobias Harris", stat_type="player_points", l5_hit_rate=40.0, l10_hit_rate=50.0, l20_hit_rate=55.0),
            HitRateModel(player_name="Cade Cunningham", stat_type="player_assists", l5_hit_rate=60.0, l10_hit_rate=65.0, l20_hit_rate=58.0)
        ]
        for h in hit_rates:
            session.sync_session.add(h)
            
        # 5. Add GameLines
        print("Adding GameLines...")
        game = GameLine(
            game_id="live_game_1",
            sport_key="basketball_nba",
            home_team="Detroit Pistons",
            away_team="San Antonio Spurs",
            commence_time=datetime.now(timezone.utc) - timedelta(hours=1),
            market_key="h2h"
        )
        session.sync_session.add(game)
        
        # 6. Update Sharp Money Signals
        print("Updating PropLines...")
        await session.execute(
            update(PropLine)
            .where(PropLine.player_name == "Victor Wembanyama")
            .values(sharp_money=True, steam_score=4.5)
        )
        
        await session.commit()
        print("✅ Seeding complete!")

if __name__ == "__main__":
    try:
        asyncio.run(run_seed())
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
