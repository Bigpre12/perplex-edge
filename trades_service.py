"""
Trades Service - Track and analyze master trade records
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

class TradeStatus(Enum):
    """Trade status categories"""
    APPLIED = "applied"
    PENDING = "pending"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class Trade:
    """Trade data structure"""
    id: int
    trade_date: datetime.date
    season_year: int
    description: str
    headline: str
    source_url: Optional[str]
    source: Optional[str]
    is_applied: bool
    created_at: datetime
    updated_at: datetime

class TradesService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_trade(self, trade_date: datetime.date, season_year: int, description: str,
                          headline: str, source_url: Optional[str], source: Optional[str],
                          is_applied: bool = False) -> bool:
        """Create a new trade"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO trades (
                    trade_date, season_year, description, headline, source_url, source,
                    is_applied, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, trade_date, season_year, description, headline, source_url, source,
                is_applied, now, now)
            
            await conn.close()
            logger.info(f"Created trade: {headline}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating trade: {e}")
            return False
    
    async def get_trades_by_season(self, season_year: int) -> List[Trade]:
        """Get trades for a specific season"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trades 
                WHERE season_year = $1
                ORDER BY trade_date DESC
            """, season_year)
            
            await conn.close()
            
            return [
                Trade(
                    id=result['id'],
                    trade_date=result['trade_date'],
                    season_year=result['season_year'],
                    description=result['description'],
                    headline=result['headline'],
                    source_url=result['source_url'],
                    source=result['source'],
                    is_applied=result['is_applied'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting trades by season: {e}")
            return []
    
    async def get_trades_by_source(self, source: str) -> List[Trade]:
        """Get trades from a specific source"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trades 
                WHERE source = $1
                ORDER BY trade_date DESC
            """, source)
            
            await conn.close()
            
            return [
                Trade(
                    id=result['id'],
                    trade_date=result['trade_date'],
                    season_year=result['season_year'],
                    description=result['description'],
                    headline=result['headline'],
                    source_url=result['source_url'],
                    source=result['source'],
                    is_applied=result['is_applied'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting trades by source: {e}")
            return []
    
    async def get_trades_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[Trade]:
        """Get trades within a date range"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trades 
                WHERE trade_date >= $1 AND trade_date <= $2
                ORDER BY trade_date DESC
            """, start_date, end_date)
            
            await conn.close()
            
            return [
                Trade(
                    id=result['id'],
                    trade_date=result['trade_date'],
                    season_year=result['season_year'],
                    description=result['description'],
                    headline=result['headline'],
                    source_url=result['source_url'],
                    source=result['source'],
                    is_applied=result['is_applied'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting trades by date range: {e}")
            return []
    
    async def get_recent_trades(self, days: int = 30) -> List[Trade]:
        """Get recent trades"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trades 
                WHERE trade_date >= CURRENT_DATE - INTERVAL '$1 days'
                ORDER BY trade_date DESC
            """, days)
            
            await conn.close()
            
            return [
                Trade(
                    id=result['id'],
                    trade_date=result['trade_date'],
                    season_year=result['season_year'],
                    description=result['description'],
                    headline=result['headline'],
                    source_url=result['source_url'],
                    source=result['source'],
                    is_applied=result['is_applied'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent trades: {e}")
            return []
    
    async def get_applied_trades(self) -> List[Trade]:
        """Get applied trades"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trades 
                WHERE is_applied = true
                ORDER BY trade_date DESC
            """)
            
            await conn.close()
            
            return [
                Trade(
                    id=result['id'],
                    trade_date=result['trade_date'],
                    season_year=result['season_year'],
                    description=result['description'],
                    headline=result['headline'],
                    source_url=result['source_url'],
                    source=result['source'],
                    is_applied=result['is_applied'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting applied trades: {e}")
            return []
    
    async def get_pending_trades(self) -> List[Trade]:
        """Get pending trades"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trades 
                WHERE is_applied = false
                ORDER BY trade_date DESC
            """)
            
            await conn.close()
            
            return [
                Trade(
                    id=result['id'],
                    trade_date=result['trade_date'],
                    season_year=result['season_year'],
                    description=result['description'],
                    headline=result['headline'],
                    source_url=result['source_url'],
                    source=result['source'],
                    is_applied=result['is_applied'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting pending trades: {e}")
            return []
    
    async def apply_trade(self, trade_id: int) -> bool:
        """Apply a trade"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                UPDATE trades 
                SET is_applied = true, updated_at = $1
                WHERE id = $2
            """, now, trade_id)
            
            await conn.close()
            logger.info(f"Applied trade {trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying trade: {e}")
            return False
    
    async def get_trade_statistics(self, days: int = 365) -> Dict[str, Any]:
        """Get overall trade statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_trades,
                    COUNT(DISTINCT season_year) as unique_seasons,
                    COUNT(DISTINCT source) as unique_sources,
                    COUNT(CASE WHEN is_applied = true THEN 1 END) as applied_trades,
                    COUNT(CASE WHEN is_applied = false THEN 1 END) as pending_trades,
                    MIN(trade_date) as earliest_trade,
                    MAX(trade_date) as latest_trade,
                    AVG(LENGTH(description)) as avg_description_length,
                    AVG(LENGTH(headline)) as avg_headline_length
                FROM trades
                WHERE trade_date >= CURRENT_DATE - INTERVAL '$1 days'
            """, days)
            
            # Trade by season
            season_stats = await conn.fetch("""
                SELECT 
                    season_year,
                    COUNT(*) as total_trades,
                    COUNT(CASE WHEN is_applied = true THEN 1 END) as applied_trades,
                    COUNT(DISTINCT source) as unique_sources
                FROM trades
                WHERE trade_date >= CURRENT_DATE - INTERVAL '$1 days'
                GROUP BY season_year
                ORDER BY season_year DESC
            """, days)
            
            # Trade by source
            source_stats = await conn.fetch("""
                SELECT 
                    source,
                    COUNT(*) as total_trades,
                    COUNT(DISTINCT season_year) as unique_seasons,
                    COUNT(CASE WHEN is_applied = true THEN 1 END) as applied_trades
                FROM trades
                WHERE trade_date >= CURRENT_DATE - INTERVAL '$1 days'
                GROUP BY source
                ORDER BY total_trades DESC
            """, days)
            
            # Trade by month
            month_stats = await conn.fetch("""
                SELECT 
                    DATE_TRUNC('month', trade_date) as trade_month,
                    COUNT(*) as total_trades,
                    COUNT(DISTINCT season_year) as unique_seasons,
                    COUNT(CASE WHEN is_applied = true THEN 1 END) as applied_trades
                FROM trades
                WHERE trade_date >= CURRENT_DATE - INTERVAL '$1 days'
                GROUP BY DATE_TRUNC('month', trade_date)
                ORDER BY trade_month DESC
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'total_trades': overall['total_trades'],
                'unique_seasons': overall['unique_seasons'],
                'unique_sources': overall['unique_sources'],
                'applied_trades': overall['applied_trades'],
                'pending_trades': overall['pending_trades'],
                'earliest_trade': overall['earliest_trade'].isoformat() if overall['earliest_trade'] else None,
                'latest_trade': overall['latest_trade'].isoformat() if overall['latest_trade'] else None,
                'avg_description_length': overall['avg_description_length'],
                'avg_headline_length': overall['avg_headline_length'],
                'season_stats': [
                    {
                        'season_year': stat['season_year'],
                        'total_trades': stat['total_trades'],
                        'applied_trades': stat['applied_trades'],
                        'unique_sources': stat['unique_sources']
                    }
                    for stat in season_stats
                ],
                'source_stats': [
                    {
                        'source': stat['source'],
                        'total_trades': stat['total_trades'],
                        'unique_seasons': stat['unique_seasons'],
                        'applied_trades': stat['applied_trades']
                    }
                    for stat in source_stats
                ],
                'month_stats': [
                    {
                        'trade_month': stat['trade_month'].isoformat(),
                        'total_trades': stat['total_trades'],
                        'unique_seasons': stat['unique_seasons'],
                        'applied_trades': stat['applied_trades']
                    }
                    for stat in month_stats
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting trade statistics: {e}")
            return {}
    
    async def search_trades(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search trades by headline or description"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            results = await conn.fetch("""
                SELECT * FROM trades 
                WHERE headline ILIKE $1 OR description ILIKE $1
                ORDER BY trade_date DESC
                LIMIT $2
            """, search_query, limit)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'trade_date': result['trade_date'].isoformat(),
                    'season_year': result['season_year'],
                    'description': result['description'],
                    'headline': result['headline'],
                    'source_url': result['source_url'],
                    'source': result['source'],
                    'is_applied': result['is_applied'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching trades: {e}")
            return []

# Global instance
trades_service = TradesService()

async def get_trade_statistics(days: int = 365):
    """Get trade statistics"""
    return await trades_service.get_trade_statistics(days)

if __name__ == "__main__":
    # Test trades service
    async def test():
        # Test getting statistics
        stats = await get_trade_statistics(365)
        print(f"Trades statistics: {stats}")
    
    asyncio.run(test())
