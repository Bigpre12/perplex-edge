"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-01-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Sports table
    op.create_table(
        'sports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('league_code', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('league_code')
    )

    # Teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('external_team_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('abbreviation', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_teams_sport_external', 'teams', ['sport_id', 'external_team_id'], unique=True)

    # Players table
    op.create_table(
        'players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('external_player_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('position', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_players_sport_external', 'players', ['sport_id', 'external_player_id'], unique=True)

    # Games table
    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('external_game_id', sa.String(length=100), nullable=False),
        sa.Column('home_team_id', sa.Integer(), nullable=False),
        sa.Column('away_team_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='scheduled'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['away_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['home_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_games_sport_external', 'games', ['sport_id', 'external_game_id'], unique=True)
    op.create_index('ix_games_start_time', 'games', ['start_time'], unique=False)

    # Markets table
    op.create_table(
        'markets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('market_type', sa.String(length=50), nullable=False),
        sa.Column('stat_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_markets_sport_type', 'markets', ['sport_id', 'market_type', 'stat_type'], unique=False)

    # Lines table
    op.create_table(
        'lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('market_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=True),
        sa.Column('sportsbook', sa.String(length=50), nullable=False),
        sa.Column('line_value', sa.Float(), nullable=True),
        sa.Column('odds', sa.Float(), nullable=False),
        sa.Column('side', sa.String(length=20), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['market_id'], ['markets.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_lines_game_market', 'lines', ['game_id', 'market_id'], unique=False)
    op.create_index('ix_lines_current', 'lines', ['is_current', 'game_id'], unique=False)
    op.create_index('ix_lines_fetched_at', 'lines', ['fetched_at'], unique=False)

    # Injuries table
    op.create_table(
        'injuries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('status_detail', sa.String(length=500), nullable=True),
        sa.Column('is_starter_flag', sa.Boolean(), nullable=True),
        sa.Column('probability', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_injuries_player', 'injuries', ['player_id'], unique=False)
    op.create_index('ix_injuries_updated', 'injuries', ['updated_at'], unique=False)

    # Player game stats table
    op.create_table(
        'player_game_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('stat_type', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('minutes', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_player_game_stats_player_game', 'player_game_stats', ['player_id', 'game_id'], unique=False)
    op.create_index('ix_player_game_stats_stat_type', 'player_game_stats', ['stat_type'], unique=False)

    # Model picks table
    op.create_table(
        'model_picks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=True),
        sa.Column('market_id', sa.Integer(), nullable=False),
        sa.Column('side', sa.String(length=20), nullable=False),
        sa.Column('line_value', sa.Float(), nullable=True),
        sa.Column('odds', sa.Float(), nullable=False),
        sa.Column('model_probability', sa.Float(), nullable=False),
        sa.Column('implied_probability', sa.Float(), nullable=False),
        sa.Column('expected_value', sa.Float(), nullable=False),
        sa.Column('hit_rate_30d', sa.Float(), nullable=True),
        sa.Column('hit_rate_10g', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['market_id'], ['markets.id'], ),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_model_picks_game', 'model_picks', ['game_id'], unique=False)
    op.create_index('ix_model_picks_active', 'model_picks', ['is_active', 'sport_id'], unique=False)
    op.create_index('ix_model_picks_generated', 'model_picks', ['generated_at'], unique=False)
    op.create_index('ix_model_picks_confidence', 'model_picks', ['confidence_score'], unique=False)


def downgrade() -> None:
    op.drop_table('model_picks')
    op.drop_table('player_game_stats')
    op.drop_table('injuries')
    op.drop_table('lines')
    op.drop_table('markets')
    op.drop_table('games')
    op.drop_table('players')
    op.drop_table('teams')
    op.drop_table('sports')
