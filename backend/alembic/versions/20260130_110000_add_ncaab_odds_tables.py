"""Add NCAAB odds tables for live and historical tracking

Revision ID: 20260130_110000
Revises: 20260130_100000
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '20260130_110000'
down_revision: Union[str, None] = '20260130_100000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create live_odds_ncaab table
    op.create_table(
        'live_odds_ncaab',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('sport', sa.String(length=20), nullable=False, server_default='NCAAB'),
        sa.Column('game_id', sa.String(length=100), nullable=False),
        sa.Column('home_team', sa.String(length=100), nullable=False),
        sa.Column('away_team', sa.String(length=100), nullable=False),
        sa.Column('home_odds', sa.Float(), nullable=False),
        sa.Column('away_odds', sa.Float(), nullable=False),
        sa.Column('draw_odds', sa.Float(), nullable=True),
        sa.Column('bookmaker', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('season', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_live_odds_ncaab_game', 'live_odds_ncaab', ['game_id'])
    op.create_index('ix_live_odds_ncaab_season', 'live_odds_ncaab', ['season'])
    op.create_index('ix_live_odds_ncaab_bookmaker', 'live_odds_ncaab', ['bookmaker'])
    op.create_index('ix_live_odds_ncaab_teams', 'live_odds_ncaab', ['home_team', 'away_team'])

    # Create historical_odds_ncaab table
    op.create_table(
        'historical_odds_ncaab',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('sport', sa.String(length=20), nullable=False, server_default='NCAAB'),
        sa.Column('game_id', sa.String(length=100), nullable=False),
        sa.Column('home_team', sa.String(length=100), nullable=False),
        sa.Column('away_team', sa.String(length=100), nullable=False),
        sa.Column('home_odds', sa.Float(), nullable=False),
        sa.Column('away_odds', sa.Float(), nullable=False),
        sa.Column('draw_odds', sa.Float(), nullable=True),
        sa.Column('bookmaker', sa.String(length=50), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('result', sa.String(length=10), nullable=True),
        sa.Column('season', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_historical_odds_ncaab_game', 'historical_odds_ncaab', ['game_id'])
    op.create_index('ix_historical_odds_ncaab_season', 'historical_odds_ncaab', ['season'])
    op.create_index('ix_historical_odds_ncaab_bookmaker', 'historical_odds_ncaab', ['bookmaker'])
    op.create_index('ix_historical_odds_ncaab_snapshot', 'historical_odds_ncaab', ['snapshot_date'])
    op.create_index('ix_historical_odds_ncaab_result', 'historical_odds_ncaab', ['result'])


def downgrade() -> None:
    # Drop historical_odds_ncaab table
    op.drop_index('ix_historical_odds_ncaab_result', table_name='historical_odds_ncaab')
    op.drop_index('ix_historical_odds_ncaab_snapshot', table_name='historical_odds_ncaab')
    op.drop_index('ix_historical_odds_ncaab_bookmaker', table_name='historical_odds_ncaab')
    op.drop_index('ix_historical_odds_ncaab_season', table_name='historical_odds_ncaab')
    op.drop_index('ix_historical_odds_ncaab_game', table_name='historical_odds_ncaab')
    op.drop_table('historical_odds_ncaab')
    
    # Drop live_odds_ncaab table
    op.drop_index('ix_live_odds_ncaab_teams', table_name='live_odds_ncaab')
    op.drop_index('ix_live_odds_ncaab_bookmaker', table_name='live_odds_ncaab')
    op.drop_index('ix_live_odds_ncaab_season', table_name='live_odds_ncaab')
    op.drop_index('ix_live_odds_ncaab_game', table_name='live_odds_ncaab')
    op.drop_table('live_odds_ncaab')
