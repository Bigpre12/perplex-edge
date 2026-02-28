import sqlite3
import os

DB_PATH = "c:\\Users\\preio\\OneDrive\\Documents\\Untitled\\perplex_engine\\perplex-edge\\backend\\perplex_local.db"

def seed_mma_boxing():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Insert Sports
    sports = [
        (54, 'UFC / MMA', 'mma_mixed_martial_arts', 'UFC'),
        (55, 'Boxing', 'boxing', 'BOX')
    ]
    
    for sid, name, key, code in sports:
        cursor.execute("""
            INSERT OR IGNORE INTO sports (id, name, key, league_code)
            VALUES (?, ?, ?, ?)
        """, (sid, name, key, code))
    
    # 2. Insert Markets
    mma_markets = [
        ('fight_result',        'Fight Winner (Moneyline)',          54),
        ('method_of_victory',   'Win by KO/TKO vs Decision vs Sub',  54),
        ('total_rounds',        'Over/Under Total Rounds',           54),
        ('goes_to_decision',    'Does fight go to decision?',        54),
        ('round_betting',       'Fight ends in Round X',             54),
        ('distance',            'Fight goes the distance',           54),
        ('finish_in_round',     'Specific round finish',             54)
    ]
    
    boxing_markets = [
        ('fight_result',        'Fight Winner (Moneyline)',          55),
        ('method_of_victory',   'Win by KO vs Decision vs TKO',     55),
        ('total_rounds',        'Over/Under Total Rounds',           55),
        ('goes_to_decision',    'Does fight go to decision?',        55),
        ('round_betting',       'Fight ends in Round X',             55),
        ('knockdown',           'Over/Under Knockdowns',             55),
        ('distance',            'Fight goes the distance',           55)
    ]
    
    for stat_type, desc, sid in mma_markets + boxing_markets:
        cursor.execute("""
            INSERT OR IGNORE INTO markets (stat_type, description, sport_id)
            VALUES (?, ?, ?)
        """, (stat_type, desc, sid))
    
    conn.commit()
    conn.close()
    print("MMA and Boxing seeding complete.")

if __name__ == "__main__":
    seed_mma_boxing()
