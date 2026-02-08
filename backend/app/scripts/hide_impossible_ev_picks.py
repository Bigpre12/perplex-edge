"""
Script to hide existing picks with impossible EV values (>15%)
Run this after Railway deployment to hide bad picks from users
"""

import asyncio
import sys
from datetime import datetime, timezone

sys.path.append('/app')

async def hide_impossible_ev_picks():
    """Hide picks with EV > 15% from the database."""
    
    print("HIDING PICKS WITH IMPOSSIBLE EV VALUES")
    print("=" * 50)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        from app.core.database import get_session_maker
        from sqlalchemy import text
        
        session_maker = get_session_maker()
        
        async with session_maker() as db:
            # Count picks with impossible EV
            count_query = text("""
                SELECT COUNT(*) FROM model_picks 
                WHERE expected_value > 0.15 AND is_active = true
            """)
            result = await db.execute(count_query)
            impossible_count = result.scalar()
            
            print(f"Found {impossible_count} picks with EV > 15%")
            
            if impossible_count == 0:
                print("✓ No impossible EV picks found - database is clean")
                return
            
            # Hide these picks by setting is_active = false
            hide_query = text("""
                UPDATE model_picks 
                SET is_active = false, 
                    notes = 'Hidden: impossible EV value'
                WHERE expected_value > 0.15 AND is_active = true
            """)
            
            await db.execute(hide_query)
            await db.commit()
            
            print(f"✓ Successfully hid {impossible_count} picks with impossible EV")
            print()
            print("IMPORTANT:")
            print("- These picks are now hidden from the frontend")
            print("- Users will no longer see 81% EV claims")
            print("- New picks should be generated with conservative model")
            print("- Verify new picks show 2-5% EV, not 81%")
            
    except Exception as e:
        print(f"✗ Error hiding picks: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(hide_impossible_ev_picks())
