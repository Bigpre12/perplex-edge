"""
User Bets Service - Track and analyze user betting activity
"""
import asyncio
import asyncpg
import os
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BetStatus(Enum):
    """Bet status categories"""
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    PUSHED = "pushed"
    CANCELLED = "cancelled"

class BetSide(Enum):
    """Bet side categories"""
    OVER = "over"
    UNDER = "under"

@dataclass
class UserBet:
    """User bet data structure"""
    id: int
    sport_id: int
    game_id: int
    player_id: Optional[int]
    market_type: str
    side: str
    line_value: Optional[float]
    sportsbook: str
    opening_odds: float
    stake: float
    status: str
    actual_value: Optional[float]
    closing_odds: Optional[float]
    closing_line: Optional[float]
    clv_cents: Optional[float]
    profit_loss: Optional[float]
    placed_at: datetime
    settled_at: Optional[datetime]
    notes: Optional[str]
    model_pick_id: Optional[int]
    created_at: datetime
    updated_at: datetime

class UserBetsService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_user_bet(self, sport_id: int, game_id: int, player_id: Optional[int],
                             market_type: str, side: str, line_value: Optional[float],
                             sportsbook: str, opening_odds: float, stake: float,
                             notes: Optional[str] = None, model_pick_id: Optional[int] = None) -> bool:
        """Create a new user bet"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO user_bets (
                    sport_id, game_id, player_id, market_type, side, line_value, sportsbook,
                    opening_odds, stake, status, placed_at, notes, model_pick_id, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'pending', $10, $11, $12, $13, $14)
            """, sport_id, game_id, player_id, market_type, side, line_value, sportsbook,
                opening_odds, stake, now, notes, model_pick_id, now, now)
            
            await conn.close()
            logger.info(f"Created user bet: {market_type} {side} {line_value}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user bet: {e}")
            return False
    
    async def get_user_bets_by_sport(self, sport_id: int) -> List[UserBet]:
        """Get user bets for a specific sport"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM user_bets 
                WHERE sport_id = $1
                ORDER BY placed_at DESC
            """, sport_id)
            
            await conn.close()
            
            return [
                UserBet(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    game_id=result['game_id'],
                    player_id=result['player_id'],
                    market_type=result['market_type'],
                    side=result['side'],
                    line_value=result['line_value'],
                    sportsbook=result['sportsbook'],
                    opening_odds=result['opening_odds'],
                    stake=result['stake'],
                    status=result['status'],
                    actual_value=result['actual_value'],
                    closing_odds=result['closing_odds'],
                    closing_line=result['closing_line'],
                    clv_cents=result['clv_cents'],
                    profit_loss=result['profit_loss'],
                    placed_at=result['placed_at'],
                    settled_at=result['settled_at'],
                    notes=result['notes'],
                    model_pick_id=result['model_pick_id'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting user bets by sport: {e}")
            return []
    
    async def get_user_bets_by_status(self, status: str) -> List[UserBet]:
        """Get user bets by status"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM user_bets 
                WHERE status = $1
                ORDER BY placed_at DESC
            """, status)
            
            await conn.close()
            
            return [
                UserBet(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    game_id=result['game_id'],
                    player_id=result['player_id'],
                    market_type=result['market_type'],
                    side=result['side'],
                    line_value=result['line_value'],
                    sportsbook=result['sportsbook'],
                    opening_odds=result['opening_odds'],
                    stake=result['stake'],
                    status=result['status'],
                    actual_value=result['actual_value'],
                    closing_odds=result['closing_odds'],
                    closing_line=result['closing_line'],
                    clv_cents=result['clv_cents'],
                    profit_loss=result['profit_loss'],
                    placed_at=result['placed_at'],
                    settled_at=result['settled_at'],
                    notes=result['notes'],
                    model_pick_id=result['model_pick_id'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting user bets by status: {e}")
            return []
    
    async def get_user_bets_by_sportsbook(self, sportsbook: str) -> List[UserBet]:
        """Get user bets from a specific sportsbook"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM user_bets 
                WHERE sportsbook = $1
                ORDER BY placed_at DESC
            """, sportsbook)
            
            await conn.close()
            
            return [
                UserBet(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    game_id=result['game_id'],
                    player_id=result['player_id'],
                    market_type=result['market_type'],
                    side=result['side'],
                    line_value=result['line_value'],
                    sportsbook=result['sportsbook'],
                    opening_odds=result['opening_odds'],
                    stake=result['stake'],
                    status=result['status'],
                    actual_value=result['actual_value'],
                    closing_odds=result['closing_odds'],
                    closing_line=result['closing_line'],
                    clv_cents=result['clv_cents'],
                    profit_loss=result['profit_loss'],
                    placed_at=result['placed_at'],
                    settled_at=result['settled_at'],
                    notes=result['notes'],
                    model_pick_id=result['model_pick_id'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting user bets by sportsbook: {e}")
            return []
    
    async def get_user_bets_by_date_range(self, start_date: datetime, end_date: datetime) -> List[UserBet]:
        """Get user bets within a date range"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM user_bets 
                WHERE placed_at >= $1 AND placed_at <= $2
                ORDER BY placed_at DESC
            """, start_date, end_date)
            
            await conn.close()
            
            return [
                UserBet(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    game_id=result['game_id'],
                    player_id=result['player_id'],
                    market_type=result['market_type'],
                    side=result['side'],
                    line_value=result['line_value'],
                    sportsbook=result['sportsbook'],
                    opening_odds=result['opening_odds'],
                    stake=result['stake'],
                    status=result['status'],
                    actual_value=result['actual_value'],
                    closing_odds=result['closing_odds'],
                    closing_line=result['closing_line'],
                    clv_cents=result['clv_cents'],
                    profit_loss=result['profit_loss'],
                    placed_at=result['placed_at'],
                    settled_at=result['settled_at'],
                    notes=result['notes'],
                    model_pick_id=result['model_pick_id'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting user bets by date range: {e}")
            return []
    
    async def get_recent_user_bets(self, days: int = 7) -> List[UserBet]:
        """Get recent user bets"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM user_bets 
                WHERE placed_at >= CURRENT_DATE - INTERVAL '$1 days'
                ORDER BY placed_at DESC
            """, days)
            
            await conn.close()
            
            return [
                UserBet(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    game_id=result['game_id'],
                    player_id=result['player_id'],
                    market_type=result['market_type'],
                    side=result['side'],
                    line_value=result['line_value'],
                    sportsbook=result['sportsbook'],
                    opening_odds=result['opening_odds'],
                    stake=result['stake'],
                    status=result['status'],
                    actual_value=result['actual_value'],
                    closing_odds=result['closing_odds'],
                    closing_line=result['closing_line'],
                    clv_cents=result['clv_cents'],
                    profit_loss=result['profit_loss'],
                    placed_at=result['placed_at'],
                    settled_at=result['settled_at'],
                    notes=result['notes'],
                    model_pick_id=result['model_pick_id'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent user bets: {e}")
            return []
    
    async def settle_user_bet(self, bet_id: int, status: str, actual_value: Optional[float] = None,
                             closing_odds: Optional[float] = None, closing_line: Optional[float] = None,
                             clv_cents: Optional[float] = None, profit_loss: Optional[float] = None) -> bool:
        """Settle a user bet"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            # Calculate profit/loss if not provided
            if profit_loss is None and status in ['won', 'lost']:
                bet = await conn.fetchrow("SELECT opening_odds, stake FROM user_bets WHERE id = $1", bet_id)
                if bet:
                    if status == 'won':
                        if bet['opening_odds'] > 0:
                            profit_loss = (bet['opening_odds'] / 100) * bet['stake']
                        else:
                            profit_loss = (100 / abs(bet['opening_odds'])) * bet['stake']
                    else:
                        profit_loss = -bet['stake']
            
            await conn.execute("""
                UPDATE user_bets 
                SET status = $1, actual_value = $2, closing_odds = $3, closing_line = $4,
                    clv_cents = $5, profit_loss = $6, settled_at = $7, updated_at = $7
                WHERE id = $8
            """, status, actual_value, closing_odds, closing_line, clv_cents, profit_loss, now, bet_id)
            
            await conn.close()
            logger.info(f"Settled user bet {bet_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error settling user bet: {e}")
            return False
    
    async def get_user_bets_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get overall user bets statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_bets,
                    COUNT(DISTINCT sport_id) as unique_sports,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT player_id) as unique_players,
                    COUNT(DISTINCT sportsbook) as unique_sportsbooks,
                    COUNT(DISTINCT market_type) as unique_market_types,
                    COUNT(CASE WHEN status = 'won' THEN 1 END) as won_bets,
                    COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_bets,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bets,
                    SUM(stake) as total_stake,
                    SUM(profit_loss) as total_profit_loss,
                    AVG(stake) as avg_stake,
                    AVG(profit_loss) as avg_profit_loss,
                    ROUND(COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0), 2) as win_rate_percentage,
                    SUM(clv_cents) as total_clv_cents,
                    AVG(clv_cents) as avg_clv_cents
                FROM user_bets
                WHERE placed_at >= CURRENT_DATE - INTERVAL '$1 days'
            """, days)
            
            # Statistics by sport
            sport_stats = await conn.fetch("""
                SELECT 
                    sport_id,
                    COUNT(*) as total_bets,
                    COUNT(CASE WHEN status = 'won' THEN 1 END) as won_bets,
                    COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_bets,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bets,
                    SUM(stake) as total_stake,
                    SUM(profit_loss) as total_profit_loss,
                    ROUND(COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0), 2) as win_rate_percentage,
                    AVG(clv_cents) as avg_clv_cents
                FROM user_bets
                WHERE placed_at >= CURRENT_DATE - INTERVAL '$1 days'
                GROUP BY sport_id
                ORDER BY total_bets DESC
            """, days)
            
            # Statistics by sportsbook
            sportsbook_stats = await conn.fetch("""
                SELECT 
                    sportsbook,
                    COUNT(*) as total_bets,
                    COUNT(CASE WHEN status = 'won' THEN 1 END) as won_bets,
                    COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_bets,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bets,
                    SUM(stake) as total_stake,
                    SUM(profit_loss) as total_profit_loss,
                    ROUND(COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0), 2) as win_rate_percentage,
                    AVG(clv_cents) as avg_clv_cents
                FROM user_bets
                WHERE placed_at >= CURRENT_DATE - INTERVAL '$1 days'
                GROUP BY sportsbook
                ORDER BY total_bets DESC
            """, days)
            
            # Statistics by market type
            market_stats = await conn.fetch("""
                SELECT 
                    market_type,
                    COUNT(*) as total_bets,
                    COUNT(CASE WHEN status = 'won' THEN 1 END) as won_bets,
                    COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_bets,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bets,
                    SUM(stake) as total_stake,
                    SUM(profit_loss) as total_profit_loss,
                    ROUND(COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0), 2) as win_rate_percentage,
                    AVG(clv_cents) as avg_clv_cents
                FROM user_bets
                WHERE placed_at >= CURRENT_DATE - INTERVAL '$1 days'
                GROUP BY market_type
                ORDER BY total_bets DESC
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'total_bets': overall['total_bets'],
                'unique_sports': overall['unique_sports'],
                'unique_games': overall['unique_games'],
                'unique_players': overall['unique_players'],
                'unique_sportsbooks': overall['unique_sportsbooks'],
                'unique_market_types': overall['unique_market_types'],
                'won_bets': overall['won_bets'],
                'lost_bets': overall['lost_bets'],
                'pending_bets': overall['pending_bets'],
                'total_stake': overall['total_stake'],
                'total_profit_loss': overall['total_profit_loss'],
                'avg_stake': overall['avg_stake'],
                'avg_profit_loss': overall['avg_profit_loss'],
                'win_rate_percentage': overall['win_rate_percentage'],
                'total_clv_cents': overall['total_clv_cents'],
                'avg_clv_cents': overall['avg_clv_cents'],
                'sport_stats': [
                    {
                        'sport_id': stat['sport_id'],
                        'total_bets': stat['total_bets'],
                        'won_bets': stat['won_bets'],
                        'lost_bets': stat['lost_bets'],
                        'pending_bets': stat['pending_bets'],
                        'total_stake': stat['total_stake'],
                        'total_profit_loss': stat['total_profit_loss'],
                        'win_rate_percentage': stat['win_rate_percentage'],
                        'avg_clv_cents': stat['avg_clv_cents']
                    }
                    for stat in sport_stats
                ],
                'sportsbook_stats': [
                    {
                        'sportsbook': stat['sportsbook'],
                        'total_bets': stat['total_bets'],
                        'won_bets': stat['won_bets'],
                        'lost_bets': stat['lost_bets'],
                        'pending_bets': stat['pending_bets'],
                        'total_stake': stat['total_stake'],
                        'total_profit_loss': stat['total_profit_loss'],
                        'win_rate_percentage': stat['win_rate_percentage'],
                        'avg_clv_cents': stat['avg_clv_cents']
                    }
                    for stat in sportsbook_stats
                ],
                'market_stats': [
                    {
                        'market_type': stat['market_type'],
                        'total_bets': stat['total_bets'],
                        'won_bets': stat['won_bets'],
                        'lost_bets': stat['lost_bets'],
                        'pending_bets': stat['pending_bets'],
                        'total_stake': stat['total_stake'],
                        'total_profit_loss': stat['total_profit_loss'],
                        'win_rate_percentage': stat['win_rate_percentage'],
                        'avg_clv_cents': stat['avg_clv_cents']
                    }
                    for stat in market_stats
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user bets statistics: {e}")
            return {}
    
    async def search_user_bets(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search user bets by player, market, or notes"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            results = await conn.fetch("""
                SELECT * FROM user_bets 
                WHERE notes ILIKE $1 OR market_type ILIKE $1 OR side ILIKE $1
                ORDER BY placed_at DESC
                LIMIT $2
            """, search_query, limit)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'sport_id': result['sport_id'],
                    'game_id': result['game_id'],
                    'player_id': result['player_id'],
                    'market_type': result['market_type'],
                    'side': result['side'],
                    'line_value': result['line_value'],
                    'sportsbook': result['sportsbook'],
                    'opening_odds': result['opening_odds'],
                    'stake': result['stake'],
                    'status': result['status'],
                    'actual_value': result['actual_value'],
                    'closing_odds': result['closing_odds'],
                    'closing_line': result['closing_line'],
                    'clv_cents': result['clv_cents'],
                    'profit_loss': result['profit_loss'],
                    'placed_at': result['placed_at'].isoformat(),
                    'settled_at': result['settled_at'].isoformat() if result['settled_at'] else None,
                    'notes': result['notes'],
                    'model_pick_id': result['model_pick_id'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching user bets: {e}")
            return []

# Global instance
user_bets_service = UserBetsService()

async def get_user_bets_statistics(days: int = 30):
    """Get user bets statistics"""
    return await user_bets_service.get_user_bets_statistics(days)

if __name__ == "__main__":
    # Test user bets service
    async def test():
        # Test getting statistics
        stats = await get_user_bets_statistics(30)
        print(f"User bets statistics: {stats}")
    
    asyncio.run(test())
