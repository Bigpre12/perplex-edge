import os
import sys
import asyncio
import sqlite3
from passlib.hash import pbkdf2_sha256

# Configuration
DB_PATH = "./data/perplex_local.db"
OWNER_EMAILS = os.getenv("OWNER_EMAILS", "brydsonpreion31@gmail.com,admin@perplex.edge").split(",")
TEMP_PW = "LUCRIX2026"

def fix():
    hashed = pbkdf2_sha256.hash(TEMP_PW)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for email in OWNER_EMAILS:
        email = email.strip()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if not cursor.fetchone():
            print(f"Adding user: {email}")
            username = email.split("@")[0]
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password, subscription_tier, is_active, is_admin) VALUES (?, ?, ?, ?, ?, ?)",
                (username, email, hashed, "elite", 1, 1)
            )
        else:
            print(f"User exists: {email}")
            # Update password anyway to be sure
            cursor.execute("UPDATE users SET hashed_password = ? WHERE email = ?", (hashed, email))
    
    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    fix()
