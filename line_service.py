"""
Line Tracking Service - Track and analyze betting lines and odds
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

class LineSide(Enum):
    """Line side types"""
    OVER = "over"
    UNDER = "under"

class Sportsbook(Enum):
    """Sportsbook types"""
    DRAFTKINGS = "draftkings"
    FANDUEL = "fanduel"
    BETMGM = "betmgm"
    CAESARS = "caesars"
    POINTSBET = "pointsbet"
    BET365 = "bet365"

@dataclass
class Line:
    """Line data structure"""
    id: int
    game_id: int
    market_id: int
    player_id: Optional[int]
    sportsbook: str
    line_value: float
    odds: int
    side: LineSide
    is_current: bool
    fetched_at: datetime

class LineService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_line(self, game_id: int, market_id: int, player_id: int, sportsbook: str,
                        line_value: float, odds: int, side: LineSide, is_current: bool = True) -> bool:
        """Create a new line record"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO lines (
                    game_id, market_id, player_id, sportsbook, line_value, odds, side,
                    is_current, fetched_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, game_id, market_id, player_id, sportsbook, line_value, odds, side.value,
                is_current, now)
            
            await conn.close()
            logger.info(f"Created line: Game {game_id}, Market {market_id}, {sportsbook} {line_value} {side.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating line: {e}")
            return False
    
    async def get_lines_by_game(self, game_id: int, is_current: bool = None) -> List[Line]:
        """Get lines for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM lines 
                WHERE game_id = $1
            """
            
            params = [game_id]
            
            if is_current is not None:
                query += " AND is_current = $2"
                params.append(is_current)
            
            query += " ORDER BY fetched_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Line(
                    id=result['id'],
                    game_id=result['game_id'],
                    market_id=result['market_id'],
                    player_id=result['player_id'],
                    sportsbook=result['sportsbook'],
                    line_value=result['line_value'],
                    odds=result['odds'],
                    side=LineSide(result['side']),
                    is_current=result['is_current'],
                    fetched_at=result['fetched_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting lines by game: {e}")
            return []
    
    async def get_lines_by_player(self, player_id: int, is_current: bool = None) -> List[Line]:
        """Get lines for a specific player"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM lines 
                WHERE player_id = $1
            """
            
            params = [player_id]
            
            if is_current is not None:
                query += " AND is_current = $2"
                params.append(is_current)
            
            query += " ORDER BY fetched_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Line(
                    id=result['id'],
                    game_id=result['game_id'],
                    market_id=result['market_id'],
                    player_id=result['player_id'],
                    sportsbook=result['sportsbook'],
                    line_value=result['line_value'],
                    odds=result['odds'],
                    side=LineSide(result['side']),
                    is_current=result['is_current'],
                    fetched_at=result['fetched_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting lines by player: {e}")
            return []
    
    async def get_lines_by_sportsbook(self, sportsbook: str, is_current: bool = None) -> List[Line]:
        """Get lines from a specific sportsbook"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM lines 
                WHERE sportsbook = $1
            """
            
            params = [sportsbook]
            
            if is_current is not None:
                query += " AND is_current = $2"
                params.append(is_current)
            
            query += " ORDER BY fetched_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Line(
                    id=result['id'],
                    game_id=result['game_id'],
                    market_id=result['market_id'],
                    player_id=result['player_id'],
                    sportsbook=result['sportsbook'],
                    line_value=result['line_value'],
                    odds=result['odds'],
                    side=LineSide(result['side']),
                    is_current=result['is_current'],
                    fetched_at=result['fetched_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting lines by sportsbook: {e}")
            return []
    
    async def get_current_lines(self, game_id: int = None, player_id: int = None) -> List[Line]:
        """Get current lines"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM lines 
                WHERE is_current = TRUE
            """
            
            params = []
            
            if game_id:
                query += " AND game_id = $1"
                params.append(game_id)
            
            if player_id:
                query += " AND player_id = $2"
                params.append(player_id)
            
            query += " ORDER BY fetched_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Line(
                    id=result['id'],
                    game_id=result['game_id'],
                    market_id=result['market_id'],
                    player_id=result['player_id'],
                    sportsbook=result['sportsbook'],
                    line_value=result['line_value'],
                    odds=result['odds'],
                    side=LineSide(result['side']),
                    is_current=result['is_current'],
                    fetched_at=result['fetched_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting current lines: {e}")
            return []
    
    async def get_line_movements(self, game_id: int, player_id: int, market_id: int = None) -> List[Dict[str, Any]]:
        """Get line movements for a specific game/player/market"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT 
                    sportsbook,
                    line_value,
                    odds,
                    side,
                    fetched_at,
                    LAG(line_value) OVER (PARTITION BY sportsbook ORDER BY fetched_at) as prev_line_value,
                    LAG(odds) OVER (PARTITION BY sportsbook ORDER BY fetched_at) as prev_odds
                FROM lines 
                WHERE game_id = $1 AND player_id = $2
            """
            
            params = [game_id, player_id]
            
            if market_id:
                query += " AND market_id = $3"
                params.append(market_id)
            
            query += " ORDER BY sportsbook, fetched_at ASC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            movements = []
            for result in results:
                line_movement = result['line_value'] - result['prev_line_value'] if result['prev_line_value'] else 0
                odds_movement = result['odds'] - result['prev_odds'] if result['prev_odds'] else 0
                
                movements.append({
                    'sportsbook': result['sportsbook'],
                    'line_value': result['line_value'],
                    'odds': result['odds'],
                    'side': result['side'],
                    'fetched_at': result['fetched_at'].isoformat(),
                    'line_movement': line_movement,
                    'odds_movement': odds_movement,
                    'prev_line_value': result['prev_line_value'],
                    'prev_odds': result['prev_odds']
                })
            
            return movements
            
        except Exception as e:
            logger.error(f"Error getting line movements: {e}")
            return []
    
    async def get_sportsbook_comparison(self, game_id: int, player_id: int, market_id: int = None) -> List[Dict[str, Any]]:
        """Compare lines across sportsbooks"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT 
                    sportsbook,
                    line_value,
                    odds,
                    side,
                    fetched_at
                FROM lines 
                WHERE game_id = $1 AND player_id = $2 AND is_current = TRUE
            """
            
            params = [game_id, player_id]
            
            if market_id:
                query += " AND market_id = $3"
                params.append(market_id)
            
            query += " ORDER BY sportsbook"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                {
                    'sportsbook': result['sportsbook'],
                    'line_value': result['line_value'],
                    'odds': result['odds'],
                    'side': result['side'],
                    'fetched_at': result['fetched_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting sportsbook comparison: {e}")
            return []
    
    async def get_line_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get line statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_lines,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT market_id) as unique_markets,
                    COUNT(DISTINCT player_id) as unique_players,
                    COUNT(DISTINCT sportsbook) as unique_sportsbooks,
                    COUNT(CASE WHEN is_current = TRUE THEN 1 END) as current_lines,
                    COUNT(CASE WHEN is_current = FALSE THEN 1 END) as historical_lines,
                    AVG(line_value) as avg_line_value,
                    AVG(odds) as avg_odds,
                    COUNT(CASE WHEN side = 'over' THEN 1 END) as over_lines,
                    COUNT(CASE WHEN side = 'under' THEN 1 END) as under_lines
                FROM lines 
                WHERE fetched_at >= NOW() - INTERVAL '$1 hours'
            """, hours)
            
            # By sportsbook statistics
            by_sportsbook = await conn.fetch("""
                SELECT 
                    sportsbook,
                    COUNT(*) as total_lines,
                    COUNT(CASE WHEN is_current = TRUE THEN 1 END) as current_lines,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT player_id) as unique_players,
                    AVG(line_value) as avg_line_value,
                    AVG(odds) as avg_odds,
                    COUNT(CASE WHEN side = 'over' THEN 1 END) as over_lines,
                    COUNT(CASE WHEN side = 'under' THEN 1 END) as under_lines
                FROM lines 
                WHERE fetched_at >= NOW() - INTERVAL '$1 hours'
                GROUP BY sportsbook
                ORDER BY total_lines DESC
            """, hours)
            
            # By side statistics
            by_side = await conn.fetch("""
                SELECT 
                    side,
                    COUNT(*) as total_lines,
                    AVG(line_value) as avg_line_value,
                    AVG(odds) as avg_odds,
                    COUNT(DISTINCT sportsbook) as unique_sportsbooks,
                    COUNT(DISTINCT player_id) as unique_players
                FROM lines 
                WHERE fetched_at >= NOW() - INTERVAL '$1 hours'
                GROUP BY side
                ORDER BY total_lines DESC
            """, hours)
            
            await conn.close()
            
            return {
                'period_hours': hours,
                'total_lines': overall['total_lines'],
                'unique_games': overall['unique_games'],
                'unique_markets': overall['unique_markets'],
                'unique_players': overall['unique_players'],
                'unique_sportsbooks': overall['unique_sportsbooks'],
                'current_lines': overall['current_lines'],
                'historical_lines': overall['historical_lines'],
                'avg_line_value': overall['avg_line_value'],
                'avg_odds': overall['avg_odds'],
                'over_lines': overall['over_lines'],
                'under_lines': overall['under_lines'],
                'by_sportsbook': [
                    {
                        'sportsbook': sportsbook['sportsbook'],
                        'total_lines': sportsbook['total_lines'],
                        'current_lines': sportsbook['current_lines'],
                        'unique_games': sportsbook['unique_games'],
                        'unique_players': sportsbook['unique_players'],
                        'avg_line_value': sportsbook['avg_line_value'],
                        'avg_odds': sportsbook['avg_odds'],
                        'over_lines': sportsbook['over_lines'],
                        'under_lines': sportsbook['under_lines']
                    }
                    for sportsbook in by_sportsbook
                ],
                'by_side': [
                    {
                        'side': side['side'],
                        'total_lines': side['total_lines'],
                        'avg_line_value': side['avg_line_value'],
                        'avg_odds': side['avg_odds'],
                        'unique_sportsbooks': side['unique_sportsbooks'],
                        'unique_players': side['unique_players']
                    }
                    for side in by_side
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting line statistics: {e}")
            return {}
    
    async def analyze_line_efficiency(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze line efficiency and market efficiency"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get line movements and calculate efficiency metrics
            efficiency = await conn.fetch("""
                SELECT 
                    sportsbook,
                    COUNT(*) as total_lines,
                    COUNT(CASE WHEN 
                        ABS(line_value - LAG(line_value) OVER (PARTITION BY sportsbook ORDER BY fetched_at)) > 0.5 
                        THEN 1 END
                    ) as significant_movements,
                    AVG(
                        ABS(line_value - LAG(line_value) OVER (PARTITION BY sportsbook ORDER BY fetched_at))
                    ) as avg_movement,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT player_id) as unique_players
                FROM lines 
                WHERE fetched_at >= NOW() - INTERVAL '$1 hours'
                AND LAG(line_value) OVER (PARTITION BY sportsbook ORDER BY fetched_at) IS NOT NULL
                GROUP BY sportsbook
                ORDER BY total_lines DESC
            """, hours)
            
            await conn.close()
            
            analysis = []
            for sportsbook in efficiency:
                movement_rate = (sportsbook['significant_movements'] / sportsbook['total_lines'] * 100) if sportsbook['total_lines'] > 0 else 0
                
                analysis.append({
                    'sportsbook': sportsbook['sportsbook'],
                    'total_lines': sportsbook['total_lines'],
                    'significant_movements': sportsbook['significant_movements'],
                    'movement_rate': movement_rate,
                    'avg_movement': sportsbook['avg_movement'],
                    'unique_games': sportsbook['unique_games'],
                    'unique_players': sportsbook['unique_players'],
                    'efficiency_score': 100 - movement_rate if movement_rate < 50 else 50
                })
            
            return {
                'period_hours': hours,
                'sportsbook_efficiency': analysis,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing line efficiency: {e}")
            return {}
    
    async def search_lines(self, query: str, sportsbook: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search lines by player ID or sportsbook"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            sql_query = """
                SELECT * FROM lines 
                WHERE player_id::text ILIKE $1
            """
            
            params = [search_query]
            
            if sportsbook:
                sql_query += " AND sportsbook = $2"
                params.append(sportsbook)
            
            sql_query += " ORDER BY fetched_at DESC LIMIT $3"
            params.append(limit)
            
            results = await conn.fetch(sql_query, params)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'game_id': result['game_id'],
                    'market_id': result['market_id'],
                    'player_id': result['player_id'],
                    'sportsbook': result['sportsbook'],
                    'line_value': result['line_value'],
                    'odds': result['odds'],
                    'side': result['side'],
                    'is_current': result['is_current'],
                    'fetched_at': result['fetched_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching lines: {e}")
            return []

# Global instance
line_service = LineService()

async def get_line_statistics(hours: int = 24):
    """Get line statistics"""
    return await line_service.get_line_statistics(hours)

if __name__ == "__main__":
    # Test line service
    async def test():
        # Test getting statistics
        stats = await get_line_statistics(24)
        print(f"Line statistics: {stats}")
    
    asyncio.run(test())
