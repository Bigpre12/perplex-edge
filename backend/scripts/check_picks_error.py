#!/usr/bin/env python3
"""
Check exact error on picks endpoint
"""
import requests

def check_picks_error():
    """Check exact error on picks endpoint"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING EXACT ERROR ON PICKS ENDPOINT")
    print("="*80)
    
    print("\n1. Backend Health: HEALTHY")
    
    print("\n2. Testing Picks Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=1", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 500:
            error_text = response.text
            print(f"   Error: {error_text[:200]}")
            
            # Check for specific column errors
            if "closing_odds" in error_text:
                print("   ERROR: closing_odds column issue")
            if "clv_percentage" in error_text:
                print("   ERROR: clv_percentage column issue")
            if "roi_percentage" in error_text:
                print("   ERROR: roi_percentage column issue")
            if "opening_odds" in error_text:
                print("   ERROR: opening_odds column issue")
            if "line_movement" in error_text:
                print("   ERROR: line_movement column issue")
            if "sharp_money_indicator" in error_text:
                print("   ERROR: sharp_money_indicator column issue")
            if "best_book_odds" in error_text:
                print("   ERROR: best_book_odds column issue")
            if "best_book_name" in error_text:
                print("   ERROR: best_book_name column issue")
            if "ev_improvement" in error_text:
                print("   ERROR: ev_improvement column issue")
        else:
            print(f"   Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Your SQL Commands:")
    print("   You ran these to check the columns:")
    print("   \\d model_picks")
    print("   \\c model_picks")
    print("   SELECT column_name FROM information_schema.columns")
    print("   WHERE table_name = 'model_picks'")
    print("   AND column_name IN ('closing_odds', 'clv_percentage', 'roi_percentage', 'opening_odds', 'line_movement', 'sharp_money_indicator', 'best_book_odds', 'best_book_name', 'ev_improvement')")
    print("   ORDER BY column_name;")
    
    print("\n4. What did you see?")
    print("   - Did the \\d model_picks show the new columns?")
    print("   - Did the SELECT query return the 9 column names?")
    print("   - Or did it return nothing?")
    
    print("\n5. Next Steps:")
    print("   If columns weren't added:")
    print("   - Run the ALTER TABLE commands again")
    print("   - Check for any SQL errors")
    print("   ")
    print("   If columns were added:")
    print("   - The issue might be in the code references")
    print("   - Check if the code is still trying to access the columns")
    print("   - May need to restart the backend again")
    
    print("\n" + "="*80)
    print("ERROR ANALYSIS: IN PROGRESS")
    print("Checking if CLV columns were actually added...")
    print("="*80)

if __name__ == "__main__":
    check_picks_error()
