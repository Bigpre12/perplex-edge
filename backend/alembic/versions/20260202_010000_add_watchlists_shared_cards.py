"""Add watchlists and shared_cards tables

Revision ID: 20260202_010000
Revises: 20260202_000000_add_tennis_sports
Create Date: 2026-02-02 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260202_010000'
down_revision: Union[str, None] = '20260202_000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create watchlists table
    op.create_table(
        'watchlists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('filters', sa.JSON(), nullable=False),
        sa.Column('alert_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('alert_discord_webhook', sa.String(length=500), nullable=True),
        sa.Column('alert_email', sa.String(length=255), nullable=True),
        sa.Column('last_check_at', sa.DateTime(), nullable=True),
        sa.Column('last_match_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_notified_at', sa.DateTime(), nullable=True),
        sa.Column('sport_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_watchlists_sport_id', 'watchlists', ['sport_id'], unique=False)
    op.create_index('ix_watchlists_alert_enabled', 'watchlists', ['alert_enabled'], unique=False)
    
    # Create shared_cards table
    op.create_table(
        'shared_cards',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=True),
        sa.Column('legs', sa.JSON(), nullable=False),
        sa.Column('leg_count', sa.Integer(), nullable=False),
        sa.Column('total_odds', sa.Integer(), nullable=False),
        sa.Column('decimal_odds', sa.Float(), nullable=False),
        sa.Column('parlay_probability', sa.Float(), nullable=False),
        sa.Column('parlay_ev', sa.Float(), nullable=False),
        sa.Column('overall_grade', sa.String(length=1), nullable=False),
        sa.Column('label', sa.String(length=10), nullable=False),
        sa.Column('kelly_suggested_units', sa.Float(), nullable=True),
        sa.Column('kelly_risk_level', sa.String(length=20), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, default=0),
        sa.Column('settled', sa.Boolean(), nullable=False, default=False),
        sa.Column('won', sa.Boolean(), nullable=True),
        sa.Column('settled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_shared_cards_platform', 'shared_cards', ['platform'], unique=False)
    op.create_index('ix_shared_cards_sport_id', 'shared_cards', ['sport_id'], unique=False)
    op.create_index('ix_shared_cards_created_at', 'shared_cards', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop shared_cards table
    op.drop_index('ix_shared_cards_created_at', table_name='shared_cards')
    op.drop_index('ix_shared_cards_sport_id', table_name='shared_cards')
    op.drop_index('ix_shared_cards_platform', table_name='shared_cards')
    op.drop_table('shared_cards')
    
    # Drop watchlists table
    op.drop_index('ix_watchlists_alert_enabled', table_name='watchlists')
    op.drop_index('ix_watchlists_sport_id', table_name='watchlists')
    op.drop_table('watchlists')
