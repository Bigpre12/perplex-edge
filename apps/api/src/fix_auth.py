import os
import sys
import asyncio
from sqlalchemy import select
from passlib.context import CryptContext

# Ensure src is in the path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from database import async_session_maker
from models.users import User

pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")

async def provision_owners():
    owner_emails_str = os.getenv("OWNER_EMAILS", "brydsonpreion31@gmail.com,admin@perplex.edge")
    owner_secret = os.getenv("OWNER_SECRET", "ag_prod_8f2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b")
    
    owner_emails = [e.strip() for e in owner_emails_str.split(",")]
    temp_password = "LUCRIX2026"
    hashed_pw = pwd_context.hash(temp_password)
    
    async with async_session_maker() as session:
        for email in owner_emails:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"Provisioning owner: {email}")
                new_user = User(
                    username=email.split("@")[0],
                    email=email,
                    hashed_password=hashed_pw,
                    subscription_tier="elite",
                    is_admin=True
                )
                session.add(new_user)
            else:
                print(f"Owner already exists: {email}")
        
        await session.commit()
    print("Owner provisioning complete.")

if __name__ == "__main__":
    # Load .env manually if needed, but run_api.py already does or we assume env is set
    asyncio.run(provision_owners())
