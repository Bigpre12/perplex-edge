"""
Line Movement Tracker - Track sharp money and market movements
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Game, Player, Market

@dataclass
class LineMovementData:
    """Line movement data for a pick."""
    pick_id: int
    opening_odds: float
    current_odds: float
    line_movement: float
    movement_percentage: float
    sharp_indicator: float  # -1 to 1 (negative = sharp under, positive = sharp over)
    steam_move: bool  # Sudden large movement
    reverse_line_movement: bool  # Public vs sharp disagreement
    time_until_game: timedelta
    books_available: int

class LineMovementTracker:
    """Tracks line movements and sharp money indicators."""
    
    def __init__(self):
        self.movement_history = []
        self.sharp_threshold = 0.10  # 10% movement threshold
        self.steam_threshold = 0.15  # 15% for steam moves
        
    def calculate_line_movement(
        self, 
        opening_odds: float, 
        current_odds: float
    ) -> Dict[str, Any]:
        """Calculate line movement metrics."""
        
        # Calculate movement percentage
        if opening_odds != 0:
            movement_percentage = ((current_odds - opening_odds) / abs(opening_odds)) * 100
        else:
            movement_percentage = 0.0
        
        # Determine movement direction
        movement_direction = "none"
        if abs(movement_percentage) > 1.0:  # 1% threshold
            movement_direction = "up" if movement_percentage > 0 else "down"
        
        # Check for steam move (sudden large movement)
        steam_move = abs(movement_percentage) >= (self.steam_threshold * 100)
        
        # Sharp money indicator (simplified)
        sharp_indicator = 0.0
        if movement_percentage > 5:  # Line moving up = sharp under
            sharp_indicator = -min(1.0, movement_percentage / 10)
        elif movement_percentage < -5:  # Line moving down = sharp over
            sharp_indicator = min(1.0, abs(movement_percentage) / 10)
        
        return {
            "opening_odds": opening_odds,
            "current_odds": current_odds,
            "line_movement": current_odds - opening_odds,
            "movement_percentage": movement_percentage,
            "movement_direction": movement_direction,
            "sharp_indicator": sharp_indicator,
            "steam_move": steam_move
        }
    
    def detect_reverse_line_movement(
        self, 
        public_percentage: float, 
        line_movement_direction: str
    ) -> bool:
        """
        Detect reverse line movement (public vs sharp disagreement).
        
        Args:
            public_percentage: Public betting percentage (0-100)
            line_movement_direction: Direction of line movement
        
        Returns:
            True if reverse line movement detected
        """
        # If public is heavy on Over (>60%) but line moves Under
        if public_percentage > 60 and line_movement_direction == "down":
            return True
        
        # If public is heavy on Under (>60%) but line moves Over  
        if public_percentage > 60 and line_movement_direction == "up":
            return True
        
        return False
    
    async def track_line_movements(
        self,
        db: AsyncSession,
        sport_id: int,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """Track line movements for recent picks."""
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        # Get recent picks with odds data
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.market),
            selectinload(ModelPick.game)
        ).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.generated_at >= cutoff_time,
                ModelPick.opening_odds.isnot(None)
            )
        ).order_by(desc(ModelPick.generated_at))
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        movements = []
        sharp_moves = []
        steam_moves = []
        reverse_moves = []
        
        for pick in picks:
            # Calculate line movement
            movement_data = self.calculate_line_movement(
                pick.opening_odds, pick.odds
            )
            
            # Add pick context
            movement_data.update({
                "pick_id": pick.id,
                "player_name": pick.player.name if pick.player else "Unknown",
                "market": pick.market.stat_type if pick.market else "Unknown",
                "line_value": pick.line_value,
                "side": pick.side,
                "generated_at": pick.generated_at.isoformat(),
                "game_time": pick.game.start_time.isoformat() if pick.game else None,
                "time_until_game": (pick.game.start_time - datetime.now(timezone.utc)) if pick.game else None
            })
            
            # Categorize movements
            if movement_data["steam_move"]:
                steam_moves.append(movement_data)
            
            if abs(movement_data["sharp_indicator"]) > 0.5:
                sharp_moves.append(movement_data)
            
            # Mock public percentage for reverse line movement detection
            public_percentage = 55 + (movement_data["movement_percentage"] * 0.5)
            if self.detect_reverse_line_movement(public_percentage, movement_data["movement_direction"]):
                movement_data["reverse_line_movement"] = True
                reverse_moves.append(movement_data)
            
            movements.append(movement_data)
        
        return {
            "total_movements": len(movements),
            "sharp_moves": sharp_moves,
            "steam_moves": steam_moves,
            "reverse_moves": reverse_moves,
            "analysis_period_hours": hours_back,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_line_movement_alerts(
        self,
        db: AsyncSession,
        sport_id: int = 30
    ) -> Dict[str, Any]:
        """Get line movement alerts for sharp money activity."""
        
        # Get recent line movements
        movements_data = await self.track_line_movements(db, sport_id, hours_back=6)
        
        alerts = []
        
        # Steam move alerts
        for steam_move in movements_data["steam_moves"]:
            alerts.append({
                "type": "steam_move",
                "severity": "high",
                "message": f"Steam move detected: {steam_move['player_name']} {steam_move['market']} {steam_move['side']} moved {steam_move['movement_percentage']:.1f}%",
                "data": steam_move
            })
        
        # Sharp money alerts
        for sharp_move in movements_data["sharp_moves"]:
            alerts.append({
                "type": "sharp_money",
                "severity": "medium",
                "message": f"Sharp money on {sharp_move['player_name']} {sharp_move['market']} {sharp_move['side']}",
                "data": sharp_move
            })
        
        # Reverse line movement alerts
        for reverse_move in movements_data["reverse_moves"]:
            alerts.append({
                "type": "reverse_line_movement",
                "severity": "high",
                "message": f"Reverse line movement: {reverse_move['player_name']} {reverse_move['market']}",
                "data": reverse_move
            })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "alert_summary": {
                "steam_moves": len(movements_data["steam_moves"]),
                "sharp_moves": len(movements_data["sharp_moves"]),
                "reverse_moves": len(movements_data["reverse_moves"])
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
