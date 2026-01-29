"""Add pick_results and player_hit_rates tables

Revision ID: 20260129_000000
Revises: 20260128_220000
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260129_000000'
down_revision: Union[str, None] = '20260128_220000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pick_results table
    op.create_table(
        'pick_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pick_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=True),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('actual_value', sa.Float(), nullable=False),
        sa.Column('line_value', sa.Float(), nullable=False),
        sa.Column('side', sa.String(length=20), nullable=False),
        sa.Column('hit', sa.Boolean(), nullable=False),
        sa.Column('settled_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['pick_id'], ['model_picks.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pick_id')
    )
    op.create_index('ix_pick_results_hit', 'pick_results', ['hit', 'player_id'], unique=False)
    op.create_index('ix_pick_results_pick', 'pick_results', ['pick_id'], unique=False)
    op.create_index('ix_pick_results_player', 'pick_results', ['player_id'], unique=False)
    op.create_index('ix_pick_results_settled', 'pick_results', ['settled_at'], unique=False)

    # Create player_hit_rates table
    op.create_table(
        'player_hit_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('hits_7d', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_7d', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hit_rate_7d', sa.Float(), nullable=True),
        sa.Column('hits_all', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_all', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hit_rate_all', sa.Float(), nullable=True),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('best_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('worst_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_5_results', sa.String(length=5), nullable=True),
        sa.Column('last_pick_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_id')
    )
    op.create_index('ix_player_hit_rates_7d', 'player_hit_rates', ['hit_rate_7d'], unique=False)
    op.create_index('ix_player_hit_rates_player', 'player_hit_rates', ['player_id'], unique=True)
    op.create_index('ix_player_hit_rates_sport', 'player_hit_rates', ['sport_id'], unique=False)
    op.create_index('ix_player_hit_rates_streak', 'player_hit_rates', ['current_streak'], unique=False)


def downgrade() -> None:
    # Drop player_hit_rates table
    op.drop_index('ix_player_hit_rates_streak', table_name='player_hit_rates')
    op.drop_index('ix_player_hit_rates_sport', table_name='player_hit_rates')
    op.drop_index('ix_player_hit_rates_player', table_name='player_hit_rates')
    op.drop_index('ix_player_hit_rates_7d', table_name='player_hit_rates')
    op.drop_table('player_hit_rates')

    # Drop pick_results table
    op.drop_index('ix_pick_results_settled', table_name='pick_results')
    op.drop_index('ix_pick_results_player', table_name='pick_results')
    op.drop_index('ix_pick_results_pick', table_name='pick_results')
    op.drop_index('ix_pick_results_hit', table_name='pick_results')
    op.drop_table('pick_results')
