"""
Player Stats Service - Track and analyze player performance statistics
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

class StatType(Enum):
    """Stat type categories"""
    POINTS = "points"
    REBOUNDS = "rebounds"
    ASSISTS = "assists"
    THREE_POINTERS = "three_pointers"
    PASSING_YARDS = "passing_yards"
    PASSING_TOUCHDOWNS = "passing_touchdowns"
    RUSHING_YARDS = "rushing_yards"
    HOME_RUNS = "home_runs"
    RBIS = "rbis"
    HITS = "hits"
    BATTING_AVERAGE = "batting_average"
    STRIKEOUTS = "strikeouts"
    SHOTS = "shots"

class OverUnderResult(Enum):
    """Over/under result categories"""
    OVER = "OVER"
    UNDER = "UNDER"
    PUSH = "PUSH"

@dataclass
class PlayerStat:
    """Player stat data structure"""
    id: int
    player_name: str
    team: str
    opponent: str
    date: datetime.date
    stat_type: str
    actual_value: float
    line: Optional[float]
    result: bool
    created_at: datetime
    updated_at: datetime

class PlayerStatsService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_player_stat(self, player_name: str, team: str, opponent: str, 
                               date: datetime.date, stat_type: str, actual_value: float,
                               line: Optional[float] = None) -> bool:
        """Create a new player stat record"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Calculate result based on line
            result = None
            if line is not None:
                if actual_value > line:
                    result = True  # OVER hit
                elif actual_value < line:
                    result = False  # UNDER hit
                else:
                    result = None  # PUSH
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO player_stats (
                    player_name, team, opponent, date, stat_type, actual_value, line, result,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, player_name, team, opponent, date, stat_type, actual_value, line, result, now, now)
            
            await conn.close()
            logger.info(f"Created player stat: {player_name} {stat_type} {actual_value} vs line {line}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating player stat: {e}")
            return False
    
    async def get_player_stats_by_player(self, player_name: str, days: int = 30) -> List[PlayerStat]:
        """Get player stats for a specific player"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM player_stats 
                WHERE player_name = $1
                AND date >= NOW() - INTERVAL '$1 days'
                ORDER BY date DESC
            """, player_name, days)
            
            await conn.close()
            
            return [
                PlayerStat(
                    id=result['id'],
                    player_name=result['player_name'],
                    team=result['team'],
                    opponent=result['opponent'],
                    date=result['date'],
                    stat_type=result['stat_type'],
                    actual_value=result['actual_value'],
                    line=result['line'],
                    result=result['result'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting player stats by player: {e}")
            return []
    
    async def get_player_stats_by_team(self, team: str, days: int = 30) -> List[PlayerStat]:
        """Get player stats for a specific team"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM player_stats 
                WHERE team = $1
                AND date >= NOW() - INTERVAL '$1 days'
                ORDER BY date DESC
            """, team, days)
            
            await conn.close()
            
            return [
                PlayerStat(
                    id=result['id'],
                    player_name=result['player_name'],
                    team=result['team'],
                    opponent=result['opponent'],
                    date=result['date'],
                    stat_type=result['stat_type'],
                    actual_value=result['actual_value'],
                    line=result['line'],
                    result=result['result'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting player stats by team: {e}")
            return []
    
    async def get_player_stats_by_stat_type(self, stat_type: str, days: int = 30) -> List[PlayerStat]:
        """Get player stats for a specific stat type"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM player_stats 
                WHERE stat_type = $1
                AND date >= NOW() - INTERVAL '$1 days'
                ORDER BY date DESC
            """, stat_type, days)
            
            await conn.close()
            
            return [
                PlayerStat(
                    id=result['id'],
                    player_name=result['player_name'],
                    team=result['team'],
                    opponent=result['opponent'],
                    date=result['date'],
                    stat_type=result['stat_type'],
                    actual_value=result['actual_value'],
                    line=result['line'],
                    result=result['result'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting player stats by stat type: {e}")
            return []
    
    async def get_player_stats_by_date_range(self, start_date: datetime.date, 
                                           end_date: datetime.date) -> List[PlayerStat]:
        """Get player stats for a specific date range"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM player_stats 
                WHERE date >= $1 AND date <= $2
                ORDER BY date DESC
            """, start_date, end_date)
            
            await conn.close()
            
            return [
                PlayerStat(
                    id=result['id'],
                    player_name=result['player_name'],
                    team=result['team'],
                    opponent=result['opponent'],
                    date=result['date'],
                    stat_type=result['stat_type'],
                    actual_value=result['actual_value'],
                    line=result['line'],
                    result=result['result'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting player stats by date range: {e}")
            return []
    
    async def get_player_hit_rates(self, player_name: str, days: int = 30) -> Dict[str, Any]:
        """Get hit rates for a specific player"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall hit rate
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_stats,
                    COUNT(CASE WHEN result = true THEN 1 END) as hits,
                    COUNT(CASE WHEN result = false THEN 1 END) as misses,
                    ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                    AVG(actual_value) as avg_actual_value,
                    AVG(line) as avg_line
                FROM player_stats
                WHERE player_name = $1
                AND date >= NOW() - INTERVAL '$1 days'
            """, player_name, days)
            
            # Hit rate by stat type
            by_stat_type = await conn.fetch("""
                SELECT 
                    stat_type,
                    COUNT(*) as total_stats,
                    COUNT(CASE WHEN result = true THEN 1 END) as hits,
                    COUNT(CASE WHEN result = false THEN 1 END) as misses,
                    ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                    AVG(actual_value) as avg_actual_value,
                    AVG(line) as avg_line
                FROM player_stats
                WHERE player_name = $1
                AND date >= NOW() - INTERVAL '$1 days'
                GROUP BY stat_type
                ORDER BY hit_rate_percentage DESC
            """, player_name, days)
            
            # Over/under performance
            over_under = await conn.fetch("""
                SELECT 
                    CASE 
                        WHEN actual_value > line THEN 'OVER'
                        WHEN actual_value < line THEN 'UNDER'
                        WHEN actual_value = line THEN 'PUSH'
                    END as over_under_result,
                    COUNT(*) as total_stats,
                    COUNT(CASE WHEN result = true THEN 1 END) as hits,
                    COUNT(CASE WHEN result = false THEN 1 END) as misses,
                    ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage
                FROM player_stats
                WHERE player_name = $1
                AND line IS NOT NULL
                AND date >= NOW() - INTERVAL '$1 days'
                GROUP BY over_under_result
                ORDER BY hit_rate_percentage DESC
            """, player_name, days)
            
            await conn.close()
            
            return {
                'player_name': player_name,
                'period_days': days,
                'overall': {
                    'total_stats': overall['total_stats'],
                    'hits': overall['hits'],
                    'misses': overall['misses'],
                    'hit_rate_percentage': overall['hit_rate_percentage'],
                    'avg_actual_value': overall['avg_actual_value'],
                    'avg_line': overall['avg_line']
                },
                'by_stat_type': [
                    {
                        'stat_type': stat['stat_type'],
                        'total_stats': stat['total_stats'],
                        'hits': stat['hits'],
                        'misses': stat['misses'],
                        'hit_rate_percentage': stat['hit_rate_percentage'],
                        'avg_actual_value': stat['avg_actual_value'],
                        'avg_line': stat['avg_line']
                    }
                    for stat in by_stat_type
                ],
                'over_under': [
                    {
                        'over_under_result': result['over_under_result'],
                        'total_stats': result['total_stats'],
                        'hits': result['hits'],
                        'misses': result['misses'],
                        'hit_rate_percentage': result['hit_rate_percentage']
                    }
                    for result in over_under
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting player hit rates: {e}")
            return {}
    
    async def get_player_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get overall player statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_stats,
                    COUNT(DISTINCT player_name) as unique_players,
                    COUNT(DISTINCT team) as unique_teams,
                    COUNT(DISTINCT opponent) as unique_opponents,
                    COUNT(DISTINCT stat_type) as unique_stat_types,
                    COUNT(DISTINCT date) as unique_dates,
                    AVG(actual_value) as avg_actual_value,
                    AVG(line) as avg_line,
                    COUNT(CASE WHEN result = true THEN 1 END) as hits,
                    COUNT(CASE WHEN result = false THEN 1 END) as misses,
                    ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage
                FROM player_stats
                WHERE date >= NOW() - INTERVAL '$1 days'
            """, days)
            
            # Top performers
            top_performers = await conn.fetch("""
                SELECT 
                    player_name,
                    COUNT(*) as total_stats,
                    COUNT(CASE WHEN result = true THEN 1 END) as hits,
                    COUNT(CASE WHEN result = false THEN 1 END) as misses,
                    ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                    AVG(actual_value) as avg_actual_value,
                    AVG(line) as avg_line,
                    COUNT(DISTINCT stat_type) as unique_stat_types
                FROM player_stats
                WHERE date >= NOW() - INTERVAL '$1 days'
                GROUP BY player_name
                HAVING COUNT(*) >= 3
                ORDER BY hit_rate_percentage DESC
                LIMIT 10
            """, days)
            
            # Stat type performance
            stat_type_performance = await conn.fetch("""
                SELECT 
                    stat_type,
                    COUNT(*) as total_stats,
                    COUNT(CASE WHEN result = true THEN 1 END) as hits,
                    COUNT(CASE WHEN result = false THEN 1 END) as misses,
                    ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                    AVG(actual_value) as avg_actual_value,
                    AVG(line) as avg_line,
                    COUNT(DISTINCT player_name) as unique_players
                FROM player_stats
                WHERE date >= NOW() - INTERVAL '$1 days'
                GROUP BY stat_type
                ORDER BY hit_rate_percentage DESC
            """, days)
            
            # Over/under performance
            over_under_performance = await conn.fetch("""
                SELECT 
                    CASE 
                        WHEN actual_value > line THEN 'OVER'
                        WHEN actual_value < line THEN 'UNDER'
                        WHEN actual_value = line THEN 'PUSH'
                    END as over_under_result,
                    COUNT(*) as total_stats,
                    COUNT(CASE WHEN result = true THEN 1 END) as hits,
                    COUNT(CASE WHEN result = false THEN 1 END) as misses,
                    ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage
                FROM player_stats
                WHERE line IS NOT NULL
                AND date >= NOW() - INTERVAL '$1 days'
                GROUP BY over_under_result
                ORDER BY hit_rate_percentage DESC
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'total_stats': overall['total_stats'],
                'unique_players': overall['unique_players'],
                'unique_teams': overall['unique_teams'],
                'unique_opponents': overall['unique_opponents'],
                'unique_stat_types': overall['unique_stat_types'],
                'unique_dates': overall['unique_dates'],
                'avg_actual_value': overall['avg_actual_value'],
                'avg_line': overall['avg_line'],
                'hits': overall['hits'],
                'misses': overall['misses'],
                'hit_rate_percentage': overall['hit_rate_percentage'],
                'top_performers': [
                    {
                        'player_name': player['player_name'],
                        'total_stats': player['total_stats'],
                        'hits': player['hits'],
                        'misses': player['misses'],
                        'hit_rate_percentage': player['hit_rate_percentage'],
                        'avg_actual_value': player['avg_actual_value'],
                        'avg_line': player['avg_line'],
                        'unique_stat_types': player['unique_stat_types']
                    }
                    for player in top_performers
                ],
                'stat_type_performance': [
                    {
                        'stat_type': stat['stat_type'],
                        'total_stats': stat['total_stats'],
                        'hits': stat['hits'],
                        'misses': stat['misses'],
                        'hit_rate_percentage': stat['hit_rate_percentage'],
                        'avg_actual_value': stat['avg_actual_value'],
                        'avg_line': stat['avg_line'],
                        'unique_players': stat['unique_players']
                    }
                    for stat in stat_type_performance
                ],
                'over_under_performance': [
                    {
                        'over_under_result': result['over_under_result'],
                        'total_stats': result['total_stats'],
                        'hits': result['hits'],
                        'misses': result['misses'],
                        'hit_rate_percentage': result['hit_rate_percentage']
                    }
                    for result in over_under_performance
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting player statistics: {e}")
            return {}
    
    async def search_player_stats(self, query: str, days: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """Search player stats by player name, team, or stat type"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            results = await conn.fetch("""
                SELECT * FROM player_stats 
                WHERE (player_name ILIKE $1 OR team ILIKE $1 OR opponent ILIKE $1 OR stat_type ILIKE $1)
                AND date >= NOW() - INTERVAL '$1 days'
                ORDER BY date DESC
                LIMIT $2
            """, search_query, days, limit)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'player_name': result['player_name'],
                    'team': result['team'],
                    'opponent': result['opponent'],
                    'date': result['date'].isoformat(),
                    'stat_type': result['stat_type'],
                    'actual_value': result['actual_value'],
                    'line': result['line'],
                    'result': result['result'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching player stats: {e}")
            return []

# Global instance
player_stats_service = PlayerStatsService()

async def get_player_statistics(days: int = 30):
    """Get player statistics"""
    return await player_stats_service.get_player_statistics(days)

if __name__ == "__main__":
    # Test player stats service
    async def test():
        # Test getting statistics
        stats = await get_player_statistics(30)
        print(f"Player statistics: {stats}")
    
    asyncio.run(test())
