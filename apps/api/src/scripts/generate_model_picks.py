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
    try:
        from services.brain_advanced_service import brain_advanced_service
        # NBA (30)
        print("Analyzing NBA slate...")
        await brain_advanced_service.analyze_all_props(sport_id=30)
        print("✅ Analysis complete.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(generate_picks())
