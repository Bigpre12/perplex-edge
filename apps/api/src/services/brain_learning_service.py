"""
Brain Learning Service - Machine learning and adaptation system
"""
import asyncio
import asyncpg
import os
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LearningType(Enum):
    """Types of learning events"""
    MODEL_IMPROVEMENT = "model_improvement"
    PARAMETER_TUNING = "parameter_tuning"
    MARKET_PATTERN = "market_pattern"
    USER_BEHAVIOR = "user_behavior"
    RISK_MANAGEMENT = "risk_management"
    ANOMALY_DETECTION = "anomaly_detection"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DATA_SOURCE_OPTIMIZATION = "data_source_optimization"
    FEATURE_ENGINEERING = "feature_engineering"
    USER_PREFERENCE = "user_preference"
    TEMPORAL_PATTERN = "temporal_pattern"
    MARKET_EFFICIENCY = "market_efficiency"
    COMPETITIVE_ANALYSIS = "competitive_analysis"

class ValidationStatus(Enum):
    """Validation status of learning events"""
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"

@dataclass
class LearningEvent:
    """Learning event data structure"""
    learning_type: LearningType
    metric_name: str
    old_value: float
    new_value: float
    confidence: float
    context: str
    impact_assessment: str

@dataclass
class LearningResult:
    """Result of learning validation"""
    success: bool
    validation_result: ValidationStatus
    actual_improvement: Optional[float] = None
    validation_details: Optional[Dict[str, Any]] = None

class BrainLearningService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.learning_algorithms = self._initialize_learning_algorithms()
        self.validation_queue = []
        self.active_learning = False
        
    def _initialize_learning_algorithms(self) -> Dict[LearningType, Callable]:
        """Initialize learning algorithms for different types"""
        return {
            LearningType.MODEL_IMPROVEMENT: self._model_improvement_learning,
            LearningType.PARAMETER_TUNING: self._parameter_tuning_learning,
            LearningType.MARKET_PATTERN: self._market_pattern_learning,
            LearningType.USER_BEHAVIOR: self._user_behavior_learning,
            LearningType.RISK_MANAGEMENT: self._risk_management_learning,
            LearningType.ANOMALY_DETECTION: self._anomaly_detection_learning,
            LearningType.PERFORMANCE_OPTIMIZATION: self._performance_optimization_learning,
            LearningType.DATA_SOURCE_OPTIMIZATION: self._data_source_optimization_learning,
            LearningType.FEATURE_ENGINEERING: self._feature_engineering_learning,
            LearningType.USER_PREFERENCE: self._user_preference_learning,
            LearningType.TEMPORAL_PATTERN: self._temporal_pattern_learning,
            LearningType.MARKET_EFFICIENCY: self._market_efficiency_learning,
            LearningType.COMPETITIVE_ANALYSIS: self._competitive_analysis_learning
        }
    
    async def record_learning_event(self, event: LearningEvent) -> str:
        """Record a learning event in the database"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            learning_id = str(uuid.uuid4())
            
            await conn.execute("""
                INSERT INTO brain_learning (
                    learning_type, metric_name, old_value, new_value,
                    confidence, context, impact_assessment, validation_result
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                event.learning_type.value,
                event.metric_name,
                event.old_value,
                event.new_value,
                event.confidence,
                event.context,
                event.impact_assessment,
                ValidationStatus.PENDING.value
            )
            
            await conn.close()
            logger.info(f"Recorded learning event: {event.learning_type.value} - {event.metric_name}")
            return learning_id
            
        except Exception as e:
            logger.error(f"Error recording learning event: {e}")
            return ""
    
    async def validate_learning_event(self, learning_id: str, days_to_validate: int = 7) -> LearningResult:
        """Validate a learning event by measuring actual improvement"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get the learning event
            event = await conn.fetchrow("""
                SELECT * FROM brain_learning 
                WHERE id = $1
            """, learning_id)
            
            if not event:
                await conn.close()
                return LearningResult(False, ValidationStatus.REJECTED, None, {"error": "Learning event not found"})
            
            # Simulate validation process
            actual_improvement = await self._calculate_actual_improvement(
                event['metric_name'],
                event['old_value'],
                event['new_value'],
                days_to_validate
            )
            
            # Determine validation result
            if actual_improvement is None:
                validation_result = ValidationStatus.PENDING
                success = False
            elif actual_improvement >= (event['new_value'] - event['old_value']) * 0.5:  # At least 50% of expected improvement
                validation_result = ValidationStatus.VALIDATED
                success = True
            else:
                validation_result = ValidationStatus.REJECTED
                success = False
            
            # Update validation status
            await conn.execute("""
                UPDATE brain_learning 
                SET validated_at = NOW(), validation_result = $1
                WHERE id = $2
            """, validation_result.value, learning_id)
            
            await conn.close()
            
            return LearningResult(
                success=success,
                validation_result=validation_result,
                actual_improvement=actual_improvement,
                validation_details={
                    "expected_improvement": event['new_value'] - event['old_value'],
                    "actual_improvement": actual_improvement,
                    "validation_days": days_to_validate
                }
            )
            
        except Exception as e:
            logger.error(f"Error validating learning event: {e}")
            return LearningResult(False, ValidationStatus.REJECTED, None, {"error": str(e)})
    
    async def _calculate_actual_improvement(self, metric_name: str, old_value: float, new_value: float, days: int) -> Optional[float]:
        """Calculate actual improvement for a metric"""
        # This would connect to actual monitoring systems
        # For now, return simulated improvements based on metric type
        
        metric_improvements = {
            "passing_yards_prediction_accuracy": 0.19,  # 19% improvement
            "confidence_calculation_method": -0.07,  # 7% decrease (intentional)
            "line_movement_detection_threshold": 0.12,  # 12% improvement
            "optimal_recommendation_count_per_hour": 0.08,  # 8% improvement
            "max_parlay_legs": 0.10,  # 10% improvement
            "error_rate_threshold": 0.15,  # 15% improvement
            "cache_ttl_seconds": 0.25,  # 25% improvement
            "primary_odds_provider_weight": 0.05,  # 5% improvement
            "weather_impact_weight": 0.03,  # 3% improvement
            "preferred_sport_weight": 0.06,  # 6% improvement
            "weekend_recommendation_multiplier": 0.07,  # 7% improvement
            "closing_line_value_adjustment": 0.04,  # 4% improvement
            "market_correlation_threshold": 0.03  # 3% improvement
        }
        
        return metric_improvements.get(metric_name, 0.0)
    
    async def run_learning_algorithm(self, learning_type: LearningType) -> List[LearningEvent]:
        """Run a specific learning algorithm"""
        algorithm = self.learning_algorithms.get(learning_type)
        if algorithm:
            return await algorithm()
        return []
    
    async def _model_improvement_learning(self) -> List[LearningEvent]:
        """Model improvement learning algorithm"""
        await asyncio.sleep(2)  # Simulate learning time
        
        return [
            LearningEvent(
                learning_type=LearningType.MODEL_IMPROVEMENT,
                metric_name="passing_yards_prediction_accuracy",
                old_value=0.52,
                new_value=0.71,
                confidence=0.85,
                context="Retrained model with new data and regularization",
                impact_assessment="High impact - 19% accuracy improvement"
            )
        ]
    
    async def _parameter_tuning_learning(self) -> List[LearningEvent]:
        """Parameter tuning learning algorithm"""
        await asyncio.sleep(1)
        
        return [
            LearningEvent(
                learning_type=LearningType.PARAMETER_TUNING,
                metric_name="confidence_calculation_method",
                old_value=0.92,
                new_value=0.85,
                confidence=0.78,
                context="Adjusted confidence based on user feedback",
                impact_assessment="Medium impact - improves user trust"
            )
        ]
    
    async def _market_pattern_learning(self) -> List[LearningEvent]:
        """Market pattern learning algorithm"""
        await asyncio.sleep(3)
        
        return [
            LearningEvent(
                learning_type=LearningType.MARKET_PATTERN,
                metric_name="line_movement_detection_threshold",
                old_value=0.05,
                new_value=0.03,
                confidence=0.92,
                context="Learned optimal line movement threshold",
                impact_assessment="High impact - identifies more value opportunities"
            )
        ]
    
    async def _user_behavior_learning(self) -> List[LearningEvent]:
        """User behavior learning algorithm"""
        await asyncio.sleep(2)
        
        return [
            LearningEvent(
                learning_type=LearningType.USER_BEHAVIOR,
                metric_name="optimal_recommendation_count_per_hour",
                old_value=15.0,
                new_value=12.0,
                confidence=0.81,
                context="Learned user preference for quality over quantity",
                impact_assessment="Medium impact - improves user engagement"
            )
        ]
    
    async def _risk_management_learning(self) -> List[LearningEvent]:
        """Risk management learning algorithm"""
        await asyncio.sleep(1)
        
        return [
            LearningEvent(
                learning_type=LearningType.RISK_MANAGEMENT,
                metric_name="max_parlay_legs",
                old_value=6,
                new_value=4,
                confidence=0.88,
                context="Learned optimal parlay leg count",
                impact_assessment="High impact - improves success rate"
            )
        ]
    
    async def _anomaly_detection_learning(self) -> List[LearningEvent]:
        """Anomaly detection learning algorithm"""
        await asyncio.sleep(1)
        
        return [
            LearningEvent(
                learning_type=LearningType.ANOMALY_DETECTION,
                metric_name="error_rate_threshold",
                old_value=0.05,
                new_value=0.03,
                confidence=0.75,
                context="Adjusted sensitivity to reduce false positives",
                impact_assessment="Medium impact - improves operational efficiency"
            )
        ]
    
    async def _performance_optimization_learning(self) -> List[LearningEvent]:
        """Performance optimization learning algorithm"""
        await asyncio.sleep(1)
        
        return [
            LearningEvent(
                learning_type=LearningType.PERFORMANCE_OPTIMIZATION,
                metric_name="cache_ttl_seconds",
                old_value=180,
                new_value=300,
                confidence=0.93,
                context="Optimized cache TTL for better performance",
                impact_assessment="High impact - reduces response time"
            )
        ]
    
    async def _data_source_optimization_learning(self) -> List[LearningEvent]:
        """Data source optimization learning algorithm"""
        await asyncio.sleep(2)
        
        return [
            LearningEvent(
                learning_type=LearningType.DATA_SOURCE_OPTIMIZATION,
                metric_name="primary_odds_provider_weight",
                old_value=0.70,
                new_value=0.60,
                confidence=0.79,
                context="Optimized data source weights for resilience",
                impact_assessment="Medium impact - improves reliability"
            )
        ]
    
    async def _feature_engineering_learning(self) -> List[LearningEvent]:
        """Feature engineering learning algorithm"""
        await asyncio.sleep(3)
        
        return [
            LearningEvent(
                learning_type=LearningType.FEATURE_ENGINEERING,
                metric_name="weather_impact_weight",
                old_value=0.15,
                new_value=0.25,
                confidence=0.82,
                context="Enhanced weather feature importance",
                impact_assessment="High impact - improves prediction accuracy"
            )
        ]
    
    async def _user_preference_learning(self) -> List[LearningEvent]:
        """User preference learning algorithm"""
        await asyncio.sleep(2)
        
        return [
            LearningEvent(
                learning_type=LearningType.USER_PREFERENCE,
                metric_name="preferred_sport_weight",
                old_value=0.50,
                new_value=0.65,
                confidence=0.76,
                context="Learned user sport preferences",
                impact_assessment="Medium impact - increases engagement"
            )
        ]
    
    async def _temporal_pattern_learning(self) -> List[LearningEvent]:
        """Temporal pattern learning algorithm"""
        await asyncio.sleep(2)
        
        return [
            LearningEvent(
                learning_type=LearningType.TEMPORAL_PATTERN,
                metric_name="weekend_recommendation_multiplier",
                old_value=1.0,
                new_value=1.3,
                confidence=0.84,
                context="Learned weekend usage patterns",
                impact_assessment="Medium impact - captures more engagement"
            )
        ]
    
    async def _market_efficiency_learning(self) -> List[LearningEvent]:
        """Market efficiency learning algorithm"""
        await asyncio.sleep(3)
        
        return [
            LearningEvent(
                learning_type=LearningType.MARKET_EFFICIENCY,
                metric_name="closing_line_value_adjustment",
                old_value=0.10,
                new_value=0.15,
                confidence=0.77,
                context="Learned closing line importance",
                impact_assessment="High impact - improves CLV accuracy"
            )
        ]
    
    async def _competitive_analysis_learning(self) -> List[LearningEvent]:
        """Competitive analysis learning algorithm"""
        await asyncio.sleep(2)
        
        return [
            LearningEvent(
                learning_type=LearningType.COMPETITIVE_ANALYSIS,
                metric_name="market_correlation_threshold",
                old_value=0.30,
                new_value=0.20,
                confidence=0.71,
                context="Learned optimal correlation thresholds",
                impact_assessment="Medium impact - improves diversification"
            )
        ]
    
    async def run_all_learning_algorithms(self) -> List[LearningEvent]:
        """Run all learning algorithms"""
        all_events = []
        
        for learning_type in LearningType:
            try:
                events = await self.run_learning_algorithm(learning_type)
                all_events.extend(events)
                
                # Record each learning event
                for event in events:
                    await self.record_learning_event(event)
                    
            except Exception as e:
                logger.error(f"Error running {learning_type.value} learning: {e}")
        
        return all_events
    
    async def get_learning_history(self, hours: int = 24) -> List[Dict]:
        """Get learning event history"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetch("""
                SELECT * FROM brain_learning 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                ORDER BY timestamp DESC
            """, hours)
            
            await conn.close()
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Error getting learning history: {e}")
            return []
    
    async def get_learning_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get learning performance metrics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Overall performance
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN validation_result = 'validated' THEN 1 END) as validated,
                    COUNT(CASE WHEN validation_result = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN validation_result = 'rejected' THEN 1 END) as rejected,
                    AVG(confidence) as avg_confidence,
                    AVG(new_value - old_value) as avg_improvement
                FROM brain_learning 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
            """, hours)
            
            # Learning type performance
            learning_types = await conn.fetch("""
                SELECT 
                    learning_type,
                    COUNT(*) as total,
                    COUNT(CASE WHEN validation_result = 'validated' THEN 1 END) as validated,
                    AVG(confidence) as avg_confidence,
                    AVG(new_value - old_value) as avg_improvement
                FROM brain_learning 
                WHERE timestamp >= NOW() - INTERVAL '$1 hours'
                GROUP BY learning_type
                ORDER BY total DESC
            """, hours)
            
            await conn.close()
            
            validation_rate = (overall['validated'] / overall['total_events'] * 100) if overall['total_events'] > 0 else 0
            
            return {
                'period_hours': hours,
                'total_events': overall['total_events'],
                'validated_events': overall['validated'],
                'pending_events': overall['pending'],
                'rejected_events': overall['rejected'],
                'validation_rate': validation_rate,
                'avg_confidence': overall['avg_confidence'],
                'avg_improvement': overall['avg_improvement'],
                'learning_type_performance': [dict(row) for row in learning_types]
            }
            
        except Exception as e:
            logger.error(f"Error getting learning performance: {e}")
            return {}
    
    async def run_learning_cycle(self):
        """Run a complete learning cycle"""
        if self.active_learning:
            logger.info("Learning cycle already in progress")
            return
        
        self.active_learning = True
        
        try:
            logger.info("Starting brain learning cycle")
            
            # Run all learning algorithms
            events = await self.run_all_learning_algorithms()
            
            logger.info(f"Learning cycle completed: {len(events)} events generated")
            
            return events
            
        except Exception as e:
            logger.error(f"Error in learning cycle: {e}")
            return []
        finally:
            self.active_learning = False

# Global instance
learning_service = BrainLearningService()

async def run_learning_cycle():
    """Run a learning cycle"""
    return await learning_service.run_learning_cycle()

async def get_learning_history(hours: int = 24):
    """Get learning history"""
    return await learning_service.get_learning_history(hours)

if __name__ == "__main__":
    # Test learning service
    async def test():
        # Test a learning event
        event = LearningEvent(
            learning_type=LearningType.MODEL_IMPROVEMENT,
            metric_name="passing_yards_prediction_accuracy",
            old_value=0.52,
            new_value=0.71,
            confidence=0.85,
            context="Test learning event",
            impact_assessment="High impact"
        )
        
        learning_id = await learning_service.record_learning_event(event)
        print(f"Recorded learning event: {learning_id}")
        
        # Test validation
        result = await learning_service.validate_learning_event(learning_id)
        print(f"Validation result: {result.validation_result.value}")
        
        # Get performance
        performance = await learning_service.get_learning_performance()
        print(f"Learning performance: {performance}")
    
    asyncio.run(test())
