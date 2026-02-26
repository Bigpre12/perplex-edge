#!/usr/bin/env python3
"""
POPULATE BRAIN DECISIONS - Initialize and populate the brain_decisions table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_brain_decisions():
    """Populate brain_decisions table with initial data"""
    
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
                WHERE table_name = 'brain_decisions'
            )
        """)
        
        if not table_check:
            print("Creating brain_decisions table...")
            await conn.execute("""
                CREATE TABLE brain_decisions (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    category VARCHAR(50) NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    reasoning TEXT,
                    outcome VARCHAR(20) DEFAULT 'pending',
                    details JSONB,
                    duration_ms INTEGER,
                    correlation_id UUID
                )
            """)
            print("Table created")
        
        # Generate sample brain decisions
        print("Generating sample brain decision data...")
        
        decisions = [
            # Player recommendation decisions
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'category': 'player_recommendation',
                'action': 'recommend_drake_mayne_passing_yards_over',
                'reasoning': 'Drake Maye has shown consistent passing performance with 65% completion rate over last 4 games. Weather conditions are favorable (no wind, 72°F). Defense ranks 25th against pass allowing 245 yards per game. EV calculation shows 12% edge with 85% confidence.',
                'outcome': 'successful',
                'details': {
                    'player_id': 1001,
                    'player_name': 'Drake Maye',
                    'stat_type': 'Passing Yards',
                    'line_value': 245.5,
                    'side': 'over',
                    'odds': -110,
                    'edge': 0.12,
                    'confidence': 0.85,
                    'ev': 0.12,
                    'market_conditions': {
                        'weather': 'clear',
                        'temperature': 72,
                        'wind_speed': 0,
                        'defensive_rank': 25
                    }
                },
                'duration_ms': 125,
                'correlation_id': uuid.uuid4()
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=25),
                'category': 'player_recommendation',
                'action': 'recommend_sam_darnold_passing_tds_under',
                'reasoning': 'Sam Darnold has been efficient with TDs, averaging 1.2 per game. Opposing defense has strong secondary allowing only 1.1 passing TDs per game. Recent trend shows under performance in 4 of last 5 games. Calculated edge of 8% with 78% confidence.',
                'outcome': 'pending',
                'details': {
                    'player_id': 1002,
                    'player_name': 'Sam Darnold',
                    'stat_type': 'Passing TDs',
                    'line_value': 1.5,
                    'side': 'under',
                    'odds': -110,
                    'edge': 0.08,
                    'confidence': 0.78,
                    'ev': 0.08,
                    'market_conditions': {
                        'weather': 'clear',
                        'temperature': 72,
                        'defensive_rank': 8
                    }
                },
                'duration_ms': 98,
                'correlation_id': uuid.uuid4()
            },
            # Parlay building decisions
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=20),
                'category': 'parlay_construction',
                'action': 'build_two_leg_parlay',
                'reasoning': 'Combining Drake Maye passing yards over (12% edge) with Sam Darnold passing TDs under (8% edge). Correlation analysis shows low correlation (r=0.15) between these outcomes. Combined EV of 22% with parlay odds of +275. Risk management approves within limits.',
                'outcome': 'successful',
                'details': {
                    'parlay_type': 'two_leg',
                    'total_ev': 0.22,
                    'parlay_odds': 275,
                    'legs': [
                        {
                            'player': 'Drake Maye',
                            'stat': 'Passing Yards',
                            'line': 245.5,
                            'side': 'over',
                            'edge': 0.12
                        },
                        {
                            'player': 'Sam Darnold',
                            'stat': 'Passing TDs',
                            'line': 1.5,
                            'side': 'under',
                            'edge': 0.08
                        }
                    ],
                    'correlation_coefficient': 0.15,
                    'risk_score': 0.3
                },
                'duration_ms': 245,
                'correlation_id': uuid.uuid4()
            },
            # Risk management decisions
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'category': 'risk_management',
                'action': 'approve_high_ev_parlay',
                'reasoning': 'Parlay shows 22% combined EV which exceeds our 15% threshold. Individual legs have strong confidence scores (85% and 78%). Correlation is low (0.15) reducing risk. Total exposure within daily limits. Risk score of 0.3 is acceptable (threshold 0.5).',
                'outcome': 'successful',
                'details': {
                    'parlay_ev': 0.22,
                    'threshold_ev': 0.15,
                    'confidence_scores': [0.85, 0.78],
                    'correlation': 0.15,
                    'risk_score': 0.3,
                    'risk_threshold': 0.5,
                    'daily_exposure': 0.12,
                    'exposure_limit': 0.25
                },
                'duration_ms': 156,
                'correlation_id': uuid.uuid4()
            },
            # Market analysis decisions
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
                'category': 'market_analysis',
                'action': 'identify_market_inefficiency',
                'reasoning': 'Detected significant line movement on Drake Maye passing yards from 235.5 to 245.5 over 6 hours. Volume analysis shows 65% of bets on over, yet line moved further up. Sharp money indicator suggests professional action. This creates value opportunity on over at current line.',
                'outcome': 'successful',
                'details': {
                    'player': 'Drake Maye',
                    'stat': 'Passing Yards',
                    'initial_line': 235.5,
                    'current_line': 245.5,
                    'line_movement': 10.0,
                    'volume_distribution': {
                        'over_percent': 0.65,
                        'under_percent': 0.35
                    },
                    'sharp_money_indicator': 0.78,
                    'timeframe': '6_hours',
                    'inefficiency_score': 0.82
                },
                'duration_ms': 189,
                'correlation_id': uuid.uuid4()
            },
            # Model training decisions
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'category': 'model_optimization',
                'action': 'adjust_weight_parameters',
                'reasoning': 'Recent backtesting shows 3% decline in prediction accuracy for passing yards. Weight optimization using gradient descent with learning rate 0.001. Cross-validation indicates improved accuracy from 68% to 71%. Early stopping triggered after 50 epochs to prevent overfitting.',
                'outcome': 'successful',
                'details': {
                    'model_type': 'passing_yards_predictor',
                    'previous_accuracy': 0.68,
                    'new_accuracy': 0.71,
                    'improvement': 0.03,
                    'learning_rate': 0.001,
                    'epochs': 50,
                    'validation_loss': 0.142,
                    'early_stopping': True,
                    'regularization': 'l2',
                    'regularization_strength': 0.01
                },
                'duration_ms': 2340,
                'correlation_id': uuid.uuid4()
            },
            # Anomaly response decisions
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=1),
                'category': 'anomaly_response',
                'action': 'handle_high_error_rate',
                'reasoning': 'Error rate spiked to 8% (normal threshold 2%). Root cause analysis identified database connection pool exhaustion. Immediate action: increase pool size from 10 to 20 connections. Secondary action: implement connection retry logic with exponential backoff. Monitor for 15 minutes before恢复正常.',
                'outcome': 'successful',
                'details': {
                    'anomaly_type': 'high_error_rate',
                    'current_rate': 0.08,
                    'threshold_rate': 0.02,
                    'root_cause': 'database_connection_pool_exhaustion',
                    'actions_taken': [
                        'increase_pool_size_10_to_20',
                        'implement_retry_logic',
                        'add_monitoring'
                    ],
                    'recovery_time': 12,
                    'prevention_measures': [
                        'connection_pool_monitoring',
                        'auto_scaling_enabled'
                    ]
                },
                'duration_ms': 890,
                'correlation_id': uuid.uuid4()
            },
            # User feedback decisions
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=2),
                'category': 'user_feedback',
                'action': 'adjust_confidence_threshold',
                'reasoning': 'User feedback analysis shows 15% decline in trust when confidence scores exceed 90%. Psychological factor: overconfidence reduces user adoption. Adjust confidence calculation to cap at 85% while maintaining internal accuracy. A/B test planned to validate impact.',
                'outcome': 'pending',
                'details': {
                    'feedback_metric': 'user_trust_score',
                    'decline_percentage': 0.15,
                    'high_confidence_threshold': 0.90,
                    'new_confidence_cap': 0.85,
                    'internal_accuracy_preserved': True,
                    'ab_test_planned': True,
                    'expected_impact': 'positive'
                },
                'duration_ms': 456,
                'correlation_id': uuid.uuid4()
            }
        ]
        
        # Insert decisions
        for decision in decisions:
            await conn.execute("""
                INSERT INTO brain_decisions (
                    timestamp, category, action, reasoning, outcome, details,
                    duration_ms, correlation_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                decision['timestamp'],
                decision['category'],
                decision['action'],
                decision['reasoning'],
                decision['outcome'],
                json.dumps(decision['details']),
                decision['duration_ms'],
                decision['correlation_id']
            )
        
        print("Sample brain decisions populated successfully")
        
        # Get decision statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_decisions,
                COUNT(CASE WHEN outcome = 'successful' THEN 1 END) as successful_decisions,
                COUNT(CASE WHEN outcome = 'pending' THEN 1 END) as pending_decisions,
                COUNT(CASE WHEN outcome = 'failed' THEN 1 END) as failed_decisions,
                AVG(duration_ms) as avg_duration_ms,
                COUNT(DISTINCT category) as unique_categories
            FROM brain_decisions
        """)
        
        print(f"\nDecision Statistics:")
        print(f"  Total: {stats['total_decisions']}")
        print(f"  Successful: {stats['successful_decisions']}")
        print(f"  Pending: {stats['pending_decisions']}")
        print(f"  Failed: {stats['failed_decisions']}")
        print(f"  Avg Duration: {stats['avg_duration_ms']:.0f}ms")
        print(f"  Categories: {stats['unique_categories']}")
        
        # Get category breakdown
        categories = await conn.fetch("""
            SELECT category, COUNT(*) as count, 
                   COUNT(CASE WHEN outcome = 'successful' THEN 1 END) as successful
            FROM brain_decisions 
            GROUP BY category
            ORDER BY count DESC
        """)
        
        print(f"\nDecision Categories:")
        for cat in categories:
            success_rate = (cat['successful'] / cat['count'] * 100) if cat['count'] > 0 else 0
            print(f"  {cat['category']}: {cat['count']} decisions ({success_rate:.1f}% success)")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_brain_decisions())
