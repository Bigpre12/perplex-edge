"""
Brain Decision Tracking Service - Tracks and analyzes brain decision-making process
"""
import asyncio
import asyncpg
import os
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BrainDecision:
    """Brain decision data structure"""
    category: str
    action: str
    reasoning: str
    details: Dict[str, Any]
    duration_ms: Optional[int] = None
    correlation_id: Optional[str] = None

class BrainDecisionTracker:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.decision_categories = [
            'player_recommendation',
            'parlay_construction', 
            'risk_management',
            'market_analysis',
            'model_optimization',
            'anomaly_response',
            'user_feedback',
            'system_maintenance'
        ]
        
    async def record_decision(self, decision: BrainDecision, outcome: str = 'pending') -> bool:
        """Record a brain decision in the database"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            correlation_id = decision.correlation_id or str(uuid.uuid4())
            
            await conn.execute("""
                INSERT INTO brain_decisions (
                    category, action, reasoning, outcome, details,
                    duration_ms, correlation_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
                decision.category,
                decision.action,
                decision.reasoning,
                outcome,
                json.dumps(decision.details),
                decision.duration_ms,
                correlation_id
            )
            
            await conn.close()
            logger.info(f"Recorded decision: {decision.category} - {decision.action}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording decision: {e}")
            return False
    
    async def update_decision_outcome(self, correlation_id: str, outcome: str, 
                                   additional_details: Optional[Dict] = None) -> bool:
        """Update the outcome of a decision"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            if additional_details:
                # Merge additional details with existing details
                await conn.execute("""
                    UPDATE brain_decisions 
                    SET outcome = $1, 
                        details = details || $2::jsonb
                    WHERE correlation_id = $3
                """, outcome, json.dumps(additional_details), correlation_id)
            else:
                await conn.execute("""
                    UPDATE brain_decisions 
                    SET outcome = $1
                    WHERE correlation_id = $2
                """, outcome, correlation_id)
            
            await conn.close()
            logger.info(f"Updated decision outcome: {correlation_id} -> {outcome}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating decision outcome: {e}")
            return False
    
    async def get_decisions_by_category(self, category: str, hours: int = 24) -> List[Dict]:
        """Get decisions by category within time range"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetch("""
                SELECT * FROM brain_decisions 
                WHERE category = $1 
                AND timestamp >= NOW() - INTERVAL '$2 hours'
                ORDER BY timestamp DESC
            """, category, hours)
            
            await conn.close()
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Error getting decisions by category: {e}")
            return []
    
    async def get_decision_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get decision performance metrics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall performance
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_decisions,
                    COUNT(CASE WHEN outcome = 'successful' THEN 1 END) as successful,
                    COUNT(CASE WHEN outcome = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN outcome = 'failed' THEN 1 END) as failed,
                    AVG(duration_ms) as avg_duration_ms
                FROM brain_decisions 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
            """, hours)
            
            # Category performance
            categories = await conn.fetch("""
                SELECT 
                    category,
                    COUNT(*) as total,
                    COUNT(CASE WHEN outcome = 'successful' THEN 1 END) as successful,
                    AVG(duration_ms) as avg_duration_ms
                FROM brain_decisions 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                GROUP BY category
                ORDER BY total DESC
            """, hours)
            
            await conn.close()
            
            success_rate = (overall['successful'] / overall['total_decisions'] * 100) if overall['total_decisions'] > 0 else 0
            
            category_performance = []
            for cat in categories:
                cat_success_rate = (cat['successful'] / cat['total'] * 100) if cat['total'] > 0 else 0
                category_performance.append({
                    'category': cat['category'],
                    'total': cat['total'],
                    'successful': cat['successful'],
                    'success_rate': cat_success_rate,
                    'avg_duration_ms': cat['avg_duration_ms']
                })
            
            return {
                'period_hours': hours,
                'total_decisions': overall['total_decisions'],
                'successful_decisions': overall['successful'],
                'pending_decisions': overall['pending'],
                'failed_decisions': overall['failed'],
                'overall_success_rate': success_rate,
                'avg_duration_ms': overall['avg_duration_ms'],
                'category_performance': category_performance
            }
            
        except Exception as e:
            logger.error(f"Error getting decision performance: {e}")
            return {}
    
    async def get_recent_decisions(self, limit: int = 50) -> List[Dict]:
        """Get recent brain decisions"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetch("""
                SELECT * FROM brain_decisions 
                ORDER BY timestamp DESC 
                LIMIT $1
            """, limit)
            
            await conn.close()
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Error getting recent decisions: {e}")
            return []
    
    async def get_decision_timeline(self, hours: int = 24) -> List[Dict]:
        """Get decision timeline for analysis"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetch("""
                SELECT 
                    timestamp,
                    category,
                    action,
                    outcome,
                    duration_ms,
                    details
                FROM brain_decisions 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                ORDER BY timestamp ASC
            """, hours)
            
            await conn.close()
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Error getting decision timeline: {e}")
            return []
    
    async def analyze_decision_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in decision making"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Most common actions
            common_actions = await conn.fetch("""
                SELECT action, COUNT(*) as count
                FROM brain_decisions 
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY action
                ORDER BY count DESC
                LIMIT 10
            """)
            
            # Decision duration analysis
            duration_stats = await conn.fetchrow("""
                SELECT 
                    MIN(duration_ms) as min_duration,
                    MAX(duration_ms) as max_duration,
                    AVG(duration_ms) as avg_duration,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_ms) as median_duration
                FROM brain_decisions 
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                AND duration_ms IS NOT NULL
            """)
            
            # Outcome patterns by category
            outcome_patterns = await conn.fetch("""
                SELECT 
                    category,
                    outcome,
                    COUNT(*) as count
                FROM brain_decisions 
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY category, outcome
                ORDER BY category, count DESC
            """)
            
            await conn.close()
            
            return {
                'common_actions': [dict(row) for row in common_actions],
                'duration_stats': dict(duration_stats),
                'outcome_patterns': [dict(row) for row in outcome_patterns]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing decision patterns: {e}")
            return {}

# Global instance
decision_tracker = BrainDecisionTracker()

# Convenience functions for common decision types
async def record_player_recommendation(player_name: str, stat_type: str, line_value: float,
                                     side: str, odds: int, edge: float, confidence: float,
                                     reasoning: str, duration_ms: Optional[int] = None) -> str:
    """Record a player recommendation decision"""
    decision = BrainDecision(
        category='player_recommendation',
        action=f'recommend_{player_name.lower().replace(" ", "_")}_{stat_type.lower().replace(" ", "_")}_{side}',
        reasoning=reasoning,
        details={
            'player_name': player_name,
            'stat_type': stat_type,
            'line_value': line_value,
            'side': side,
            'odds': odds,
            'edge': edge,
            'confidence': confidence
        },
        duration_ms=duration_ms
    )
    
    correlation_id = str(uuid.uuid4())
    decision.correlation_id = correlation_id
    
    await decision_tracker.record_decision(decision)
    return correlation_id

async def record_parlay_construction(legs: List[Dict], total_ev: float, parlay_odds: int,
                                 reasoning: str, duration_ms: Optional[int] = None) -> str:
    """Record a parlay construction decision"""
    decision = BrainDecision(
        category='parlay_construction',
        action=f'build_{len(legs)}_leg_parlay',
        reasoning=reasoning,
        details={
            'parlay_type': f'{len(legs)}_leg',
            'total_ev': total_ev,
            'parlay_odds': parlay_odds,
            'legs': legs
        },
        duration_ms=duration_ms
    )
    
    correlation_id = str(uuid.uuid4())
    decision.correlation_id = correlation_id
    
    await decision_tracker.record_decision(decision)
    return correlation_id

async def record_risk_management(decision_type: str, risk_score: float, threshold: float,
                               reasoning: str, duration_ms: Optional[int] = None) -> str:
    """Record a risk management decision"""
    decision = BrainDecision(
        category='risk_management',
        action=f'{decision_type}_risk_assessment',
        reasoning=reasoning,
        details={
            'decision_type': decision_type,
            'risk_score': risk_score,
            'threshold': threshold,
            'approved': risk_score <= threshold
        },
        duration_ms=duration_ms
    )
    
    correlation_id = str(uuid.uuid4())
    decision.correlation_id = correlation_id
    
    await decision_tracker.record_decision(decision)
    return correlation_id

if __name__ == "__main__":
    # Test decision tracking
    async def test():
        # Test player recommendation
        correlation_id = await record_player_recommendation(
            player_name="Drake Maye",
            stat_type="Passing Yards",
            line_value=245.5,
            side="over",
            odds=-110,
            edge=0.12,
            confidence=0.85,
            reasoning="Strong performance metrics and favorable conditions",
            duration_ms=125
        )
        
        print(f"Recorded decision with correlation_id: {correlation_id}")
        
        # Update outcome
        await decision_tracker.update_decision_outcome(correlation_id, "successful")
        
        # Get performance
        performance = await decision_tracker.get_decision_performance()
        print(f"Decision performance: {performance}")
    
    asyncio.run(test())
