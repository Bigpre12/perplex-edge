"""Add ATP and WTA tennis sports

Revision ID: 20260202_000000
Revises: 20260201_010000
Create Date: 2026-02-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260202_000000'
down_revision = '20260201_010000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert ATP tennis row if it doesn't exist (using id=50)
    op.execute("""
        INSERT INTO sports (id, name, league_code, key, created_at, updated_at)
        SELECT 50, 'Tennis ATP', 'ATP', 'tennis_atp', NOW(), NOW()
        WHERE NOT EXISTS (SELECT 1 FROM sports WHERE league_code = 'ATP')
    """)
    
    # Insert WTA tennis row if it doesn't exist (using id=51)
    op.execute("""
        INSERT INTO sports (id, name, league_code, key, created_at, updated_at)
        SELECT 51, 'Tennis WTA', 'WTA', 'tennis_wta', NOW(), NOW()
        WHERE NOT EXISTS (SELECT 1 FROM sports WHERE league_code = 'WTA')
    """)
    
    # Ensure sequence is at least 52 to avoid conflicts
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('sports', 'id'),
            GREATEST(
                (SELECT MAX(id) FROM sports),
                51
            )
        )
    """)


def downgrade() -> None:
    # Remove tennis rows (only if we added them)
    op.execute("DELETE FROM sports WHERE id = 50 AND league_code = 'ATP'")
    op.execute("DELETE FROM sports WHERE id = 51 AND league_code = 'WTA'")
