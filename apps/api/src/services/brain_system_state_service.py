"""
Brain System State Service - Comprehensive system state monitoring and management
"""
import asyncio
import os
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import dataclass
from enum import Enum
from db.session import async_session_maker
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """System status levels"""
    INITIALIZING = "initializing"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    RECOVERING = "recovering"
    ACTIVE = "active"
    HEALTHY = "healthy"
    OPTIMAL = "optimal"

class SportPriority(Enum):
    """Sport priority levels"""
    LOW_PRIORITY = "low_priority"
    BALANCED = "balanced"
    NFL_PRIORITY = "nfl_priority"
    NBA_PRIORITY = "nba_priority"
    MLB_PRIORITY = "mlb_priority"
    SUPER_BOWL_PRIORITY = "super_bowl_priority"
    MULTI_SPORT = "multi_sport"

@dataclass
class SystemState:
    """System state data structure"""
    cycle_count: int
    overall_status: SystemStatus
    heals_attempted: int
    heals_succeeded: int
    consecutive_failures: int
    sport_priority: SportPriority
    quota_budget: int
    auto_commit_enabled: bool
    git_commits_made: int
    betting_opportunities_found: int
    strong_bets_identified: int
    last_betting_scan: Optional[datetime]
    top_betting_opportunities: Dict[str, Any]
    last_cycle_duration_ms: int
    uptime_hours: float

class BrainSystemStateService:
    def __init__(self):
        self.state_monitoring_active = False
        self.current_state = None
        
    async def get_current_state(self) -> Optional[SystemState]:
        """Get current system state"""
        try:
            async with async_session_maker() as conn:
                result = await conn.execute(text("""
                    SELECT * FROM brain_system_state 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """))
                row = result.mappings().first()
                if row:
                    return SystemState(
                        cycle_count=row['cycle_count'],
                        overall_status=SystemStatus(row['overall_status']),
                        heals_attempted=row['heals_attempted'],
                        heals_succeeded=row['heals_succeeded'],
                        consecutive_failures=row['consecutive_failures'],
                        sport_priority=SportPriority(row['sport_priority']),
                        quota_budget=row['quota_budget'],
                        auto_commit_enabled=row['auto_commit_enabled'],
                        git_commits_made=row['git_commits_made'],
                        betting_opportunities_found=row['betting_opportunities_found'],
                        strong_bets_identified=row['strong_bets_identified'],
                        last_betting_scan=row['last_betting_scan'],
                        top_betting_opportunities=json.loads(row['top_betting_opportunities']),
                        last_cycle_duration_ms=row['last_cycle_duration_ms'],
                        uptime_hours=row['uptime_hours']
                    )
            return None
        except Exception as e:
            logger.error(f"Error getting current state: {e}")
            return None
    
    async def update_system_state(self, state: SystemState) -> bool:
        """Update system state in database"""
        try:
            async with async_session_maker() as conn:
                await conn.execute(text("""
                    INSERT INTO brain_system_state (
                        cycle_count, overall_status, heals_attempted, heals_succeeded,
                        consecutive_failures, sport_priority, quota_budget, auto_commit_enabled,
                        git_commits_made, betting_opportunities_found, strong_bets_identified,
                        last_betting_scan, top_betting_opportunities, last_cycle_duration_ms, uptime_hours
                    ) VALUES (:p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9, :p10, :p11, :p12, :p13, :p14, :p15)
                """), {
                    "p1": state.cycle_count,
                    "p2": state.overall_status.value,
                    "p3": state.heals_attempted,
                    "p4": state.heals_succeeded,
                    "p5": state.consecutive_failures,
                    "p6": state.sport_priority.value,
                    "p7": state.quota_budget,
                    "p8": state.auto_commit_enabled,
                    "p9": state.git_commits_made,
                    "p10": state.betting_opportunities_found,
                    "p11": state.strong_bets_identified,
                    "p12": state.last_betting_scan,
                    "p13": json.dumps(state.top_betting_opportunities),
                    "p14": state.last_cycle_duration_ms,
                    "p15": state.uptime_hours
                })
                await conn.commit()
            
            logger.info(f"Updated system state: {state.overall_status.value}")
            return True
        except Exception as e:
            logger.error(f"Error updating system state: {e}")
            return False
    
    async def calculate_system_status(self, metrics: Dict[str, Any]) -> SystemStatus:
        """Calculate overall system status based on metrics"""
        # Status calculation logic
        health_score = 0
        issues = []
        
        # Check healing success rate
        if metrics.get('heals_attempted', 0) > 0:
            healing_success_rate = metrics['heals_succeeded'] / metrics['heals_attempted']
            if healing_success_rate >= 0.9:
                health_score += 30
            elif healing_success_rate >= 0.7:
                health_score += 20
            elif healing_success_rate >= 0.5:
                health_score += 10
            else:
                issues.append("Low healing success rate")
        
        # Check consecutive failures
        if metrics.get('consecutive_failures', 0) >= 3:
            health_score -= 20
            issues.append("Multiple consecutive failures")
        elif metrics.get('consecutive_failures', 0) >= 2:
            health_score -= 10
            issues.append("Recent failures")
        
        # Check uptime
        if metrics.get('uptime_hours', 0) < 1:
            health_score -= 30
            issues.append("Low uptime")
        elif metrics.get('uptime_hours', 0) < 6:
            health_score -= 15
            issues.append("Recent startup")
        
        # Check betting opportunities
        if metrics.get('betting_opportunities_found', 0) == 0:
            health_score -= 20
            issues.append("No betting opportunities")
        elif metrics.get('betting_opportunities_found', 0) < 5:
            health_score -= 10
            issues.append("Low opportunity count")
        
        # Check cycle performance
        if metrics.get('last_cycle_duration_ms', 0) > 60000:  # > 1 minute
            health_score -= 15
            issues.append("Slow cycle performance")
        elif metrics.get('last_cycle_duration_ms', 0) > 120000:  # > 2 minutes
            health_score -= 30
            issues.append("Very slow cycle performance")
        
        # Check auto commit status
        if not metrics.get('auto_commit_enabled', True):
            health_score -= 10
            issues.append("Auto commit disabled")
        
        # Check quota budget
        if metrics.get('quota_budget', 100) < 50:
            health_score -= 15
            issues.append("Low quota budget")
        
        # Determine status
        if health_score >= 80:
            return SystemStatus.OPTIMAL
        elif health_score >= 60:
            return SystemStatus.HEALTHY
        elif health_score >= 40:
            return SystemStatus.ACTIVE
        elif health_score >= 20:
            return SystemStatus.RECOVERING
        elif health_score >= 0:
            return SystemStatus.DEGRADED
        else:
            return SystemStatus.MAINTENANCE
    
    async def determine_sport_priority(self, current_time: datetime) -> SportPriority:
        """Determine sport priority based on current time and events"""
        # Super Bowl priority during Super Bowl period
        if current_time.month == 2 and current_time.day >= 7 and current_time.day <= 14:
            return SportPriority.SUPER_BOWL_PRIORITY
        
        # NFL priority during NFL season
        if current_time.month in [9, 10, 11, 12, 1]:  # Sept-Jan
            return SportPriority.NFL_PRIORITY
        
        # NBA priority during NBA season
        if current_time.month in [10, 11, 12, 1, 2, 3, 4, 5, 6]:  # Oct-Jun
            return SportPriority.NBA_PRIORITY
        
        # MLB priority during MLB season
        if current_time.month in [3, 4, 5, 6, 7, 8, 9]:  # Mar-Sep
            return SportPriority.MLB_PRIORITY
        
        # Multi-sport during overlapping seasons
        if current_time.month in [10, 11, 12]:  # Oct-Dec (NFL + NBA)
            return SportPriority.MULTI_SPORT
        
        return SportPriority.BALANCED
    
    async def calculate_quota_budget(self, system_status: SystemStatus, sport_priority: SportPriority) -> int:
        """Calculate quota budget based on system status and sport priority"""
        base_budget = 100
        
        # Adjust based on system status
        if system_status == SystemStatus.OPTIMAL:
            status_multiplier = 1.2
        elif system_status == SystemStatus.HEALTHY:
            status_multiplier = 1.0
        elif system_status == SystemStatus.ACTIVE:
            status_multiplier = 0.9
        elif system_status == SystemStatus.RECOVERING:
            status_multiplier = 0.7
        elif system_status == SystemStatus.DEGRADED:
            status_multiplier = 0.5
        else:  # MAINTENANCE
            status_multiplier = 0.3
        
        # Adjust based on sport priority
        if sport_priority == SportPriority.SUPER_BOWL_PRIORITY:
            priority_multiplier = 1.5
        elif sport_priority == SportPriority.NFL_PRIORITY:
            priority_multiplier = 1.3
        elif sport_priority == SportPriority.NBA_PRIORITY:
            priority_multiplier = 1.2
        elif sport_priority == SportPriority.MLB_PRIORITY:
            priority_multiplier = 1.1
        elif sport_priority == SportPriority.MULTI_SPORT:
            priority_multiplier = 1.4
        else:  # BALANCED or LOW_PRIORITY
            priority_multiplier = 1.0
        
        return int(base_budget * status_multiplier * priority_multiplier)
    
    async def update_cycle_metrics(self, cycle_start_time: datetime, opportunities: Dict[str, Any], 
                                heals_attempted: int, heals_succeeded: int, git_commits: int) -> bool:
        """Update cycle metrics after a cycle completes"""
        try:
            current_state = await self.get_current_state()
            if not current_state:
                return False
            
            # Calculate new metrics
            new_cycle_count = current_state.cycle_count + 1
            new_consecutive_failures = 0 if heals_succeeded > 0 else current_state.consecutive_failures + 1
            
            cycle_duration_ms = int((datetime.now(timezone.utc) - cycle_start_time).total_seconds() * 1000)
            new_uptime_hours = current_state.uptime_hours + (cycle_duration_ms / 3600000)
            
            # Update top betting opportunities
            total_opps = opportunities.get('total_opportunities', 0)
            strong_bets = opportunities.get('strong_bets', 0)
            medium_bets = opportunities.get('medium_bets', 0)
            weak_bets = opportunities.get('weak_bets', 0)
            sports_breakdown = opportunities.get('sports_breakdown', {})
            
            # Calculate new state
            metrics = {
                'heals_attempted': current_state.heals_attempted + heals_attempted,
                'heals_succeeded': current_state.heals_succeeded + heals_succeeded,
                'consecutive_failures': new_consecutive_failures,
                'last_cycle_duration_ms': cycle_duration_ms,
                'uptime_hours': new_uptime_hours,
                'betting_opportunities_found': current_state.betting_opportunities_found + total_opps,
                'strong_bets_identified': current_state.strong_bets_identified + strong_bets,
                'git_commits_made': current_state.git_commits_made + git_commits
            }
            
            # Calculate new status
            new_status = await self.calculate_system_status(metrics)
            new_sport_priority = await self.determine_sport_priority(datetime.now(timezone.utc))
            new_quota_budget = await self.calculate_quota_budget(new_status, new_sport_priority)
            
            # Create updated state
            updated_state = SystemState(
                cycle_count=new_cycle_count,
                overall_status=new_status,
                heals_attempted=metrics['heals_attempted'],
                heals_succeeded=metrics['heals_succeeded'],
                consecutive_failures=new_consecutive_failures,
                sport_priority=new_sport_priority,
                quota_budget=new_quota_budget,
                auto_commit_enabled=current_state.auto_commit_enabled,
                git_commits_made=metrics['git_commits_made'],
                betting_opportunities_found=metrics['betting_opportunities_found'],
                strong_bets_identified=metrics['strong_bets_identified'],
                last_betting_scan=datetime.now(timezone.utc),
                top_betting_opportunities={
                    'total_opportunities': total_opps,
                    'strong_bets': strong_bets,
                    'medium_bets': medium_bets,
                    'weak_bets': weak_bets,
                    'sports_breakdown': sports_breakdown
                },
                last_cycle_duration_ms=cycle_duration_ms,
                uptime_hours=new_uptime_hours
            )
            
            # Update state
            success = await self.update_system_state(updated_state)
            
            if success:
                logger.info(f"Updated system state: {new_status.value} (Cycle {new_cycle_count})")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating cycle metrics: {e}")
            return False
    
    async def get_system_state_history(self, hours: int = 24) -> List[Dict]:
        """Get system state history"""
        try:
            async with async_session_maker() as conn:
                result = await conn.execute(text("""
                    SELECT * FROM brain_system_state 
                    WHERE timestamp >= NOW() - make_interval(hours => :h)
                    ORDER BY timestamp DESC
                """), {"h": hours})
                return [dict(row) for row in result.mappings()]
        except Exception as e:
            logger.error(f"Error getting system state history: {e}")
            return []
    
    async def get_system_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            async with async_session_maker() as conn:
                result_overall = await conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_states,
                        COUNT(CASE WHEN overall_status = 'optimal' THEN 1 END) as optimal_states,
                        COUNT(CASE WHEN overall_status = 'healthy' THEN 1 END) as healthy_states,
                        COUNT(CASE WHEN overall_status = 'active' THEN 1 END) as active_states,
                        COUNT(CASE WHEN overall_status = 'degraded' THEN 1 END) as degraded_states,
                        COUNT(CASE WHEN overall_status = 'maintenance' THEN 1 END) as maintenance_states,
                        COUNT(CASE WHEN overall_status = 'recovering' THEN 1 END) as recovering_states,
                        AVG(heals_attempted) as avg_heals_attempted,
                        AVG(heals_succeeded) as avg_heals_succeeded,
                        AVG(consecutive_failures) as avg_consecutive_failures,
                        AVG(last_cycle_duration_ms) as avg_cycle_duration,
                        AVG(uptime_hours) as avg_uptime,
                        SUM(git_commits_made) as total_commits,
                        SUM(betting_opportunities_found) as total_opportunities,
                        SUM(strong_bets_identified) as total_strong_bets
                    FROM brain_system_state 
                    WHERE timestamp >= NOW() - make_interval(hours => :h)
                """), {"h": hours})
                overall = result_overall.mappings().first()
                if not overall or not overall['total_states']:
                    return {}
                
                result_status = await conn.execute(text("""
                    SELECT timestamp, overall_status, heals_attempted, heals_succeeded, uptime_hours
                    FROM brain_system_state 
                    WHERE timestamp >= NOW() - make_interval(hours => :h)
                    ORDER BY timestamp ASC
                """), {"h": hours})
                status_timeline = result_status.mappings().all()
                
                result_perf = await conn.execute(text("""
                    SELECT timestamp, cycle_count, betting_opportunities_found, strong_bets_identified, last_cycle_duration_ms
                    FROM brain_system_state 
                    WHERE timestamp >= NOW() - make_interval(hours => :h)
                    ORDER BY timestamp ASC
                """), {"h": hours})
                performance_trends = result_perf.mappings().all()
                
            success_rate = (overall['avg_heals_succeeded'] / overall['avg_heals_attempted'] * 100) if overall['avg_heals_attempted'] and overall['avg_heals_attempted'] > 0 else 0
            
            return {
                'period_hours': hours,
                'total_states': overall['total_states'],
                'optimal_states': overall['optimal_states'],
                'healthy_states': overall['healthy_states'],
                'active_states': overall['active_states'],
                'degraded_states': overall['degraded_states'],
                'maintenance_states': overall['maintenance_states'],
                'recovering_states': overall['recovering_states'],
                'healing_success_rate': success_rate,
                'avg_heals_attempted': overall['avg_heals_attempted'] or 0,
                'avg_heals_succeeded': overall['avg_heals_succeeded'] or 0,
                'avg_consecutive_failures': overall['avg_consecutive_failures'] or 0,
                'avg_cycle_duration_ms': overall['avg_cycle_duration'] or 0,
                'avg_uptime_hours': overall['avg_uptime'] or 0,
                'total_commits': overall['total_commits'] or 0,
                'total_opportunities': overall['total_opportunities'] or 0,
                'total_strong_bets': overall['total_strong_bets'] or 0,
                'status_timeline': [dict(row) for row in status_timeline],
                'performance_trends': [dict(row) for row in performance_trends]
            }
        except Exception as e:
            logger.error(f"Error getting system performance: {e}")
            return {}
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics for dashboard"""
        try:
            current_state = await self.get_current_state()
            if not current_state:
                return {
                    "status": "unknown",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            return {
                "status": current_state.overall_status.value,
                "cycle_count": current_state.cycle_count,
                "heals_attempted": current_state.heals_attempted,
                "heals_succeeded": current_state.heals_succeeded,
                "consecutive_failures": current_state.consecutive_failures,
                "healing_success_rate": (current_state.heals_succeeded / current_state.heals_attempted * 100) if current_state.heals_attempted > 0 else 0,
                "sport_priority": current_state.sport_priority.value,
                "quota_budget": current_state.quota_budget,
                "auto_commit_enabled": current_state.auto_commit_enabled,
                "git_commits_made": current_state.git_commits_made,
                "betting_opportunities_found": current_state.betting_opportunities_found,
                "strong_bets_identified": current_state.strong_bets_identified,
                "last_betting_scan": current_state.last_betting_scan.isoformat() if current_state.last_betting_scan else None,
                "top_betting_opportunities": current_state.top_betting_opportunities,
                "last_cycle_duration_ms": current_state.last_cycle_duration_ms,
                "uptime_hours": current_state.uptime_hours,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# Global instance
system_state_service = BrainSystemStateService()

async def get_current_system_state():
    """Get current system state"""
    return await system_state_service.get_current_state()

async def get_system_performance(hours: int = 24):
    """Get system performance metrics"""
    return await system_state_service.get_system_performance(hours)

if __name__ == "__main__":
    # Test system state service
    async def test():
        # Test getting current state
        state = await get_current_system_state()
        if state:
            print(f"Current state: {state.overall_status.value}")
            print(f"Cycle count: {state.cycle_count}")
            print(f"Uptime: {state.uptime_hours:.1f} hours")
        
        # Test performance
        performance = await get_system_performance()
        print(f"Performance: {performance}")
    
    asyncio.run(test())
