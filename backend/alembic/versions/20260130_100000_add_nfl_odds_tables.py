"""Add NFL odds tables for live and historical tracking

Revision ID: 20260130_100000
Revises: 20260130_000000
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '20260130_100000'
down_revision: Union[str, None] = '20260130_000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create live_odds_nfl table
    op.create_table(
        'live_odds_nfl',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('sport', sa.String(length=20), nullable=False, server_default='NFL'),
        sa.Column('game_id', sa.String(length=100), nullable=False),
        sa.Column('home_team', sa.String(length=100), nullable=False),
        sa.Column('away_team', sa.String(length=100), nullable=False),
        sa.Column('home_odds', sa.Float(), nullable=False),
        sa.Column('away_odds', sa.Float(), nullable=False),
        sa.Column('draw_odds', sa.Float(), nullable=True),
        sa.Column('bookmaker', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_live_odds_nfl_game', 'live_odds_nfl', ['game_id'])
    op.create_index('ix_live_odds_nfl_week_season', 'live_odds_nfl', ['week', 'season'])
    op.create_index('ix_live_odds_nfl_bookmaker', 'live_odds_nfl', ['bookmaker'])
    op.create_index('ix_live_odds_nfl_teams', 'live_odds_nfl', ['home_team', 'away_team'])

    # Create historical_odds_nfl table
    op.create_table(
        'historical_odds_nfl',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('sport', sa.String(length=20), nullable=False, server_default='NFL'),
        sa.Column('game_id', sa.String(length=100), nullable=False),
        sa.Column('home_team', sa.String(length=100), nullable=False),
        sa.Column('away_team', sa.String(length=100), nullable=False),
        sa.Column('home_odds', sa.Float(), nullable=False),
        sa.Column('away_odds', sa.Float(), nullable=False),
        sa.Column('draw_odds', sa.Float(), nullable=True),
        sa.Column('bookmaker', sa.String(length=50), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('result', sa.String(length=10), nullable=True),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_historical_odds_nfl_game', 'historical_odds_nfl', ['game_id'])
    op.create_index('ix_historical_odds_nfl_week_season', 'historical_odds_nfl', ['week', 'season'])
    op.create_index('ix_historical_odds_nfl_bookmaker', 'historical_odds_nfl', ['bookmaker'])
    op.create_index('ix_historical_odds_nfl_snapshot', 'historical_odds_nfl', ['snapshot_date'])
    op.create_index('ix_historical_odds_nfl_result', 'historical_odds_nfl', ['result'])


def downgrade() -> None:
    # Drop historical_odds_nfl table
    op.drop_index('ix_historical_odds_nfl_result', table_name='historical_odds_nfl')
    op.drop_index('ix_historical_odds_nfl_snapshot', table_name='historical_odds_nfl')
    op.drop_index('ix_historical_odds_nfl_bookmaker', table_name='historical_odds_nfl')
    op.drop_index('ix_historical_odds_nfl_week_season', table_name='historical_odds_nfl')
    op.drop_index('ix_historical_odds_nfl_game', table_name='historical_odds_nfl')
    op.drop_table('historical_odds_nfl')
    
    # Drop live_odds_nfl table
    op.drop_index('ix_live_odds_nfl_teams', table_name='live_odds_nfl')
    op.drop_index('ix_live_odds_nfl_bookmaker', table_name='live_odds_nfl')
    op.drop_index('ix_live_odds_nfl_week_season', table_name='live_odds_nfl')
    op.drop_index('ix_live_odds_nfl_game', table_name='live_odds_nfl')
    op.drop_table('live_odds_nfl')
