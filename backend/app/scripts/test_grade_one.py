"""
Test grading one pick - verify end-to-end grading pipeline works
Run on Railway after deployment: python app/scripts/test_grade_one.py
"""

import asyncio
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

async def test_grade_one_pick():
    """Grade one completed pick to test the pipeline."""
    
    print("=" * 60)
    print("TEST: Grade One Pick")
    print("=" * 60)
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        from sqlalchemy import select, and_
        from app.core.database import AsyncSession, engine
        from app.tasks.grade_picks import pick_grader
        from app.models import ModelPick, Game
        
        async with AsyncSession(engine) as db:
            # Find completed games (3+ hours ago)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=3)
            
            query = select(ModelPick).join(Game).where(
                and_(
                    Game.start_time < cutoff,
                    ModelPick.result_id.is_(None)  # Not yet graded
                )
            ).limit(1)
            
            result = await db.execute(query)
            pick = result.scalar_one_or_none()
            
            if not pick:
                print("[INFO] No completed picks found to grade")
                print("       (This is normal if no games have finished yet)")
                print()
                print("Next steps:")
                print("1. Wait for games to complete (3+ hours after start)")
                print("2. Run this script again")
                return
            
            print(f"Found pick to grade: {pick.id}")
            print(f"Player ID: {pick.player_id}")
            print(f"Expected: {pick.side} {pick.line_value}")
            print(f"Game ID: {pick.game_id}")
            print()
            
            # Grade the pick
            success = await pick_grader.grade_single_pick(db, pick)
            
            if success:
                await db.commit()
                print("[PASS] Pick graded successfully!")
                print(f"       Result: {pick.result.result if pick.result else 'N/A'}")
                print(f"       CLV: {pick.clv_percentage}%")
            else:
                print("[FAIL] Failed to grade pick")
                print("       Check logs for errors")
                
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("=" * 60)
    print("Test complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_grade_one_pick())
