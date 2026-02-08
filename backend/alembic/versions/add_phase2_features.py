"""Add Phase 2 Features - Line Movement, Multi-Book Shopping, Performance Attribution

Revision ID: add_phase2_features
Revises: add_clv_tracking
Create Date: 2026-02-07 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_phase2_features'
down_revision = 'add_clv_tracking'
branch_labels = None
depends_on = None

def upgrade():
    """Add Phase 2 features to model_picks table."""
    # Add line movement tracking fields
    op.add_column('model_picks', sa.Column('opening_odds', sa.Float(), nullable=True))
    op.add_column('model_picks', sa.Column('line_movement', sa.Float(), nullable=True))
    op.add_column('model_picks', sa.Column('sharp_money_indicator', sa.Float(), nullable=True))
    
    # Add multi-book shopping fields
    op.add_column('model_picks', sa.Column('best_book_odds', sa.Float(), nullable=True))
    op.add_column('model_picks', sa.Column('best_book_name', sa.String(length=50), nullable=True))
    op.add_column('model_picks', sa.Column('ev_improvement', sa.Float(), nullable=True))
    
    # Add indexes for new fields
    op.create_index('ix_model_picks_opening_odds', 'model_picks', ['opening_odds'])
    op.create_index('ix_model_picks_line_movement', 'model_picks', ['line_movement'])
    op.create_index('ix_model_picks_best_book', 'model_picks', ['best_book_name'])

def downgrade():
    """Remove Phase 2 features from model_picks table."""
    # Remove indexes
    op.drop_index('ix_model_picks_best_book', table_name='model_picks')
    op.drop_index('ix_model_picks_line_movement', table_name='model_picks')
    op.drop_index('ix_model_picks_opening_odds', table_name='model_picks')
    
    # Remove columns
    op.drop_column('model_picks', 'ev_improvement')
    op.drop_column('model_picks', 'best_book_name')
    op.drop_column('model_picks', 'best_book_odds')
    op.drop_column('model_picks', 'sharp_money_indicator')
    op.drop_column('model_picks', 'line_movement')
    op.drop_column('model_picks', 'opening_odds')
