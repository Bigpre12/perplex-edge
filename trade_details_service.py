"""
Trade Details Service - Track and analyze player trades between teams
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

class AssetType(Enum):
    """Asset type categories"""
    PLAYER = "player"
    DRAFT_PICK = "draft_pick"
    CASH = "cash"
    TRADE_EXCEPTION = "trade_exception"

@dataclass
class TradeDetail:
    """Trade detail data structure"""
    id: int
    trade_id: str
    player_id: int
    from_team_id: Optional[int]
    to_team_id: Optional[int]
    asset_type: str
    asset_description: Optional[str]
    player_name: str
    created_at: datetime
    updated_at: datetime

class TradeDetailsService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_trade_detail(self, trade_id: str, player_id: int, from_team_id: Optional[int],
                                 to_team_id: Optional[int], asset_type: str, asset_description: Optional[str],
                                 player_name: str) -> bool:
        """Create a new trade detail"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO trade_details (
                    trade_id, player_id, from_team_id, to_team_id, asset_type, asset_description,
                    player_name, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, trade_id, player_id, from_team_id, to_team_id, asset_type, asset_description,
                player_name, now, now)
            
            await conn.close()
            logger.info(f"Created trade detail: {trade_id} - {player_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating trade detail: {e}")
            return False
    
    async def get_trade_details_by_trade_id(self, trade_id: str) -> List[TradeDetail]:
        """Get all trade details for a specific trade"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trade_details 
                WHERE trade_id = $1
                ORDER BY created_at
            """, trade_id)
            
            await conn.close()
            
            return [
                TradeDetail(
                    id=result['id'],
                    trade_id=result['trade_id'],
                    player_id=result['player_id'],
                    from_team_id=result['from_team_id'],
                    to_team_id=result['to_team_id'],
                    asset_type=result['asset_type'],
                    asset_description=result['asset_description'],
                    player_name=result['player_name'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting trade details by trade ID: {e}")
            return []
    
    async def get_trade_details_by_team(self, team_id: int, role: str = 'both') -> List[TradeDetail]:
        """Get trade details for a specific team"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            if role == 'from':
                results = await conn.fetch("""
                    SELECT * FROM trade_details 
                    WHERE from_team_id = $1
                    ORDER BY created_at DESC
                """, team_id)
            elif role == 'to':
                results = await conn.fetch("""
                    SELECT * FROM trade_details 
                    WHERE to_team_id = $1
                    ORDER BY created_at DESC
                """, team_id)
            else:  # both
                results = await conn.fetch("""
                    SELECT * FROM trade_details 
                    WHERE from_team_id = $1 OR to_team_id = $1
                    ORDER BY created_at DESC
                """, team_id)
            
            await conn.close()
            
            return [
                TradeDetail(
                    id=result['id'],
                    trade_id=result['trade_id'],
                    player_id=result['player_id'],
                    from_team_id=result['from_team_id'],
                    to_team_id=result['to_team_id'],
                    asset_type=result['asset_type'],
                    asset_description=result['asset_description'],
                    player_name=result['player_name'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting trade details by team: {e}")
            return []
    
    async def get_trade_details_by_player(self, player_id: int) -> List[TradeDetail]:
        """Get trade details for a specific player"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trade_details 
                WHERE player_id = $1
                ORDER BY created_at DESC
            """, player_id)
            
            await conn.close()
            
            return [
                TradeDetail(
                    id=result['id'],
                    trade_id=result['trade_id'],
                    player_id=result['player_id'],
                    from_team_id=result['from_team_id'],
                    to_team_id=result['to_team_id'],
                    asset_type=result['asset_type'],
                    asset_description=result['asset_description'],
                    player_name=result['player_name'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting trade details by player: {e}")
            return []
    
    async def get_trade_details_by_asset_type(self, asset_type: str, limit: int = 50) -> List[TradeDetail]:
        """Get trade details by asset type"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trade_details 
                WHERE asset_type = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, asset_type, limit)
            
            await conn.close()
            
            return [
                TradeDetail(
                    id=result['id'],
                    trade_id=result['trade_id'],
                    player_id=result['player_id'],
                    from_team_id=result['from_team_id'],
                    to_team_id=result['to_team_id'],
                    asset_type=result['asset_type'],
                    asset_description=result['asset_description'],
                    player_name=result['player_name'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting trade details by asset type: {e}")
            return []
    
    async def get_recent_trades(self, days: int = 30, limit: int = 20) -> List[TradeDetail]:
        """Get recent trades"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            results = await conn.fetch("""
                SELECT * FROM trade_details 
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                ORDER BY created_at DESC
                LIMIT $2
            """, days, limit)
            
            await conn.close()
            
            return [
                TradeDetail(
                    id=result['id'],
                    trade_id=result['trade_id'],
                    player_id=result['player_id'],
                    from_team_id=result['from_team_id'],
                    to_team_id=result['to_team_id'],
                    asset_type=result['asset_type'],
                    asset_description=result['asset_description'],
                    player_name=result['player_name'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent trades: {e}")
            return []
    
    async def get_trade_summary(self, trade_id: str) -> Dict[str, Any]:
        """Get a summary of a specific trade"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get all trade details
            details = await conn.fetch("""
                SELECT * FROM trade_details 
                WHERE trade_id = $1
                ORDER BY created_at
            """, trade_id)
            
            if not details:
                await conn.close()
                return {}
            
            # Calculate summary
            from_teams = set()
            to_teams = set()
            player_assets = []
            draft_pick_assets = []
            other_assets = []
            
            for detail in details:
                if detail['from_team_id']:
                    from_teams.add(detail['from_team_id'])
                if detail['to_team_id']:
                    to_teams.add(detail['to_team_id'])
                
                asset = {
                    'player_id': detail['player_id'],
                    'player_name': detail['player_name'],
                    'asset_type': detail['asset_type'],
                    'asset_description': detail['asset_description'],
                    'from_team_id': detail['from_team_id'],
                    'to_team_id': detail['to_team_id']
                }
                
                if detail['asset_type'] == 'player':
                    player_assets.append(asset)
                elif detail['asset_type'] == 'draft_pick':
                    draft_pick_assets.append(asset)
                else:
                    other_assets.append(asset)
            
            summary = {
                'trade_id': trade_id,
                'total_assets': len(details),
                'from_teams': list(from_teams),
                'to_teams': list(to_teams),
                'player_assets': player_assets,
                'draft_pick_assets': draft_pick_assets,
                'other_assets': other_assets,
                'created_at': details[0]['created_at'].isoformat(),
                'updated_at': details[-1]['updated_at'].isoformat()
            }
            
            await conn.close()
            return summary
            
        except Exception as e:
            logger.error(f"Error getting trade summary: {e}")
            return {}
    
    async def get_team_trade_history(self, team_id: int, days: int = 365) -> Dict[str, Any]:
        """Get trade history for a specific team"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get all trades involving the team
            details = await conn.fetch("""
                SELECT * FROM trade_details 
                WHERE from_team_id = $1 OR to_team_id = $1
                AND created_at >= NOW() - INTERVAL '$2 days'
                ORDER BY created_at DESC
            """, team_id, days)
            
            if not details:
                await conn.close()
                return {}
            
            # Calculate summary
            trades_sent = []
            trades_received = []
            unique_trades = set()
            
            for detail in details:
                unique_trades.add(detail['trade_id'])
                
                asset = {
                    'trade_id': detail['trade_id'],
                    'player_id': detail['player_id'],
                    'player_name': detail['player_name'],
                    'asset_type': detail['asset_type'],
                    'asset_description': detail['asset_description'],
                    'created_at': detail['created_at'].isoformat()
                }
                
                if detail['from_team_id'] == team_id:
                    trades_sent.append(asset)
                if detail['to_team_id'] == team_id:
                    trades_received.append(asset)
            
            summary = {
                'team_id': team_id,
                'period_days': days,
                'total_trades': len(unique_trades),
                'total_assets_sent': len(trades_sent),
                'total_assets_received': len(trades_received),
                'trades_sent': trades_sent,
                'trades_received': trades_received,
                'first_trade': details[-1]['created_at'].isoformat(),
                'last_trade': details[0]['created_at'].isoformat()
            }
            
            await conn.close()
            return summary
            
        except Exception as e:
            logger.error(f"Error getting team trade history: {e}")
            return {}
    
    async def get_trade_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get overall trade statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_trade_records,
                    COUNT(DISTINCT trade_id) as unique_trades,
                    COUNT(DISTINCT player_id) as unique_players,
                    COUNT(DISTINCT from_team_id) as unique_from_teams,
                    COUNT(DISTINCT to_team_id) as unique_to_teams,
                    COUNT(DISTINCT asset_type) as unique_asset_types,
                    COUNT(CASE WHEN asset_type = 'player' THEN 1 END) as player_trades,
                    COUNT(CASE WHEN asset_type = 'draft_pick' THEN 1 END) as draft_pick_trades,
                    COUNT(CASE WHEN from_team_id = to_team_id THEN 1 END) as same_team_trades,
                    COUNT(CASE WHEN from_team_id != to_team_id THEN 1 END) as different_team_trades
                FROM trade_details
                WHERE created_at >= NOW() - INTERVAL '$1 days'
            """, days)
            
            # Trade by asset type
            asset_type_stats = await conn.fetch("""
                SELECT 
                    asset_type,
                    COUNT(*) as total_trades,
                    COUNT(DISTINCT trade_id) as unique_trades,
                    COUNT(DISTINCT player_id) as unique_players
                FROM trade_details
                WHERE created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY asset_type
                ORDER BY total_trades DESC
            """, days)
            
            # Trade by team
            team_stats = await conn.fetch("""
                SELECT 
                    from_team_id as team_id,
                    COUNT(*) as trades_sent,
                    COUNT(DISTINCT trade_id) as unique_trade_ids_sent
                FROM trade_details
                WHERE from_team_id IS NOT NULL
                AND created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY from_team_id
                ORDER BY trades_sent DESC
                LIMIT 10
            """, days)
            
            # Most traded players
            player_stats = await conn.fetch("""
                SELECT 
                    player_id,
                    player_name,
                    COUNT(*) as trade_count,
                    COUNT(DISTINCT trade_id) as unique_trade_count,
                    COUNT(DISTINCT from_team_id) as unique_from_teams,
                    COUNT(DISTINCT to_team_id) as unique_to_teams
                FROM trade_details
                WHERE asset_type = 'player'
                AND created_at >= NOW() - INTERVAL '$1 days'
                GROUP BY player_id, player_name
                ORDER BY trade_count DESC
                LIMIT 10
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'total_trade_records': overall['total_trade_records'],
                'unique_trades': overall['unique_trades'],
                'unique_players': overall['unique_players'],
                'unique_from_teams': overall['unique_from_teams'],
                'unique_to_teams': overall['unique_to_teams'],
                'unique_asset_types': overall['unique_asset_types'],
                'player_trades': overall['player_trades'],
                'draft_pick_trades': overall['draft_pick_trades'],
                'same_team_trades': overall['same_team_trades'],
                'different_team_trades': overall['different_team_trades'],
                'asset_type_stats': [
                    {
                        'asset_type': stat['asset_type'],
                        'total_trades': stat['total_trades'],
                        'unique_trades': stat['unique_trades'],
                        'unique_players': stat['unique_players']
                    }
                    for stat in asset_type_stats
                ],
                'team_stats': [
                    {
                        'team_id': stat['team_id'],
                        'trades_sent': stat['trades_sent'],
                        'unique_trade_ids_sent': stat['unique_trade_ids_sent']
                    }
                    for stat in team_stats
                ],
                'player_stats': [
                    {
                        'player_id': stat['player_id'],
                        'player_name': stat['player_name'],
                        'trade_count': stat['trade_count'],
                        'unique_trade_count': stat['unique_trade_count'],
                        'unique_from_teams': stat['unique_from_teams'],
                        'unique_to_teams': stat['unique_to_teams']
                    }
                    for stat in player_stats
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting trade statistics: {e}")
            return {}
    
    async def search_trade_details(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search trade details by player name or trade ID"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            results = await conn.fetch("""
                SELECT * FROM trade_details 
                WHERE trade_id ILIKE $1 OR player_name ILIKE $1 OR asset_description ILIKE $1
                ORDER BY created_at DESC
                LIMIT $2
            """, search_query, limit)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'trade_id': result['trade_id'],
                    'player_id': result['player_id'],
                    'from_team_id': result['from_team_id'],
                    'to_team_id': result['to_team_id'],
                    'asset_type': result['asset_type'],
                    'asset_description': result['asset_description'],
                    'player_name': result['player_name'],
                    'created_at': result['created_at'].isoformat(),
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching trade details: {e}")
            return []

# Global instance
trade_details_service = TradeDetailsService()

async def get_trade_statistics(days: int = 30):
    """Get trade statistics"""
    return await trade_details_service.get_trade_statistics(days)

if __name__ == "__main__":
    # Test trade details service
    async def test():
        # Test getting statistics
        stats = await get_trade_statistics(30)
        print(f"Trade details statistics: {stats}")
    
    asyncio.run(test())
