"""Hide impossible EV picks - deactivate picks with EV > 15%

Revision ID: 20260207_010000
Revises: 20260207_000000
Create Date: 2026-02-07 18:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20260207_010000'
down_revision = '20260207_000000'
branch_labels = None
depends_on = None


def upgrade():
    """Hide picks with impossible EV values (>15%)."""
    # Deactivate picks with EV > 15% - these are mathematically impossible
    op.execute("""
        UPDATE model_picks 
        SET is_active = false, 
            notes = COALESCE(notes || '; ', '') || 'Auto-deactivated: EV > 15% (impossible value)'
        WHERE expected_value > 0.15 
        AND is_active = true
    """)
    
    # Log how many were affected (this will show in Railway logs)
    result = op.get_bind().execute(sa.text("""
        SELECT COUNT(*) FROM model_picks 
        WHERE expected_value > 0.15 
        AND notes LIKE '%Auto-deactivated%'
    """))
    count = result.scalar()
    
    # This print will show in migration logs
    print(f"Migration: Deactivated {count} picks with EV > 15%")


def downgrade():
    """Reactivate the hidden picks (if needed for rollback)."""
    op.execute("""
        UPDATE model_picks 
        SET is_active = true,
            notes = REPLACE(notes, 'Auto-deactivated: EV > 15% (impossible value); ', '')
        WHERE notes LIKE '%Auto-deactivated: EV > 15% (impossible value)%'
    """)
