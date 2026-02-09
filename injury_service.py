"""
Injury Tracking Service - Track and analyze player injuries and availability
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

class InjuryStatus(Enum):
    """Injury status types"""
    ACTIVE = "ACTIVE"
    DAY_TO_DAY = "DAY_TO_DAY"
    OUT = "OUT"
    QUESTIONABLE = "QUESTIONABLE"
    DOUBTFUL = "DOUBTFUL"
    SUSPENDED = "SUSPENDED"
    INJURED_RESERVE = "INJURED_RESERVE"

class InjurySource(Enum):
    """Injury reporting sources"""
    OFFICIAL = "official"
    TEAM_REPORT = "team_report"
    LEAGUE_REPORT = "league_report"
    MEDIA_REPORT = "media_report"
    INSIDER = "insider"

@dataclass
class Injury:
    """Injury data structure"""
    id: int
    sport_id: int
    player_id: int
    status: InjuryStatus
    status_detail: str
    is_starter_flag: bool
    probability: float
    source: InjurySource
    updated_at: datetime

class InjuryService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        
    async def create_injury_record(self, sport_id: int, player_id: int, status: InjuryStatus,
                                status_detail: str, is_starter_flag: bool, probability: float,
                                source: InjurySource) -> bool:
        """Create a new injury record"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                INSERT INTO injuries (
                    sport_id, player_id, status, status_detail, is_starter_flag,
                    probability, source, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, sport_id, player_id, status.value, status_detail, is_starter_flag,
                probability, source.value, now)
            
            await conn.close()
            logger.info(f"Created injury record: Sport {sport_id}, Player {player_id} - {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating injury record: {e}")
            return False
    
    async def update_injury_status(self, injury_id: int, status: InjuryStatus, status_detail: str,
                                is_starter_flag: bool, probability: float) -> bool:
        """Update injury status"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            now = datetime.now(timezone.utc)
            
            await conn.execute("""
                UPDATE injuries 
                SET status = $1, status_detail = $2, is_starter_flag = $3, probability = $4, updated_at = $5
                WHERE id = $6
            """, status.value, status_detail, is_starter_flag, probability, now, injury_id)
            
            await conn.close()
            logger.info(f"Updated injury {injury_id} to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating injury status: {e}")
            return False
    
    async def get_injuries_by_sport(self, sport_id: int, status: InjuryStatus = None) -> List[Injury]:
        """Get injuries for a specific sport"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM injuries 
                WHERE sport_id = $1
            """
            
            params = [sport_id]
            
            if status:
                query += " AND status = $2"
                params.append(status.value)
            
            query += " ORDER BY updated_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Injury(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    player_id=result['player_id'],
                    status=InjuryStatus(result['status']),
                    status_detail=result['status_detail'],
                    is_starter_flag=result['is_starter_flag'],
                    probability=result['probability'],
                    source=InjurySource(result['source']),
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting injuries by sport: {e}")
            return []
    
    async def get_injuries_by_player(self, player_id: int) -> List[Injury]:
        """Get injuries for a specific player"""
        try:
            conn = await asyncpg.connect(self.db_id)
            
            results = await conn.fetch("""
                SELECT * FROM injuries 
                WHERE player_id = $1
                ORDER BY updated_at DESC
            """, player_id)
            
            await conn.close()
            
            return [
                Injury(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    player_id=result['player_id'],
                    status=InjuryStatus(result['status']),
                    status_detail=result['status_detail'],
                    is_starter_flag=result['is_starter_flag'],
                    probability=result['probability'],
                    source=InjurySource(result['source']),
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting injuries by player: {e}")
            return []
    
    async def get_active_injuries(self, sport_id: int = None) -> List[Injury]:
        """Get currently active injuries"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM injuries 
                WHERE status IN ('DAY_TO_DAY', 'QUESTIONABLE', 'DOUBTFUL')
            """
            
            params = []
            
            if sport_id:
                query += " AND sport_id = $1"
                params.append(sport_id)
            
            query += " ORDER BY updated_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Injury(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    player_id=result['player_id'],
                    status=InjuryStatus(result['status']),
                    status_detail=result['status_detail'],
                    is_starter_flag=result['is_starter_flag'],
                    probability=result['probability'],
                    source=InjurySource(result['source']),
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting active injuries: {e}")
            return []
    
    async def get_out_injuries(self, sport_id: int = None) -> List[Injury]:
        """Get players who are out"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM injuries 
                WHERE status = 'OUT'
            """
            
            params = []
            
            if sport_id:
                query += " AND sport_id = $1"
                params.append(sport_id)
            
            query += " ORDER BY updated_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Injury(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    player_id=result['player_id'],
                    status=InjuryStatus(result['status']),
                    status_detail=result['status_detail'],
                    is_starter_flag=result['is_starter_flag'],
                    probability=result['probability'],
                    source=InjurySource(result['source']),
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting out injuries: {e}")
            return []
    
    async def get_starter_injuries(self, sport_id: int = None) -> List[Injury]:
        """Get injuries to starter players"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT * FROM injuries 
                WHERE is_starter_flag = TRUE
            """
            
            params = []
            
            if sport_id:
                query += " AND sport_id = $1"
                params.append(sport_id)
            
            query += " ORDER BY updated_at DESC"
            
            results = await conn.fetch(query, params)
            
            await conn.close()
            
            return [
                Injury(
                    id=result['id'],
                    sport_id=result['sport_id'],
                    player_id=result['player_id'],
                    status=InjuryStatus(result['status']),
                    status_detail=result['status_detail'],
                    is_starter_flag=result['is_starter_flag'],
                    probability=result['probability'],
                    source=InjurySource(result['source']),
                    updated_at=result['updated_at']
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting starter injuries: {e}")
            return []
    
    async def get_injury_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get injury statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall statistics
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_injuries,
                    COUNT(DISTINCT sport_id) as unique_sports,
                    COUNT(DISTINCT player_id) as unique_players,
                    COUNT(CASE WHEN status = 'OUT' THEN 1 END) as out_injuries,
                    COUNT(CASE WHEN status = 'DAY_TO_DAY' THEN 1 END) as day_to_day_injuries,
                    COUNT(CASE WHEN status = 'QUESTIONABLE' THEN 1 END) as questionable_injuries,
                    COUNT(CASE WHEN status = 'DOUBTFUL' THEN 1 END) as doubtful_injuries,
                    COUNT(CASE WHEN is_starter_flag = TRUE THEN 1 END) as starter_injuries,
                    AVG(probability) as avg_probability,
                    COUNT(CASE WHEN source = 'official' THEN 1 END) as official_injuries
                FROM injuries 
                WHERE updated_at >= NOW() - INTERVAL '$1 days'
            """, days)
            
            # By sport statistics
            by_sport = await conn.fetch("""
                SELECT 
                    sport_id,
                    COUNT(*) as total_injuries,
                    COUNT(CASE WHEN status = 'OUT' THEN 1 END) as out_injuries,
                    COUNT(CASE WHEN status = 'DAY_TO_DAY' THEN 1 END) as day_to_day_injuries,
                    COUNT(CASE WHEN status = 'QUESTIONABLE' THEN 1 END) as questionable_injuries,
                    COUNT(CASE WHEN status = 'DOUBTFUL' THEN 1 END) as doubtful_injuries,
                    COUNT(CASE WHEN is_starter_flag = TRUE THEN 1 END) as starter_injuries,
                    AVG(probability) as avg_probability,
                    COUNT(DISTINCT player_id) as unique_players
                FROM injuries 
                WHERE updated_at >= NOW() - INTERVAL '$1 days'
                GROUP BY sport_id
                ORDER BY total_injuries DESC
            """, days)
            
            # By status statistics
            by_status = await conn.fetch("""
                SELECT 
                    status,
                    COUNT(*) as total_injuries,
                    AVG(probability) as avg_probability,
                    COUNT(CASE WHEN is_starter_flag = TRUE THEN 1 END) as starter_injuries,
                    COUNT(DISTINCT player_id) as unique_players
                FROM injuries 
                WHERE updated_at >= NOW() - INTERVAL '$1 days'
                GROUP BY status
                ORDER BY total_injuries DESC
            """, days)
            
            # By source statistics
            by_source = await conn.fetch("""
                SELECT 
                    source,
                    COUNT(*) as total_injuries,
                    AVG(probability) as avg_probability,
                    COUNT(DISTINCT player_id) as unique_players
                FROM injuries 
                WHERE updated_at >= NOW() - INTERVAL '$1 days'
                GROUP BY source
                ORDER BY total_injuries DESC
            """, days)
            
            await conn.close()
            
            return {
                'period_days': days,
                'total_injuries': overall['total_injuries'],
                'unique_sports': overall['unique_sports'],
                'unique_players': overall['unique_players'],
                'out_injuries': overall['out_injuries'],
                'day_to_day_injuries': overall['day_to_day_injuries'],
                'questionable_injuries': overall['questionable_injuries'],
                'doubtful_injuries': overall['doubtful_injuries'],
                'starter_injuries': overall['starter_injuries'],
                'avg_probability': overall['avg_probability'],
                'official_injuries': overall['official_injuries'],
                'by_sport': [
                    {
                        'sport_id': sport['sport_id'],
                        'total_injuries': sport['total_injuries'],
                        'out_injuries': sport['out_injuries'],
                        'day_to_day_injuries': sport['day_to_day_injuries'],
                        'questionable_injuries': sport['questionable_injuries'],
                        'doubtful_injuries': sport['doubtful_injuries'],
                        'starter_injuries': sport['starter_injuries'],
                        'avg_probability': sport['avg_probability'],
                        'unique_players': sport['unique_players']
                    }
                    for sport in by_sport
                ],
                'by_status': [
                    {
                        'status': status['status'],
                        'total_injuries': status['total_injuries'],
                        'avg_probability': status['avg_probability'],
                        'starter_injuries': status['status_injuries'],
                        'unique_players': status['unique_players']
                    }
                    for status in by_status
                ],
                'by_source': [
                    {
                        'source': source['source'],
                        'total_injuries': source['total_injuries'],
                        'avg_probability': source['avg_probability'],
                        'unique_players': source['unique_players']
                    }
                    for source in by_source
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting injury statistics: {e}")
            return {}
    
    async def get_injury_impact_analysis(self, sport_id: int, days: int = 30) -> Dict[str, Any]:
        """Analyze injury impact on team performance"""
        try:
            conn = await asyncpg.connect(self.db_id)
            
            # Get injury data for analysis
            injuries = await conn.fetch("""
                SELECT 
                    player_id, status, status_detail, is_starter_flag, probability,
                    updated_at
                FROM injuries 
                WHERE sport_id = $1
                AND updated_at >= NOW() - INTERVAL '$1 days'
                ORDER BY updated_at DESC
            """, sport_id, days)
            
            await conn.close()
            
            if not injuries:
                return {
                    'sport_id': sport_id,
                    'period_days': days,
                    'total_injuries': 0,
                    'impact_analysis': 'No injury data available',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate impact metrics
            total_injuries = len(injuries)
            active_injuries = len([i for i in injuries if i['status'] in ['DAY_TO_DAY', 'QUESTIONABLE', 'DOUBTFUL']])
            out_injuries = len([i for i in injuries if i['status'] == 'OUT'])
            starter_injuries = len([i for i in injuries if i['is_starter_flag']])
            
            # Calculate impact scores
            starter_impact_score = (starter_injuries / total_injuries) * 100 if total_injuries > 0 else 0
            active_impact_score = (active_injuries / total_injuries) * 100 if total_injuries > 0 else 0
            out_impact_score = (out_injuries / total_injuries) * 100 if total_injuries > 0 else 0
            
            # Calculate probability-weighted impact
            weighted_impact = sum(i['probability'] for i in injuries) / total_injuries if total_injuries > 0 else 0
            
            # Identify most concerning injuries
            concerning_injuries = [
                {
                    'player_id': i['player_id'],
                    'status': i['status'],
                    'status_detail': i['status_detail'],
                    'is_starter': i['is_starter_flag'],
                    'probability': i['probability']
                }
                for i in injuries if i['probability'] > 0.7 or i['status'] == 'OUT'
            ]
            
            # Sort by probability (descending)
            concerning_injuries.sort(key=lambda x: x['probability'], reverse=True)
            
            return {
                'sport_id': sport_id,
                'period_days': days,
                'total_injuries': total_injuries,
                'active_injuries': active_injuries,
                'out_injuries': out_injuries,
                'starter_injuries': starter_injuries,
                'starter_impact_score': starter_impact_score,
                'active_impact_score': active_impact_score,
                'out_impact_score': out_impact_score,
                'weighted_impact': weighted_impact,
                'concerning_injuries': concerning_injuries[:10],
                'impact_analysis': self._generate_impact_analysis(starter_impact_score, active_impact_score, out_impact_score),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing injury impact: {e}")
            return {}
    
    def _generate_impact_analysis(self, starter_impact: float, active_impact: float, out_impact: float) -> str:
        """Generate impact analysis text"""
        if starter_impact > 20:
            return "Critical impact - many starters injured"
        elif starter_impact > 10:
            return "High impact - significant starter injuries"
        elif starter_impact > 5:
            return "Moderate impact - some starters injured"
        elif active_impact > 30:
            return "Critical impact - many active injuries"
        elif active_impact > 20:
            return "High impact - many active injuries"
        elif active_impact > 10:
            return "Moderate impact - some active injuries"
        elif out_impact > 15:
            return "High impact - many players out"
        elif out_impact > 10:
            return "Moderate impact - some players out"
        else:
            return "Low impact - manageable injury situation"
    
    async def get_injury_trends(self, sport_id: int, days: int = 30) -> Dict[str, Any]:
        """Analyze injury trends over time"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get daily injury counts
            daily_counts = await conn.fetch("""
                SELECT 
                    DATE(updated_at) as injury_date,
                    COUNT(*) as total_injuries,
                    COUNT(CASE WHEN status = 'OUT' THEN 1 END) as out_injuries,
                    COUNT(CASE WHEN status = 'DAY_TO_DAY' THEN 1 END) as day_to_day_injuries,
                    COUNT(CASE WHEN is_starter_flag = TRUE THEN 1 END) as starter_injuries
                FROM injuries 
                WHERE sport_id = $1
                AND updated_at >= NOW() - INTERVAL '$1 days'
                GROUP BY DATE(updated_at)
                ORDER BY injury_date ASC
            """, sport_id, days)
            
            await conn.close()
            
            if not daily_counts:
                return {
                    'sport_id': sport_id,
                    'period_days': days,
                    'daily_trends': [],
                    'trend_analysis': 'No injury data available',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate trend analysis
            if len(daily_counts) >= 7:
                recent_avg = sum(d['total_injuries'] for d in daily_counts[-7:]) / 7
                earlier_avg = sum(d['total_injuries'] for d in daily_counts[-14:-7]) / 7 if len(daily_counts) >= 14 else recent_avg
                
                if recent_avg > earlier_avg * 1.2:
                    trend_analysis = "Increasing injuries - concerning trend"
                elif recent_avg < earlier_avg * 0.8:
                    trend_analysis = "Decreasing injuries - positive trend"
                else:
                    trend_analysis = "Stable injury rate"
            else:
                trend_analysis = "Insufficient data for trend analysis"
            
            return {
                'sport_id': sport_id,
                'period_days': days,
                'daily_trends': [
                    {
                        'date': str(row['injury_date']),
                        'total_injuries': row['total_injuries'],
                        'out_injuries': row['out_injuries'],
                        'day_to_day_injuries': row['day_to_day_injuries'],
                        'starter_injuries': row['starter_injuries']
                    }
                    for row in daily_counts
                ],
                'trend_analysis': trend_analysis,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing injury trends: {e}")
            return {}
    
    async def search_injuries(self, query: str, sport_id: int = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search injuries by player ID or status detail"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            search_query = f"%{query}%"
            
            sql_query = """
                SELECT * FROM injuries 
                WHERE player_id::text ILIKE $1
            """
            
            params = [search_query]
            
            if sport_id:
                sql_query += " AND sport_id = $2"
                params.append(sport_id)
            
            sql_query += " ORDER BY updated_at DESC LIMIT $3"
            params.append(limit)
            
            results = await conn.fetch(sql_query, params)
            
            await conn.close()
            
            return [
                {
                    'id': result['id'],
                    'sport_id': result['sport_id'],
                    'player_id': result['player_id'],
                    'status': result['status'],
                    'status_detail': result['status_detail'],
                    'is_starter_flag': result['is_starter_flag'],
                    'probability': result['probability'],
                    'source': result['source'],
                    'updated_at': result['updated_at'].isoformat()
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching injuries: {e}")
            return []

# Global instance
injury_service = InjuryService()

async def get_injury_statistics(days: int = 30):
    """Get injury statistics"""
    return await injury_service.get_injury_statistics(days)

if __name__ == "__main__":
    # Test injury service
    async def test():
        # Test getting statistics
        stats = await get_injury_statistics(30)
        print(f"Injury statistics: {stats}")
    
    asyncio.run(test())
