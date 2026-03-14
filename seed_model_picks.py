import asyncio
import os
import sys
import random
from datetime import datetime, timezone

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
os.environ["DEVELOPMENT_MODE"] = "1"

from database import async_session_maker
from models.props import PropLine, PropOdds
from models.brain import ModelPick
from services.picks_service import PicksService
from sqlalchemy import select, delete

async def seed_picks():
    print("🧹 Purging existing ModelPicks...")
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(delete(ModelPick))
    
    print("📈 Generating ModelPicks for Pistons/Spurs...")
    picks_service = PicksService()
    
    async with async_session_maker() as session:
        # Select players we know are from the recent seed
        target_names = ['Tobias Harris', 'Cade Cunningham', 'Ausar Thompson', 'Stephon Castle', 'Victor Wembanyama']
        stmt = select(PropLine).where(PropLine.player_name.in_(target_names))
        res = await session.execute(stmt)
        lines = res.scalars().all()
        
        print(f"Found {len(lines)} specific PropLines. Processing...")
        
        for line in lines:
            # Get odds for this line
            stmt_odds = select(PropOdds).where(PropOdds.prop_line_id == line.id)
            res_odds = await session.execute(stmt_odds)
            odds_list = res_odds.scalars().all()
            
            if not odds_list:
                continue
                
            # Pick a random book's odds
            o = random.choice(odds_list)
            
            # Generate a "model edge"
            edge = random.uniform(0.04, 0.12)
            
            # Implied from odds (simplified)
            odds_val = o.over_odds
            if odds_val < 0:
                implied = abs(odds_val) / (abs(odds_val) + 100)
            else:
                implied = 100 / (odds_val + 100)
                
            model_prob = implied + edge
            
            print(f"Adding pick for {line.player_name}: {line.stat_type} @ {line.line} (Edge: {edge*100:.1f}%)")
            
            await picks_service.create_pick(
                game_id=line.game_id or 12345,
                pick_type="player_prop",
                player_name=line.player_name,
                stat_type=line.stat_type,
                line=line.line,
                odds=odds_val,
                model_probability=model_prob,
                confidence=model_prob,
                hit_rate=0.6,
                sport_key=line.sport_key
            )
            
    print("✅ ModelPick seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_picks())
