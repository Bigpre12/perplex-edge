import os
import sys
import asyncio
from sqlalchemy import text

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from db.session import AsyncSessionLocal
from services.auth_service import auth_service

async def main():
    async with AsyncSessionLocal() as db:
        # Check if user exists
        res = await db.execute(text("SELECT id FROM users WHERE email = 'owner@lucrix.io'"))
        row = res.fetchone()
        
        pw_hash = auth_service.get_password_hash("LucrixAdmin2026!")
        
        if not row:
            print("Creating new owner account...")
            sql = text("""
                INSERT INTO users (username, email, hashed_password, subscription_tier, is_admin, is_active, created_at)
                VALUES ('lucrix_owner', 'owner@lucrix.io', :pw, 'elite', true, true, NOW())
            """)
            await db.execute(sql, {"pw": pw_hash})
        else:
            print(f"Updating existing owner account (ID {row[0]})...")
            sql = text("""
                UPDATE users 
                SET subscription_tier = 'elite', is_admin = true, hashed_password = :pw
                WHERE id = :uid
            """)
            await db.execute(sql, {"pw": pw_hash, "uid": row[0]})
            
        await db.commit()
        print("Owner account provisioned completely.")

if __name__ == "__main__":
    asyncio.run(main())
