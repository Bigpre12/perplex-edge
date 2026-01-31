"""Add user_bets table for personal results tracking

Revision ID: 20260131_000000
Revises: 20260130_140000
Create Date: 2026-01-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260131_000000'
down_revision = '20260130_140000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create bet_status enum type if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'betstatus') THEN
                CREATE TYPE betstatus AS ENUM ('pending', 'won', 'lost', 'push', 'void');
            END IF;
        END$$;
    """)
    
    # Create user_bets table
    # Note: create_type=False since we handle enum creation above
    betstatus_enum = sa.Enum('pending', 'won', 'lost', 'push', 'void', name='betstatus', create_type=False)
    
    op.create_table(
        'user_bets',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # What was bet on
        sa.Column('sport_id', sa.Integer(), sa.ForeignKey('sports.id'), nullable=False),
        sa.Column('game_id', sa.Integer(), sa.ForeignKey('games.id'), nullable=True),
        sa.Column('player_id', sa.Integer(), sa.ForeignKey('players.id'), nullable=True),
        
        # Market details
        sa.Column('market_type', sa.String(50), nullable=False),
        sa.Column('side', sa.String(20), nullable=False),
        sa.Column('line_value', sa.Float(), nullable=True),
        
        # Sportsbook and odds
        sa.Column('sportsbook', sa.String(50), nullable=False),
        sa.Column('opening_odds', sa.Integer(), nullable=False),
        
        # Stake
        sa.Column('stake', sa.Float(), nullable=False, server_default='1.0'),
        
        # Status
        sa.Column('status', betstatus_enum, nullable=False, server_default='pending'),
        
        # Result details
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('closing_odds', sa.Integer(), nullable=True),
        sa.Column('closing_line', sa.Float(), nullable=True),
        sa.Column('clv_cents', sa.Float(), nullable=True),
        sa.Column('profit_loss', sa.Float(), nullable=True),
        
        # Timestamps
        sa.Column('placed_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('settled_at', sa.DateTime(), nullable=True),
        
        # Optional fields
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('model_pick_id', sa.Integer(), sa.ForeignKey('model_picks.id'), nullable=True),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes
    op.create_index('ix_user_bets_sport', 'user_bets', ['sport_id'])
    op.create_index('ix_user_bets_game', 'user_bets', ['game_id'])
    op.create_index('ix_user_bets_player', 'user_bets', ['player_id'])
    op.create_index('ix_user_bets_status', 'user_bets', ['status'])
    op.create_index('ix_user_bets_sportsbook', 'user_bets', ['sportsbook'])
    op.create_index('ix_user_bets_market', 'user_bets', ['market_type'])
    op.create_index('ix_user_bets_placed_at', 'user_bets', ['placed_at'])
    op.create_index('ix_user_bets_settled_at', 'user_bets', ['settled_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_user_bets_settled_at', 'user_bets')
    op.drop_index('ix_user_bets_placed_at', 'user_bets')
    op.drop_index('ix_user_bets_market', 'user_bets')
    op.drop_index('ix_user_bets_sportsbook', 'user_bets')
    op.drop_index('ix_user_bets_status', 'user_bets')
    op.drop_index('ix_user_bets_player', 'user_bets')
    op.drop_index('ix_user_bets_game', 'user_bets')
    op.drop_index('ix_user_bets_sport', 'user_bets')
    
    # Drop table
    op.drop_table('user_bets')
    
    # Drop enum type if it exists
    op.execute("DROP TYPE IF EXISTS betstatus")
