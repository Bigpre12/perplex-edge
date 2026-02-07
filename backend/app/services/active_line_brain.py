"""
Active Line Monitoring Brain - Real-time line and stat monitoring service.

Continuously monitors:
- Line movements across sportsbooks
- Over/under opportunities and changes
- Player stat increases and trends
- Dynamic endpoint updates with real-time data
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text, func

from app.core.config import get_settings
from app.core.database import get_session_maker
from app.models import (
    ModelPick, Player, Game, Team, Market, Line, 
    Injury, PlayerGameStats, Sport
)
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

@dataclass
class LineMovement:
    """Track line movement data."""
    player_id: int
    market_id: int
    stat_type: str
    line_value: float
    previous_line: float
    movement_amount: float
    movement_pct: float
    sportsbook: str
    timestamp: datetime
    direction: str  # "up", "down", "stable"
    
@dataclass
class OverUnderOpportunity:
    """Over/under opportunity tracking."""
    player_id: int
    player_name: str
    stat_type: str
    current_line: float
    model_projection: float
    over_edge: float
    under_edge: float
    confidence: float
    sportsbooks: List[str]
    timestamp: datetime
    recommendation: str  # "over", "under", "pass"

class ActiveLineBrain:
    """Active brain for real-time line and stat monitoring."""
    
    def __init__(self):
        self.settings = get_settings()
        self.is_running = False
        self.cycle_count = 0
        self.last_cycle_time = None
        
        # Tracking data structures
        self.line_movements: deque = deque(maxlen=1000)
        self.over_under_opportunities: Dict[str, OverUnderOpportunity] = {}
        self.active_players: Set[int] = set()
        self.ruled_out_players: Set[int] = set()
        
        # Performance metrics
        self.processed_lines = 0
        self.detected_opportunities = 0
        self.updated_endpoints = 0
        self.errors = deque(maxlen=100)
        
        # Configuration
        self.monitoring_interval = 30  # seconds
        self.line_movement_threshold = 0.5  # minimum line movement to track
        self.edge_threshold = 0.05  # 5% edge for over/under
        
    async def start_monitoring(self):
        """Start the active line monitoring brain."""
        if self.is_running:
            logger.warning("[ACTIVE_BRAIN] Already running")
            return
            
        self.is_running = True
        logger.info("[ACTIVE_BRAIN] Starting real-time line monitoring")
        
        try:
            while self.is_running:
                cycle_start = datetime.now(timezone.utc)
                
                try:
                    await self.monitoring_cycle()
                    self.cycle_count += 1
                    self.last_cycle_time = cycle_start
                    
                    # Log cycle metrics
                    cycle_duration = (datetime.now(timezone.utc) - cycle_start).total_seconds()
                    logger.info(
                        f"[ACTIVE_BRAIN] Cycle {self.cycle_count} completed in {cycle_duration:.2f}s - "
                        f"Lines: {self.processed_lines}, Opportunities: {self.detected_opportunities}"
                    )
                    
                except Exception as e:
                    logger.error(f"[ACTIVE_BRAIN] Cycle {self.cycle_count} error: {e}")
                    self.errors.append({
                        "cycle": self.cycle_count,
                        "timestamp": datetime.now(timezone.utc),
                        "error": str(e)
                    })
                
                # Sleep until next cycle
                await asyncio.sleep(self.monitoring_interval)
                
        except asyncio.CancelledError:
            logger.info("[ACTIVE_BRAIN] Monitoring cancelled")
        except Exception as e:
            logger.error(f"[ACTIVE_BRAIN] Fatal error: {e}")
        finally:
            self.is_running = False
            logger.info("[ACTIVE_BRAIN] Monitoring stopped")
    
    async def stop_monitoring(self):
        """Stop the active line monitoring brain."""
        self.is_running = False
        logger.info("[ACTIVE_BRAIN] Stop signal sent")
    
    async def monitoring_cycle(self):
        """Single monitoring cycle."""
        async with get_session_maker()() as db:
            # 1. Monitor line movements
            await self.monitor_line_movements(db)
            
            # 2. Detect over/under opportunities
            await self.detect_over_under_opportunities(db)
            
            # 3. Update dynamic endpoints
            await self.update_dynamic_endpoints(db)
            
            # 4. Cache results for fast access
            await self.cache_monitoring_results()
    
    async def monitor_line_movements(self, db: AsyncSession):
        """Monitor line movements across all sportsbooks."""
        try:
            # Get current lines with historical comparison
            result = await db.execute(text("""
                SELECT 
                    l_current.game_id, l_current.player_id, l_current.market_id,
                    l_current.line_value as current_line, l_current.sportsbook,
                    l_current.odds as current_odds, l_current.updated_at as current_time,
                    l_historical.line_value as historical_line, l_historical.updated_at as historical_time,
                    p.name as player_name, m.stat_type, g.start_time as game_time
                FROM lines l_current
                LEFT JOIN lines l_historical ON (
                    l_current.game_id = l_historical.game_id 
                    AND l_current.player_id = l_historical.player_id
                    AND l_current.market_id = l_historical.market_id
                    AND l_current.sportsbook = l_historical.sportsbook
                    AND l_historical.updated_at < l_current.updated_at
                )
                JOIN players p ON l_current.player_id = p.id
                JOIN markets m ON l_current.market_id = m.id
                JOIN games g ON l_current.game_id = g.id
                WHERE l_current.is_current = true
                AND l_current.updated_at > NOW() - INTERVAL '1 hour'
                AND g.start_time > NOW() - INTERVAL '6 hours'
                AND g.start_time < NOW() + INTERVAL '48 hours'
                ORDER BY l_current.updated_at DESC
                LIMIT 500
            """))
            
            rows = result.fetchall()
            self.processed_lines = len(rows)
            
            for row in rows:
                if row.historical_line and row.historical_line != row.current_line:
                    movement = row.current_line - row.historical_line
                    movement_pct = (movement / row.historical_line) * 100 if row.historical_line else 0
                    
                    if abs(movement) >= self.line_movement_threshold:
                        direction = "up" if movement > 0 else "down"
                        
                        line_movement = LineMovement(
                            player_id=row.player_id,
                            market_id=row.market_id,
                            stat_type=row.stat_type,
                            line_value=row.current_line,
                            previous_line=row.historical_line,
                            movement_amount=movement,
                            movement_pct=movement_pct,
                            sportsbook=row.sportsbook,
                            timestamp=row.current_time,
                            direction=direction
                        )
                        
                        self.line_movements.append(line_movement)
                        
                        # Log significant movements
                        if abs(movement_pct) >= 5.0:  # 5%+ movement
                            logger.info(
                                f"[ACTIVE_BRAIN] SIGNIFICANT MOVEMENT: {row.player_name} "
                                f"{row.stat_type} {row.historical_line}→{row.current_line} "
                                f"({row.sportsbook}) {direction} {movement_pct:.1f}%"
                            )
            
        except Exception as e:
            logger.error(f"[ACTIVE_BRAIN] Line movement monitoring error: {e}")
            raise
    
    async def detect_over_under_opportunities(self, db: AsyncSession):
        """Detect over/under opportunities based on model projections."""
        try:
            # Get model picks with current lines
            result = await db.execute(text("""
                SELECT 
                    mp.id, mp.player_id, mp.game_id, mp.market_id,
                    mp.model_projection, mp.line_value, mp.side,
                    mp.expected_value, mp.confidence_score,
                    p.name as player_name, m.stat_type,
                    l_current.line_value as current_line, l_current.sportsbook
                FROM model_picks mp
                JOIN players p ON mp.player_id = p.id
                JOIN markets m ON mp.market_id = m.id
                LEFT JOIN lines l_current ON (
                    mp.game_id = l_current.game_id 
                    AND mp.player_id = l_current.player_id
                    AND mp.market_id = l_current.market_id
                    AND l_current.is_current = true
                )
                WHERE mp.generated_at > NOW() - INTERVAL '2 hours'
                AND mp.line_value IS NOT NULL AND mp.line_value > 0
                AND mp.model_projection IS NOT NULL
                AND l_current.line_value IS NOT NULL
                ORDER BY mp.expected_value DESC
                LIMIT 200
            """))
            
            rows = result.fetchall()
            opportunities = []
            
            for row in rows:
                current_line = row.current_line or row.line_value
                model_proj = row.model_projection
                
                # Calculate edges
                over_edge = ((model_proj - current_line) / current_line) * 100 if current_line else 0
                under_edge = ((current_line - model_proj) / current_line) * 100 if current_line else 0
                
                # Determine recommendation
                recommendation = "pass"
                edge = 0
                if over_edge >= self.edge_threshold * 100:
                    recommendation = "over"
                    edge = over_edge
                elif under_edge >= self.edge_threshold * 100:
                    recommendation = "under"
                    edge = under_edge
                
                if recommendation != "pass":
                    opportunity_key = f"{row.player_id}_{row.market_id}"
                    
                    opportunity = OverUnderOpportunity(
                        player_id=row.player_id,
                        player_name=row.player_name,
                        stat_type=row.stat_type,
                        current_line=current_line,
                        model_projection=model_proj,
                        over_edge=over_edge,
                        under_edge=under_edge,
                        confidence=row.confidence_score or 0.5,
                        sportsbooks=[row.sportsbook] if row.sportsbook else [],
                        timestamp=datetime.now(timezone.utc),
                        recommendation=recommendation
                    )
                    
                    # Update or add opportunity
                    if opportunity_key in self.over_under_opportunities:
                        existing = self.over_under_opportunities[opportunity_key]
                        if edge > max(existing.over_edge, existing.under_edge):
                            self.over_under_opportunities[opportunity_key] = opportunity
                    else:
                        self.over_under_opportunities[opportunity_key] = opportunity
                    
                    opportunities.append(opportunity)
            
            self.detected_opportunities = len(opportunities)
            
            # Log top opportunities
            top_opps = sorted(opportunities, key=lambda x: max(x.over_edge, x.under_edge), reverse=True)[:5]
            for opp in top_opps:
                logger.info(
                    f"[ACTIVE_BRAIN] OPPORTUNITY: {opp.player_name} {opp.stat_type} "
                    f"{opp.current_line} (proj: {opp.model_projection}) - {opp.recommendation} "
                    f"edge: {max(opp.over_edge, opp.under_edge):.1f}%"
                )
            
        except Exception as e:
            logger.error(f"[ACTIVE_BRAIN] Over/under detection error: {e}")
            raise
    
    async def update_dynamic_endpoints(self, db: AsyncSession):
        """Update dynamic endpoints with real-time data."""
        try:
            # Prepare real-time data for endpoints
            realtime_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cycle_count": self.cycle_count,
                "line_movements": [
                    {
                        "player_id": lm.player_id,
                        "stat_type": lm.stat_type,
                        "current_line": lm.line_value,
                        "previous_line": lm.previous_line,
                        "movement": lm.movement_amount,
                        "movement_pct": lm.movement_pct,
                        "sportsbook": lm.sportsbook,
                        "direction": lm.direction,
                        "timestamp": lm.timestamp.isoformat()
                    }
                    for lm in list(self.line_movements)[-20:]  # Last 20 movements
                ],
                "opportunities": [
                    {
                        "player_id": opp.player_id,
                        "player_name": opp.player_name,
                        "stat_type": opp.stat_type,
                        "current_line": opp.current_line,
                        "model_projection": opp.model_projection,
                        "recommendation": opp.recommendation,
                        "edge": max(opp.over_edge, opp.under_edge),
                        "confidence": opp.confidence,
                        "sportsbooks": opp.sportsbooks,
                        "timestamp": opp.timestamp.isoformat()
                    }
                    for opp in list(self.over_under_opportunities.values())[:10]  # Top 10 opportunities
                ],
                "metrics": {
                    "processed_lines": self.processed_lines,
                    "detected_opportunities": self.detected_opportunities,
                    "active_players": len(self.active_players),
                    "ruled_out_players": len(self.ruled_out_players),
                    "updated_endpoints": self.updated_endpoints
                }
            }
            
            # Cache for API endpoints
            await cache_service.set("active_brain_realtime_data", realtime_data, ttl=60)
            self.updated_endpoints += 1
            
        except Exception as e:
            logger.error(f"[ACTIVE_BRAIN] Dynamic endpoint update error: {e}")
            raise
    
    async def cache_monitoring_results(self):
        """Cache monitoring results for fast API access."""
        try:
            # Cache line movements
            recent_movements = list(self.line_movements)[-50:]
            await cache_service.set("line_movements", [
                {
                    "player_id": lm.player_id,
                    "stat_type": lm.stat_type,
                    "movement": lm.movement_amount,
                    "direction": lm.direction,
                    "sportsbook": lm.sportsbook,
                    "timestamp": lm.timestamp.isoformat()
                }
                for lm in recent_movements
            ], ttl=300)
            
            # Cache opportunities
            opportunities = list(self.over_under_opportunities.values())
            await cache_service.set("over_under_opportunities", [
                {
                    "player_id": opp.player_id,
                    "player_name": opp.player_name,
                    "stat_type": opp.stat_type,
                    "recommendation": opp.recommendation,
                    "edge": max(opp.over_edge, opp.under_edge),
                    "confidence": opp.confidence,
                    "timestamp": opp.timestamp.isoformat()
                }
                for opp in sorted(opportunities, key=lambda x: max(x.over_edge, x.under_edge), reverse=True)[:20]
            ], ttl=300)
            
            # Cache ruled out players
            await cache_service.set("ruled_out_players", {
                "players": list(self.ruled_out_players),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "count": len(self.ruled_out_players)
            }, ttl=600)
            
        except Exception as e:
            logger.error(f"[ACTIVE_BRAIN] Caching error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current brain status."""
        return {
            "is_running": self.is_running,
            "cycle_count": self.cycle_count,
            "last_cycle_time": self.last_cycle_time.isoformat() if self.last_cycle_time else None,
            "monitoring_interval": self.monitoring_interval,
            "metrics": {
                "processed_lines": self.processed_lines,
                "detected_opportunities": self.detected_opportunities,
                "updated_endpoints": self.updated_endpoints,
                "active_players": len(self.active_players),
                "ruled_out_players": len(self.ruled_out_players)
            },
            "tracking": {
                "line_movements": len(self.line_movements),
                "over_under_opportunities": len(self.over_under_opportunities)
            },
            "recent_errors": list(self.errors)[-5:] if self.errors else []
        }

# Global active brain instance
active_line_brain = ActiveLineBrain()
