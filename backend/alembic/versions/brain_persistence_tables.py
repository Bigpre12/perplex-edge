"""Add brain persistence tables

Revision ID: brain_persistence_001
Revises: 
Create Date: 2026-02-06 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'brain_persistence_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create brain_decisions table
    op.create_table(
        'brain_decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=200), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('outcome', sa.String(length=50), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('correlation_id', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_brain_decisions_timestamp', 'brain_decisions', ['timestamp'])
    op.create_index('ix_brain_decisions_category', 'brain_decisions', ['category'])
    op.create_index('ix_brain_decisions_outcome', 'brain_decisions', ['outcome'])
    op.create_index('ix_brain_decisions_correlation', 'brain_decisions', ['correlation_id'])

    # Create brain_health_checks table
    op.create_table(
        'brain_health_checks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('component', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_brain_health_timestamp', 'brain_health_checks', ['timestamp'])
    op.create_index('ix_brain_health_component', 'brain_health_checks', ['component'])
    op.create_index('ix_brain_health_status', 'brain_health_checks', ['status'])

    # Create brain_healing_actions table
    op.create_table(
        'brain_healing_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('action', sa.String(length=200), nullable=False),
        sa.Column('target', sa.String(length=100), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('result', sa.String(length=20), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_brain_healing_timestamp', 'brain_healing_actions', ['timestamp'])
    op.create_index('ix_brain_healing_action', 'brain_healing_actions', ['action'])
    op.create_index('ix_brain_healing_result', 'brain_healing_actions', ['result'])
    op.create_index('ix_brain_healing_target', 'brain_healing_actions', ['target'])

    # Create brain_system_state table
    op.create_table(
        'brain_system_state',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cycle_count', sa.Integer(), nullable=True),
        sa.Column('overall_status', sa.String(length=20), nullable=True),
        sa.Column('heals_attempted', sa.Integer(), nullable=True),
        sa.Column('heals_succeeded', sa.Integer(), nullable=True),
        sa.Column('consecutive_failures', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sport_priority', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('quota_budget', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('auto_commit_enabled', sa.Boolean(), nullable=True),
        sa.Column('git_commits_made', sa.Integer(), nullable=True),
        sa.Column('betting_opportunities_found', sa.Integer(), nullable=True),
        sa.Column('strong_bets_identified', sa.Integer(), nullable=True),
        sa.Column('last_betting_scan', sa.DateTime(timezone=True), nullable=True),
        sa.Column('top_betting_opportunities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_cycle_duration_ms', sa.Integer(), nullable=True),
        sa.Column('uptime_hours', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_brain_state_timestamp', 'brain_system_state', ['timestamp'])
    op.create_index('ix_brain_state_status', 'brain_system_state', ['overall_status'])

    # Create brain_anomalies table
    op.create_table(
        'brain_anomalies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('baseline_value', sa.Float(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('change_pct', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_method', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_brain_anomalies_timestamp', 'brain_anomalies', ['timestamp'])
    op.create_index('ix_brain_anomalies_metric', 'brain_anomalies', ['metric_name'])
    op.create_index('ix_brain_anomalies_severity', 'brain_anomalies', ['severity'])
    op.create_index('ix_brain_anomalies_status', 'brain_anomalies', ['status'])

    # Create brain_business_metrics table
    op.create_table(
        'brain_business_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_recommendations', sa.Integer(), nullable=True),
        sa.Column('recommendation_hit_rate', sa.Float(), nullable=True),
        sa.Column('average_ev', sa.Float(), nullable=True),
        sa.Column('clv_trend', sa.Float(), nullable=True),
        sa.Column('prop_volume', sa.Integer(), nullable=True),
        sa.Column('user_confidence_score', sa.Float(), nullable=True),
        sa.Column('api_response_time_ms', sa.Float(), nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('throughput', sa.Float(), nullable=True),
        sa.Column('cpu_usage', sa.Float(), nullable=True),
        sa.Column('memory_usage', sa.Float(), nullable=True),
        sa.Column('disk_usage', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_brain_metrics_timestamp', 'brain_business_metrics', ['timestamp'])
    op.create_index('ix_brain_metrics_hit_rate', 'brain_business_metrics', ['recommendation_hit_rate'])
    op.create_index('ix_brain_metrics_ev', 'brain_business_metrics', ['average_ev'])

    # Create brain_correlations table
    op.create_table(
        'brain_correlations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('correlation_id', sa.String(length=100), nullable=False),
        sa.Column('operation_type', sa.String(length=100), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('events', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('correlation_id')
    )
    op.create_index('ix_brain_correlations_id', 'brain_correlations', ['correlation_id'])
    op.create_index('ix_brain_correlations_type', 'brain_correlations', ['operation_type'])
    op.create_index('ix_brain_correlations_status', 'brain_correlations', ['status'])
    op.create_index('ix_brain_correlations_started', 'brain_correlations', ['started_at'])

    # Create brain_learning table
    op.create_table(
        'brain_learning',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('learning_type', sa.String(length=50), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('old_value', sa.Float(), nullable=False),
        sa.Column('new_value', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('impact_assessment', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validation_result', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_brain_learning_timestamp', 'brain_learning', ['timestamp'])
    op.create_index('ix_brain_learning_type', 'brain_learning', ['learning_type'])
    op.create_index('ix_brain_learning_metric', 'brain_learning', ['metric_name'])


def downgrade():
    # Drop indexes first
    op.drop_index('ix_brain_learning_metric', table_name='brain_learning')
    op.drop_index('ix_brain_learning_type', table_name='brain_learning')
    op.drop_index('ix_brain_learning_timestamp', table_name='brain_learning')
    
    op.drop_index('ix_brain_correlations_started', table_name='brain_correlations')
    op.drop_index('ix_brain_correlations_status', table_name='brain_correlations')
    op.drop_index('ix_brain_correlations_type', table_name='brain_correlations')
    op.drop_index('ix_brain_correlations_id', table_name='brain_correlations')
    
    op.drop_index('ix_brain_metrics_ev', table_name='brain_business_metrics')
    op.drop_index('ix_brain_metrics_hit_rate', table_name='brain_business_metrics')
    op.drop_index('ix_brain_metrics_timestamp', table_name='brain_business_metrics')
    
    op.drop_index('ix_brain_anomalies_status', table_name='brain_anomalies')
    op.drop_index('ix_brain_anomalies_severity', table_name='brain_anomalies')
    op.drop_index('ix_brain_anomalies_metric', table_name='brain_anomalies')
    op.drop_index('ix_brain_anomalies_timestamp', table_name='brain_anomalies')
    
    op.drop_index('ix_brain_state_status', table_name='brain_system_state')
    op.drop_index('ix_brain_state_timestamp', table_name='brain_system_state')
    
    op.drop_index('ix_brain_healing_target', table_name='brain_healing_actions')
    op.drop_index('ix_brain_healing_result', table_name='brain_healing_actions')
    op.drop_index('ix_brain_healing_action', table_name='brain_healing_actions')
    op.drop_index('ix_brain_healing_timestamp', table_name='brain_healing_actions')
    
    op.drop_index('ix_brain_health_status', table_name='brain_health_checks')
    op.drop_index('ix_brain_health_component', table_name='brain_health_checks')
    op.drop_index('ix_brain_health_timestamp', table_name='brain_health_checks')
    
    op.drop_index('ix_brain_decisions_correlation', table_name='brain_decisions')
    op.drop_index('ix_brain_decisions_outcome', table_name='brain_decisions')
    op.drop_index('ix_brain_decisions_category', table_name='brain_decisions')
    op.drop_index('ix_brain_decisions_timestamp', table_name='brain_decisions')
    
    # Drop tables
    op.drop_table('brain_learning')
    op.drop_table('brain_correlations')
    op.drop_table('brain_business_metrics')
    op.drop_table('brain_anomalies')
    op.drop_table('brain_system_state')
    op.drop_table('brain_healing_actions')
    op.drop_table('brain_health_checks')
    op.drop_table('brain_decisions')
