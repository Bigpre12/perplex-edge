"""
Script to fix existing impossible EV values in the database
"""

import asyncio
import sys
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

# Add the backend directory to the path
sys.path.append('/app')

from app.core.database import get_session_maker
from app.models import ModelPick
from app.services.model import american_to_implied_prob
from app.services.probability_calibration import ProbabilityCalibrator

async def fix_existing_ev():
    """Fix existing impossible EV values in the database."""
    
    print("🔧 FIXING EXISTING EV VALUES...")
    
    # Get database session
    session_maker = get_session_maker()
    async with session_maker() as db:
        
        # Get all picks with impossible EV values
        query = select(ModelPick).where(ModelPick.expected_value > 0.10)
        result = await db.execute(query)
        impossible_picks = result.scalars().all()
        
        print(f"   Found {len(impossible_picks)} picks with impossible EV > 10%")
        
        calibrator = ProbabilityCalibrator()
        fixed_count = 0
        
        for pick in impossible_picks:
            try:
                # Get implied probability from odds
                implied_prob = american_to_implied_prob(int(pick.odds))
                
                # Calibrate the model probability
                calibrated_prob = calibrator.calibrate_probability(
                    pick.model_probability,
                    implied_prob,
                    sample_size=10,  # Default sample size
                    market_type="player_props"
                )
                
                # Calculate new EV
                from app.services.model import compute_ev
                new_ev = compute_ev(calibrated_prob, int(pick.odds))
                
                # Update the pick
                await db.execute(
                    update(ModelPick)
                    .where(ModelPick.id == pick.id)
                    .values(
                        model_probability=calibrated_prob,
                        expected_value=new_ev
                    )
                )
                
                fixed_count += 1
                
                if fixed_count <= 5:  # Show first 5 fixes
                    print(f"   Fixed Pick {pick.id}: {pick.expected_value:.4f} → {new_ev:.4f}")
                
            except Exception as e:
                print(f"   Error fixing pick {pick.id}: {e}")
                continue
        
        # Commit changes
        await db.commit()
        
        print(f"   ✅ Fixed {fixed_count} picks with impossible EV values")
        print(f"   🎯 Database now contains realistic EV values")

if __name__ == "__main__":
    asyncio.run(fix_existing_ev())
