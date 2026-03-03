"""
DFS Service for Lucrix

Handles logic specific to Pickem platforms (PrizePicks, Underdog, Sleeper).
Calculates implied odds and payout structures for DFS slips.
"""
from typing import Dict, List, Optional

class DFSService:
    # Common payout structures for Pickem platforms
    # Format: {platform: {num_legs: {"payout": x, "implied_odds": y}}}
    PAYOUT_STRUCTURES = {
        "prizepicks": {
            2: {"type": "Power Play", "payout": 3.0, "implied_odds": -137},
            3: {"type": "Power Play", "payout": 5.0, "implied_odds": -141},
            4: {"type": "Power Play", "payout": 10.0, "implied_odds": -128},
            5: {"type": "Flex Play", "payout": 10.0, "implied_odds": -119}, # 10x for 5/5
            6: {"type": "Flex Play", "payout": 25.0, "implied_odds": -119},
        },
        "underdog": {
            2: {"type": "Standard", "payout": 3.0, "implied_odds": -137},
            3: {"type": "Standard", "payout": 6.0, "implied_odds": -122},
            4: {"type": "Standard", "payout": 10.0, "implied_odds": -128},
            5: {"type": "Standard", "payout": 20.0, "implied_odds": -122},
        }
    }

    def get_implied_odds(self, platform: str, num_legs: int) -> int:
        """Get the implied odds for a single leg in a DFS slip."""
        platform = platform.lower()
        if platform not in self.PAYOUT_STRUCTURES:
            return -119 # Industry standard default for flex
        
        structure = self.PAYOUT_STRUCTURES[platform]
        if num_legs not in structure:
            return -119
            
        return structure[num_legs]["implied_odds"]

    def calculate_dfs_ev(self, win_probability: float, platform: str, num_legs: int) -> float:
        """
        Calculate Expected Value for a DFS leg based on true win probability.
        EV = (Win Prob * Implied Odds Payout) - (Loss Prob * 1)
        Note: Since DFS is fixed odds, we use the implied win prob from the odds.
        """
        implied_odds = self.get_implied_odds(platform, num_legs)
        # Convert American odds to decimal for calculation if needed, 
        # but usually EV for DFS is just (Win Prob - Breakeven Prob)
        
        # Breakeven probabilities:
        # -119 => 54.3%
        # -137 => 57.8%
        
        if implied_odds < 0:
            breakeven_prob = abs(implied_odds) / (abs(implied_odds) + 100)
        else:
            breakeven_prob = 100 / (implied_odds + 100)
            
        return win_probability - breakeven_prob

# Singleton instance
dfs_service = DFSService()
