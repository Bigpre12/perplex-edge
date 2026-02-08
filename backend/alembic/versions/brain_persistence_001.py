"""brain persistence placeholder

Revision ID: brain_persistence_001
Revises: 20260204_030000
Create Date: 2026-02-07 23:04:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'brain_persistence_001'
down_revision = '20260204_030000'
branch_labels = None
depends_on = None


def upgrade():
    """Empty migration - tables already exist."""
    pass


def downgrade():
    """Empty downgrade."""
    pass
