
import os
import asyncio
from supabase import create_client

async def check_supabase_user():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    email = "brydsonpreion31@gmail.com"
    
    if not url or not key:
        print("SUPABASE_NOT_CONFIGURED")
        return

    supabase = create_client(url, key)
    # List users (requires service role key)
    try:
        res = supabase.auth.admin.list_users()
        users = res.users
        user = next((u for u in users if u.email == email), None)
        if user:
            print(f"SUPABASE_USER_FOUND: {user.email}")
            print(f"ID: {user.id}")
            print(f"METADATA: {user.user_metadata}")
        else:
            print("SUPABASE_USER_NOT_FOUND")
    except Exception as e:
        print(f"SUPABASE_ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check_supabase_user())
