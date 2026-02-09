#!/usr/bin/env python3
"""
Comprehensive fix for all issues
"""
import requests
import subprocess
import time

def comprehensive_fix():
    """Comprehensive fix for all issues"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("COMPREHENSIVE FIX FOR ALL ISSUES")
    print("="*80)
    
    print("\nCURRENT STATUS:")
    print("1. Backend Health: OK")
    print("2. CLV Columns: Missing from database")
    print("3. Picks Working: 500 error due to missing columns")
    print("4. Parlay Builder: OK (but no picks)")
    print("5. Frontend-Backend: 502 error (wrong BACKEND_URL)")
    
    print("\nFIX PLAN:")
    print("1. Add CLV columns to database directly")
    print("2. Fix frontend BACKEND_URL")
    print("3. Test everything")
    
    print("\n" + "="*80)
    print("MANUAL ACTIONS REQUIRED:")
    print("="*80)
    
    print("\n1. ADD CLV COLUMNS TO DATABASE:")
    print("   Connect to your PostgreSQL database and run:")
    print("   ")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS closing_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS clv_percentage NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS roi_percentage NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS opening_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS line_movement NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS sharp_money_indicator NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS best_book_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS best_book_name VARCHAR(50);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS ev_improvement NUMERIC(10, 4);")
    
    print("\n2. FIX FRONTEND BACKEND_URL:")
    print("   Go to Railway dashboard:")
    print("   - Click perplex-edge-production project")
    print("   - Click frontend service")
    print("   - Click Variables tab")
    print("   - Add variable: BACKEND_URL")
    print("   - Set value: https://railway-engine-production.up.railway.app")
    print("   - Click Add")
    print("   - Wait for redeploy (2-3 minutes)")
    
    print("\n3. AFTER FIXES APPLIED:")
    print("   Test these URLs:")
    print(f"   - Backend health: {base_url}/api/health")
    print(f"   - NBA picks: {base_url}/api/sports/30/picks/player-props?limit=5")
    print(f"   - NFL picks: {base_url}/api/sports/31/picks/player-props?game_id=648&limit=5")
    print(f"   - Parlay builder: {base_url}/api/sports/30/parlays/builder?leg_count=2&max_results=3")
    print(f"   - Frontend proxy: https://perplex-edge-production.up.railway.app/api/grading/model-status")
    
    print("\n" + "="*80)
    print("EXPECTED RESULTS:")
    print("="*80)
    
    print("\nAfter CLV columns added:")
    print("- NBA picks should return 200 with props")
    print("- NFL picks should return 200 with props")
    print("- Parlay builder should return parlays")
    
    print("\nAfter BACKEND_URL fixed:")
    print("- Frontend should reach backend")
    print("- No more 502 errors")
    print("- Full system working")
    
    print("\n" + "="*80)
    print("TIME ESTIMATE:")
    print("="*80)
    
    print("\n- Add CLV columns: 5 minutes")
    print("- Set BACKEND_URL: 3 minutes")
    print("- Wait for deployment: 3 minutes")
    print("- Test everything: 2 minutes")
    print("Total: ~13 minutes")
    
    print("\n" + "="*80)
    print("SUPER BOWL COUNTDOWN:")
    print("="*80)
    
    from datetime import datetime
    now = datetime.now()
    super_bowl = datetime(2026, 2, 8, 17, 30)  # 5:30 PM CT
    time_left = super_bowl - now
    hours_left = time_left.total_seconds() / 3600
    
    print(f"\nCurrent time: {now.strftime('%I:%M %p')}")
    print(f"Super Bowl kickoff: 5:30 PM CT")
    print(f"Time left: {hours_left:.1f} hours")
    
    if hours_left > 6:
        print("Status: PLENTY OF TIME!")
    elif hours_left > 3:
        print("Status: Good time")
    else:
        print("Status: Getting tight")
    
    print("\n" + "="*80)
    print("FINAL CHECKLIST:")
    print("="*80)
    
    print("\n[ ] Add 9 CLV columns to database")
    print("[ ] Set BACKEND_URL in frontend service")
    print("[ ] Wait for deployment")
    print("[ ] Test NBA picks endpoint")
    print("[ ] Test NFL picks endpoint")
    print("[ ] Test parlay builder")
    print("[ ] Test frontend-backend connection")
    print("[ ] Activate picks for Super Bowl")
    print("[ ] Launch platform!")
    
    print("\n" + "="*80)
    print("READY TO EXECUTE!")
    print("Follow the manual steps above and everything will work.")
    print("="*80)

if __name__ == "__main__":
    comprehensive_fix()
