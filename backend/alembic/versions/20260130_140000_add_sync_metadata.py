"""Add sync_metadata table for tracking data freshness

Revision ID: 20260130_140000
Revises: 20260130_120000
Create Date: 2026-01-30 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260130_140000'
down_revision = '20260130_120000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sync_metadata table
    op.create_table(
        'sync_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_key', sa.String(50), nullable=False),
        sa.Column('data_type', sa.String(30), nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('games_count', sa.Integer(), nullable=True),
        sa.Column('lines_count', sa.Integer(), nullable=True),
        sa.Column('props_count', sa.Integer(), nullable=True),
        sa.Column('picks_count', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(30), nullable=True),
        sa.Column('sync_duration_seconds', sa.Float(), nullable=True),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('is_healthy', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create index for quick lookups
    op.create_index('ix_sync_metadata_sport_type', 'sync_metadata', ['sport_key', 'data_type'])


def downgrade() -> None:
    op.drop_index('ix_sync_metadata_sport_type', table_name='sync_metadata')
    op.drop_table('sync_metadata')
