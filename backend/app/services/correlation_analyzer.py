"""
Correlation Analyzer - Same-game parlay correlation analysis
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Game, Player, Team, Market

@dataclass
class CorrelationData:
    """Correlation data between two picks."""
    pick1_id: int
    pick2_id: int
    correlation_coefficient: float
    correlation_type: str  # "positive", "negative", "neutral"
    correlation_strength: str  # "weak", "moderate", "strong"
    game_script_impact: float
    rationale: str

class CorrelationAnalyzer:
    """Analyzes correlations between player props in same game."""
    
    def __init__(self):
        self.correlation_cache = {}
        self.correlation_thresholds = {
            "strong": 0.7,
            "moderate": 0.4,
            "weak": 0.2
        }
    
    def calculate_stat_correlation(
        self, 
        stat1: str, 
        stat2: str,
        player_position: str
    ) -> Tuple[float, str]:
        """
        Calculate correlation between two statistics based on player position.
        
        Args:
            stat1: First statistic (e.g., "PTS", "AST")
            stat2: Second statistic (e.g., "REB", "BLK")
            player_position: Player position (e.g., "PG", "C")
        
        Returns:
            Tuple of (correlation_coefficient, correlation_type)
        """
        
        # Define correlation matrix by position
        correlation_matrix = {
            "PG": {  # Point Guard
                ("PTS", "AST"): (0.65, "positive"),
                ("PTS", "REB"): (0.35, "positive"),
                ("AST", "TOV"): (0.55, "positive"),
                ("PTS", "TOV"): (0.45, "positive"),
                ("AST", "REB"): (0.25, "positive"),
                ("PTS", "BLK"): (-0.15, "negative"),
                ("AST", "BLK"): (-0.10, "negative"),
            },
            "SG": {  # Shooting Guard
                ("PTS", "AST"): (0.45, "positive"),
                ("PTS", "REB"): (0.40, "positive"),
                ("PTS", "3PM"): (0.75, "positive"),
                ("AST", "TOV"): (0.40, "positive"),
                ("REB", "BLK"): (0.30, "positive"),
                ("PTS", "BLK"): (-0.05, "negative"),
            },
            "SF": {  # Small Forward
                ("PTS", "REB"): (0.55, "positive"),
                ("PTS", "AST"): (0.35, "positive"),
                ("REB", "AST"): (0.30, "positive"),
                ("PTS", "BLK"): (0.25, "positive"),
                ("REB", "BLK"): (0.45, "positive"),
                ("3PM", "PTS"): (0.60, "positive"),
            },
            "PF": {  # Power Forward
                ("PTS", "REB"): (0.70, "positive"),
                ("REB", "BLK"): (0.60, "positive"),
                ("PTS", "BLK"): (0.35, "positive"),
                ("REB", "AST"): (0.25, "positive"),
                ("PTS", "AST"): (0.20, "positive"),
                ("BLK", "PF"): (0.50, "positive"),
            },
            "C": {  # Center
                ("PTS", "REB"): (0.60, "positive"),
                ("REB", "BLK"): (0.75, "positive"),
                ("PTS", "BLK"): (0.40, "positive"),
                ("REB", "AST"): (0.15, "positive"),
                ("BLK", "PF"): (0.55, "positive"),
                ("PTS", "PF"): (0.30, "positive"),
            }
        }
        
        # Default correlations for unknown positions
        default_correlations = {
            ("PTS", "AST"): (0.40, "positive"),
            ("PTS", "REB"): (0.45, "positive"),
            ("AST", "REB"): (0.25, "positive"),
            ("REB", "BLK"): (0.50, "positive"),
            ("PTS", "BLK"): (0.25, "positive"),
            ("AST", "TOV"): (0.45, "positive"),
        }
        
        # Normalize stat order for lookup
        stat_pair = tuple(sorted([stat1, stat2]))
        
        # Get correlation from position matrix
        position_correlations = correlation_matrix.get(player_position, {})
        
        if stat_pair in position_correlations:
            return position_correlations[stat_pair]
        elif stat_pair in default_correlations:
            return default_correlations[stat_pair]
        else:
            return (0.0, "neutral")
    
    def calculate_game_script_correlation(
        self,
        stat1: str,
        side1: str,
        stat2: str,
        side2: str,
        team_favorite: bool
    ) -> float:
        """
        Calculate game script impact on correlation.
        
        Args:
            stat1, stat2: Statistics
            side1, side2: "over" or "under"
            team_favorite: Whether the player's team is favorite
        
        Returns:
            Game script impact factor (-1 to 1)
        """
        
        # Game script scenarios
        scenarios = {
            # Team winning big (blowout)
            ("blowout_win", "PTS", "over"): 0.3,  # Star plays more minutes
            ("blowout_win", "AST", "over"): 0.2,  # More ball movement
            ("blowout_win", "REB", "over"): 0.1,  # More opportunities
            ("blowout_win", "PTS", "under"): -0.3,  # Star sits in 4th
            ("blowout_win", "AST", "under"): -0.2,  # Less ball movement
            ("blowout_win", "REB", "under"): -0.1,  # Less playing time
            
            # Close game
            ("close_game", "PTS", "over"): 0.1,
            ("close_game", "AST", "over"): 0.1,
            ("close_game", "REB", "over"): 0.1,
            ("close_game", "PTS", "under"): -0.1,
            ("close_game", "AST", "under"): -0.1,
            ("close_game", "REB", "under"): -0.1,
        }
        
        # Determine game script
        if team_favorite:
            game_script = "blowout_win" if team_favorite else "close_game"
        else:
            game_script = "close_game"
        
        # Get impact for both stats
        key1 = (game_script, stat1, side1)
        key2 = (game_script, stat2, side2)
        
        impact1 = scenarios.get(key1, 0.0)
        impact2 = scenarios.get(key2, 0.0)
        
        return (impact1 + impact2) / 2
    
    def get_correlation_strength(self, correlation: float) -> str:
        """Categorize correlation strength."""
        abs_corr = abs(correlation)
        
        if abs_corr >= self.correlation_thresholds["strong"]:
            return "strong"
        elif abs_corr >= self.correlation_thresholds["moderate"]:
            return "moderate"
        elif abs_corr >= self.correlation_thresholds["weak"]:
            return "weak"
        else:
            return "neutral"
    
    def generate_correlation_rationale(
        self,
        stat1: str,
        stat2: str,
        correlation: float,
        correlation_type: str,
        player_position: str
    ) -> str:
        """Generate rationale for correlation."""
        
        if correlation_type == "positive":
            if abs(correlation) > 0.6:
                return f"Strong positive correlation between {stat1} and {stat2} for {player_position} - both stats tend to increase together"
            elif abs(correlation) > 0.3:
                return f"Moderate positive correlation between {stat1} and {stat2} for {player_position} - related skill sets"
            else:
                return f"Weak positive correlation between {stat1} and {stat2} for {player_position}"
        elif correlation_type == "negative":
            if abs(correlation) > 0.6:
                return f"Strong negative correlation between {stat1} and {stat2} for {player_position} - inverse relationship"
            elif abs(correlation) > 0.3:
                return f"Moderate negative correlation between {stat1} and {stat2} for {player_position} - trade-off effect"
            else:
                return f"Weak negative correlation between {stat1} and {stat2} for {player_position}"
        else:
            return f"No significant correlation between {stat1} and {stat2} for {player_position}"
    
    async def analyze_same_game_correlations(
        self,
        db: AsyncSession,
        game_id: int
    ) -> Dict[str, Any]:
        """Analyze correlations between all picks in the same game."""
        
        # Get all picks for this game
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market)
        ).where(ModelPick.game_id == game_id)
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if len(picks) < 2:
            return {
                "status": "insufficient_picks",
                "message": f"Only {len(picks)} picks found for game {game_id}",
                "correlations": []
            }
        
        correlations = []
        
        # Analyze all pairs
        for i, pick1 in enumerate(picks):
            for j, pick2 in enumerate(picks[i+1:], i+1):
                
                # Skip same player
                if pick1.player_id == pick2.player_id:
                    continue
                
                # Get player positions (mock data for now)
                position1 = "PG"  # Would get from player data
                position2 = "SG"  # Would get from player data
                
                # Calculate correlation
                stat1 = pick1.market.stat_type if pick1.market else "unknown"
                stat2 = pick2.market.stat_type if pick2.market else "unknown"
                side1 = pick1.side
                side2 = pick2.side
                
                correlation_coeff, correlation_type = self.calculate_stat_correlation(
                    stat1, stat2, position1
                )
                
                # Adjust for game script
                game_script_impact = self.calculate_game_script_correlation(
                    stat1, side1, stat2, side2, True  # Would get from game data
                )
                
                # Final correlation with game script adjustment
                final_correlation = correlation_coeff + game_script_impact
                final_correlation = max(-1.0, min(1.0, final_correlation))
                
                # Determine correlation strength
                correlation_strength = self.get_correlation_strength(final_correlation)
                
                # Generate rationale
                rationale = self.generate_correlation_rationale(
                    stat1, stat2, final_correlation, correlation_type, position1
                )
                
                correlation_data = CorrelationData(
                    pick1_id=pick1.id,
                    pick2_id=pick2.id,
                    correlation_coefficient=final_correlation,
                    correlation_type=correlation_type if final_correlation != 0 else "neutral",
                    correlation_strength=correlation_strength,
                    game_script_impact=game_script_impact,
                    rationale=rationale
                )
                
                correlations.append({
                    "pick1": {
                        "id": pick1.id,
                        "player": pick1.player.name if pick1.player else "Unknown",
                        "stat": stat1,
                        "side": side1,
                        "odds": pick1.odds
                    },
                    "pick2": {
                        "id": pick2.id,
                        "player": pick2.player.name if pick2.player else "Unknown",
                        "stat": stat2,
                        "side": side2,
                        "odds": pick2.odds
                    },
                    "correlation_coefficient": final_correlation,
                    "correlation_type": correlation_data.correlation_type,
                    "correlation_strength": correlation_strength,
                    "game_script_impact": game_script_impact,
                    "rationale": rationale
                })
        
        # Sort by absolute correlation (strongest first)
        correlations.sort(key=lambda x: abs(x["correlation_coefficient"]), reverse=True)
        
        return {
            "status": "success",
            "game_id": game_id,
            "total_picks": len(picks),
            "total_correlations": len(correlations),
            "correlations": correlations,
            "summary": {
                "strong_correlations": len([c for c in correlations if c["correlation_strength"] == "strong"]),
                "moderate_correlations": len([c for c in correlations if c["correlation_strength"] == "moderate"]),
                "weak_correlations": len([c for c in correlations if c["correlation_strength"] == "weak"]),
                "positive_correlations": len([c for c in correlations if c["correlation_type"] == "positive"]),
                "negative_correlations": len([c for c in correlations if c["correlation_type"] == "negative"])
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def calculate_parlay_correlation_adjustment(
        self,
        correlations: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate correlation adjustment for parlay probability.
        
        Args:
            correlations: List of correlation data for parlay legs
        
        Returns:
            Correlation adjustment factor
        """
        
        if not correlations:
            return 1.0
        
        # Calculate average correlation
        avg_correlation = sum(c["correlation_coefficient"] for c in correlations) / len(correlations)
        
        # Adjustment factor (simplified)
        # Positive correlations increase risk (lower adjustment)
        # Negative correlations decrease risk (higher adjustment)
        if avg_correlation > 0.2:
            adjustment = 1.0 - (avg_correlation * 0.3)  # Reduce probability for positive correlation
        elif avg_correlation < -0.2:
            adjustment = 1.0 + (abs(avg_correlation) * 0.2)  # Increase probability for negative correlation
        else:
            adjustment = 1.0  # No adjustment for weak correlation
        
        return max(0.7, min(1.3, adjustment))  # Clamp to reasonable range
