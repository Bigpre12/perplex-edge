"""Add performance indexes for Phase 2 features

Revision ID: 20260207_000000
Revises: 20260204_030000
Create Date: 2026-02-07 23:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20260207_000000'
down_revision = '20260204_030000'
branch_labels = None
depends_on = None

def upgrade():
    """Add performance indexes for new Phase 2 features."""
    
    # ModelPick performance indexes
    op.create_index('ix_model_picks_odds_range', 'model_picks', ['odds'])
    op.create_index('ix_model_picks_line_value', 'model_picks', ['line_value'])
    op.create_index('ix_model_picks_side', 'model_picks', ['side'])
    op.create_index('ix_model_picks_sport_confidence', 'model_picks', ['sport_id', 'confidence_score'])
    op.create_index('ix_model_picks_sport_ev', 'model_picks', ['sport_id', 'expected_value'])
    
    # Composite indexes for common queries
    op.create_index('ix_model_picks_game_active', 'model_picks', ['game_id', 'is_active'])
    op.create_index('ix_model_picks_player_market', 'model_picks', ['player_id', 'market_id'])
    op.create_index('ix_model_picks_sport_generated', 'model_picks', ['sport_id', 'generated_at'])
    
    # Performance attribution indexes
    op.create_index('ix_model_picks_confidence_ev', 'model_picks', ['confidence_score', 'expected_value'])
    op.create_index('ix_model_picks_line_movement_sharp', 'model_picks', ['line_movement', 'sharp_money_indicator'])
    
    # CLV tracking indexes
    op.create_index('ix_model_picks_clv_roi', 'model_picks', ['clv_percentage', 'roi_percentage'])
    op.create_index('ix_model_picks_closing_odds', 'model_picks', ['closing_odds'])
    
    # Line shopping indexes
    op.create_index('ix_model_picks_best_book', 'model_picks', ['best_book_name'])
    op.create_index('ix_model_picks_ev_improvement', 'model_picks', ['ev_improvement'])

def downgrade():
    """Remove performance indexes."""
    
    # Remove indexes in reverse order
    op.drop_index('ix_model_picks_ev_improvement', table_name='model_picks')
    op.drop_index('ix_model_picks_best_book', table_name='model_picks')
    op.drop_index('ix_model_picks_closing_odds', table_name='model_picks')
    op.drop_index('ix_model_picks_clv_roi', table_name='model_picks')
    op.drop_index('ix_model_picks_line_movement_sharp', table_name='model_picks')
    op.drop_index('ix_model_picks_confidence_ev', table_name='model_picks')
    op.drop_index('ix_model_picks_player_market', table_name='model_picks')
    op.drop_index('ix_model_picks_game_active', table_name='model_picks')
    op.drop_index('ix_model_picks_sport_generated', table_name='model_picks')
    op.drop_index('ix_model_picks_sport_ev', table_name='model_picks')
    op.drop_index('ix_model_picks_sport_confidence', table_name='model_picks')
    op.drop_index('ix_model_picks_side', table_name='model_picks')
    op.drop_index('ix_model_picks_line_value', table_name='model_picks')
    op.drop_index('ix_model_picks_odds_range', table_name='model_picks')
