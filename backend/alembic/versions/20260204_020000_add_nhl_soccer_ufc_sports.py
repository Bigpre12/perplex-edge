"""Add NHL, Soccer, and UFC sports

Adds the following sports if they don't exist:
- NHL (id=53, key=icehockey_nhl)
- EPL (id=70, key=soccer_epl)
- UCL (id=71, key=soccer_uefa_champs_league)
- MLS (id=72, key=soccer_usa_mls)
- UFC (id=80, key=mma_mixed_martial_arts)

Revision ID: 20260204_020000
Revises: 20260204_010000
Create Date: 2026-02-04 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260204_020000'
down_revision = '20260204_010000'
branch_labels = None
depends_on = None


# Sports to add with their expected IDs
SPORTS_TO_ADD = [
    # (id, name, league_code, key)
    (53, 'NHL', 'NHL', 'icehockey_nhl'),
    (70, 'English Premier League', 'EPL', 'soccer_epl'),
    (71, 'UEFA Champions League', 'UCL', 'soccer_uefa_champs_league'),
    (72, 'MLS', 'MLS', 'soccer_usa_mls'),
    (80, 'UFC', 'UFC', 'mma_mixed_martial_arts'),
]


def upgrade() -> None:
    # Insert sports that don't exist yet
    for sport_id, name, league_code, key in SPORTS_TO_ADD:
        op.execute(f"""
            INSERT INTO sports (id, name, league_code, key, created_at, updated_at)
            VALUES ({sport_id}, '{name}', '{league_code}', '{key}', NOW(), NOW())
            ON CONFLICT (league_code) DO NOTHING
        """)
    
    # Reset sequence to be above max ID to avoid conflicts
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('sports', 'id'),
            GREATEST(
                COALESCE((SELECT MAX(id) FROM sports), 0),
                100
            )
        )
    """)


def downgrade() -> None:
    # Remove the added sports
    for sport_id, name, league_code, key in SPORTS_TO_ADD:
        op.execute(f"DELETE FROM sports WHERE league_code = '{league_code}'")
