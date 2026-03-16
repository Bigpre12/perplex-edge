# apps/api/db_integrity_check.py
import os
import sqlite3
import sys
from datetime import datetime

# Add src to path to use config
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from config import settings

def check():
    print(f"--- DATABASE INTEGRITY CHECK ---")
    print(f"Time: {datetime.now()}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Path from Settings
    print(f"Settings DATABASE_URL: {settings.DATABASE_URL}")
    raw_path = settings.DATABASE_URL.replace("sqlite:///", "")
    abs_path = os.path.abspath(raw_path)
    print(f"Resolved Absolute Path: {abs_path}")
    
    if not os.path.exists(abs_path):
        print(f"ERROR: File does not exist at {abs_path}")
        return

    print(f"File Size: {os.path.getsize(abs_path)} bytes")
    print(f"Last Modified: {datetime.fromtimestamp(os.path.getmtime(abs_path))}")
    
    try:
        conn = sqlite3.connect(abs_path)
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables found: {tables}")
        
        for table in tables:
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table '{table}' row count: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                first_row = cursor.fetchone()
                print(f"  Sample row from '{table}': {first_row}")
        
        conn.close()
    except Exception as e:
        print(f"ERROR during SQLite connect/query: {e}")

if __name__ == "__main__":
    check()
