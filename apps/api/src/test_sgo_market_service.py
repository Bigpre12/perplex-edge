import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from services.sgo_market_service import SGOMarketService

def test_sgo_market_service():
    print("Testing SportsGameOdds Market Parsing Service...")
    
    test_cases = [
        # 1. Moneyline
        ("points-home-game-ml-home", "BASKETBALL", "Home Team Moneyline (Full Event)"),
        
        # 2. Spread
        ("points-away-game-sp-away", "FOOTBALL", "Away Team Spread (Full Event)"),
        
        # 3. Over/Under (Special labels)
        ("points-all-game-ou-over", "BASKETBALL", "Over Points - All / Combined (Full Event)"),
        
        # 4. 1st Half Moneyline
        ("points-home-1h-ml-home", "SOCCER", "Home Team Moneyline (1st Half)"),
        
        # 5. Hockey Goals (Points)
        ("points-home-game-ml-home", "HOCKEY", "Home Team Moneyline (Full Event)"),
        
        # 6. Player Prop
        ("assists-LEBRON_JAMES_NBA-game-ou-over", "BASKETBALL", "Over Assists - Lebron James Nba (Full Event)"),
        
        # 7. 3-Way Market
        ("points-all-game-ml3way-draw", "SOCCER", "All / Combined 3-Way Moneyline (Full Event)"),
    ]
    
    print("\n--- Testing Market Descriptions ---")
    for odd_id, sport_id, expected in test_cases:
        actual = SGOMarketService.get_market_description(odd_id, sport_id)
        if actual == expected:
            print(f"SUCCESS: {odd_id} ({sport_id}) -> {actual}")
        else:
            print(f"FAIL: {odd_id} ({sport_id}) -> Got: {actual}, Expected: {expected}")

    print("\n--- Testing Market Labels ---")
    label = SGOMarketService.get_market_label("points-all-game-ou-over", "BASKETBALL")
    print(f"Label: {label} (Expected: Total Points Over)")

if __name__ == "__main__":
    test_sgo_market_service()
