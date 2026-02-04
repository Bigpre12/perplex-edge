"""Add seasons and season_rosters tables.

Revision ID: 20260204_010000
Revises: 20260204_000000
Create Date: 2026-02-04 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260204_010000'
down_revision = '20260204_000000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create seasons table
    op.create_table(
        'seasons',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('season_year', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('sport_id', 'season_year', name='uq_season_sport_year'),
    )
    
    # Create indexes for seasons
    op.create_index('ix_seasons_sport_id', 'seasons', ['sport_id'])
    op.create_index('ix_seasons_is_current', 'seasons', ['is_current'])
    
    # Create season_rosters table
    op.create_table(
        'season_rosters',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('season_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('jersey_number', sa.String(10), nullable=True),
        sa.Column('position', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('season_id', 'team_id', 'player_id', name='uq_roster_season_team_player'),
    )
    
    # Create indexes for season_rosters
    op.create_index('ix_season_rosters_season_id', 'season_rosters', ['season_id'])
    op.create_index('ix_season_rosters_team_id', 'season_rosters', ['team_id'])
    op.create_index('ix_season_rosters_player_id', 'season_rosters', ['player_id'])
    op.create_index('ix_season_rosters_is_active', 'season_rosters', ['is_active'])
    
    # Add season_id column to games table
    op.add_column(
        'games',
        sa.Column('season_id', sa.Integer(), nullable=True),
    )
    
    # Add foreign key constraint for games.season_id
    op.create_foreign_key(
        'fk_games_season_id',
        'games',
        'seasons',
        ['season_id'],
        ['id'],
        ondelete='SET NULL',
    )
    
    # Create index for games.season_id
    op.create_index('ix_games_season_id', 'games', ['season_id'])


def downgrade() -> None:
    # Drop games.season_id
    op.drop_index('ix_games_season_id', table_name='games')
    op.drop_constraint('fk_games_season_id', 'games', type_='foreignkey')
    op.drop_column('games', 'season_id')
    
    # Drop season_rosters indexes and table
    op.drop_index('ix_season_rosters_is_active', table_name='season_rosters')
    op.drop_index('ix_season_rosters_player_id', table_name='season_rosters')
    op.drop_index('ix_season_rosters_team_id', table_name='season_rosters')
    op.drop_index('ix_season_rosters_season_id', table_name='season_rosters')
    op.drop_table('season_rosters')
    
    # Drop seasons indexes and table
    op.drop_index('ix_seasons_is_current', table_name='seasons')
    op.drop_index('ix_seasons_sport_id', table_name='seasons')
    op.drop_table('seasons')
