"""patch whale_moves missing selection and market_key

Revision ID: f2a7c9e1b4d2
Revises: c1d2e3f4a5b6
Create Date: 2026-04-26 08:55:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2a7c9e1b4d2"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE whale_moves ADD COLUMN IF NOT EXISTS market_key TEXT"))
    conn.execute(sa.text("ALTER TABLE whale_moves ADD COLUMN IF NOT EXISTS selection TEXT"))


def downgrade() -> None:
    # Preserve data safety: no-op downgrade for additive hotfix columns.
    pass

