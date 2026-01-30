"""Add CLV tracking and calibration metrics

Revision ID: 20260130_120000
Revises: 20260130_110000_add_ncaab_odds_tables
Create Date: 2026-01-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260130_120000'
down_revision = '20260130_110000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add CLV and P/L fields to pick_results
    op.add_column('pick_results', sa.Column('closing_odds', sa.Integer(), nullable=True))
    op.add_column('pick_results', sa.Column('closing_line', sa.Float(), nullable=True))
    op.add_column('pick_results', sa.Column('clv_cents', sa.Float(), nullable=True))
    op.add_column('pick_results', sa.Column('profit_loss', sa.Float(), nullable=True))
    
    # Create calibration_metrics table
    op.create_table(
        'calibration_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('probability_bucket', sa.String(10), nullable=False),
        sa.Column('bucket_min', sa.Float(), nullable=False),
        sa.Column('bucket_max', sa.Float(), nullable=False),
        sa.Column('predicted_prob', sa.Float(), nullable=False),
        sa.Column('actual_hit_rate', sa.Float(), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=False),
        sa.Column('brier_score', sa.Float(), nullable=False),
        sa.Column('total_wagered', sa.Float(), default=0.0),
        sa.Column('total_profit', sa.Float(), default=0.0),
        sa.Column('roi_percent', sa.Float(), default=0.0),
        sa.Column('avg_clv_cents', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id']),
    )
    
    # Create indexes for calibration_metrics
    op.create_index('ix_calibration_date_sport', 'calibration_metrics', ['date', 'sport_id'])
    op.create_index('ix_calibration_bucket', 'calibration_metrics', ['probability_bucket'])


def downgrade() -> None:
    # Drop calibration_metrics table
    op.drop_index('ix_calibration_bucket', table_name='calibration_metrics')
    op.drop_index('ix_calibration_date_sport', table_name='calibration_metrics')
    op.drop_table('calibration_metrics')
    
    # Remove CLV and P/L fields from pick_results
    op.drop_column('pick_results', 'profit_loss')
    op.drop_column('pick_results', 'clv_cents')
    op.drop_column('pick_results', 'closing_line')
    op.drop_column('pick_results', 'closing_odds')
