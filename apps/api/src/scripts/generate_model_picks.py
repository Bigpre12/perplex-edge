import asyncio
import os
import sys
from datetime import datetime, timezone

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
os.environ["DEVELOPMENT_MODE"] = "1"

from services.brain_service import brain_service
from db.session import get_db

async def generate_picks():
    print("🧠 Triggering Brain analysis to generate ModelPicks...")
    async with async_session_maker() as session:
        # We need to simulate the slate decision process
        # This usually involves analyze_all_props()
        try:
            # Let's try to analyze NBA (30)
            print("Analyzing NBA slate...")
            await brain_service.analyze_all_props(sport_id=30)
            
            # Check results
            from sqlalchemy import select
            from models.brain import ModelPick
            res = await session.execute(select(ModelPick))
            picks = res.scalars().all()
            print(f"Generated {len(picks)} ModelPicks.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(generate_picks())
