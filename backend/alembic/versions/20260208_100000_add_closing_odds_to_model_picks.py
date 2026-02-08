"""Add closing_odds column to model_picks

Revision ID: 20260208_100000_add_closing_odds_to_model_picks
Revises: 20260207_030000_add_performance_indexes.py
Create Date: 2026-02-08 16:08:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20260208_100000_add_closing_odds_to_model_picks'
down_revision = '20260207_030000_add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Add CLV columns to model_picks if they don't exist"""
    # Check if columns exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns
    columns = [column['name'] for column in inspector.get_columns('model_picks')]
    
    # CLV columns to add
    clv_columns = [
        ('closing_odds', sa.Float, nullable=True),
        ('clv_percentage', sa.Float, nullable=True),
        ('roi_percentage', sa.Float, nullable=True),
        ('opening_odds', sa.Float, nullable=True),
        ('line_movement', sa.Float, nullable=True),
        ('sharp_money_indicator', sa.Float, nullable=True),
        ('best_book_odds', sa.Float, nullable=True),
        ('best_book_name', sa.String(50), nullable=True),
        ('ev_improvement', sa.Float, nullable=True)
    ]
    
    for col_name, col_type, nullable in clv_columns:
        if col_name not in columns:
            # Add the column
            op.add_column('model_picks', sa.Column(col_name, col_type, nullable=nullable))
            print(f"Added {col_name} column to model_picks table")
        else:
            print(f"{col_name} column already exists")


def downgrade():
    """Remove CLV columns from model_picks"""
    clv_columns = [
        'closing_odds',
        'clv_percentage',
        'roi_percentage',
        'opening_odds',
        'line_movement',
        'sharp_money_indicator',
        'best_book_odds',
        'best_book_name',
        'ev_improvement'
    ]
    
    for col_name in clv_columns:
        try:
            op.drop_column('model_picks', col_name)
            print(f"Dropped {col_name} column from model_picks table")
        except:
            pass  # Column might not exist
