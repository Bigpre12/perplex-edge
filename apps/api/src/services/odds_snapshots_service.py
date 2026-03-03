"""
Odds Snapshots Service - Track and analyze historical odds snapshots from external sportsbooks
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

class OddsSide(Enum):
    """Odds side types"""
    OVER = "over"
    UNDER = "under"
    HOME = "home"
    AWAY = "away"

class Bookmaker(Enum):
    """Sportsbook types"""
    DRAFTKINGS = "DraftKings"
    FANDUEL = "FanDuel"
    BETMGM = "BetMGM"
    CAESARS = "Caesars"
    POINTSBET = "PointsBet"
    BET365 = "Bet365"

@dataclass
class OddsSnapshot:
    """Odds snapshot data structure"""
    id: int
    game_id: int
    market_id: int
    player_id: Optional[int]
    external_fixture_id: str
    external_market_id: str
    external_outcome_id: str
    bookmaker: str
    line_value: Optional[float]
    price: float
    american_odds: int
    side: OddsSide
    is_active: bool
    snapshot_at: datetime
    created_at: datetime
    updated_at: datetime

class OddsSnapshotsService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_odds_snapshot(self, game_id: int, market_id: int, player_id: Optional[int],
                                  external_fixture_id: str, external_market_id: str, external_outcome_id: str,
                                  bookmaker: str, line_value: Optional[float], price: float,
                                  american_odds: int, side: OddsSide, is_active: bool = True) -> bool:
        """Create a new odds snapshot"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO odds_snapshots (
                    game_id, market_id, player_id, external_fixture_id, external_market_id,
                    external_outcome_id, bookmaker, line_value, price, american_odds, side,
                    is_active, snapshot_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """, game_id, market_id, player_id, external_fixture_id, external_market_id,
                external_outcome_id, bookmaker, line_value, price, american_odds, side.value,
                is_active, now, now, now)
            
            await conn.close()
            logger.info(f"Created odds snapshot: Game {game_id}, Market {market_id}, {bookmaker}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating odds snapshot: {e}")
            return False
    
    async def get_odds_snapshots_by_game(self, game_id: int, bookmaker: str = None, 
                                        hours: int = 24) -> List[OddsSnapshot]:
        """Get odds snapshots for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM odds_snapshots 
                WHERE game_id = $1
                AND snapshot_at >= NOW() - INTERVAL '$1 hours'
            """
            
            params = [game_id, hours]
            
            if bookmaker:
                query += " AND bookmaker = $3"
                params.append(bookmaker)
            
            query += " ORDER BY snapshot_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                OddsSnapshot(
                    id=result['id'],
                    game_id=result['game_id'],
                    market_id=result['market_id'],
                    player_id=result['player_id'],
                    external_fixture_id=result['external_fixture_id'],
                    external_market_id=result['external_market_id'],
                    external_outcome_id=result['external_outcome_id'],
                    bookmaker=result['bookmaker'],
                    line_value=result['line_value'],
                    price=result['price'],
                    american_odds=result['american_odds'],
                    side=OddsSide(result['side']),
                    is_active=result['is_active'],
                    snapshot_at=result['snapshot_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting odds snapshots by game: {e}")
            return []
    
    async def get_odds_snapshots_by_player(self, player_id: int, bookmaker: str = None,
                                           hours: int = 24) -> List[OddsSnapshot]:
        """Get odds snapshots for a specific player"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM odds_snapshots 
                WHERE player_id = $1
                AND snapshot_at >= NOW() - INTERVAL '$1 hours'
            """
            
            params = [player_id, hours]
            
            if bookmaker:
                query += " AND bookmaker = $3"
                params.append(bookmaker)
            
            query += " ORDER BY snapshot_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                OddsSnapshot(
                    id=result['id'],
                    game_id=result['game_id'],
                    market_id=result['market_id'],
                    player_id=result['player_id'],
                    external_fixture_id=result['external_fixture_id'],
                    external_market_id=result['external_market_id'],
                    external_outcome_id=result['external_outcome_id'],
                    bookmaker=result['bookmaker'],
                    line_value=result['line_value'],
                    price=result['price'],
                    american_odds=result['american_odds'],
                    side=OddsSide(result['side']),
                    is_active=result['is_active'],
                    snapshot_at=result['snapshot_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting odds snapshots by player: {e}")
            return []
    
    async def get_odds_snapshots_by_bookmaker(self, bookmaker: str, hours: int = 24) -> List[OddsSnapshot]:
        """Get odds snapshots from a specific bookmaker"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM odds_snapshots 
                WHERE bookmaker = $1
                AND snapshot_at >= NOW() - INTERVAL '$1 hours'
                ORDER BY snapshot_at DESC
            """, bookmaker, hours)
            
            await conn.close()
            
            return [
                OddsSnapshot(
                    id=result['id'],
                    game_id=result['game_id'],
                    market_id=result['market_id'],
                    player_id=result['player_id'],
                    external_fixture_id=result['external_fixture_id'],
                    external_market_id=result['external_market_id'],
                    external_outcome_id=result['external_outcome_id'],
                    bookmaker=result['bookmaker'],
                    line_value=result['line_value'],
                    price=result['price'],
                    american_odds=result['american_odds'],
                    side=OddsSide(result['side']),
                    is_active=result['is_active'],
                    snapshot_at=result['snapshot_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting odds snapshots by bookmaker: {e}")
            return []
    
    async def get_odds_movements(self, game_id: int, market_id: int, player_id: int = None,
                                hours: int = 24) -> List[Dict[str, Any]]:
        """Get odds movements for a specific game/market/player combination"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT 
                    bookmaker,
                    line_value,
                    price,
                    american_odds,
                    side,
                    snapshot_at,
                    LAG(line_value) OVER (PARTITION BY bookmaker ORDER BY snapshot_at) as prev_line_value,
                    LAG(price) OVER (PARTITION BY bookmaker ORDER BY snapshot_at) as prev_price,
                    LAG(american_odds) OVER (PARTITION BY bookmaker ORDER BY snapshot_at) as prev_american_odds
                FROM odds_snapshots 
                WHERE game_id = $1 AND market_id = $2
                AND snapshot_at >= NOW() - INTERVAL '$1 hours'
            """
            
            params = [game_id, market_id, hours]
            
            if player_id:
                query += " AND player_id = $4"
                params.append(player_id)
            
            query += " ORDER BY bookmaker, snapshot_at ASC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            movements = []
            for result in results:
                line_movement = result['line_value'] - result['prev_line_value'] if result['prev_line_value'] else 0
                price_movement = result['price'] - result['prev_price'] if result['prev_price'] else 0
                odds_movement = result['american_odds'] - result['prev_american_odds'] if result['prev_american_odds'] else 0
                
                movements.append({
                    'bookmaker': result['bookmaker'],
                    'line_value': result['line_value'],
                    'price': result['price'],
                    'american_odds': result['american_odds'],
                    'side': result['side'],
                    'snapshot_at': result['snapshot_at'].isoformat(),
                    'line_movement': line_movement,
                    'price_movement': price_movement,
                    'odds_movement': odds_movement,
                    'prev_line_value': result['prev_line_value'],
                    'prev_price': result['prev_price'],
                    'prev_american_odds': result['prev_american_odds']
                })
            
            return movements
            
        except Exception as e:
            logger.error(f"Error getting odds movements: {e}")
            return []
    
    async def get_bookmaker_comparison(self, game_id: int, market_id: int, player_id: int = None,
                                      hours: int = 1) -> Dict[str, Any]:
        """Compare odds across bookmakers for a specific game/market/player"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT DISTINCT ON (bookmaker)
                    bookmaker,
                    line_value,
                    price,
                    american_odds,
                    side,
                    snapshot_at
                FROM odds_snapshots 
                WHERE game_id = $1 AND market_id = $2
                AND snapshot_at >= NOW() - INTERVAL '$1 hours'
            """
            
            params = [game_id, market_id, hours]
            
            if player_id:
                query += " AND player_id = $4"
                params.append(player_id)
            
            query += " ORDER BY bookmaker, snapshot_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            # Calculate best odds
            best_over = max(results, key=lambda x: x['price'] if x['side'] == 'over' else float('inf'))
            best_under = max(results, key=lambda x: x['price'] if x['side'] == 'under' else float('inf'))
            
            return {
                'game_id': game_id,
                'market_id': market_id,
                'player_id': player_id,
                'comparison': [
                    {
                        'bookmaker': result['bookmaker'],
                        'line_value': result['line_value'],
                        'price': result['price'],
                        'american_odds': result['american_odds'],
                        'side': result['side'],
                        'snapshot_at': result['snapshot_at'].isoformat()
                    }
                    for result in results
                ],
                'best_over_odds': {
                    'bookmaker': best_over['bookmaker'],
                    'line_value': best_over['line_value'],
                    'price': best_over['price'],
                    'american_odds': best_over['american_odds']
                },
                'best_under_odds': {
                    'bookmaker': best_under['bookmaker'],
                    'line_value': best_under['line_value'],
                    'price': best_under['price'],
                    'american_odds': best_under['american_odds']
                },
                'total_bookmakers': len(results),
                'hours': hours,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting bookmaker comparison: {e}")
            return {}
    
    async def get_odds_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get odds snapshot statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_snapshots,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT market_id) as unique_markets,
                    COUNT(DISTINCT player_id) as unique_players,
                    COUNT(DISTINCT bookmaker) as unique_bookmakers,
                    COUNT(DISTINCT external_fixture_id) as unique_fixtures,
                    COUNT(DISTINCT external_market_id) as unique_external_markets,
                    COUNT(DISTINCT external_outcome_id) as unique_external_outcomes,
                    AVG(line_value) as avg_line_value,
                    AVG(price) as avg_price,
                    AVG(american_odds) as avg_american_odds,
                    COUNT(CASE WHEN side = 'over' THEN 1 END) as over_snapshots,
                    COUNT(CASE WHEN side = 'under' THEN 1 END) as under_snapshots,
                    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_snapshots
                FROM odds_snapshots 
                WHERE snapshot_at >= NOW() - INTERVAL '$1 hours'
            """, hours)
            
            # By bookmaker statistics
            by_bookmaker = await conn.fetch("""
                SELECT 
                    bookmaker,
                    COUNT(*) as total_snapshots,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT market_id) as unique_markets,
                    AVG(line_value) as avg_line_value,
                    AVG(price) as avg_price,
                    AVG(american_odds) as avg_american_odds,
                    COUNT(CASE WHEN side = 'over' THEN 1 END) as over_snapshots,
                    COUNT(CASE WHEN side = 'under' THEN 1 END) as under_snapshots
                FROM odds_snapshots 
                WHERE snapshot_at >= NOW() - INTERVAL '$1 hours'
                GROUP BY bookmaker
                ORDER BY total_snapshots DESC
            """, hours)
            
            # By game statistics
            by_game = await conn.fetch("""
                SELECT 
                    game_id,
                    COUNT(*) as total_snapshots,
                    COUNT(DISTINCT market_id) as unique_markets,
                    COUNT(DISTINCT player_id) as unique_players,
                    COUNT(DISTINCT bookmaker) as unique_bookmakers,
                    MIN(snapshot_at) as first_snapshot,
                    MAX(snapshot_at) as last_snapshot
                FROM odds_snapshots 
                WHERE snapshot_at >= NOW() - INTERVAL '$1 hours'
                GROUP BY game_id
                ORDER BY total_snapshots DESC
                LIMIT 10
            """, hours)
            
            # By side statistics
            by_side = await conn.fetch("""
                SELECT 
                    side,
                    COUNT(*) as total_snapshots,
                    AVG(line_value) as avg_line_value,
                    AVG(price) as avg_price,
                    AVG(american_odds) as avg_american_odds,
                    COUNT(DISTINCT bookmaker) as unique_bookmakers,
                    COUNT(DISTINCT game_id) as unique_games
                FROM odds_snapshots 
                WHERE snapshot_at >= NOW() - INTERVAL '$1 hours'
                GROUP BY side
                ORDER BY total_snapshots DESC
            """, hours)
            
            await conn.close()
            
            return {
                'period_hours': hours,
                'total_snapshots': overall['total_snapshots'],
                'unique_games': overall['unique_games'],
                'unique_markets': overall['unique_markets'],
                'unique_players': overall['unique_players'],
                'unique_bookmakers': overall['unique_bookmakers'],
                'unique_fixtures': overall['unique_fixtures'],
                'unique_external_markets': overall['unique_external_markets'],
                'unique_external_outcomes': overall['unique_external_outcomes'],
                'avg_line_value': overall['avg_line_value'],
                'avg_price': overall['avg_price'],
                'avg_american_odds': overall['avg_american_odds'],
                'over_snapshots': overall['over_snapshots'],
                'under_snapshots': overall['under_snapshots'],
                'active_snapshots': overall['active_snapshots'],
                'by_bookmaker': [
                    {
                        'bookmaker': bookmaker['bookmaker'],
                        'total_snapshots': bookmaker['total_snapshots'],
                        'unique_games': bookmaker['unique_games'],
                        'unique_markets': bookmaker['unique_markets'],
                        'avg_line_value': bookmaker['avg_line_value'],
                        'avg_price': bookmaker['avg_price'],
                        'avg_american_odds': bookmaker['avg_american_odds'],
                        'over_snapshots': bookmaker['over_snapshots'],
                        'under_snapshots': bookmaker['under_snapshots']
                    }
                    for bookmaker in by_bookmaker
                ],
                'by_game': [
                    {
                        'game_id': game['game_id'],
                        'total_snapshots': game['total_snapshots'],
                        'unique_markets': game['unique_markets'],
                        'unique_players': game['unique_players'],
                        'unique_bookmakers': game['unique_bookmakers'],
                        'first_snapshot': game['first_snapshot'].isoformat(),
                        'last_snapshot': game['last_snapshot'].isoformat()
                    }
                    for game in by_game
                ],
                'by_side': [
                    {
                        'side': side['side'],
                        'total_snapshots': side['total_snapshots'],
                        'avg_line_value': side['avg_line_value'],
                        'avg_price': side['avg_price'],
                        'avg_american_odds': side['avg_american_odds'],
                        'unique_bookmakers': side['unique_bookmakers'],
                        'unique_games': side['unique_games']
                    }
                    for side in by_side
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting odds statistics: {e}")
            return {}
    
    async def search_odds_snapshots(self, query: str, bookmaker: str = None, hours: int = 24,
                                    limit: int = 50) -> List[Dict[str, Any]]:
        """Search odds snapshots by external IDs or bookmaker"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            sql_query = """
                SELECT * FROM odds_snapshots 
                WHERE (external_fixture_id ILIKE $1 
                   OR external_market_id ILIKE $1 
                   OR external_outcome_id ILIKE $1
                   OR bookmaker ILIKE $1)
                AND snapshot_at >= NOW() - INTERVAL '$1 hours'
            """
            
            params = [search_query, hours]
            
            if bookmaker:
                sql_query += " AND bookmaker = $3"
                params.append(bookmaker)
            
            sql_query += " ORDER BY snapshot_at DESC LIMIT $4"
            params.append(limit)
            
            results = await conn.fetch(sql_query, params)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'game_id': result['game_id'],
                    'market_id': result['market_id'],
                    'player_id': result['player_id'],
                    'external_fixture_id': result['external_fixture_id'],
                    'external_market_id': result['external_market_id'],
                    'external_outcome_id': result['external_outcome_id'],
                    'bookmaker': result['bookmaker'],
                    'line_value': result['line_value'],
                    'price': result['price'],
                    'american_odds': result['american_odds'],
                    'side': result['side'],
                    'is_active': result['is_active'],
                    'snapshot_at': result['snapshot_at'].isoformat(),
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching odds snapshots: {e}")
            return []

# Global instance
odds_snapshots_service = OddsSnapshotsService()

async def get_odds_snapshots_statistics(hours: int = 24):
    """Get odds snapshots statistics"""
    return await odds_snapshots_service.get_odds_statistics(hours)

if __name__ == "__main__":
    # Test odds snapshots service
    async def test():
        # Test getting statistics
        stats = await get_odds_snapshots_statistics(24)
        print(f"Odds snapshots statistics: {stats}")
    
    asyncio.run(test())
