"""
Games Management Service - Track and manage game schedules and metadata
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

class GameStatus(Enum):
    """Game status levels"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINAL = "final"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"
    SUSPENDED = "suspended"

@dataclass
class Game:
    """Game data structure"""
    id: int
    sport_id: int
    external_game_id: str
    home_team_id: int
    away_team_id: int
    start_time: datetime
    status: GameStatus
    created_at: datetime
    updated_at: datetime
    season_id: Optional[int]

class GamesService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_game(self, sport_id: int, external_game_id: str, home_team_id: int, 
                        away_team_id: int, start_time: datetime, season_id: int = None) -> bool:
        """Create a new game record"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO games (
                    sport_id, external_game_id, home_team_id, away_team_id,
                    start_time, status, created_at, updated_at, season_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, sport_id, external_game_id, home_team_id, away_team_id, 
                start_time, GameStatus.SCHEDULED.value, now, now, season_id)
            
            await conn.close()
            logger.info(f"Created game: {external_game_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating game: {e}")
            return False
    
    async def update_game_status(self, game_id: int, status: GameStatus) -> bool:
        """Update game status"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                UPDATE games 
                SET status = $1, updated_at = $2
                WHERE id = $3
            """, status.value, now, game_id)
            
            await conn.close()
            logger.info(f"Updated game {game_id} status to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating game status: {e}")
            return False
    
    async def get_game_by_id(self, game_id: int) -> Optional[Game]:
        """Get game by ID"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetchrow("""
                SELECT * FROM games 
                WHERE id = $1
            """, game_id)
            
            await conn.close()
            
            if result:
                return Game(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    external_game_id=result['external_game_id'],
                    home_team_id=result['home_team_id'],
                    away_team_id=result['away_team_id'],
                    start_time=result['start_time'],
                    status=GameStatus(result['status']),
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    season_id=result['season_id']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting game by ID: {e}")
            return None
    
    async def get_games_by_sport(self, sport_id: int, status: GameStatus = None, 
                             start_date: str = None, end_date: str = None) -> List[Game]:
        """Get games by sport with optional filters"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM games 
                WHERE sport_id = $1
            """
            
            params = [sport_id]
            
            if status:
                query += " AND status = $2"
                params.append(status.value)
            
            if start_date:
                query += " AND DATE(start_time) >= $3"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(start_time) <= $4"
                params.append(end_date)
            
            query += " ORDER BY start_time DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Game(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    external_game_id=result['external_game_id'],
                    home_team_id=result['home_team_id'],
                    away_team_id=result['away_team_id'],
                    start_time=result['start_time'],
                    status=GameStatus(result['status']),
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    season_id=result['season_id']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting games by sport: {e}")
            return []
    
    async def get_games_by_date(self, date: str, sport_id: int = None) -> List[Game]:
        """Get games for a specific date"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM games 
                WHERE DATE(start_time) = $1
            """
            
            params = [date]
            
            if sport_id:
                query += " AND sport_id = $2"
                params.append(sport_id)
            
            query += " ORDER BY start_time ASC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Game(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    external_game_id=result['external_game_id'],
                    home_team_id=result['home_team_id'],
                    away_team_id=result['away_team_id'],
                    start_time=result['start_time'],
                    status=GameStatus(result['status']),
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    season_id=result['season_id']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting games by date: {e}")
            return []
    
    async def get_upcoming_games(self, hours: int = 24, sport_id: int = None) -> List[Game]:
        """Get upcoming games within specified hours"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM games 
                WHERE start_time > NOW() 
                AND start_time <= NOW() + INTERVAL '$1 hours'
            """
            
            params = [hours]
            
            if sport_id:
                query += " AND sport_id = $2"
                params.append(sport_id)
            
            query += " ORDER BY start_time ASC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Game(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    external_game_id=result['external_game_id'],
                    home_team_id=result['home_team_id'],
                    away_team_id=result['away_team_id'],
                    start_time=result['start_time'],
                    status=GameStatus(result['status']),
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    season_id=result['season_id']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting upcoming games: {e}")
            return []
    
    async def get_recent_games(self, hours: int = 24, sport_id: int = None) -> List[Game]:
        """Get recent games within specified hours"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM games 
                WHERE start_time >= NOW() - INTERVAL '$1 hours'
            """
            
            params = [hours]
            
            if sport_id:
                query += " AND sport_id = $2"
                params.append(sport_id)
            
            query += " ORDER BY start_time DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Game(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    external_game_id=result['external_game_id'],
                    home_team_id=result['home_team_id'],
                    away_team_id=result['away_team_id'],
                    start_time=result['start_time'],
                    status=GameStatus(result['status']),
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    season_id=result['season_id']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent games: {e}")
            return []
    
    async def get_games_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get games statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN status = 'final' THEN 1 END) as final_games,
                    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_games,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_games,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_games,
                    COUNT(CASE WHEN status = 'postponed' THEN 1 END) as postponed_games,
                    COUNT(CASE WHEN status = 'suspended' THEN 1 END) as suspended_games
                FROM games 
                WHERE created_at >= NOW() - INTERVAL '$1 days'
            """, days)
            
            # By sport statistics
            by_sport = await conn.fetch("""
                SELECT 
                    sport_id,
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN status = 'final' THEN 1 END) as final_games,
                    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_games,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_games
                FROM games 
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY sport_id
                ORDER BY total_games DESC
            """, days)
            
            # By date statistics
            by_date = await conn.fetch("""
                SELECT 
                    DATE(start_time) as game_date,
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN status = 'final' THEN 1 END) as final_games,
                    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_games
                FROM games 
                WHERE start_time >= NOW() - INTERVAL '$1 days'
                GROUP BY DATE(start_time)
                ORDER BY game_date DESC
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'total_games': overall['total_games'],
                'final_games': overall['final_games'],
                'scheduled_games': overall['scheduled_games'],
                'in_progress_games': overall['in_progress_games'],
                'cancelled_games': overall['cancelled_games'],
                'postponed_games': overall['postponed_games'],
                'suspended_games': overall['suspended_games'],
                'by_sport': [
                    {
                        'sport_id': sport['sport_id'],
                        'total_games': sport['total_games'],
                        'final_games': sport['final_games'],
                        'scheduled_games': sport['scheduled_games'],
                        'in_progress_games': sport['in_progress_games']
                    }
                    for sport in by_sport
                ],
                'by_date': [
                    {
                        'date': str(row['game_date']),
                        'total_games': row['total_games'],
                        'final_games': row['final_games'],
                        'scheduled_games': row['scheduled_games']
                    }
                    for row in by_date
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting games statistics: {e}")
            return {}
    
    async def get_game_schedule(self, start_date: str, end_date: str, sport_id: int = None) -> List[Dict[str, Any]]:
        """Get game schedule for a date range"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT 
                    g.*,
                    ht.name as home_team_name,
                    at.name as away_team_name,
                    s.name as sport_name
                FROM games g
                LEFT JOIN teams ht ON g.home_team_id = ht.id
                LEFT JOIN teams at ON g.away_team_id = at.id
                LEFT JOIN sports s ON g.sport_id = s.id
                WHERE DATE(start_time) >= $1 AND DATE(start_time) <= $2
            """
            
            params = [start_date, end_date]
            
            if sport_id:
                query += " AND g.sport_id = $3"
                params.append(sport_id)
            
            query += " ORDER BY start_time ASC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'sport_id': result['sport_id'],
                    'external_game_id': result['external_game_id'],
                    'home_team_id': result['home_team_id'],
                    'away_team_id': result['away_team_id'],
                    'home_team_name': result['home_team_name'],
                    'away_team_name': result['away_team_name'],
                    'sport_name': result['sport_name'],
                    'start_time': result['start_time'].isoformat(),
                    'status': result['status'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat(),
                    'season_id': result['season_id']
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting game schedule: {e}")
            return []
    
    async def update_game_statuses(self, game_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update multiple game statuses"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            updated_count = 0
            failed_count = 0
            update_results = []
            
            for update in game_updates:
                try:
                    game_id = update.get('game_id')
                    status = update.get('status')
                    
                    if not all([game_id, status]):
                        failed_count += 1
                        update_results.append({
                            'game_id': game_id,
                            'status': 'failed',
                            'error': 'Missing required fields'
                        })
                        continue
                    
                    # Validate status
                    try:
                        game_status = GameStatus(status.lower())
                    except ValueError:
                        failed_count += 1
                        update_results.append({
                            'game_id': game_id,
                            'status': 'failed',
                            'error': f'Invalid status: {status}'
                        })
                        continue
                    
                    # Update the game status
                    await conn.execute("""
                        UPDATE games 
                        SET status = $1, updated_at = NOW()
                        WHERE id = $2
                    """, game_status.value, game_id)
                    
                    updated_count += 1
                    update_results.append({
                        'game_id': game_id,
                        'status': 'updated',
                        'new_status': game_status.value,
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    })
                    
                except Exception as e:
                    failed_count += 1
                    update_results.append({
                        'game_id': update.get('game_id'),
                        'status': 'failed',
                        'error': str(e)
                    })
            
            await conn.close()
            
            return {
                'total_processed': len(game_updates),
                'updated_count': updated_count,
                'failed_count': failed_count,
                'update_results': update_results,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating game statuses: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def search_games(self, query: str, sport_id: int = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search games by external ID or team names"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            sql_query = """
                SELECT 
                    g.*,
                    ht.name as home_team_name,
                    at.name as away_team_name,
                    s.name as sport_name
                FROM games g
                LEFT JOIN teams ht ON g.home_team_id = ht.id
                LEFT JOIN teams at ON g.away_team_id = at.id
                LEFT JOIN sports s ON g.sport_id = s.id
                WHERE g.external_game_id ILIKE $1
                   OR ht.name ILIKE $1
                   OR at.name ILIKE $1
            """
            
            params = [search_query]
            
            if sport_id:
                sql_query += " AND g.sport_id = $2"
                params.append(sport_id)
            
            sql_query += " ORDER BY g.start_time DESC LIMIT $3"
            params.append(limit)
            
            results = await conn.fetch(sql_query, params)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'sport_id': result['sport_id'],
                    'external_game_id': result['external_game_id'],
                    'home_team_id': result['home_team_id'],
                    'away_team_id': result['away_team_id'],
                    'home_team_name': result['home_team_name'],
                    'away_team_name': result['away_team_name'],
                    'sport_name': result['sport_name'],
                    'start_time': result['start_time'].isoformat(),
                    'status': result['status'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat(),
                    'season_id': result['season_id']
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching games: {e}")
            return []

# Global instance
games_service = GamesService()

async def get_game_schedule(start_date: str, end_date: str, sport_id: int = None):
    """Get game schedule for a date range"""
    return await games_service.get_game_schedule(start_date, end_date, sport_id)

async def get_upcoming_games(hours: int = 24, sport_id: int = None):
    """Get upcoming games"""
    return await games_service.get_upcoming_games(hours, sport_id)

if __name__ == "__main__":
    # Test games service
    async def test():
        # Test getting upcoming games
        upcoming = await get_upcoming_games(24)
        print(f"Upcoming games: {len(upcoming)}")
        
        # Test getting game statistics
        stats = await games_service.get_games_statistics()
        print(f"Game statistics: {stats}")
    
    asyncio.run(test())
