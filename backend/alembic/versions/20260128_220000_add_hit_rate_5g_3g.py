"""add hit_rate_5g and hit_rate_3g columns

Revision ID: add_hit_rate_5g_3g
Revises: 744eb1c7924e
Create Date: 2026-01-28 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_hit_rate_5g_3g'
down_revision: Union[str, None] = '744eb1c7924e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add hit_rate_5g and hit_rate_3g columns to model_picks table
    op.add_column('model_picks', sa.Column('hit_rate_5g', sa.Float(), nullable=True))
    op.add_column('model_picks', sa.Column('hit_rate_3g', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('model_picks', 'hit_rate_3g')
    op.drop_column('model_picks', 'hit_rate_5g')
