"""add missing whale_moves columns: market_key, event_id, selection, bookmaker,
price_before, price_after, move_type, whale_rating, move_size, line_before, line_after

Revision ID: a1b2c3d4e5f6
Revises: ba1137c91a76
Create Date: 2026-04-24 05:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'ba1137c91a76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to whale_moves table."""
    with op.batch_alter_table('whale_moves', schema=None) as batch_op:
        batch_op.add_column(sa.Column('event_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('market_key', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('selection', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('bookmaker', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('price_before', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('price_after', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('line_before', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('line_after', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('move_type', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('whale_rating', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('move_size', sa.Float(), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_whale_moves_event_id'), ['event_id'], unique=False
        )


def downgrade() -> None:
    """Remove added columns from whale_moves table."""
    with op.batch_alter_table('whale_moves', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_whale_moves_event_id'))
        batch_op.drop_column('move_size')
        batch_op.drop_column('whale_rating')
        batch_op.drop_column('move_type')
        batch_op.drop_column('line_after')
        batch_op.drop_column('line_before')
        batch_op.drop_column('price_after')
        batch_op.drop_column('price_before')
        batch_op.drop_column('bookmaker')
        batch_op.drop_column('selection')
        batch_op.drop_column('market_key')
        batch_op.drop_column('event_id')
