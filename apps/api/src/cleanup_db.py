import sqlite3
import os

db_path = './data/perplex_local.db'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables_to_drop = [
    'whale_moves', 
    'steam_events', 
    'clv_records', 
    'refereegame', 
    'referral', 
    'schedule', 
    'playerstats', 
    'picks', 
    'prop_history'
]

for table in tables_to_drop:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"Dropped {table}")
    except Exception as e:
        print(f"Failed to drop {table}: {e}")

conn.commit()
conn.close()
print("Database cleanup complete.")
