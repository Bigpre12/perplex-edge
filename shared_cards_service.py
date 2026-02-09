"""
Shared Cards Service - Track and analyze shared betting cards/slips
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

class Platform(Enum):
    """Platform categories"""
    TWITTER = "twitter"
    DISCORD = "discord"
    REDDIT = "reddit"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"

class Grade(Enum):
    """Card grading categories"""
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"

class RiskLevel(Enum):
    """Kelly risk level categories"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"

@dataclass
class SharedCard:
    """Shared card data structure"""
    id: int
    platform: str
    sport_id: int
    legs: List[Dict[str, Any]]
    leg_count: int
    total_odds: float
    decimal_odds: float
    parlay_probability: float
    parlay_ev: float
    overall_grade: str
    label: str
    kelly_suggested_units: Optional[float]
    kelly_risk_level: Optional[str]
    view_count: int
    settled: bool
    won: Optional[bool]
    settled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class SharedCardsService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_shared_card(self, platform: str, sport_id: int, legs: List[Dict[str, Any]], 
                                label: str, total_odds: float, decimal_odds: float,
                                parlay_probability: float, parlay_ev: float, 
                                overall_grade: str, kelly_suggested_units: Optional[float] = None,
                                kelly_risk_level: Optional[str] = None) -> bool:
        """Create a new shared card"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO shared_cards (
                    platform, sport_id, legs, leg_count, total_odds, decimal_odds,
                    parlay_probability, parlay_ev, overall_grade, label,
                    kelly_suggested_units, kelly_risk_level, view_count,
                    settled, won, settled_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
            """, platform, sport_id, json.dumps(legs), len(legs), total_odds, decimal_odds,
                parlay_probability, parlay_ev, overall_grade, label,
                kelly_suggested_units, kelly_risk_level, 0, False, None, None, now, now)
            
            await conn.close()
            logger.info(f"Created shared card: {label}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating shared card: {e}")
            return False
    
    async def get_shared_cards_by_platform(self, platform: str, limit: int = 50) -> List[SharedCard]:
        """Get shared cards for a specific platform"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM shared_cards 
                WHERE platform = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, platform, limit)
            
            await conn.close()
            
            return [
                SharedCard(
                    id=result['id'],
                    platform=result['platform'],
                    sport_id=result['sport_id'],
                    legs=json.loads(result['legs']),
                    leg_count=result['leg_count'],
                    total_odds=result['total_odds'],
                    decimal_odds=result['decimal_odds'],
                    parlay_probability=result['parlay_probability'],
                    parlay_ev=result['parlay_ev'],
                    overall_grade=result['overall_grade'],
                    label=result['label'],
                    kelly_suggested_units=result['kelly_suggested_units'],
                    kelly_risk_level=result['kelly_risk_level'],
                    view_count=result['view_count'],
                    settled=result['settled'],
                    won=result['won'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting shared cards by platform: {e}")
            return []
    
    async def get_shared_cards_by_sport(self, sport_id: int, limit: int = 50) -> List[SharedCard]:
        """Get shared cards for a specific sport"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM shared_cards 
                WHERE sport_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, sport_id, limit)
            
            await conn.close()
            
            return [
                SharedCard(
                    id=result['id'],
                    platform=result['platform'],
                    sport_id=result['sport_id'],
                    legs=json.loads(result['legs']),
                    leg_count=result['leg_count'],
                    total_odds=result['total_odds'],
                    decimal_odds=result['decimal_odds'],
                    parlay_probability=result['parlay_probability'],
                    parlay_ev=result['parlay_ev'],
                    overall_grade=result['overall_grade'],
                    label=result['label'],
                    kelly_suggested_units=result['kelly_suggested_units'],
                    kelly_risk_level=result['kelly_risk_level'],
                    view_count=result['view_count'],
                    settled=result['settled'],
                    won=result['won'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting shared cards by sport: {e}")
            return []
    
    async def get_shared_cards_by_grade(self, grade: str, limit: int = 50) -> List[SharedCard]:
        """Get shared cards by grade"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM shared_cards 
                WHERE overall_grade = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, grade, limit)
            
            await conn.close()
            
            return [
                SharedCard(
                    id=result['id'],
                    platform=result['platform'],
                    sport_id=result['sport_id'],
                    legs=json.loads(result['legs']),
                    leg_count=result['leg_count'],
                    total_odds=result['total_odds'],
                    decimal_odds=result['decimal_odds'],
                    parlay_probability=result['parlay_probability'],
                    parlay_ev=result['parlay_ev'],
                    overall_grade=result['overall_grade'],
                    label=result['label'],
                    kelly_suggested_units=result['kelly_suggested_units'],
                    kelly_risk_level=result['kelly_risk_level'],
                    view_count=result['view_count'],
                    settled=result['settled'],
                    won=result['won'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting shared cards by grade: {e}")
            return []
    
    async def get_trending_cards(self, hours: int = 24, limit: int = 20) -> List[SharedCard]:
        """Get trending shared cards based on views and recent activity"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM shared_cards 
                WHERE created_at >= NOW() - INTERVAL '$1 hours'
                ORDER BY view_count DESC, created_at DESC
                LIMIT $2
            """, hours, limit)
            
            await conn.close()
            
            return [
                SharedCard(
                    id=result['id'],
                    platform=result['platform'],
                    sport_id=result['sport_id'],
                    legs=json.loads(result['legs']),
                    leg_count=result['leg_count'],
                    total_odds=result['total_odds'],
                    decimal_odds=result['decimal_odds'],
                    parlay_probability=result['parlay_probability'],
                    parlay_ev=result['parlay_ev'],
                    overall_grade=result['overall_grade'],
                    label=result['label'],
                    kelly_suggested_units=result['kelly_suggested_units'],
                    kelly_risk_level=result['kelly_risk_level'],
                    view_count=result['view_count'],
                    settled=result['settled'],
                    won=result['won'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting trending cards: {e}")
            return []
    
    async def get_top_performing_cards(self, days: int = 30, limit: int = 20) -> List[SharedCard]:
        """Get top performing shared cards"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM shared_cards 
                WHERE settled = true AND won = true
                AND settled_at >= NOW() - INTERVAL '$1 days'
                ORDER BY parlay_ev DESC, view_count DESC
                LIMIT $2
            """, days, limit)
            
            await conn.close()
            
            return [
                SharedCard(
                    id=result['id'],
                    platform=result['platform'],
                    sport_id=result['sport_id'],
                    legs=json.loads(result['legs']),
                    leg_count=result['leg_count'],
                    total_odds=result['total_odds'],
                    decimal_odds=result['decimal_odds'],
                    parlay_probability=result['parlay_probability'],
                    parlay_ev=result['parlay_ev'],
                    overall_grade=result['overall_grade'],
                    label=result['label'],
                    kelly_suggested_units=result['kelly_suggested_units'],
                    kelly_risk_level=result['kelly_risk_level'],
                    view_count=result['view_count'],
                    settled=result['settled'],
                    won=result['won'],
                    settled_at=result['settled_at'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting top performing cards: {e}")
            return []
    
    async def update_card_views(self, card_id: int) -> bool:
        """Update card view count"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            await conn.execute("""
                UPDATE shared_cards 
                SET view_count = view_count + 1, updated_at = NOW()
                WHERE id = $1
            """, card_id)
            
            await conn.close()
            logger.info(f"Updated view count for card {card_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating card views: {e}")
            return False
    
    async def settle_card(self, card_id: int, won: bool) -> bool:
        """Settle a shared card"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                UPDATE shared_cards 
                SET settled = true, won = $1, settled_at = $2, updated_at = $2
                WHERE id = $3
            """, won, now, card_id)
            
            await conn.close()
            logger.info(f"Settled card {card_id}: {'Won' if won else 'Lost'}")
            return True
            
        except Exception as e:
            logger.error(f"Error settling card: {e}")
            return False
    
    async def get_shared_card_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get overall shared card statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_cards,
                    COUNT(DISTINCT platform) as unique_platforms,
                    COUNT(DISTINCT sport_id) as unique_sports,
                    AVG(total_odds) as avg_total_odds,
                    AVG(decimal_odds) as avg_decimal_odds,
                    AVG(parlay_probability) as avg_parlay_probability,
                    AVG(parlay_ev) as avg_parlay_ev,
                    COUNT(CASE WHEN overall_grade = 'A' THEN 1 END) as grade_a_cards,
                    COUNT(CASE WHEN settled = true THEN 1 END) as settled_cards,
                    COUNT(CASE WHEN settled = true AND won = true THEN 1 END) as won_cards,
                    COUNT(CASE WHEN settled = true AND won = false THEN 1 END) as lost_cards,
                    SUM(view_count) as total_views,
                    AVG(view_count) as avg_views_per_card
                FROM shared_cards
                WHERE created_at >= NOW() - INTERVAL '$1 days'
            """, days)
            
            # Platform performance
            platform_performance = await conn.fetch("""
                SELECT 
                    platform,
                    COUNT(*) as total_cards,
                    COUNT(CASE WHEN settled = true THEN 1 END) as settled_cards,
                    COUNT(CASE WHEN settled = true AND won = true THEN 1 END) as won_cards,
                    ROUND(COUNT(CASE WHEN settled = true AND won = true THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN settled = true THEN 1 END), 0), 2) as win_rate_percentage,
                    AVG(parlay_ev) as avg_parlay_ev,
                    SUM(view_count) as total_views,
                    AVG(view_count) as avg_views_per_card
                FROM shared_cards
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY platform
                ORDER BY total_cards DESC
            """, days)
            
            # Sport performance
            sport_performance = await conn.fetch("""
                SELECT 
                    sport_id,
                    COUNT(*) as total_cards,
                    COUNT(CASE WHEN settled = true THEN 1 END) as settled_cards,
                    COUNT(CASE WHEN settled = true AND won = true THEN 1 END) as won_cards,
                    ROUND(COUNT(CASE WHEN settled = true AND won = true THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN settled = true THEN 1 END), 0), 2) as win_rate_percentage,
                    AVG(parlay_ev) as avg_parlay_ev,
                    SUM(view_count) as total_views,
                    AVG(view_count) as avg_views_per_card
                FROM shared_cards
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY sport_id
                ORDER BY total_cards DESC
            """, days)
            
            # Grade performance
            grade_performance = await conn.fetch("""
                SELECT 
                    overall_grade,
                    COUNT(*) as total_cards,
                    COUNT(CASE WHEN settled = true THEN 1 END) as settled_cards,
                    COUNT(CASE WHEN settled = true AND won = true THEN 1 END) as won_cards,
                    ROUND(COUNT(CASE WHEN settled = true AND won = true THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN settled = true THEN 1 END), 0), 2) as win_rate_percentage,
                    AVG(parlay_ev) as avg_parlay_ev,
                    AVG(kelly_suggested_units) as avg_kelly_units,
                    SUM(view_count) as total_views,
                    AVG(view_count) as avg_views_per_card
                FROM shared_cards
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY overall_grade
                ORDER BY overall_grade DESC
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'total_cards': overall['total_cards'],
                'unique_platforms': overall['unique_platforms'],
                'unique_sports': overall['unique_sports'],
                'avg_total_odds': overall['avg_total_odds'],
                'avg_decimal_odds': overall['avg_decimal_odds'],
                'avg_parlay_probability': overall['avg_parlay_probability'],
                'avg_parlay_ev': overall['avg_parlay_ev'],
                'grade_a_cards': overall['grade_a_cards'],
                'settled_cards': overall['settled_cards'],
                'won_cards': overall['won_cards'],
                'lost_cards': overall['lost_cards'],
                'total_views': overall['total_views'],
                'avg_views_per_card': overall['avg_views_per_card'],
                'platform_performance': [
                    {
                        'platform': platform['platform'],
                        'total_cards': platform['total_cards'],
                        'settled_cards': platform['settled_cards'],
                        'won_cards': platform['won_cards'],
                        'win_rate_percentage': platform['win_rate_percentage'],
                        'avg_parlay_ev': platform['avg_parlay_ev'],
                        'total_views': platform['total_views'],
                        'avg_views_per_card': platform['avg_views_per_card']
                    }
                    for platform in platform_performance
                ],
                'sport_performance': [
                    {
                        'sport_id': sport['sport_id'],
                        'total_cards': sport['total_cards'],
                        'settled_cards': sport['settled_cards'],
                        'won_cards': sport['won_cards'],
                        'win_rate_percentage': sport['win_rate_percentage'],
                        'avg_parlay_ev': sport['avg_parlay_ev'],
                        'total_views': sport['total_views'],
                        'avg_views_per_card': sport['avg_views_per_card']
                    }
                    for sport in sport_performance
                ],
                'grade_performance': [
                    {
                        'overall_grade': grade['overall_grade'],
                        'total_cards': grade['total_cards'],
                        'settled_cards': grade['settled_cards'],
                        'won_cards': grade['won_cards'],
                        'win_rate_percentage': grade['win_rate_percentage'],
                        'avg_parlay_ev': grade['avg_parlay_ev'],
                        'avg_kelly_units': grade['avg_kelly_units'],
                        'total_views': grade['total_views'],
                        'avg_views_per_card': grade['avg_views_per_card']
                    }
                    for grade in grade_performance
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting shared card statistics: {e}")
            return {}
    
    async def search_shared_cards(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search shared cards by label or legs"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            results = await conn.fetch("""
                SELECT * FROM shared_cards 
                WHERE label ILIKE $1 OR legs::text ILIKE $1
                ORDER BY view_count DESC, created_at DESC
                LIMIT $2
            """, search_query, limit)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'platform': result['platform'],
                    'sport_id': result['sport_id'],
                    'legs': json.loads(result['legs']),
                    'leg_count': result['leg_count'],
                    'total_odds': result['total_odds'],
                    'decimal_odds': result['decimal_odds'],
                    'parlay_probability': result['parlay_probability'],
                    'parlay_ev': result['parlay_ev'],
                    'overall_grade': result['overall_grade'],
                    'label': result['label'],
                    'kelly_suggested_units': result['kelly_suggested_units'],
                    'kelly_risk_level': result['kelly_risk_level'],
                    'view_count': result['view_count'],
                    'settled': result['settled'],
                    'won': result['won'],
                    'settled_at': result['settled_at'].isoformat() if result['settled_at'] else None,
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching shared cards: {e}")
            return []

# Global instance
shared_cards_service = SharedCardsService()

async def get_shared_card_statistics(days: int = 30):
    """Get shared card statistics"""
    return await shared_cards_service.get_shared_card_statistics(days)

if __name__ == "__main__":
    # Test shared cards service
    async def test():
        # Test getting statistics
        stats = await get_shared_card_statistics(30)
        print(f"Shared card statistics: {stats}")
    
    asyncio.run(test())
