import sqlite3
DB_PATH = "perplex_local.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print([t[0] for t in cursor.fetchall()])
conn.close()
