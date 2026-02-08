"""Add closing_odds column to model_picks

Revision ID: 20260208_100000_add_closing_odds_to_model_picks
Revises: 20260207_030000_add_performance_indexes.py
Create Date: 2026-02-08 16:08:00.000000

"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    """Add closing_odds column to model_picks if it doesn't exist"""
    # Check if column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if closing_odds column exists
    columns = [column['name'] for column in inspector.get_columns('model_picks')]
    
    if 'closing_odds' not in columns:
        # Add the column
        op.add_column('model_picks', sa.Column('closing_odds', sa.Float, nullable=True))
        print("Added closing_odds column to model_picks table")
    else:
        print("closing_odds column already exists")


def downgrade():
    """Remove closing_odds column from model_picks"""
    op.drop_column('model_picks', 'closing_odds')
