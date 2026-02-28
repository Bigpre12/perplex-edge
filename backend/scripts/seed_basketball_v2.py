
import sqlite3
import os

DB_PATH = "c:\\Users\\preio\\OneDrive\\Documents\\Untitled\\perplex_engine\\perplex-edge\\backend\\perplex_local.db"

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Basketball Stat Types (IDs: 30 NBA, 39 NCAAB, 53 WNBA)
    sports = [30, 39, 53]
    stats = [
        ('points', 'Over/Under Points'),
        ('rebounds', 'Over/Under Rebounds'),
        ('assists', 'Over/Under Assists'),
        ('steals', 'Over/Under Steals'),
        ('three_pointers', 'Over/Under 3-Pointers Made')
    ]
    
    for sport_id in sports:
        for stat_type, desc in stats:
            cursor.execute("""
                INSERT OR IGNORE INTO markets (stat_type, description, sport_id)
                VALUES (?, ?, ?)
            """, (stat_type, desc, sport_id))
    
    conn.commit()
    conn.close()
    print("Market seeding complete.")

if __name__ == "__main__":
    seed()
