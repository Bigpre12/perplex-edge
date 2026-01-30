"""Add odds_snapshots and game_results tables for OddsPapi historical tracking

Revision ID: 20260130_000000
Revises: 20260129_000000
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260130_000000'
down_revision: Union[str, None] = '20260129_000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create odds_snapshots table for tracking historical odds movements
    op.create_table(
        'odds_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('market_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=True),
        sa.Column('external_fixture_id', sa.String(length=100), nullable=False),
        sa.Column('external_market_id', sa.String(length=100), nullable=True),
        sa.Column('external_outcome_id', sa.String(length=100), nullable=True),
        sa.Column('bookmaker', sa.String(length=50), nullable=False),
        sa.Column('line_value', sa.Float(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('american_odds', sa.Float(), nullable=True),
        sa.Column('side', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('snapshot_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['market_id'], ['markets.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_odds_snapshots_game', 'odds_snapshots', ['game_id'])
    op.create_index('ix_odds_snapshots_player', 'odds_snapshots', ['player_id'])
    op.create_index('ix_odds_snapshots_snapshot_at', 'odds_snapshots', ['snapshot_at'])
    op.create_index('ix_odds_snapshots_game_market', 'odds_snapshots', ['game_id', 'market_id'])

    # Create game_results table for final scores and settlements
    op.create_table(
        'game_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('external_fixture_id', sa.String(length=100), nullable=False),
        sa.Column('home_score', sa.Integer(), nullable=False),
        sa.Column('away_score', sa.Integer(), nullable=False),
        sa.Column('period_scores', sa.String(length=500), nullable=True),
        sa.Column('is_settled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('settled_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id')
    )
    op.create_index('ix_game_results_game', 'game_results', ['game_id'], unique=True)
    op.create_index('ix_game_results_external', 'game_results', ['external_fixture_id'])
    op.create_index('ix_game_results_settled', 'game_results', ['settled_at'])


def downgrade() -> None:
    op.drop_index('ix_game_results_settled', table_name='game_results')
    op.drop_index('ix_game_results_external', table_name='game_results')
    op.drop_index('ix_game_results_game', table_name='game_results')
    op.drop_table('game_results')
    
    op.drop_index('ix_odds_snapshots_game_market', table_name='odds_snapshots')
    op.drop_index('ix_odds_snapshots_snapshot_at', table_name='odds_snapshots')
    op.drop_index('ix_odds_snapshots_player', table_name='odds_snapshots')
    op.drop_index('ix_odds_snapshots_game', table_name='odds_snapshots')
    op.drop_table('odds_snapshots')
