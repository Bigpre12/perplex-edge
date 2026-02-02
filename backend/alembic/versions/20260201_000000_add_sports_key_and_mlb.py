"""Add sports.key column and MLB sport row

Revision ID: 20260201_000000
Revises: 20260131_000000
Create Date: 2026-02-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260201_000000'
down_revision = '20260131_000000'
branch_labels = None
depends_on = None


# Mapping from league_code to The Odds API sport key
LEAGUE_CODE_TO_KEY = {
    "NBA": "basketball_nba",
    "NFL": "americanfootball_nfl",
    "NCAAB": "basketball_ncaab",
    "NCAA Basketball": "basketball_ncaab",
    "MLB": "baseball_mlb",
    "NHL": "icehockey_nhl",
    "ATP": "tennis_atp",
    "WTA": "tennis_wta",
    "NCAAF": "americanfootball_ncaaf",
}


def upgrade() -> None:
    # 1. Add key column (nullable first for backfill)
    op.add_column('sports', sa.Column('key', sa.String(length=50), nullable=True))
    
    # 2. Backfill existing rows based on league_code
    for league_code, sport_key in LEAGUE_CODE_TO_KEY.items():
        op.execute(
            f"UPDATE sports SET key = '{sport_key}' WHERE league_code = '{league_code}'"
        )
    
    # 3. Set any remaining NULL keys to a fallback (league_code lowercased with underscore)
    op.execute(
        "UPDATE sports SET key = LOWER(REPLACE(league_code, ' ', '_')) WHERE key IS NULL"
    )
    
    # 4. Make key column NOT NULL now that all rows have values
    op.alter_column('sports', 'key', nullable=False)
    
    # 5. Add unique constraint on key
    op.create_unique_constraint('uq_sports_key', 'sports', ['key'])
    
    # 6. Insert MLB row if it doesn't exist (using id=40)
    op.execute("""
        INSERT INTO sports (id, name, league_code, key, created_at, updated_at)
        SELECT 40, 'MLB', 'MLB', 'baseball_mlb', NOW(), NOW()
        WHERE NOT EXISTS (SELECT 1 FROM sports WHERE league_code = 'MLB')
    """)
    
    # 7. Ensure sequence is at least 41 to avoid conflicts
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('sports', 'id'),
            GREATEST(
                (SELECT MAX(id) FROM sports),
                40
            )
        )
    """)


def downgrade() -> None:
    # Remove MLB row (only if we added it)
    op.execute("DELETE FROM sports WHERE id = 40 AND league_code = 'MLB'")
    
    # Remove unique constraint
    op.drop_constraint('uq_sports_key', 'sports', type_='unique')
    
    # Remove key column
    op.drop_column('sports', 'key')
