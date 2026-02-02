"""Add NCAAF sport row

Revision ID: 20260201_010000
Revises: 20260201_000000
Create Date: 2026-02-01 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260201_010000'
down_revision = '20260201_000000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert NCAAF row if it doesn't exist (using id=41)
    op.execute("""
        INSERT INTO sports (id, name, league_code, key, created_at, updated_at)
        SELECT 41, 'NCAA Football', 'NCAAF', 'americanfootball_ncaaf', NOW(), NOW()
        WHERE NOT EXISTS (SELECT 1 FROM sports WHERE league_code = 'NCAAF')
    """)
    
    # Ensure sequence is at least 42 to avoid conflicts
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('sports', 'id'),
            GREATEST(
                (SELECT MAX(id) FROM sports),
                41
            )
        )
    """)


def downgrade() -> None:
    # Remove NCAAF row (only if we added it)
    op.execute("DELETE FROM sports WHERE id = 41 AND league_code = 'NCAAF'")
