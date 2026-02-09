"""
Game Results Service - Track and manage game results for settlement and analysis
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
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SETTLED = "settled"
    CANCELLED = "cancelled"

@dataclass
class GameResult:
    """Game result data structure"""
    game_id: int
    external_fixture_id: str
    home_score: Optional[int]
    away_score: Optional[int]
    period_scores: Dict[str, Dict[str, int]]
    is_settled: bool
    settled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class GameResultsService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_game_result(self, game_id: int, external_fixture_id: str) -> bool:
        """Create a new game result record"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            await conn.execute("""
                INSERT INTO game_results (game_id, external_fixture_id, home_score, away_score, period_scores, is_settled)
                VALUES ($1, $2, NULL, NULL, '{}', FALSE)
            """, game_id, external_fixture_id)
            
            await conn.close()
            logger.info(f"Created game result record: {game_id} - {external_fixture_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating game result: {e}")
            return False
    
    async def update_game_result(self, game_id: int, home_score: int, away_score: int, 
                               period_scores: Dict[str, Dict[str, int]] = None) -> bool:
        """Update game result with scores"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            period_scores = period_scores or {}
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                UPDATE game_results 
                SET home_score = $1, away_score = $2, period_scores = $3, 
                    is_settled = TRUE, settled_at = $4, updated_at = $5
                WHERE game_id = $6
            """, home_score, away_score, json.dumps(period_scores), now, now, game_id)
            
            await conn.close()
            logger.info(f"Updated game result: {game_id} - {home_score}-{away_score}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating game result: {e}")
            return False
    
    async def get_game_result(self, game_id: int) -> Optional[GameResult]:
        """Get game result by ID"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetchrow("""
                SELECT * FROM game_results 
                WHERE game_id = $1
            """, game_id)
            
            await conn.close()
            
            if result:
                return GameResult(
                    game_id=result['game_id'],
                    external_fixture_id=result['external_fixture_id'],
                    home_score=result['home_score'],
                    away_score=result['away_score'],
                    period_scores=json.loads(result['period_scores']) if result['period_scores'] else {},
                    is_settled=result['is_settled'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting game result: {e}")
            return None
    
    async def get_game_results_by_date(self, date: str, sport_id: int = None) -> List[GameResult]:
        """Get game results for a specific date"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM game_results 
                WHERE DATE(created_at) = $1
            """
            
            params = [date]
            
            if sport_id:
                query += " AND sport_id = $2"
                params.append(sport_id)
            
            query += " ORDER BY created_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                GameResult(
                    game_id=result['game_id'],
                    external_fixture_id=result['external_fixture_id'],
                    home_score=result['home_score'],
                    away_score=result['away_score'],
                    period_scores=json.loads(result['period_scores']) if result['period_scores'] else {},
                    is_settled=result['is_settled'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting game results by date: {e}")
            return []
    
    async def get_pending_games(self) -> List[GameResult]:
        """Get all pending games"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM game_results 
                WHERE is_settled = FALSE 
                ORDER BY created_at DESC
            """)
            
            await conn.close()
            
            return [
                GameResult(
                    game_id=result['game_id'],
                    external_fixture_id=result['external_fixture_id'],
                    home_score=result['home_score'],
                    away_score=result['away_score'],
                    period_scores=json.loads(result['period_scores']) if result['period_scores'] else {},
                    is_settled=result['is_settled'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting pending games: {e}")
            return []
    
    async def get_settled_games(self, days: int = 7) -> List[GameResult]:
        """Get settled games within specified days"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM game_results 
                WHERE is_settled = TRUE 
                AND settled_at >= NOW() - INTERVAL '$1 days'
                ORDER BY settled_at DESC
            """, days)
            
            await conn.close()
            
            return [
                GameResult(
                    game_id=result['game_id'],
                    external_fixture_id=result['external_fixture_id'],
                    home_score=result['home_score'],
                    away_score=result['away_score'],
                    period_scores=json.loads(result['period_scores']) if result['period_scores'] else {},
                    is_settled=result['is_settled'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting settled games: {e}")
            return []
    
    async def get_game_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get game statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN is_settled = TRUE THEN 1 END) as settled_games,
                    COUNT(CASE WHEN is_settled = FALSE THEN 1 END) as pending_games,
                    AVG(home_score) as avg_home_score,
                    AVG(away_score) as avg_away_score,
                    AVG(home_score + away_score) as avg_total_score,
                    COUNT(CASE WHEN home_score > away_score THEN 1 END) as home_wins,
                    COUNT(CASE WHEN away_score > home_score THEN 1 END) as away_wins,
                    COUNT(CASE WHEN home_score = away_score THEN 1 END) as ties
                FROM game_results 
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                AND is_settled = TRUE
            """, days)
            
            # By sport statistics
            by_sport = await conn.fetch("""
                SELECT 
                    sport_id,
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN is_settled = TRUE THEN 1 END) as settled_games,
                    AVG(home_score) as avg_home_score,
                    AVG(away_score) as avg_away_score,
                    COUNT(CASE WHEN home_score > away_score THEN 1 END) as home_wins,
                    COUNT(CASE WHEN away_score > home_score THEN 1 END) as away_wins
                FROM game_results 
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY sport_id
                ORDER BY total_games DESC
            """, days)
            
            await conn.close()
            
            home_win_rate = (overall['home_wins'] / overall['settled_games'] * 100) if overall['settled_games'] > 0 else 0
            away_win_rate = (overall['away_wins'] / overall['settled_games'] * 100) if overall['settled_games'] > 0 else 0
            tie_rate = (overall['ties'] / overall['settled_games'] * 100) if overall['settled_games'] > 0 else 0
            
            return {
                'period_days': days,
                'total_games': overall['total_games'],
                'settled_games': overall['settled_games'],
                'pending_games': overall['pending_games'],
                'avg_home_score': overall['avg_home_score'],
                'avg_away_score': overall['avg_away_score'],
                'avg_total_score': overall['avg_total_score'],
                'home_wins': overall['home_wins'],
                'away_wins': overall['away_wins'],
                'ties': overall['ties'],
                'home_win_rate': home_win_rate,
                'away_win_rate': away_win_rate,
                'tie_rate': tie_rate,
                'by_sport': [
                    {
                        'sport_id': sport['sport_id'],
                        'total_games': sport['total_games'],
                        'settled_games': sport['settled_games'],
                        'avg_home_score': sport['avg_home_score'],
                        'avg_away_score': sport['avg_away_score'],
                        'home_wins': sport['home_wins'],
                        'away_wins': sport['away_wins']
                    }
                    for sport in by_sport
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting game statistics: {e}")
            return {}
    
    async def settle_pending_games(self, external_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Settle pending games with external results"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            settled_count = 0
            failed_count = 0
            settlement_results = []
            
            for result in external_results:
                try:
                    game_id = result.get('game_id')
                    home_score = result.get('home_score')
                    away_score = result.get('away_score')
                    period_scores = result.get('period_scores', {})
                    
                    if not all([game_id, home_score is not None, away_score is not None]):
                        failed_count += 1
                        settlement_results.append({
                            'game_id': game_id,
                            'status': 'failed',
                            'error': 'Missing required fields'
                        })
                        continue
                    
                    # Update the game result
                    await conn.execute("""
                        UPDATE game_results 
                        SET home_score = $1, away_score = $2, period_scores = $3, 
                            is_settled = TRUE, settled_at = NOW(), updated_at = NOW()
                        WHERE game_id = $4 AND is_settled = FALSE
                    """, home_score, away_score, json.dumps(period_scores), game_id)
                    
                    settled_count += 1
                    settlement_results.append({
                        'game_id': game_id,
                        'status': 'settled',
                        'home_score': home_score,
                        'away_score': away_score
                    })
                    
                except Exception as e:
                    failed_count += 1
                    settlement_results.append({
                        'game_id': result.get('game_id'),
                        'status': 'failed',
                        'error': str(e)
                    })
            
            await conn.close()
            
            return {
                'total_processed': len(external_results),
                'settled_count': settled_count,
                'failed_count': failed_count,
                'settlement_results': settlement_results,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error settling pending games: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def get_game_results_for_settlement(self, sport_id: int = None) -> List[Dict[str, Any]]:
        """Get pending games that need settlement"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT game_id, external_fixture_id, created_at 
                FROM game_results 
                WHERE is_settled = FALSE 
            """
            
            params = []
            
            if sport_id:
                query += " AND sport_id = $1"
                params.append(sport_id)
            
            query += " ORDER BY created_at ASC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                {
                    'game_id': result['game_id'],
                    'external_fixture_id': result['external_fixture_id'],
                    'created_at': result['created_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting games for settlement: {e}")
            return []
    
    async def analyze_game_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze game patterns and trends"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Score distribution
            score_dist = await conn.fetch("""
                SELECT 
                    home_score,
                    away_score,
                    COUNT(*) as frequency
                FROM game_results 
                WHERE is_settled = TRUE 
                AND created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY home_score, away_score
                ORDER BY frequency DESC
                LIMIT 20
            """, days)
            
            # Total score distribution
            total_score_dist = await conn.fetch("""
                SELECT 
                    (home_score + away_score) as total_score,
                    COUNT(*) as frequency
                FROM game_results 
                WHERE is_settled = TRUE 
                AND created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY (home_score + away_score)
                ORDER BY total_score DESC
                LIMIT 20
            """, days)
            
            # Margin distribution
            margin_dist = await conn.fetch("""
                SELECT 
                    ABS(home_score - away_score) as margin,
                    COUNT(*) as frequency
                FROM game_results 
                WHERE is_settled = TRUE 
                AND created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY ABS(home_score - away_score)
                ORDER BY margin DESC
                LIMIT 20
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'score_distribution': [
                    {
                        'home_score': row['home_score'],
                        'away_score': row['away_score'],
                        'frequency': row['frequency']
                    }
                    for row in score_dist
                ],
                'total_score_distribution': [
                    {
                        'total_score': row['total_score'],
                        'frequency': row['frequency']
                    }
                    for row in total_score_dist
                ],
                'margin_distribution': [
                    {
                        'margin': row['margin'],
                        'frequency': row['frequency']
                    }
                    for row in margin_dist
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing game patterns: {e}")
            return {}

# Global instance
game_results_service = GameResultsService()

async def get_game_result(game_id: int):
    """Get game result by ID"""
    return await game_results_service.get_game_result(game_id)

async def get_pending_games():
    """Get all pending games"""
    return await game_results_service.get_pending_games()

if __name__ == "__main__":
    # Test game results service
    async def test():
        # Test getting pending games
        pending = await get_pending_games()
        print(f"Pending games: {len(pending)}")
        
        # Test getting game statistics
        stats = await game_results_service.get_game_statistics()
        print(f"Game statistics: {stats}")
    
    asyncio.run(test())
