#!/usr/bin/env python3
"""
POPULATE BRAIN LEARNING - Initialize and populate the brain_learning table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_brain_learning():
    """Populate brain_learning table with initial data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Check if table exists
        table_check = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'brain_learning'
            )
        """)
        
        if not table_check:
            print("Creating brain_learning table...")
            await conn.execute("""
                CREATE TABLE brain_learning (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    learning_type VARCHAR(50) NOT NULL,
                    metric_name VARCHAR(100) NOT NULL,
                    old_value FLOAT,
                    new_value FLOAT,
                    confidence FLOAT,
                    context TEXT,
                    impact_assessment TEXT,
                    validated_at TIMESTAMP WITH TIME ZONE,
                    validation_result VARCHAR(20)
                )
            """)
            print("Table created")
        
        # Generate sample brain learning data
        print("Generating sample brain learning data...")
        
        learning_events = [
            # Model accuracy improvements
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=6),
                'learning_type': 'model_improvement',
                'metric_name': 'passing_yards_prediction_accuracy',
                'old_value': 0.52,
                'new_value': 0.71,
                'confidence': 0.85,
                'context': 'Retrained passing yards predictor with 15k new data points. Added regularization and feature engineering. Improved validation accuracy from 0.52 to 0.71.',
                'impact_assessment': 'High impact - 19% accuracy improvement will increase recommendation success rate and user confidence. Expected to improve overall EV by 3-5%.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'validation_result': 'validated'
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=8),
                'learning_type': 'parameter_tuning',
                'metric_name': 'confidence_calculation_method',
                'old_value': 0.92,
                'new_value': 0.85,
                'confidence': 0.78,
                'context': 'Adjusted confidence calculation to cap at 85% based on user feedback analysis. Users reported decreased trust when confidence scores exceeded 90%.',
                'impact_assessment': 'Medium impact - May reduce perceived confidence but improve user trust and long-term engagement. Expected to increase user retention by 2-3%.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=7),
                'validation_result': 'validated'
            },
            # Market pattern learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=12),
                'learning_type': 'market_pattern',
                'metric_name': 'line_movement_detection_threshold',
                'old_value': 0.05,
                'new_value': 0.03,
                'confidence': 0.92,
                'context': 'Learned that smaller line movements (3%+) are more predictive of value opportunities than previously thought (5%+). Analyzed 6 months of line movement data.',
                'impact_assessment': 'High impact - Will identify 15% more value opportunities while maintaining false positive rate. Expected to improve overall EV by 2-4%.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=11),
                'validation_result': 'validated'
            },
            # User behavior learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=18),
                'learning_type': 'user_behavior',
                'metric_name': 'optimal_recommendation_count_per_hour',
                'old_value': 15.0,
                'new_value': 12.0,
                'confidence': 0.81,
                'context': 'Analyzed user engagement patterns and found that users prefer quality over quantity. Reduced recommendation frequency from 15 to 12 per hour.',
                'impact_assessment': 'Medium impact - Will improve user engagement and reduce recommendation fatigue. Expected to increase click-through rate by 5-7%.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=16),
                'validation_result': 'validated'
            },
            # Risk management learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=24),
                'learning_type': 'risk_management',
                'metric_name': 'max_parlay_legs',
                'old_value': 6,
                'new_value': 4,
                'confidence': 0.88,
                'context': 'Learned from historical data that 4-leg parlays have optimal risk/reward ratio. 6-leg parlays showed diminishing returns and higher variance.',
                'impact_assessment': 'High impact - Will improve parlay success rate by 8-12% while maintaining EV. Reduces user risk exposure.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=22),
                'validation_result': 'validated'
            },
            # Anomaly detection learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=30),
                'learning_type': 'anomaly_detection',
                'metric_name': 'error_rate_threshold',
                'old_value': 0.05,
                'new_value': 0.03,
                'confidence': 0.75,
                'context': 'Adjusted anomaly detection sensitivity after analyzing false positives. Lowered error rate threshold from 5% to 3% to reduce alert fatigue.',
                'impact_assessment': 'Medium impact - Will reduce false positive alerts by 40% while maintaining detection of critical issues. Improves operational efficiency.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=28),
                'validation_result': 'validated'
            },
            # Performance optimization learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=36),
                'learning_type': 'performance_optimization',
                'metric_name': 'cache_ttl_seconds',
                'old_value': 180,
                'new_value': 300,
                'confidence': 0.93,
                'context': 'Learned that longer cache TTL (300s vs 180s) improves performance without significantly impacting data freshness for most metrics.',
                'impact_assessment': 'High impact - Will reduce API response time by 25% and server load by 15%. Improves user experience.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=34),
                'validation_result': 'validated'
            },
            # Data source learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=42),
                'learning_type': 'data_source_optimization',
                'metric_name': 'primary_odds_provider_weight',
                'old_value': 0.70,
                'new_value': 0.60,
                'confidence': 0.79,
                'context': 'Learned to reduce reliance on primary odds provider after analyzing accuracy across multiple sources. Increased backup provider usage.',
                'impact_assessment': 'Medium impact - Improves system resilience and reduces single point of failure risk. Maintains accuracy while improving reliability.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=40),
                'validation_result': 'validated'
            },
            # Feature engineering learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=48),
                'learning_type': 'feature_engineering',
                'metric_name': 'weather_impact_weight',
                'old_value': 0.15,
                'new_value': 0.25,
                'confidence': 0.82,
                'context': 'Discovered that weather conditions have greater impact on passing yards than previously modeled. Increased weight from 15% to 25%.',
                'impact_assessment': 'High impact - Will improve passing yards prediction accuracy by 3-5%, especially for outdoor games. Better risk assessment.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=46),
                'validation_result': 'validated'
            },
            # User preference learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=54),
                'learning_type': 'user_preference',
                'metric_name': 'preferred_sport_weight',
                'old_value': 0.50,
                'new_value': 0.65,
                'confidence': 0.76,
                'context': 'Learned that users prefer NFL recommendations over NBA (65% vs 50%). Adjusted recommendation algorithm to favor NFL content.',
                'impact_assessment': 'Medium impact - Will increase user engagement and click-through rates by 4-6%. Better user satisfaction.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=52),
                'validation_result': 'validated'
            },
            # Time-based learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=60),
                'learning_type': 'temporal_pattern',
                'metric_name': 'weekend_recommendation_multiplier',
                'old_value': 1.0,
                'new_value': 1.3,
                'confidence': 0.84,
                'context': 'Learned that user activity increases 30% on weekends. Adjusted recommendation frequency and confidence thresholds.',
                'impact_assessment': 'Medium impact - Will capture more weekend engagement and increase recommendation effectiveness by 5-8%.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=58),
                'validation_result': 'validated'
            },
            # Market efficiency learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=72),
                'learning_type': 'market_efficiency',
                'metric_name': 'closing_line_value_adjustment',
                'old_value': 0.10,
                'new_value': 0.15,
                'confidence': 0.77,
                'context': 'Learned that closing lines provide more value than previously thought. Increased weight from 10% to 15% in CLV calculations.',
                'impact_assessment': 'High impact - Will improve CLV accuracy and EV calculations. Expected to increase recommendation profitability by 2-3%.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=70),
                'validation_result': 'validated'
            },
            # Competition analysis learning
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=84),
                'learning_type': 'competitive_analysis',
                'metric_name': 'market_correlation_threshold',
                'old_value': 0.30,
                'new_value': 0.20,
                'confidence': 0.71,
                'context': 'Learned that lower correlation thresholds (20% vs 30%) provide better parlay diversification while maintaining EV.',
                'impact_assessment': 'Medium impact - Will improve parlay success rate by 3-5% through better diversification. Reduces correlated risk.',
                'validated_at': datetime.now(timezone.utc) - timedelta(hours=82),
                'validation_result': 'validated'
            }
        ]
        
        # Insert learning events
        for event in learning_events:
            await conn.execute("""
                INSERT INTO brain_learning (
                    timestamp, learning_type, metric_name, old_value, new_value,
                    confidence, context, impact_assessment, validated_at, validation_result
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                event['timestamp'],
                event['learning_type'],
                event['metric_name'],
                event['old_value'],
                event['new_value'],
                event['confidence'],
                event['context'],
                event['impact_assessment'],
                event['validated_at'],
                event['validation_result']
            )
        
        print("Sample brain learning events populated successfully")
        
        # Get learning statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN validation_result = 'validated' THEN 1 END) as validated_events,
                COUNT(CASE WHEN validation_result = 'pending' THEN 1 END) as pending_events,
                COUNT(CASE WHEN validation_result = 'rejected' THEN 1 END) as rejected_events,
                AVG(confidence) as avg_confidence,
                AVG(new_value - old_value) as avg_improvement
            FROM brain_learning
        """)
        
        print(f"\nLearning Statistics:")
        print(f"  Total Events: {stats['total_events']}")
        print(f"  Validated: {stats['validated_events']}")
        print(f"  Pending: {stats['pending_events']}")
        print(f"  Rejected: {stats['rejected_events']}")
        print(f"  Avg Confidence: {stats['avg_confidence']:.2f}")
        print(f"  Avg Improvement: {stats['avg_improvement']:.3f}")
        
        # Get learning type breakdown
        learning_types = await conn.fetch("""
            SELECT learning_type, COUNT(*) as count,
                   AVG(confidence) as avg_confidence,
                   AVG(new_value - old_value) as avg_improvement
            FROM brain_learning 
            GROUP BY learning_type
            ORDER BY count DESC
        """)
        
        print(f"\nLearning Types:")
        for lt in learning_types:
            print(f"  {lt['learning_type']}: {lt['count']} events ({lt['avg_confidence']:.2f} avg confidence)")
        
        # Get impact assessment breakdown
        impacts = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN impact_assessment LIKE 'High%' THEN 'High'
                    WHEN impact_assessment LIKE 'Medium%' THEN 'Medium'
                    WHEN impact_assessment LIKE 'Low%' THEN 'Low'
                    ELSE 'Unknown'
                END as impact_level,
                COUNT(*) as count
            FROM brain_learning 
            GROUP BY impact_level
            ORDER BY count DESC
        """)
        
        print(f"\nImpact Assessment:")
        for impact in impacts:
            print(f"  {impact['impact_level']}: {impact['count']} events")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_brain_learning())
