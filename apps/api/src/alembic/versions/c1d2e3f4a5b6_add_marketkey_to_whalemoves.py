"""add marketkey and all missing columns to legacy whalemoves table

Revision ID: c1d2e3f4a5b6
Revises: a1b2c3d4e5f6
Create Date: 2026-04-24 07:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to legacy whalemoves table (no-underscore variant)."""
    conn = op.get_bind()
    # Check if whalemoves table exists (legacy table without underscores)
    result = conn.execute(sa.text(
        "SELECT to_regclass('public.whalemoves')"
    ))
    row = result.fetchone()
    if row and row[0] is None:
        # Table doesn't exist yet - nothing to patch
        return

    # Add each missing column with IF NOT EXISTS guards
    cols_to_add = [
        ("marketkey", "TEXT"),
        ("eventid", "TEXT"),
        ("playername", "TEXT"),
        ("selection", "TEXT"),
        ("bookmaker", "TEXT"),
        ("booksinvolved", "TEXT"),
        ("pricebefore", "DOUBLE PRECISION"),
        ("priceafter", "DOUBLE PRECISION"),
        ("line", "DOUBLE PRECISION"),
        ("movetype", "TEXT"),
        ("whalelabel", "TEXT"),
        ("amountestimate", "DOUBLE PRECISION"),
        ("severity", "TEXT"),
        ("createdat", "TIMESTAMP WITH TIME ZONE"),
    ]
    for col_name, col_type in cols_to_add:
        conn.execute(sa.text(
            f"ALTER TABLE public.whalemoves ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
        ))


def downgrade() -> None:
    pass
