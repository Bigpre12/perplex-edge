"""Add player_market_hit_rates table for per-market hot/cold tracking.

Revision ID: 20260203_000000
Revises: 20260202_020000_fix_sport_ids
Create Date: 2026-02-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260203_000000'
down_revision = '20260202_020000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create player_market_hit_rates table
    op.create_table(
        'player_market_hit_rates',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('player_id', sa.BigInteger(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('market', sa.String(50), nullable=False),
        sa.Column('side', sa.String(10), nullable=False),
        sa.Column('hits_7d', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_7d', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hit_rate_7d', sa.Float(), nullable=True),
        sa.Column('hits_all', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_all', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hit_rate_all', sa.Float(), nullable=True),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('best_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('worst_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_5_results', sa.String(5), nullable=True),
        sa.Column('last_pick_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('player_id', 'sport_id', 'market', 'side', name='uq_player_market_side'),
    )
    
    # Create indexes
    op.create_index('ix_player_market_hit_rates_player', 'player_market_hit_rates', ['player_id'])
    op.create_index('ix_player_market_hit_rates_sport', 'player_market_hit_rates', ['sport_id'])
    op.create_index('ix_player_market_hit_rates_market', 'player_market_hit_rates', ['market'])
    op.create_index('ix_player_market_hit_rates_streak', 'player_market_hit_rates', ['current_streak'])
    op.create_index('ix_player_market_hit_rates_7d', 'player_market_hit_rates', ['hit_rate_7d'])


def downgrade() -> None:
    op.drop_index('ix_player_market_hit_rates_7d', table_name='player_market_hit_rates')
    op.drop_index('ix_player_market_hit_rates_streak', table_name='player_market_hit_rates')
    op.drop_index('ix_player_market_hit_rates_market', table_name='player_market_hit_rates')
    op.drop_index('ix_player_market_hit_rates_sport', table_name='player_market_hit_rates')
    op.drop_index('ix_player_market_hit_rates_player', table_name='player_market_hit_rates')
    op.drop_table('player_market_hit_rates')
