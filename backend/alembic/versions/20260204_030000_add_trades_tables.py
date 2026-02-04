"""Add trades and trade_details tables

Revision ID: 20260204_030000
Revises: 20260204_020000
Create Date: 2026-02-04 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260204_030000'
down_revision = '20260204_020000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create trades table
    op.create_table(
        'trades',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('season_year', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('headline', sa.String(500), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('source', sa.String(100), nullable=True, server_default='nba.com'),
        sa.Column('is_applied', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for trades
    op.create_index('ix_trades_trade_date', 'trades', ['trade_date'])
    op.create_index('ix_trades_season_year', 'trades', ['season_year'])
    op.create_index('ix_trades_is_applied', 'trades', ['is_applied'])
    
    # Create trade_details table
    op.create_table(
        'trade_details',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('trade_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=True),
        sa.Column('from_team_id', sa.Integer(), nullable=False),
        sa.Column('to_team_id', sa.Integer(), nullable=False),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('asset_description', sa.String(500), nullable=True),
        sa.Column('player_name', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['from_team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_team_id'], ['teams.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for trade_details
    op.create_index('ix_trade_details_trade_id', 'trade_details', ['trade_id'])
    op.create_index('ix_trade_details_player_id', 'trade_details', ['player_id'])
    op.create_index('ix_trade_details_from_team_id', 'trade_details', ['from_team_id'])
    op.create_index('ix_trade_details_to_team_id', 'trade_details', ['to_team_id'])
    op.create_index('ix_trade_details_asset_type', 'trade_details', ['asset_type'])


def downgrade() -> None:
    # Drop trade_details indexes and table
    op.drop_index('ix_trade_details_asset_type', table_name='trade_details')
    op.drop_index('ix_trade_details_to_team_id', table_name='trade_details')
    op.drop_index('ix_trade_details_from_team_id', table_name='trade_details')
    op.drop_index('ix_trade_details_player_id', table_name='trade_details')
    op.drop_index('ix_trade_details_trade_id', table_name='trade_details')
    op.drop_table('trade_details')
    
    # Drop trades indexes and table
    op.drop_index('ix_trades_is_applied', table_name='trades')
    op.drop_index('ix_trades_season_year', table_name='trades')
    op.drop_index('ix_trades_trade_date', table_name='trades')
    op.drop_table('trades')
