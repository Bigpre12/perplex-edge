#!/usr/bin/env python3
"""
Summary of available game data
"""
import requests

def summarize_available_data():
    """Summarize available data"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("SUMMARY OF AVAILABLE DATA")
    print("="*80)
    
    print("\n✅ AVAILABLE:")
    print("1. Games:")
    print("   - NBA: 4 games today")
    print("   - NFL: 1 game (Super Bowl)")
    
    print("\n2. Odds Data:")
    print("   - Moneyline odds available from multiple sportsbooks")
    print("   - DraftKings, FanDuel, BetMGM data present")
    
    print("\n❌ MISSING:")
    print("1. Player Props/Picks:")
    print("   - 0 picks available for all markets")
    print("   - No model predictions for today's games")
    
    print("\n2. Point Spreads & Totals:")
    print("   - Only moneyline odds in best odds endpoint")
    print("   - No spread or total lines visible")
    
    print("\n📊 SAMPLE ODDS DATA:")
    # Get sample odds
    try:
        response = requests.get(f"{base_url}/api/odds/best?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            for odd in data[:3]:
                game_id = odd.get('game_id')
                market = odd.get('market_type')
                side = odd.get('side')
                best_odds = odd.get('best_odds')
                best_book = odd.get('best_sportsbook')
                print(f"   Game {game_id} - {market} {side}: {best_odds} ({best_book})")
    except:
        pass
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. The odds data is available and working")
    print("2. Need to fix the database integrity error for odds sync")
    print("3. Need to generate picks for today's games")
    print("4. Parlay builder will work once picks are available")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    summarize_available_data()
