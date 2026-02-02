"""Fix sport IDs to match expected values

This migration ensures NBA, NFL, and NCAAB have the expected IDs:
- NBA = 30
- NFL = 31  
- NCAAB = 32

These sports were previously auto-assigned IDs by PostgreSQL, which may
not match the hardcoded mappings in the codebase.

Revision ID: 20260202_020000
Revises: 20260202_010000
Create Date: 2026-02-02 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260202_020000'
down_revision: Union[str, None] = '20260202_010000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Expected sport ID mappings
EXPECTED_IDS = {
    'NBA': 30,
    'NFL': 31,
    'NCAAB': 32,
    'MLB': 40,
    'NCAAF': 41,
    'ATP': 50,
    'WTA': 51,
}

# Tables with sport_id foreign key that need updating
TABLES_WITH_SPORT_ID = [
    'teams',
    'players', 
    'games',
    'markets',
    'injuries',
    'model_picks',
    'player_hit_rates',
    'calibration_metrics',
    'user_bets',
    'watchlists',
    'shared_cards',
]


def upgrade() -> None:
    # Get connection for raw SQL execution
    connection = op.get_bind()
    
    # Step 1: Get current sport IDs from database
    result = connection.execute(sa.text("SELECT id, league_code FROM sports"))
    current_sports = {row[1]: row[0] for row in result}
    
    # Step 2: Build mapping of old_id -> new_id for sports that need fixing
    id_mapping = {}
    for league_code, expected_id in EXPECTED_IDS.items():
        current_id = current_sports.get(league_code)
        if current_id is not None and current_id != expected_id:
            id_mapping[current_id] = expected_id
            print(f"Will remap {league_code}: {current_id} -> {expected_id}")
    
    if not id_mapping:
        print("All sport IDs already match expected values. No changes needed.")
        return
    
    # Step 3: Temporarily disable FK constraints
    # Use deferred constraints to allow updates
    op.execute("SET CONSTRAINTS ALL DEFERRED")
    
    # Step 4: Insert sports that don't exist yet with correct IDs
    for league_code, expected_id in EXPECTED_IDS.items():
        if league_code not in current_sports:
            # Sport doesn't exist, insert it
            sport_names = {
                'NBA': 'NBA',
                'NFL': 'NFL',
                'NCAAB': 'NCAA Basketball',
                'MLB': 'MLB',
                'NCAAF': 'NCAA Football',
                'ATP': 'Tennis ATP',
                'WTA': 'Tennis WTA',
            }
            sport_keys = {
                'NBA': 'basketball_nba',
                'NFL': 'americanfootball_nfl',
                'NCAAB': 'basketball_ncaab',
                'MLB': 'baseball_mlb',
                'NCAAF': 'americanfootball_ncaaf',
                'ATP': 'tennis_atp',
                'WTA': 'tennis_wta',
            }
            op.execute(f"""
                INSERT INTO sports (id, name, league_code, key, created_at, updated_at)
                VALUES ({expected_id}, '{sport_names[league_code]}', '{league_code}', 
                        '{sport_keys[league_code]}', NOW(), NOW())
                ON CONFLICT (league_code) DO NOTHING
            """)
    
    # Step 5: For each sport that needs ID change, use temp IDs to avoid conflicts
    # First pass: move conflicting sports to temporary negative IDs
    for old_id, new_id in id_mapping.items():
        temp_id = -old_id  # Use negative as temp
        
        # Update sport ID to temp
        op.execute(f"UPDATE sports SET id = {temp_id} WHERE id = {old_id}")
        
        # Update all FK references to temp
        for table in TABLES_WITH_SPORT_ID:
            op.execute(f"UPDATE {table} SET sport_id = {temp_id} WHERE sport_id = {old_id}")
    
    # Second pass: move from temp IDs to final IDs
    for old_id, new_id in id_mapping.items():
        temp_id = -old_id
        
        # Update sport ID to final
        op.execute(f"UPDATE sports SET id = {new_id} WHERE id = {temp_id}")
        
        # Update all FK references to final
        for table in TABLES_WITH_SPORT_ID:
            op.execute(f"UPDATE {table} SET sport_id = {new_id} WHERE sport_id = {temp_id}")
    
    # Step 6: Reset the sequence to be above max ID
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('sports', 'id'),
            GREATEST(
                COALESCE((SELECT MAX(id) FROM sports), 0),
                51
            )
        )
    """)
    
    # Re-enable constraints
    op.execute("SET CONSTRAINTS ALL IMMEDIATE")
    
    print("Sport ID migration completed successfully!")
    print("Expected mapping:")
    for league, id in EXPECTED_IDS.items():
        print(f"  {league} = {id}")


def downgrade() -> None:
    # Downgrade is not straightforward since we don't know original IDs
    # Just log a warning
    print("WARNING: Downgrade does not restore original sport IDs.")
    print("If you need to revert, check your database backup.")
