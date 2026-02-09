"""
Picks Service - Manage and analyze betting picks with EV calculations
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

class PickType(Enum):
    """Pick type categories"""
    PLAYER_PROP = "player_prop"
    TEAM_PROP = "team_prop"
    GAME_PROP = "game_prop"
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"

class StatType(Enum):
    """Stat type categories"""
    POINTS = "points"
    REBOUNDS = "rebounds"
    ASSISTS = "assists"
    PASSING_YARDS = "passing_yards"
    PASSING_TOUCHDOWNS = "passing_touchdowns"
    RUSHING_YARDS = "rushing_yards"
    HOME_RUNS = "home_runs"
    RBIS = "rbis"
    STRIKEOUTS = "strikeouts"
    HITS = "hits"

@dataclass
class Pick:
    """Pick data structure"""
    id: int
    game_id: int
    pick_type: str
    player_name: str
    stat_type: str
    line: float
    odds: int
    model_probability: float
    implied_probability: float
    ev_percentage: float
    confidence: float
    hit_rate: float
    created_at: datetime
    updated_at: datetime

class PicksService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_pick(self, game_id: int, pick_type: str, player_name: str, stat_type: str,
                         line: float, odds: int, model_probability: float, confidence: float,
                         hit_rate: float) -> Optional[int]:
        """Create a new pick with EV calculation"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Calculate implied probability from odds
            if odds < 0:
                implied_probability = abs(odds) / (abs(odds) + 100)
            else:
                implied_probability = 100 / (odds + 100)
            
            # Calculate EV percentage
            ev_percentage = (model_probability - implied_probability) * 100
            
            now = datetime.now(timezone.utc)
            
            result = await conn.fetchrow("""
                INSERT INTO picks (
                    game_id, pick_type, player_name, stat_type, line, odds, model_probability,
                    implied_probability, ev_percentage, confidence, hit_rate, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id
            """, game_id, pick_type, player_name, stat_type, line, odds, model_probability,
                implied_probability, ev_percentage, confidence, hit_rate, now, now)
            
            await conn.close()
            logger.info(f"Created pick: {player_name} {stat_type} {line} with EV {ev_percentage:.2f}%")
            return result['id']
            
        except Exception as e:
            logger.error(f"Error creating pick: {e}")
            return None
    
    async def get_picks_by_game(self, game_id: int) -> List[Pick]:
        """Get picks for a specific game"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM picks 
                WHERE game_id = $1
                ORDER BY ev_percentage DESC
            """, game_id)
            
            await conn.close()
            
            return [
                Pick(
                    id=result['id'],
                    game_id=result['game_id'],
                    pick_type=result['pick_type'],
                    player_name=result['player_name'],
                    stat_type=result['stat_type'],
                    line=result['line'],
                    odds=result['odds'],
                    model_probability=result['model_probability'],
                    implied_probability=result['implied_probability'],
                    ev_percentage=result['ev_percentage'],
                    confidence=result['confidence'],
                    hit_rate=result['hit_rate'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting picks by game: {e}")
            return []
    
    async def get_picks_by_player(self, player_name: str, hours: int = 24) -> List[Pick]:
        """Get picks for a specific player"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM picks 
                WHERE player_name = $1
                AND created_at >= NOW() - INTERVAL '$1 hours'
                ORDER BY created_at DESC
            """, player_name, hours)
            
            await conn.close()
            
            return [
                Pick(
                    id=result['id'],
                    game_id=result['game_id'],
                    pick_type=result['pick_type'],
                    player_name=result['player_name'],
                    stat_type=result['stat_type'],
                    line=result['line'],
                    odds=result['odds'],
                    model_probability=result['model_probability'],
                    implied_probability=result['implied_probability'],
                    ev_percentage=result['ev_percentage'],
                    confidence=result['confidence'],
                    hit_rate=result['hit_rate'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting picks by player: {e}")
            return []
    
    async def get_high_ev_picks(self, min_ev: float = 5.0, hours: int = 24) -> List[Pick]:
        """Get picks with high expected value"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM picks 
                WHERE ev_percentage >= $1
                AND created_at >= NOW() - INTERVAL '$1 hours'
                ORDER BY ev_percentage DESC
            """, min_ev, hours)
            
            await conn.close()
            
            return [
                Pick(
                    id=result['id'],
                    game_id=result['game_id'],
                    pick_type=result['pick_type'],
                    player_name=result['player_name'],
                    stat_type=result['stat_type'],
                    line=result['line'],
                    odds=result['odds'],
                    model_probability=result['model_probability'],
                    implied_probability=result['implied_probability'],
                    ev_percentage=result['ev_percentage'],
                    confidence=result['confidence'],
                    hit_rate=result['hit_rate'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting high EV picks: {e}")
            return []
    
    async def get_high_confidence_picks(self, min_confidence: float = 80.0, hours: int = 24) -> List[Pick]:
        """Get picks with high confidence"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM picks 
                WHERE confidence >= $1
                AND created_at >= NOW() - INTERVAL '$1 hours'
                ORDER BY confidence DESC
            """, min_confidence, hours)
            
            await conn.close()
            
            return [
                Pick(
                    id=result['id'],
                    game_id=result['game_id'],
                    pick_type=result['pick_type'],
                    player_name=result['player_name'],
                    stat_type=result['stat_type'],
                    line=result['line'],
                    odds=result['odds'],
                    model_probability=result['model_probability'],
                    implied_probability=result['implied_probability'],
                    ev_percentage=result['ev_percentage'],
                    confidence=result['confidence'],
                    hit_rate=result['hit_rate'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting high confidence picks: {e}")
            return []
    
    async def get_picks_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get picks statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_picks,
                    COUNT(DISTINCT game_id) as unique_games,
                    COUNT(DISTINCT player_name) as unique_players,
                    COUNT(DISTINCT stat_type) as unique_stat_types,
                    COUNT(DISTINCT pick_type) as unique_pick_types,
                    AVG(line) as avg_line,
                    AVG(odds) as avg_odds,
                    AVG(model_probability) as avg_model_prob,
                    AVG(implied_probability) as avg_implied_prob,
                    AVG(ev_percentage) as avg_ev,
                    AVG(confidence) as avg_confidence,
                    AVG(hit_rate) as avg_hit_rate,
                    COUNT(CASE WHEN ev_percentage > 5.0 THEN 1 END) as high_ev_picks,
                    COUNT(CASE WHEN confidence >= 80.0 THEN 1 END) as high_confidence_picks,
                    COUNT(CASE WHEN hit_rate >= 60.0 THEN 1 END) as high_hit_rate_picks
                FROM picks
                WHERE created_at >= NOW() - INTERVAL '$1 hours'
            """, hours)
            
            # By player statistics
            by_player = await conn.fetch("""
                SELECT 
                    player_name,
                    COUNT(*) as total_picks,
                    AVG(ev_percentage) as avg_ev,
                    AVG(confidence) as avg_confidence,
                    AVG(hit_rate) as avg_hit_rate,
                    AVG(model_probability) as avg_model_prob,
                    AVG(implied_probability) as avg_implied_prob,
                    COUNT(CASE WHEN ev_percentage > 5.0 THEN 1 END) as high_ev_picks,
                    COUNT(CASE WHEN confidence >= 80.0 THEN 1 END) as high_confidence_picks
                FROM picks
                WHERE created_at >= NOW() - INTERVAL '$1 hours'
                GROUP BY player_name
                ORDER BY avg_ev DESC
                LIMIT 10
            """, hours)
            
            # By stat type statistics
            by_stat_type = await conn.fetch("""
                SELECT 
                    stat_type,
                    COUNT(*) as total_picks,
                    AVG(ev_percentage) as avg_ev,
                    AVG(confidence) as avg_confidence,
                    AVG(hit_rate) as avg_hit_rate,
                    AVG(model_probability) as avg_model_prob,
                    AVG(implied_probability) as avg_implied_prob,
                    COUNT(CASE WHEN ev_percentage > 5.0 THEN 1 END) as high_ev_picks
                FROM picks
                WHERE created_at >= NOW() - INTERVAL '$1 hours'
                GROUP BY stat_type
                ORDER BY avg_ev DESC
            """, hours)
            
            # EV distribution
            ev_distribution = await conn.fetch("""
                SELECT 
                    CASE 
                        WHEN ev_percentage >= 15.0 THEN 'Very High EV (15%+)'
                        WHEN ev_percentage >= 10.0 THEN 'High EV (10-15%)'
                        WHEN ev_percentage >= 5.0 THEN 'Medium EV (5-10%)'
                        WHEN ev_percentage >= 0.0 THEN 'Low EV (0-5%)'
                        ELSE 'Negative EV (<0%)'
                    END as ev_category,
                    COUNT(*) as total_picks,
                    AVG(ev_percentage) as avg_ev,
                    AVG(confidence) as avg_confidence,
                    AVG(hit_rate) as avg_hit_rate
                FROM picks
                WHERE created_at >= NOW() - INTERVAL '$1 hours'
                GROUP BY ev_category
                ORDER BY avg_ev DESC
            """, hours)
            
            await conn.close()
            
            return {
                'period_hours': hours,
                'total_picks': overall['total_picks'],
                'unique_games': overall['unique_games'],
                'unique_players': overall['unique_players'],
                'unique_stat_types': overall['unique_stat_types'],
                'unique_pick_types': overall['unique_pick_types'],
                'avg_line': overall['avg_line'],
                'avg_odds': overall['avg_odds'],
                'avg_model_prob': overall['avg_model_prob'],
                'avg_implied_prob': overall['avg_implied_prob'],
                'avg_ev': overall['avg_ev'],
                'avg_confidence': overall['avg_confidence'],
                'avg_hit_rate': overall['avg_hit_rate'],
                'high_ev_picks': overall['high_ev_picks'],
                'high_confidence_picks': overall['high_confidence_picks'],
                'high_hit_rate_picks': overall['high_hit_rate_picks'],
                'by_player': [
                    {
                        'player_name': player['player_name'],
                        'total_picks': player['total_picks'],
                        'avg_ev': player['avg_ev'],
                        'avg_confidence': player['avg_confidence'],
                        'avg_hit_rate': player['avg_hit_rate'],
                        'avg_model_prob': player['avg_model_prob'],
                        'avg_implied_prob': player['avg_implied_prob'],
                        'high_ev_picks': player['high_ev_picks'],
                        'high_confidence_picks': player['high_confidence_picks']
                    }
                    for player in by_player
                ],
                'by_stat_type': [
                    {
                        'stat_type': stat['stat_type'],
                        'total_picks': stat['total_picks'],
                        'avg_ev': stat['avg_ev'],
                        'avg_confidence': stat['avg_confidence'],
                        'avg_hit_rate': stat['avg_hit_rate'],
                        'avg_model_prob': stat['avg_model_prob'],
                        'avg_implied_prob': stat['avg_implied_prob'],
                        'high_ev_picks': stat['high_ev_picks']
                    }
                    for stat in by_stat_type
                ],
                'ev_distribution': [
                    {
                        'ev_category': ev['ev_category'],
                        'total_picks': ev['total_picks'],
                        'avg_ev': ev['avg_ev'],
                        'avg_confidence': ev['avg_confidence'],
                        'avg_hit_rate': ev['avg_hit_rate']
                    }
                    for ev in ev_distribution
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting picks statistics: {e}")
            return {}
    
    async def search_picks(self, query: str, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Search picks by player name or stat type"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            results = await conn.fetch("""
                SELECT * FROM picks 
                WHERE (player_name ILIKE $1 OR stat_type ILIKE $1 OR pick_type ILIKE $1)
                AND created_at >= NOW() - INTERVAL '$1 hours'
                ORDER BY ev_percentage DESC
                LIMIT $2
            """, search_query, hours, limit)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'game_id': result['game_id'],
                    'pick_type': result['pick_type'],
                    'player_name': result['player_name'],
                    'stat_type': result['stat_type'],
                    'line': result['line'],
                    'odds': result['odds'],
                    'model_probability': result['model_probability'],
                    'implied_probability': result['implied_probability'],
                    'ev_percentage': result['ev_percentage'],
                    'confidence': result['confidence'],
                    'hit_rate': result['hit_rate'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching picks: {e}")
            return []
    
    async def calculate_ev(self, model_probability: float, odds: int) -> float:
        """Calculate expected value percentage"""
        try:
            # Calculate implied probability from odds
            if odds < 0:
                implied_probability = abs(odds) / (abs(odds) + 100)
            else:
                implied_probability = 100 / (odds + 100)
            
            # Calculate EV percentage
            ev_percentage = (model_probability - implied_probability) * 100
            
            return ev_percentage
            
        except Exception as e:
            logger.error(f"Error calculating EV: {e}")
            return 0.0

# Global instance
picks_service = PicksService()

async def get_picks_statistics(hours: int = 24):
    """Get picks statistics"""
    return await picks_service.get_picks_statistics(hours)

if __name__ == "__main__":
    # Test picks service
    async def test():
        # Test getting statistics
        stats = await get_picks_statistics(24)
        print(f"Picks statistics: {stats}")
    
    asyncio.run(test())
