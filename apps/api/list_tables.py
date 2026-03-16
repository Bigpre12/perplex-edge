# apps/api/list_tables.py
import sqlite3
import os

db_path = os.path.abspath(os.path.join("src", "data", "perplex_local.db"))
print(f"Checking DB: {db_path}")

if not os.path.exists(db_path):
    print("Database file does not exist!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    for table_name in [t[0] for t in tables]:
        cursor.execute(f"SELECT count(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Table: {table_name}, Count: {count}")
    
    conn.close()
