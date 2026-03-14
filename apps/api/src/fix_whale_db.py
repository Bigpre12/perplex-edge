import sqlite3
import os

# Correct DB path from settings
db_path = r"c:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\src\data\perplex_local.db"

def create_whale_table():
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing table if it's broken or start fresh
    cursor.execute("DROP TABLE IF EXISTS whale_moves")
    
    cursor.execute("""
        CREATE TABLE whale_moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT,
            player_name TEXT,
            stat_type TEXT,
            line REAL,
            move_type TEXT,
            side TEXT,
            severity TEXT,
            amount_estimate REAL,
            sportsbook TEXT,
            books_involved TEXT,
            whale_label TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print(f"Whale moves table created successfully at {db_path}.")

if __name__ == "__main__":
    create_whale_table()
