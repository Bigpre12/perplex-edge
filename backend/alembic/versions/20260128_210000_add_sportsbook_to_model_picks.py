"""add sportsbook to model picks

Revision ID: add_sportsbook_picks
Revises: add_picks_playerstat
Create Date: 2026-01-28 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_sportsbook_picks'
down_revision: Union[str, None] = '744eb1c7924e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add sportsbook column to model_picks table
    op.add_column('model_picks', sa.Column('sportsbook', sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column('model_picks', 'sportsbook')
