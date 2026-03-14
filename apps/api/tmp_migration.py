import sqlite3
import os

db_path = "./data/perplex_local.db"
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column(table, column, type, default=None):
    try:
        query = f"ALTER TABLE {table} ADD COLUMN {column} {type}"
        if default is not None:
            query += f" DEFAULT {default}"
        cursor.execute(query)
        print(f"Added {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding {column} to {table}: {e}")

# Contests
add_column("contests", "description", "TEXT")
add_column("contests", "prize_description", "TEXT")
add_column("contests", "required_legs", "INTEGER", default=5)
add_column("contests", "entry_count", "INTEGER", default=0)

# ContestEntries
add_column("contestentries", "display_name", "TEXT")
add_column("contestentries", "prop_ids_json", "TEXT")
add_column("contestentries", "hits", "INTEGER", default=0)
add_column("contestentries", "total_legs", "INTEGER", default=0)
add_column("contestentries", "submitted_at", "DATETIME")

conn.commit()
conn.close()
print("Migration completed.")
