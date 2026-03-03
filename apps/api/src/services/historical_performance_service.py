"""
Historical Performance Service - Track and analyze player and system performance
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
    PASSING_YARDS = "passing_yards"
    PASSING_TOUCHDOWNS = "passing_touchdowns"
    RUSHING_YARDS = "rushing_yards"
    RECEIVING_YARDS = "receiving_yards"
    POINTS = "points"
    REBOUNDS = "rebounds"
    ASSISTS = "assists"
    THREE_POINTERS = "three_pointers"
    FIELD_GOAL_PERCENTAGE = "field_goal_percentage"
    HOME_RUNS = "home_runs"
    BATTING_AVERAGE = "batting_average"
    STRIKEOUTS = "strikeouts"
    OVERALL_PREDICTIONS = "overall_predictions"
    NFL_PREDICTIONS = "nfl_predictions"
    NBA_PREDICTIONS = "nba_predictions"
    MLB_PREDICTIONS = "mlb_predictions"

@dataclass
class HistoricalPerformance:
    """Historical performance data structure"""
    id: int
    player_name: str
    stat_type: str
    total_picks: int
    hits: int
    misses: int
    hit_rate_percentage: float
    avg_ev: float
    created_at: datetime
    updated_at: datetime

class HistoricalPerformanceService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_performance_record(self, player_name: str, stat_type: str, total_picks: int,
                                     hits: int, misses: int, avg_ev: float) -> bool:
        """Create a new performance record"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            hit_rate = (hits / total_picks * 100) if total_picks > 0 else 0
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO historical_performances (
                    player_name, stat_type, total_picks, hits, misses, hit_rate_percentage,
                    avg_ev, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, player_name, stat_type, total_picks, hits, misses, hit_rate, avg_ev, now, now)
            
            await conn.close()
            logger.info(f"Created performance record: {player_name} - {stat_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating performance record: {e}")
            return False
    
    async def update_performance_record(self, performance_id: int, total_picks: int,
                                      hits: int, misses: int, avg_ev: float) -> bool:
        """Update an existing performance record"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            hit_rate = (hits / total_picks * 100) if total_picks > 0 else 0
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                UPDATE historical_performances 
                SET total_picks = $1, hits = $2, misses = $3, hit_rate_percentage = $4,
                    avg_ev = $5, updated_at = $6
                WHERE id = $7
            """, total_picks, hits, misses, hit_rate, avg_ev, now, performance_id)
            
            await conn.close()
            logger.info(f"Updated performance record {performance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating performance record: {e}")
            return False
    
    async def get_performance_by_player(self, player_name: str, stat_type: str = None) -> List[HistoricalPerformance]:
        """Get performance records for a specific player"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            if stat_type:
                results = await conn.fetch("""
                    SELECT * FROM historical_performances 
                    WHERE player_name = $1 AND stat_type = $2
                    ORDER BY updated_at DESC
                """, player_name, stat_type)
            else:
                results = await conn.fetch("""
                    SELECT * FROM historical_performances 
                    WHERE player_name = $1
                    ORDER BY updated_at DESC
                """, player_name)
            
            await conn.close()
            
            return [
                HistoricalPerformance(
                    id=result['id'],
                    player_name=result['player_name'],
                    stat_type=result['stat_type'],
                    total_picks=result['total_picks'],
                    hits=result['hits'],
                    misses=result['misses'],
                    hit_rate_percentage=result['hit_rate_percentage'],
                    avg_ev=result['avg_ev'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting performance by player: {e}")
            return []
    
    async def get_performance_by_stat_type(self, stat_type: str) -> List[HistoricalPerformance]:
        """Get performance records for a specific stat type"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM historical_performances 
                WHERE stat_type = $1
                ORDER BY hit_rate_percentage DESC
            """, stat_type)
            
            await conn.close()
            
            return [
                HistoricalPerformance(
                    id=result['id'],
                    player_name=result['player_name'],
                    stat_type=result['stat_type'],
                    total_picks=result['total_picks'],
                    hits=result['hits'],
                    misses=result['misses'],
                    hit_rate_percentage=result['hit_rate_percentage'],
                    avg_ev=result['avg_ev'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting performance by stat type: {e}")
            return []
    
    async def get_top_performers(self, limit: int = 10, stat_type: str = None) -> List[Dict[str, Any]]:
        """Get top performers by hit rate"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            if stat_type:
                results = await conn.fetch("""
                    SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks, hits, misses
                    FROM historical_performances 
                    WHERE stat_type = $1
                    ORDER BY hit_rate_percentage DESC
                    LIMIT $2
                """, stat_type, limit)
            else:
                results = await conn.fetch("""
                    SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks, hits, misses
                    FROM historical_performances 
                    ORDER BY hit_rate_percentage DESC
                    LIMIT $1
                """, limit)
            
            await conn.close()
            
            return [
                {
                    'player_name': result['player_name'],
                    'stat_type': result['stat_type'],
                    'hit_rate_percentage': result['hit_rate_percentage'],
                    'avg_ev': result['avg_ev'],
                    'total_picks': result['total_picks'],
                    'hits': result['hits'],
                    'misses': result['misses']
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting top performers: {e}")
            return []
    
    async def get_best_ev_performers(self, limit: int = 10, stat_type: str = None) -> List[Dict[str, Any]]:
        """Get best performers by expected value"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            if stat_type:
                results = await conn.fetch("""
                    SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks, hits, misses
                    FROM historical_performances 
                    WHERE stat_type = $1
                    ORDER BY avg_ev DESC
                    LIMIT $2
                """, stat_type, limit)
            else:
                results = await conn.fetch("""
                    SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks, hits, misses
                    FROM historical_performances 
                    ORDER BY avg_ev DESC
                    LIMIT $1
                """, limit)
            
            await conn.close()
            
            return [
                {
                    'player_name': result['player_name'],
                    'stat_type': result['stat_type'],
                    'hit_rate_percentage': result['hit_rate_percentage'],
                    'avg_ev': result['avg_ev'],
                    'total_picks': result['total_picks'],
                    'hits': result['hits'],
                    'misses': result['misses']
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting best EV performers: {e}")
            return []
    
    async def get_worst_performers(self, limit: int = 10, stat_type: str = None) -> List[Dict[str, Any]]:
        """Get worst performers by hit rate"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            if stat_type:
                results = await conn.fetch("""
                    SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks, hits, misses
                    FROM historical_performances 
                    WHERE stat_type = $1
                    ORDER BY hit_rate_percentage ASC
                    LIMIT $2
                """, stat_type, limit)
            else:
                results = await conn.fetch("""
                    SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks, hits, misses
                    FROM historical_performances 
                    ORDER BY hit_rate_percentage ASC
                    LIMIT $1
                """, limit)
            
            await conn.close()
            
            return [
                {
                    'player_name': result['player_name'],
                    'stat_type': result['stat_type'],
                    'hit_rate_percentage': result['hit_rate_percentage'],
                    'avg_ev': result['avg_ev'],
                    'total_picks': result['total_picks'],
                    'hits': result['hits'],
                    'misses': result['misses']
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting worst performers: {e}")
            return []
    
    async def get_performance_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get overall performance statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_performances,
                    COUNT(DISTINCT player_name) as unique_players,
                    COUNT(DISTINCT stat_type) as unique_stat_types,
                    AVG(hit_rate_percentage) as avg_hit_rate,
                    AVG(avg_ev) as avg_ev,
                    SUM(total_picks) as total_picks_all,
                    SUM(hits) as total_hits_all,
                    SUM(misses) as total_misses_all
                FROM historical_performances
                WHERE created_at >= NOW() - INTERVAL '$1 days'
            """, days)
            
            # By stat type statistics
            by_stat_type = await conn.fetch("""
                SELECT 
                    stat_type,
                    COUNT(*) as total_performances,
                    AVG(hit_rate_percentage) as avg_hit_rate,
                    AVG(avg_ev) as avg_ev,
                    SUM(total_picks) as total_picks,
                    SUM(hits) as total_hits,
                    COUNT(DISTINCT player_name) as unique_players
                FROM historical_performances
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY stat_type
                ORDER BY avg_hit_rate DESC
            """, days)
            
            # By player statistics
            by_player = await conn.fetch("""
                SELECT 
                    player_name,
                    COUNT(*) as total_performances,
                    AVG(hit_rate_percentage) as avg_hit_rate,
                    AVG(avg_ev) as avg_ev,
                    SUM(total_picks) as total_picks,
                    SUM(hits) as total_hits,
                    COUNT(DISTINCT stat_type) as unique_stat_types
                FROM historical_performances
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY player_name
                ORDER BY avg_hit_rate DESC
                LIMIT 20
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'total_performances': overall['total_performances'],
                'unique_players': overall['unique_players'],
                'unique_stat_types': overall['unique_stat_types'],
                'avg_hit_rate': overall['avg_hit_rate'],
                'avg_ev': overall['avg_ev'],
                'total_picks_all': overall['total_picks_all'],
                'total_hits_all': overall['total_hits_all'],
                'total_misses_all': overall['total_misses_all'],
                'by_stat_type': [
                    {
                        'stat_type': stat['stat_type'],
                        'total_performances': stat['total_performances'],
                        'avg_hit_rate': stat['avg_hit_rate'],
                        'avg_ev': stat['avg_ev'],
                        'total_picks': stat['total_picks'],
                        'total_hits': stat['total_hits'],
                        'unique_players': stat['unique_players']
                    }
                    for stat in by_stat_type
                ],
                'by_player': [
                    {
                        'player_name': player['player_name'],
                        'total_performances': player['total_performances'],
                        'avg_hit_rate': player['avg_hit_rate'],
                        'avg_ev': player['avg_ev'],
                        'total_picks': player['total_picks'],
                        'total_hits': player['total_hits'],
                        'unique_stat_types': player['unique_stat_types']
                    }
                    for player in by_player
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance statistics: {e}")
            return {}
    
    async def analyze_performance_trends(self, player_name: str, stat_type: str) -> Dict[str, Any]:
        """Analyze performance trends for a specific player and stat type"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT hit_rate_percentage, avg_ev, total_picks, hits, misses, updated_at
                FROM historical_performances 
                WHERE player_name = $1 AND stat_type = $2
                ORDER BY updated_at ASC
            """, player_name, stat_type)
            
            await conn.close()
            
            if not results:
                return {
                    'player_name': player_name,
                    'stat_type': stat_type,
                    'trend_data': [],
                    'trend_analysis': 'No data available',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            trend_data = []
            for result in results:
                trend_data.append({
                    'hit_rate_percentage': result['hit_rate_percentage'],
                    'avg_ev': result['avg_ev'],
                    'total_picks': result['total_picks'],
                    'hits': result['hits'],
                    'misses': result['misses'],
                    'updated_at': result['updated_at'].isoformat()
                })
            
            # Calculate trend analysis
            if len(trend_data) >= 2:
                first_hit_rate = trend_data[0]['hit_rate_percentage']
                last_hit_rate = trend_data[-1]['hit_rate_percentage']
                hit_rate_trend = last_hit_rate - first_hit_rate
                
                first_ev = trend_data[0]['avg_ev']
                last_ev = trend_data[-1']['avg_ev']
                ev_trend = last_ev - first_ev
                
                if hit_rate_trend > 5:
                    hit_rate_analysis = "Improving"
                elif hit_rate_trend < -5:
                    hit_rate_analysis = "Declining"
                else:
                    hit_rate_analysis = "Stable"
                
                if ev_trend > 0.01:
                    ev_analysis = "Improving"
                elif ev_trend < -0.01:
                    ev_analysis = "Declining"
                else:
                    ev_analysis = "Stable"
            else:
                hit_rate_trend = 0
                ev_trend = 0
                hit_rate_analysis = "Insufficient data"
                ev_analysis = "Insufficient data"
            
            return {
                'player_name': player_name,
                'stat_type': stat_type,
                'trend_data': trend_data,
                'hit_rate_trend': hit_rate_trend,
                'ev_trend': ev_trend,
                'hit_rate_analysis': hit_rate_analysis,
                'ev_analysis': ev_analysis,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {}
    
    async def search_performances(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search performances by player name or stat type"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            results = await conn.fetch("""
                SELECT * FROM historical_performances 
                WHERE player_name ILIKE $1 OR stat_type ILIKE $1
                ORDER BY hit_rate_percentage DESC
                LIMIT $2
            """, search_query, limit)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'player_name': result['player_name'],
                    'stat_type': result['stat_type'],
                    'total_picks': result['total_picks'],
                    'hits': result['hits'],
                    'misses': result['misses'],
                    'hit_rate_percentage': result['hit_rate_percentage'],
                    'avg_ev': result['avg_ev'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching performances: {e}")
            return []
    
    async def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get a comprehensive performance summary"""
        try:
            # Get top performers
            top_performers = await self.get_top_performers(10)
            
            # Get best EV performers
            best_ev = await self.get_best_ev_performers(10)
            
            # Get worst performers
            worst_performers = await self.get_worst_performers(5)
            
            # Get statistics
            stats = await self.get_performance_statistics(days)
            
            return {
                'period_days': days,
                'top_performers': top_performers,
                'best_ev_performers': best_ev,
                'worst_performers': worst_performers,
                'statistics': stats,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}

# Global instance
historical_performance_service = HistoricalPerformanceService()

async def get_performance_summary(days: int = 30):
    """Get performance summary"""
    return await historical_performance_service.get_performance_summary(days)

if __name__ == "__main__":
    # Test historical performance service
    async def test():
        # Test getting performance summary
        summary = await get_performance_summary(30)
        print(f"Performance summary: {summary}")
    
    asyncio.run(test())
