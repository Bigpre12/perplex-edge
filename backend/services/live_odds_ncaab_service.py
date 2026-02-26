"""
Live Odds NCAAB Service - Track and analyze NCAA basketball live odds
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

class OddsType(Enum):
    """Odds type categories"""
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"
    PLAYER_PROP = "player_prop"
    TEAM_PROP = "team_prop"

class Sportsbook(Enum):
    """Sportsbook types"""
    DRAFTKINGS = "draftkings"
    FANDUEL = "fanduel"
    BETMGM = "betmgm"
    CAESARS = "caesars"
    POINTSBET = "pointsbet"
    BET365 = "bet365"

@dataclass
class LiveOdds:
    """Live odds data structure"""
    id: int
    sport: int
    game_id: int
    home_team: str
    away_team: str
    home_odds: int
    away_odds: int
    draw_odds: Optional[int]
    bookmaker: str
    timestamp: datetime
    season: int
    created_at: datetime
    updated_at: datetime

class LiveOddsNCAABService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_live_odds(self, sport: int, game_id: int, home_team: str, away_team: str,
                              home_odds: int, away_odds: int, draw_odds: Optional[int],
                              bookmaker: str, season: int) -> bool:
        """Create a new live odds record"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO live_odds_ncaab (
                    sport, game_id, home_team, away_team, home_odds, away_odds, draw_odds,
                    bookmaker, timestamp, season, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, sport, game_id, home_team, away_team, home_odds, away_odds, draw_odds,
                bookmaker, now, season, now, now)
            
            await conn.close()
            logger.info(f"Created live odds: {home_team} vs {away_team} - {bookmaker}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating live odds: {e}")
            return False
    
    async def update_live_odds(self, odds_id: int, home_odds: int, away_odds: int, 
                             draw_odds: Optional[int] = None) -> bool:
        """Update live odds"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            if draw_odds is not None:
                await conn.execute("""
                    UPDATE live_odds_ncaab 
                    SET home_odds = $1, away_odds = $2, draw_odds = $3, updated_at = $4
                    WHERE id = $5
                """, home_odds, away_odds, draw_odds, now, odds_id)
            else:
                await conn.execute("""
                    UPDATE live_odds_ncaab 
                    SET home_odds = $1, away_odds = $2, updated_at = $3
                    WHERE id = $4
                """, home_odds, away_odds, now, odds_id)
            
            await conn.close()
            logger.info(f"Updated live odds {odds_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating live odds: {e}")
            return False
    
    async def get_live_odds_by_game(self, game_id: int, bookmaker: str = None) -> List[LiveOdds]:
        """Get live odds for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM live_odds_ncaab 
                WHERE game_id = $1
            """
            
            params = [game_id]
            
            if bookmaker:
                query += " AND bookmaker = $2"
                params.append(bookmaker)
            
            query += " ORDER BY timestamp DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                LiveOdds(
                    id=result['id'],
                    sport=result['sport'],
                    game_id=result['game_id'],
                    home_team=result['home_team'],
                    away_team=result['away_team'],
                    home_odds=result['home_odds'],
                    away_odds=result['away_odds'],
                    draw_odds=result['draw_odds'],
                    bookmaker=result['bookmaker'],
                    timestamp=result['timestamp'],
                    season=result['season'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting live odds by game: {e}")
            return []
    
    async def get_live_odds_by_team(self, team_name: str, bookmaker: str = None) -> List[LiveOdds]:
        """Get live odds for a specific team"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM live_odds_ncaab 
                WHERE home_team = $1 OR away_team = $1
            """
            
            params = [team_name]
            
            if bookmaker:
                query += " AND bookmaker = $2"
                params.append(bookmaker)
            
            query += " ORDER BY timestamp DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                LiveOdds(
                    id=result['id'],
                    sport=result['sport'],
                    game_id=result['game_id'],
                    home_team=result['home_team'],
                    away_team=result['away_team'],
                    home_odds=result['home_odds'],
                    away_odds=result['away_odds'],
                    draw_odds=result['draw_odds'],
                    bookmaker=result['bookmaker'],
                    timestamp=result['timestamp'],
                    season=result['season'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting live odds by team: {e}")
            return []
    
    async def get_current_odds(self, game_id: int = None, bookmaker: str = None) -> List[LiveOdds]:
        """Get current live odds"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM live_odds_ncaab 
                WHERE timestamp >= NOW() - INTERVAL '5 minutes'
            """
            
            params = []
            
            if game_id:
                query += " AND game_id = $1"
                params.append(game_id)
            
            if bookmaker:
                query += " AND bookmaker = $2"
                params.append(bookmaker)
            
            query += " ORDER BY timestamp DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                LiveOdds(
                    id=result['id'],
                    sport=result['sport'],
                    game_id=result['game_id'],
                    home_team=result['home_team'],
                    away_team=result['away_team'],
                    home_odds=result['home_odds'],
                    away_odds=result['away_odds'],
                    draw_odds=result['draw_odds'],
                    bookmaker=result['bookmaker'],
                    timestamp=result['timestamp'],
                    season=result['season'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting current odds: {e}")
            return []
    
    async def get_odds_by_sportsbook(self, bookmaker: str, hours: int = 24) -> List[LiveOdds]:
        """Get odds from a specific sportsbook"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM live_odds_ncaab 
                WHERE bookmaker = $1
                AND timestamp >= NOW() - INTERVAL '$1 hours'
                ORDER BY timestamp DESC
            """, bookmaker, hours)
            
            await conn.close()
            
            return [
                LiveOdds(
                    id=result['id'],
                    sport=result['sport'],
                    game_id=result['game_id'],
                    home_team=result['home_team'],
                    away_team=result['away_team'],
                    home_odds=result['home_odds'],
                    away_odds=result['away_odds'],
                    draw_odds=result['draw_odds'],
                    bookmaker=result['bookmaker'],
                    timestamp=result['timestamp'],
                    season=result['season'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting odds by sportsbook: {e}")
            return []
    
    async def get_odds_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get live odds statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_odds,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT home_team) as unique_teams,
                    COUNT(DISTINCT away_team) as unique_opponents,
                    COUNT(DISTINCT bookmaker) as unique_bookmakers,
                    AVG(home_odds) as avg_home_odds,
                    AVG(away_odds) as avg_away_odds,
                    COUNT(CASE WHEN home_odds < 0 THEN 1 END) as home_favorites,
                    COUNT(CASE WHEN away_odds < 0 THEN 1 END) as away_favorites,
                    COUNT(CASE WHEN draw_odds IS NOT NULL THEN 1 END) as draw_markets
                FROM live_odds_ncaab 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
            """, hours)
            
            # By sportsbook statistics
            by_sportsbook = await conn.fetch("""
                SELECT 
                    bookmaker,
                    COUNT(*) as total_odds,
                    COUNT(DISTINCT game_id) as unique_games,
                    AVG(home_odds) as avg_home_odds,
                    AVG(away_odds) as avg_away_odds,
                    COUNT(CASE WHEN home_odds < 0 THEN 1 END) as home_favorites,
                    COUNT(CASE WHEN away_odds < 0 THEN 1 END) as away_favorites,
                    COUNT(DISTINCT home_team) as unique_teams,
                    COUNT(DISTINCT away_team) as unique_opponents
                FROM live_odds_ncaab 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                GROUP BY bookmaker
                ORDER BY total_odds DESC
            """, hours)
            
            # By team statistics
            by_team = await conn.fetch("""
                SELECT 
                    home_team,
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN home_odds < 0 THEN 1 END) as home_wins,
                    COUNT(CASE WHEN away_odds < 0 THEN 1 END) as away_wins,
                    AVG(home_odds) as avg_home_odds,
                    AVG(away_odds) as avg_away_odds,
                    COUNT(DISTINCT game_id) as unique_games
                FROM live_odds_ncaab 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                GROUP BY home_team
                ORDER BY total_games DESC
                LIMIT 20
            """, hours)
            
            # By odds range statistics
            by_odds_range = await conn.fetch("""
                SELECT 
                    CASE 
                        WHEN home_odds < -200 THEN 'Heavy Favorite'
                        WHEN home_odds < -150 THEN 'Strong Favorite'
                        WHEN home_odds < -110 THEN 'Moderate Favorite'
                        WHEN home_odds < -100 THEN 'Light Favorite'
                        WHEN home_odds < -50 THEN 'Slight Favorite'
                        WHEN home_odds < 0 THEN 'Pickem' 
                        WHEN home_odds <= 50 THEN 'Slight Underdog'
                        WHEN home_odds <= 100 THEN 'Moderate Underdog'
                        WHEN home_odds <= 150 THEN 'Strong Underdog'
                        WHEN home_odds <= 200 THEN 'Heavy Underdog'
                        ELSE 'Extreme Underdog'
                    END as odds_range,
                    COUNT(*) as total_odds,
                    AVG(home_odds) as avg_odds,
                    AVG(away_odds) as avg_away_odds
                FROM live_odds_ncaab 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                GROUP BY odds_range
                ORDER BY avg_odds ASC
            """, hours)
            
            await conn.close()
            
            return {
                'period_hours': hours,
                'total_odds': overall['total_odds'],
                'unique_games': overall['unique_games'],
                'unique_teams': overall['unique_teams'],
                'unique_opponents': overall['unique_opponents'],
                'unique_bookmakers': overall['unique_bookmakers'],
                'avg_home_odds': overall['avg_home_odds'],
                'avg_away_odds': overall['avg_away_odds'],
                'home_favorites': overall['home_favorites'],
                'away_favorites': overall['away_favorites'],
                'draw_markets': overall['draw_markets'],
                'by_sportsbook': [
                    {
                        'bookmaker': bookmaker['bookmaker'],
                        'total_odds': bookmaker['total_odds'],
                        'unique_games': bookmaker['unique_games'],
                        'avg_home_odds': bookmaker['avg_home_odds'],
                        'avg_away_odds': bookmaker['avg_away_odds'],
                        'home_favorites': bookmaker['home_favorites'],
                        'away_favorites': bookmaker['away_favorites'],
                        'unique_teams': bookmaker['unique_teams'],
                        'unique_opponents': bookmaker['unique_opponents']
                    }
                    for bookmaker in by_sportsbook
                ],
                'by_team': [
                    {
                        'team': team['home_team'],
                        'total_games': team['total_games'],
                        'home_wins': team['home_wins'],
                        'away_wins': team['away_wins'],
                        'avg_home_odds': team['avg_home_odds'],
                        'avg_away_odds': team['avg_away_odds'],
                        'unique_games': team['unique_games']
                    }
                    for team in by_team
                ],
                'by_odds_range': [
                    {
                        'odds_range': range['odds_range'],
                        'total_odds': range['total_odds'],
                        'avg_odds': range['avg_odds'],
                        'avg_away_odds': range['avg_away_odds']
                    }
                    for range in by_odds_range
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting odds statistics: {e}")
            return {}
    
    async def get_odds_movements(self, game_id: int, minutes: int = 30) -> List[Dict[str, Any]]:
        """Get odds movements for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT 
                    sportsbook,
                    home_odds,
                    away_odds,
                    draw_odds,
                    timestamp,
                    LAG(home_odds) OVER (PARTITION BY sportsbook ORDER BY timestamp) as prev_home_odds,
                    LAG(away_odds) OVER (PARTITION BY sportsbook ORDER BY timestamp) as prev_away_odds,
                    LAG(draw_odds) OVER (PARTITION BY sportsbook ORDER BY timestamp) as prev_draw_odds
                FROM live_odds_ncaab 
                WHERE game_id = $1
                AND timestamp >= NOW() - INTERVAL '$1 minutes'
                ORDER BY sportsbook, timestamp ASC
            """, game_id, minutes)
            
            await conn.close()
            
            movements = []
            for result in results:
                home_movement = result['home_odds'] - result['prev_home_odds'] if result['prev_home_odds'] else 0
                away_movement = result['away_odds'] - result['prev_away_odds'] if result['prev_away_odds'] else 0
                draw_movement = (result['draw_odds'] - result['prev_draw_odds']) if result['prev_draw_odds'] else 0
                
                movements.append({
                    'sportsbook': result['sportsbook'],
                    'home_odds': result['home_odds'],
                    'away_odds': result['away_odds'],
                    'draw_odds': result['draw_odds'],
                    'timestamp': result['timestamp'].isoformat(),
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
    
    async def get_sportsbook_comparison(self, game_id: int, minutes: int = 30) -> Dict[str, Any]:
        """Compare odds across sportsbooks for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT 
                    sportsbook,
                    home_odds,
                    away_odds,
                    draw_odds,
                    timestamp
                FROM live_odds_ncaab 
                WHERE game_id = $1
                AND timestamp >= NOW() - INTERVAL '$1 minutes'
                ORDER BY sportsbook, timestamp DESC
            """, game_id, minutes)
            
            await conn.close()
            
            # Calculate best odds
            best_home_odds = max(results, key=lambda x: x['home_odds'] if x['home_odds'] < 0 else float('inf'))
            best_away_odds = max(results, key=lambda x: x['away_odds'] if x['away_odds'] < 0 else float('inf'))
            
            return {
                'game_id': game_id,
                'comparison': [
                    {
                        'sportsbook': result['sportsbook'],
                        'home_odds': result['home_odds'],
                        'away_odds': result['away_odds'],
                        'draw_odds': result['draw_odds'],
                        'timestamp': result['timestamp'].isoformat()
                    }
                    for result in results
                ],
                'best_home_odds': {
                    'sportsbook': best_home_odds['sportsbook'],
                    'line_value': best_home_odds['home_odds'],
                    'odds': best_home_odds['odds']
                },
                'best_away_odds': {
                    'best_away_odds': best_away_odds['sportsbook'],
                    'line_value': best_away_odds['away_odds'],
                    'odds': best_away_odds['odds']
                },
                'total_sportsbooks': len(results),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting sportsbook comparison: {e}")
            return {}
    
    async def analyze_market_efficiency(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze market efficiency and arbitrage opportunities"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get arbitrage opportunities
            arbitrage = await conn.fetch("""
                SELECT 
                    game_id,
                    home_team,
                    away_team,
                    COUNT(DISTINCT sportsbook) as sportsbooks_count,
                    MIN(home_odds) as best_home_odds,
                    MAX(home_odds) as worst_home_odds,
                    MIN(away_odds) as best_away_odds,
                    MAX(away_odds) as worst_away_odds,
                    AVG(home_odds) as avg_home_odds,
                    AVG(away_odds) as avg_away_odds,
                    MAX(home_odds) - MIN(home_odds) as home_odds_range,
                    MAX(away_odds) - MIN(away_odds) as away_odds_range
                FROM live_odds_ncaab 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                GROUP BY game_id, home_team, away_team
                HAVING COUNT(DISTINCT sportsbook) >= 2
                ORDER BY home_odds_range DESC
                LIMIT 10
            """, hours)
            
            await conn.close()
            
            # Calculate efficiency metrics
            total_arbitrage = len(arbitrage)
            avg_home_range = sum(a['home_odds_range'] for a in arbitrage) / total_arbitrage if total_arbitrage > 0 else 0
            avg_away_range = sum(a['away_odds_range'] for a in arbitrage) / total_arbitrage if total_arbitrage > 0 else 0
            
            return {
                'period_hours': hours,
                'total_arbitrage_opportunities': total_arbitrage,
                'avg_home_range': avg_home_range,
                'avg_away_range': avg_away_range,
                'arbitrage_opportunities': [
                    {
                        'game_id': arb['game_id'],
                        'home_team': arb['home_team'],
                        'away_team': arb['away_team'],
                        'sportsbooks_count': arb['sportsbooks_count'],
                        'best_home_odds': arb['best_home_odds'],
                        'worst_home_odds': arb['worst_home_odds'],
                        'best_away_odds': arb['best_away_odds'],
                        'worst_away_odds': arb['worst_away_odds'],
                        'home_odds_range': arb['home_odds_range'],
                        'away_odds_range': arb['away_odds_range'],
                        'avg_home_odds': arb['avg_home_odds'],
                        'avg_away_odds': arb['avg_away_odds']
                    }
                    for arb in arbitrage
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market efficiency: {e}")
            return {}
    
    async def search_live_odds(self, query: str, sportsbook: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search live odds by team name or sportsbook"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            sql_query = """
                SELECT * FROM live_odds_ncaab 
                WHERE (home_team ILIKE $1 OR away_team ILIKE $1 OR sportsbook ILIKE $1)
            """
            
            params = [search_query]
            
            if sportsbook:
                sql_query += " AND sportsbook = $2"
                params.append(sportsbook)
            
            sql_query += " ORDER BY timestamp DESC LIMIT $3"
            params.append(limit)
            
            results = await conn.fetch(sql_query, params)
            
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
                    'timestamp': result['timestamp'].isoformat(),
                    'season': result['season'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching live odds: {e}")
            return []

# Global instance
live_odds_ncaab_service = LiveOddsNCAABService()

async def get_live_odds_statistics(hours: int = 24):
    """Get live odds statistics"""
    return await live_odds_ncaab_service.get_odds_statistics(hours)

if __name__ == "__main__":
    # Test live odds service
    async def test():
        # Test getting statistics
        stats = await get_live_odds_statistics(24)
        print(f"Live odds statistics: {stats}")
    
    asyncio.run(test())
