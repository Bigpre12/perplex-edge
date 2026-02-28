# backend/services/brain_exposure_risk.py
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from services.user_bets_service import user_bets_service

logger = logging.getLogger(__name__)

class ExposureRisk:
    def __init__(self):
        # Risk limits (percentage of bankroll)
        self.MAX_TOTAL_EXPOSURE = 0.25  # 25% total bankroll at risk
        self.MAX_SINGLE_GAME_EXPOSURE = 0.10  # 10% max on one game
        self.MAX_PLAYER_EXPOSURE = 0.05  # 5% max on one player

    async def get_current_exposure(self) -> Dict[str, Any]:
        """
        Scans pending bets and calculates current exposure and liability.
        """
        pending_bets = await user_bets_service.get_user_bets_by_status("pending")
        
        total_stake = 0.0
        by_game = {}
        by_player = {}
        
        for bet in pending_bets:
            stake = bet.stake
            total_stake += stake
            
            # Game exposure
            game_id = bet.game_id
            by_game[game_id] = by_game.get(game_id, 0.0) + stake
            
            # Player exposure
            if bet.player_id:
                p_id = bet.player_id
                by_player[p_id] = by_player.get(p_id, 0.0) + stake
                
        return {
            "total_at_risk": total_stake,
            "exposure_by_game": by_game,
            "exposure_by_player": by_player,
            "num_pending_bets": len(pending_bets)
        }

    async def calculate_risk_adjusted_kelly(self, proposed_bet: Dict[str, Any], base_kelly: float, current_bankroll: float) -> float:
        """
        Adjusts the proposed Kelly sizing based on existing exposure and correlations.
        """
        exposure = await self.get_current_exposure()
        
        # 1. Total Bankroll Limit
        current_total_pct = exposure["total_at_risk"] / current_bankroll if current_bankroll > 0 else 0
        if current_total_pct > self.MAX_TOTAL_EXPOSURE:
            logger.warning("Total exposure limit reached. Reducing Kelly.")
            return base_kelly * 0.5 # Aggressive reduction
            
        # 2. Single Game Correlation
        game_id = proposed_bet.get("game_id")
        game_exposure = exposure["exposure_by_game"].get(game_id, 0.0)
        game_pct = game_exposure / current_bankroll if current_bankroll > 0 else 0
        
        if game_pct > self.MAX_SINGLE_GAME_EXPOSURE:
            logger.warning(f"Single game exposure high for {game_id}. Capping Kelly.")
            return min(base_kelly, 0.01) # Cap at 1% for new additions to this game
            
        # 3. Player Correlation
        player_id = proposed_bet.get("player_id")
        if player_id:
            player_exposure = exposure["exposure_by_player"].get(player_id, 0.0)
            player_pct = player_exposure / current_bankroll if current_bankroll > 0 else 0
            
            if player_pct > self.MAX_PLAYER_EXPOSURE:
                logger.warning(f"Player exposure high for {player_id}. Reducing Kelly.")
                return base_kelly * 0.25
                
        return base_kelly

exposure_risk = ExposureRisk()
