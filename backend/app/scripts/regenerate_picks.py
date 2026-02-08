"""
Regenerate picks with conservative model
Run on Railway: railway run python app/scripts/regenerate_picks.py
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

async def regenerate_picks():
    """Generate new NBA picks with conservative model."""
    
    print("=" * 70)
    print("REGENERATING PICKS WITH CONSERVATIVE MODEL")
    print("=" * 70)
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from app.services.model import generate_model_picks_for_sport
        import os
        
        # Create async engine
        db_url = os.environ.get('DATABASE_URL', '')
        if not db_url:
            print("ERROR: DATABASE_URL not set")
            return
            
        # Convert to async URL
        async_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
        engine = create_async_engine(async_url)
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            print("Generating new NBA picks (sport_id=30)...")
            print("Using conservative model (2-4% EV, 25-75% probability range)")
            print()
            
            # Generate picks for NBA
            await generate_model_picks_for_sport(session, sport_id=30)
            await session.commit()
            
            print("✅ Picks generated successfully!")
            print()
            print("Verifying new picks...")
            
            # Check how many good picks we now have
            from sqlalchemy import text
            result = await session.execute(text('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_active AND expected_value <= 0.15 THEN 1 ELSE 0 END) as good_picks,
                    ROUND(AVG(expected_value) * 100, 2) as avg_ev
                FROM model_picks
                WHERE sport_id = 30
            '''))
            row = result.first()
            
            print(f"  Total NBA picks: {row[0]}")
            print(f"  Good picks (EV <= 15%): {row[1]}")
            print(f"  Average EV: {row[2]}%")
            
            if row[1] > 0:
                print()
                print("✅ SUCCESS: You now have good picks for the parlay builder!")
                print("   Refresh the frontend to see candidates.")
            else:
                print()
                print("⚠️  WARNING: No good picks generated")
                print("   Check model logs for errors")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("=" * 70)
    print("REGENERATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(regenerate_picks())
