import sqlite3
import os
DB_PATH = os.path.join("data", "perplex_local.db")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT id, username, email, subscription_tier, is_admin FROM users")
users = [dict(row) for row in cursor.fetchall()]
for user in users:
    print(user)
conn.close()
