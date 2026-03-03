"""
Historical Odds NCAAB Service - Track and analyze NCAA basketball betting odds
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

class GameResult(Enum):
    """Game result types"""
    HOME_WIN = "home_win"
    AWAY_WIN = "away_win"
    DRAW = "draw"
    PENDING = "pending"
    CANCELLED = "cancelled"

@dataclass
class HistoricalOdds:
    """Historical odds data structure"""
    id: int
    sport: int
    game_id: int
    home_team: str
    away_team: str
    home_odds: float
    away_odds: float
    draw_odds: Optional[float]
    bookmaker: str
    snapshot_date: datetime
    result: Optional[GameResult]
    season: int
    created_at: datetime
    updated_at: datetime

class HistoricalOddsNCAABService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_odds_snapshot(self, sport: int, game_id: int, home_team: str, away_team: str,
                                 home_odds: float, away_odds: float, draw_odds: Optional[float],
                                 bookmaker: str, season: int = None) -> bool:
        """Create a new odds snapshot"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO historical_odds_ncaab (
                    sport, game_id, home_team, away_team, home_odds, away_odds, draw_odds,
                    bookmaker, snapshot_date, season, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, sport, game_id, home_team, away_team, home_odds, away_odds, draw_odds,
                bookmaker, now, season, now, now)
            
            await conn.close()
            logger.info(f"Created odds snapshot: {home_team} vs {away_team} - {bookmaker}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating odds snapshot: {e}")
            return False
    
    async def update_odds_result(self, game_id: int, result: GameResult) -> bool:
        """Update odds result for a game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                UPDATE historical_odds_ncaab 
                SET result = $1, updated_at = $2
                WHERE game_id = $3
            """, result.value, now, game_id)
            
            await conn.close()
            logger.info(f"Updated odds result for game {game_id} to {result.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating odds result: {e}")
            return False
    
    async def get_odds_by_game(self, game_id: int) -> List[HistoricalOdds]:
        """Get odds snapshots for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM historical_odds_ncaab 
                WHERE game_id = $1
                ORDER BY snapshot_date ASC
            """, game_id)
            
            await conn.close()
            
            return [
                HistoricalOdds(
                    id=result['id'],
                    sport=result['sport'],
                    game_id=result['game_id'],
                    home_team=result['home_team'],
                    away_team=result['away_team'],
                    home_odds=result['home_odds'],
                    away_odds=result['away_odds'],
                    draw_odds=result['draw_odds'],
                    bookmaker=result['bookmaker'],
                    snapshot_date=result['snapshot_date'],
                    result=GameResult(result['result']) if result['result'] else None,
                    season=result['season'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting odds by game: {e}")
            return []
    
    async def get_odds_by_bookmaker(self, bookmaker: str, days: int = 30) -> List[HistoricalOdds]:
        """Get odds snapshots from a specific bookmaker"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM historical_odds_ncaab 
                WHERE bookmaker = $1
                AND snapshot_date >= NOW() - INTERVAL '$2 days'
                ORDER BY snapshot_date DESC
            """, bookmaker, days)
            
            await conn.close()
            
            return [
                HistoricalOdds(
                    id=result['id'],
                    sport=result['sport'],
                    game_id=result['game_id'],
                    home_team=result['home_team'],
                    away_team=result['away_team'],
                    home_odds=result['home_odds'],
                    away_odds=result['away_odds'],
                    draw_odds=result['draw_odds'],
                    bookmaker=result['bookmaker'],
                    snapshot_date=result['snapshot_date'],
                    result=GameResult(result['result']) if result['result'] else None,
                    season=result['season'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting odds by bookmaker: {e}")
            return []
    
    async def get_odds_by_team(self, team_name: str, days: int = 30) -> List[HistoricalOdds]:
        """Get odds snapshots for a specific team"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM historical_odds_ncaab 
                WHERE home_team = $1 OR away_team = $1
                AND snapshot_date >= NOW() - INTERVAL '$2 days'
                ORDER BY snapshot_date DESC
            """, team_name, days)
            
            await conn.close()
            
            return [
                HistoricalOdds(
                    id=result['id'],
                    sport=result['sport'],
                    game_id=result['game_id'],
                    home_team=result['home_team'],
                    away_team=result['away_team'],
                    home_odds=result['home_odds'],
                    away_odds=result['away_odds'],
                    draw_odds=result['draw_odds'],
                    bookmaker=result['bookmaker'],
                    snapshot_date=result['snapshot_date'],
                    result=GameResult(result['result']) if result['result'] else None,
                    season=result['season'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting odds by team: {e}")
            return []
    
    async def get_odds_movements(self, game_id: int) -> List[Dict[str, Any]]:
        """Get odds movements for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT 
                    bookmaker,
                    home_odds,
                    away_odds,
                    draw_odds,
                    snapshot_date,
                    LAG(home_odds) OVER (PARTITION BY bookmaker ORDER BY snapshot_date) as prev_home_odds,
                    LAG(away_odds) OVER (PARTITION BY bookmaker ORDER BY snapshot_date) as prev_away_odds,
                    LAG(draw_odds) OVER (PARTITION BY bookmaker ORDER BY snapshot_date) as prev_draw_odds
                FROM historical_odds_ncaab 
                WHERE game_id = $1
                ORDER BY bookmaker, snapshot_date ASC
            """, game_id)
            
            await conn.close()
            
            movements = []
            for result in results:
                home_movement = result['home_odds'] - result['prev_home_odds'] if result['prev_home_odds'] else 0
                away_movement = result['away_odds'] - result['prev_away_odds'] if result['prev_away_odds'] else 0
                draw_movement = result['draw_odds'] - result['prev_draw_odds'] if result['prev_draw_odds'] and result['prev_draw_odds'] else 0
                
                movements.append({
                    'bookmaker': result['bookmaker'],
                    'home_odds': result['home_odds'],
                    'away_odds': result['away_odds'],
                    'draw_odds': result['draw_odds'],
                    'snapshot_date': result['snapshot_date'].isoformat(),
                    'home_movement': home_movement,
                    'away_movement': away_movement,
                    'draw_movement': draw_movement,
                    'prev_home_odds': result['prev_home_odds'],
                    'prev_away_odds': result['prev_away_odds'],
                    'prev_draw_odds': result['prev_draw_odds']
                })
            
            return movements
            
        except Exception as e:
            logger.error(f"Error getting odds movements: {e}")
            return []
    
    async def get_bookmaker_comparison(self, game_id: int) -> List[Dict[str, Any]]:
        """Compare odds across bookmakers for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT 
                    bookmaker,
                    home_odds,
                    away_odds,
                    draw_odds,
                    snapshot_date,
                    result
                FROM historical_odds_ncaab 
                WHERE game_id = $1
                AND snapshot_date = (
                    SELECT MAX(snapshot_date) 
                    FROM historical_odds_ncaab 
                    WHERE game_id = $1
                )
                ORDER BY bookmaker
            """, game_id)
            
            await conn.close()
            
            return [
                {
                    'bookmaker': result['bookmaker'],
                    'home_odds': result['home_odds'],
                    'away_odds': result['away_odds'],
                    'draw_odds': result['draw_odds'],
                    'snapshot_date': result['snapshot_date'].isoformat(),
                    'result': result['result']
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting bookmaker comparison: {e}")
            return []
    
    async def get_odds_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get odds statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_odds,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT bookmaker) as unique_bookmakers,
                    COUNT(DISTINCT home_team) as unique_teams,
                    COUNT(CASE WHEN result = 'home_win' THEN 1 END) as home_wins,
                    COUNT(CASE WHEN result = 'away_win' THEN 1 END) as away_wins,
                    COUNT(CASE WHEN result IS NULL THEN 1 END) as pending_games,
                    AVG(home_odds) as avg_home_odds,
                    AVG(away_odds) as avg_away_odds,
                    AVG(draw_odds) as avg_draw_odds
                FROM historical_odds_ncaab 
                WHERE snapshot_date >= NOW() - INTERVAL '$1 days'
            """, days)
            
            # By bookmaker statistics
            by_bookmaker = await conn.fetch("""
                SELECT 
                    bookmaker,
                    COUNT(*) as total_odds,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(CASE WHEN result = 'home_win' THEN 1 END) as home_wins,
                    COUNT(CASE WHEN result = 'away_win' THEN 1 END) as away_wins,
                    COUNT(CASE WHEN result IS NULL THEN 1 END) as pending_games,
                    AVG(home_odds) as avg_home_odds,
                    AVG(away_odds) as avg_away_odds,
                    AVG(draw_odds) as avg_draw_odds
                FROM historical_odds_ncaab 
                WHERE snapshot_date >= NOW() - INTERVAL '$1 days'
                GROUP BY bookmaker
                ORDER BY total_odds DESC
            """, days)
            
            # By team statistics
            by_team = await conn.fetch("""
                SELECT 
                    home_team,
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN result = 'home_win' THEN 1 END) as home_wins,
                    COUNT(CASE WHEN result = 'away_win' THEN 1 END) as home_losses,
                    AVG(home_odds) as avg_home_odds,
                    AVG(away_odds) as avg_away_odds
                FROM historical_odds_ncaab 
                WHERE snapshot_date >= NOW() - INTERVAL '$1 days'
                GROUP BY home_team
                ORDER BY total_games DESC
                LIMIT 20
            """, days)
            
            await conn.close()
            
            home_win_rate = (overall['home_wins'] / (overall['home_wins'] + overall['away_wins']) * 100) if (overall['home_wins'] + overall['away_wins']) > 0 else 0
            
            return {
                'period_days': days,
                'total_odds': overall['total_odds'],
                'unique_games': overall['unique_games'],
                'unique_bookmakers': overall['unique_bookmakers'],
                'unique_teams': overall['unique_teams'],
                'home_wins': overall['home_wins'],
                'away_wins': overall['away_wins'],
                'pending_games': overall['pending_games'],
                'home_win_rate': home_win_rate,
                'avg_home_odds': overall['avg_home_odds'],
                'avg_away_odds': overall['avg_away_odds'],
                'avg_draw_odds': overall['avg_draw_odds'],
                'by_bookmaker': [
                    {
                        'bookmaker': bookmaker['bookmaker'],
                        'total_odds': bookmaker['total_odds'],
                        'unique_games': bookmaker['unique_games'],
                        'home_wins': bookmaker['home_wins'],
                        'away_wins': bookmaker['away_wins'],
                        'pending_games': bookmaker['pending_games'],
                        'avg_home_odds': bookmaker['avg_home_odds'],
                        'avg_away_odds': bookmaker['avg_away_odds'],
                        'avg_draw_odds': bookmaker['avg_draw_odds']
                    }
                    for bookmaker in by_bookmaker
                ],
                'by_team': [
                    {
                        'team': team['home_team'],
                        'total_games': team['total_games'],
                        'home_wins': team['home_wins'],
                        'home_losses': team['home_losses'],
                        'avg_home_odds': team['avg_home_odds'],
                        'avg_away_odds': team['avg_away_odds']
                    }
                    for team in by_team
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting odds statistics: {e}")
            return {}
    
    async def analyze_odds_efficiency(self, days: int = 30) -> Dict[str, Any]:
        """Analyze odds efficiency and accuracy"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Calculate implied probabilities vs actual results
            efficiency = await conn.fetch("""
                SELECT 
                    bookmaker,
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN result = 'home_win' THEN 1 END) as home_wins,
                    COUNT(CASE WHEN result = 'away_win' THEN 1 END) as away_wins,
                    AVG(
                        CASE 
                            WHEN home_odds < 0 THEN -100 / home_odds
                            ELSE 100 / home_odds
                        END
                    ) as avg_implied_home_prob,
                    AVG(
                        CASE 
                            WHEN away_odds < 0 THEN -100 / away_odds
                            ELSE 100 / away_odds
                        END
                    ) as avg_implied_away_prob,
                    AVG(
                        CASE 
                            WHEN result = 'home_win' THEN 1 
                            WHEN result = 'away_win' THEN 0 
                            ELSE 0.5 
                        END
                    ) as actual_home_win_rate
                FROM historical_odds_ncaab 
                WHERE snapshot_date >= NOW() - INTERVAL '$1 days'
                AND result IS NOT NULL
                GROUP BY bookmaker
                ORDER BY total_games DESC
            """, days)
            
            await conn.close()
            
            analysis = []
            for bookmaker in efficiency:
                implied_home_prob = bookmaker['avg_implied_home_prob'] / 100
                actual_home_prob = bookmaker['actual_home_win_rate']
                
                # Calculate efficiency metrics
                home_accuracy = 1 - abs(implied_home_prob - actual_home_prob)
                implied_away_prob = 1 - implied_home_prob
                actual_away_prob = 1 - actual_home_prob
                away_accuracy = 1 - abs(implied_away_prob - actual_away_prob)
                overall_accuracy = (home_accuracy + away_accuracy) / 2
                
                # Calculate theoretical edge
                home_edge = actual_home_prob - implied_home_prob
                away_edge = actual_away_prob - implied_away_prob
                
                analysis.append({
                    'bookmaker': bookmaker['bookmaker'],
                    'total_games': bookmaker['total_games'],
                    'home_wins': bookmaker['home_wins'],
                    'away_wins': bookmaker['away_wins'],
                    'avg_implied_home_prob': bookmaker['avg_implied_home_prob'],
                    'avg_implied_away_prob': bookmaker['avg_implied_away_prob'],
                    'actual_home_win_rate': bookmaker['actual_home_win_rate'] * 100,
                    'home_accuracy': home_accuracy * 100,
                    'away_accuracy': away_accuracy * 100,
                    'overall_accuracy': overall_accuracy * 100,
                    'home_edge': home_edge * 100,
                    'away_edge': away_edge * 100
                })
            
            return {
                'period_days': days,
                'bookmaker_efficiency': analysis,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing odds efficiency: {e}")
            return {}
    
    async def search_odds(self, query: str, days: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """Search odds by team names or bookmaker"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            results = await conn.fetch("""
                SELECT * FROM historical_odds_ncaab 
                WHERE (home_team ILIKE $1 OR away_team ILIKE $1 OR bookmaker ILIKE $1)
                AND snapshot_date >= NOW() - INTERVAL '$2 days'
                ORDER BY snapshot_date DESC
                LIMIT $3
            """, search_query, days, limit)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'sport': result['sport'],
                    'game_id': result['game_id'],
                    'home_team': result['home_team'],
                    'away_team': result['away_team'],
                    'home_odds': result['home_odds'],
                    'away_odds': result['away_odds'],
                    'draw_odds': result['draw_odds'],
                    'bookmaker': result['bookmaker'],
                    'snapshot_date': result['snapshot_date'].isoformat(),
                    'result': result['result'],
                    'season': result['season'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching odds: {e}")
            return []

# Global instance
historical_odds_ncaab_service = HistoricalOddsNCAABService()

async def get_odds_by_game(game_id: int):
    """Get odds by game ID"""
    return await historical_odds_ncaab_service.get_odds_by_game(game_id)

async def get_odds_statistics(days: int = 30):
    """Get odds statistics"""
    return await historical_odds_ncaab_service.get_odds_statistics(days)

if __name__ == "__main__":
    # Test historical odds service
    async def test():
        # Test getting odds by game
        odds = await get_odds_by_game(1001)
        print(f"Odds for game 1001: {len(odds)}")
        
        # Test getting statistics
        stats = await get_odds_statistics(30)
        print(f"Odds statistics: {stats}")
    
    asyncio.run(test())
