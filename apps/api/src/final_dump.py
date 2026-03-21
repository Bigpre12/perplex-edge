import sqlite3
import os

db_path = "apps/api/src/data/perplex_local.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT * FROM props_live;")
    rows = cursor.fetchall()
    print(f"PropLive FINAL DUMP: {rows}")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    conn.close()
