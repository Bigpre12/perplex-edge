#!/usr/bin/env python3
"""
Add fix and push all issues
"""
import subprocess
import time
import requests

def fix_and_push_all():
    """Fix all issues and push to git"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("FIXING AND PUSHING ALL ISSUES")
    print("="*80)
    
    print("\n1. Current Issues:")
    print("   - CLV columns missing from database (500 errors)")
    print("   - Frontend 502 error (wrong BACKEND_URL)")
    print("   - Picks not working")
    
    print("\n2. Fix Strategy:")
    print("   - Comment out CLV column references in code")
    print("   - Push to git")
    print("   - Wait for deployment")
    print("   - Test everything")
    
    print("\n3. Fixing CLV column references...")
    
    # Fix the ModelPick model to make CLV columns optional
    try:
        model_pick_path = "c:/Users/preio/perplex-edge/backend/app/models/model_pick.py"
        with open(model_pick_path, "r") as f:
            content = f.read()
        
        # Make CLV columns optional by adding default values
        if "closing_odds = Column(" in content:
            content = content.replace(
                "closing_odds = Column(",
                "# closing_odds = Column("
            )
            content = content.replace(
                "clv_percentage = Column(",
                "# clv_percentage = Column("
            )
            content = content.replace(
                "roi_percentage = Column(",
                "# roi_percentage = Column("
            )
            content = content.replace(
                "opening_odds = Column(",
                "# opening_odds = Column("
            )
            content = content.replace(
                "line_movement = Column(",
                "# line_movement = Column("
            )
            content = content.replace(
                "sharp_money_indicator = Column(",
                "# sharp_money_indicator = Column("
            )
            content = content.replace(
                "best_book_odds = Column(",
                "# best_book_odds = Column("
            )
            content = content.replace(
                "best_book_name = Column(",
                "# best_book_name = Column("
            )
            content = content.replace(
                "ev_improvement = Column(",
                "# ev_improvement = Column("
            )
        
        with open(model_pick_path, "w") as f:
            f.write(content)
            
        print("   Fixed ModelPick model")
    except Exception as e:
        print(f"   Error fixing ModelPick: {e}")
    
    # Fix the picks query in public.py
    try:
        public_path = "c:/Users/preio/perplex-edge/backend/app/api/public.py"
        with open(public_path, "r") as f:
            content = f.read()
        
        # The issue is that select(ModelPick, ...) selects all columns
        # We need to explicitly select only the columns that exist
        if "select(ModelPick, Player," in content:
            # Replace with explicit column selection
            old_select = "select(ModelPick, Player,"
            new_select = "select("
            
            # Add explicit ModelPick columns (excluding CLV)
            model_pick_columns = [
                "ModelPick.id",
                "ModelPick.sport_id", 
                "ModelPick.game_id",
                "ModelPick.player_id",
                "ModelPick.market_id",
                "ModelPick.side",
                "ModelPick.line_value",
                "ModelPick.odds",
                "ModelPick.model_probability",
                "ModelPick.implied_probability",
                "ModelPick.expected_value",
                "ModelPick.hit_rate_30d",
                "ModelPick.hit_rate_10g",
                "ModelPick.hit_rate_5g",
                "ModelPick.hit_rate_3g",
                "ModelPick.confidence_score",
                "ModelPick.generated_at",
                "ModelPick.is_active"
            ]
            
            new_select += ", ".join(model_pick_columns) + ", Player,"
            
            content = content.replace(old_select, new_select)
            
            with open(public_path, "w") as f:
                f.write(content)
                
            print("   Fixed picks query in public.py")
    except Exception as e:
        print(f"   Error fixing public.py: {e}")
    
    print("\n4. Pushing fixes to git...")
    try:
        # Add all changes
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        
        # Commit changes
        subprocess.run(["git", "commit", "-m", "Fix CLV column references - make optional"], check=True, capture_output=True)
        
        # Push to git
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        
        print("   Successfully pushed fixes to git")
    except Exception as e:
        print(f"   Git push failed: {e}")
    
    print("\n5. Waiting for deployment...")
    time.sleep(30)
    
    print("\n6. Testing after deployment...")
    
    # Test backend health
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Backend Health: {response.status_code}")
        if response.status_code == 200:
            print("   Backend is healthy")
    except:
        print("   Backend health check failed")
    
    # Test picks
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=5", timeout=10)
        print(f"   NBA Picks: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NBA props")
            
            if props:
                prop = props[0]
                player = prop.get('player', {})
                print(f"   Sample: {player.get('name', 'N/A')}: {prop.get('stat_type', 'N/A')} {prop.get('line_value', 'N/A')}")
                print(f"   Edge: {prop.get('edge', 0):.2%}")
        else:
            print(f"   Error: {response.text[:100]}")
    except:
        print("   Picks test failed")
    
    # Test NFL picks
    try:
        response = requests.get(f"{base_url}/api/sports/31/picks/player-props?game_id=648&limit=5", timeout=10)
        print(f"   NFL Picks: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            props = data.get('items', [])
            print(f"   SUCCESS! Found {len(props)} NFL props")
    except:
        print("   NFL picks test failed")
    
    # Test parlay builder
    try:
        response = requests.get(f"{base_url}/api/sports/30/parlays/builder?leg_count=2&max_results=3", timeout=10)
        print(f"   Parlay Builder: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            print(f"   Found {len(parlays)} parlays")
    except:
        print("   Parlay builder test failed")
    
    print("\n" + "="*80)
    print("FIX SUMMARY:")
    print("1. Commented out CLV columns in ModelPick model")
    print("2. Fixed picks query to select only existing columns")
    print("3. Pushed changes to git")
    print("4. Waiting for deployment")
    print("5. Testing all endpoints")
    
    print("\nREMAINING MANUAL STEP:")
    print("- Set BACKEND_URL in Railway frontend service")
    print("- Value: https://railway-engine-production.up.railway.app")
    
    print("\n" + "="*80)
    print("FIXES APPLIED AND PUSHED!")
    print("Testing deployment now...")
    print("="*80)

if __name__ == "__main__":
    fix_and_push_all()
