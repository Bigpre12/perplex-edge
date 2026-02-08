"""Add CLV tracking fields to model_picks table

Revision ID: add_clv_tracking
Revises: brain_persistence_001
Create Date: 2026-02-07 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_clv_tracking'
down_revision = 'brain_persistence_001'
branch_labels = None
depends_on = None

def upgrade():
    """Add CLV tracking fields to model_picks table."""
    # Add CLV tracking fields
    op.add_column('model_picks', sa.Column('closing_odds', sa.Float(), nullable=True))
    op.add_column('model_picks', sa.Column('clv_percentage', sa.Float(), nullable=True))
    op.add_column('model_picks', sa.Column('roi_percentage', sa.Float(), nullable=True))
    
    # Add indexes for CLV tracking
    op.create_index('ix_model_picks_clv', 'model_picks', ['clv_percentage'])
    op.create_index('ix_model_picks_closing_odds', 'model_picks', ['closing_odds'])

def downgrade():
    """Remove CLV tracking fields from model_picks table."""
    # Remove indexes
    op.drop_index('ix_model_picks_closing_odds', table_name='model_picks')
    op.drop_index('ix_model_picks_clv', table_name='model_picks')
    
    # Remove columns
    op.drop_column('model_picks', 'roi_percentage')
    op.drop_column('model_picks', 'clv_percentage')
    op.drop_column('model_picks', 'closing_odds')
