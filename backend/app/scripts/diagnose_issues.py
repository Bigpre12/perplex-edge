"""
Diagnostic script - Check database state and API endpoints
Run on Railway: railway run python app/scripts/diagnose_issues.py
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

async def diagnose():
    """Diagnose the two critical issues."""
    
    print("=" * 70)
    print("DIAGNOSTIC: Checking critical issues")
    print("=" * 70)
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    # Issue 1: Check database state
    print("ISSUE 1: Database State (Zero Candidates)")
    print("-" * 70)
    
    try:
        from sqlalchemy import create_engine, text
        import os
        
        engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://localhost/perplex'))
        
        with engine.connect() as conn:
            # Check NBA picks
            result = conn.execute(text('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN expected_value > 0.15 THEN 1 ELSE 0 END) as high_ev,
                    SUM(CASE WHEN expected_value <= 0.15 AND is_active THEN 1 ELSE 0 END) as good_picks,
                    ROUND(AVG(expected_value) * 100, 2) as avg_ev,
                    ROUND(MIN(expected_value) * 100, 2) as min_ev,
                    ROUND(MAX(expected_value) * 100, 2) as max_ev
                FROM model_picks
                WHERE sport_id = 30
            ''')).first()
            
            print(f"  Total NBA picks: {result[0]}")
            print(f"  Active picks: {result[1]}")
            print(f"  Hidden (EV>15%): {result[2]}")
            print(f"  Good picks (EV<=15% & active): {result[3]}")
            print(f"  Average EV: {result[4]}%")
            print(f"  EV range: {result[5]}% to {result[6]}%")
            print()
            
            if result[3] == 0:
                print("  ❌ PROBLEM: All picks were hidden or have EV > 15%")
                print("  🔧 FIX NEEDED: Generate new picks with conservative model")
            else:
                print(f"  ✅ You have {result[3]} good picks")
                print("  Check parlay builder filters if still showing 0 candidates")
                
    except Exception as e:
        print(f"  ❌ Database error: {e}")
    
    print()
    
    # Issue 2: Check API routes
    print("ISSUE 2: API Routes (HTML instead of JSON)")
    print("-" * 70)
    
    try:
        from app.main import app
        
        # Check if grading routes exist
        grading_routes = [r for r in app.routes if hasattr(r, 'path') and '/api/grading' in r.path]
        
        print(f"  Found {len(grading_routes)} grading routes:")
        for route in grading_routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"    {route.methods} {route.path}")
        
        if len(grading_routes) == 0:
            print("  ❌ PROBLEM: No grading routes found")
            print("  🔧 FIX NEEDED: Router not registered in main.py")
        else:
            print(f"  ✅ Grading router registered with {len(grading_routes)} routes")
            
    except Exception as e:
        print(f"  ❌ Error checking routes: {e}")
    
    print()
    print("=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    print()
    print("NEXT STEPS:")
    print("1. If all picks hidden: Run regenerate_picks.py")
    print("2. If no grading routes: Check main.py router registration")
    print("3. If both OK: Check Railway logs for runtime errors")

if __name__ == "__main__":
    asyncio.run(diagnose())
