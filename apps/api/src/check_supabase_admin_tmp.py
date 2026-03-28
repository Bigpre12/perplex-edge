
import httpx
import asyncio
import os

async def test_supabase_auth():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    email = "brydsonpreion31@gmail.com"
    password = "USER_PASSWORD_PLACEHOLDER" # I don't know the password
    
    # Actually, I can't test auth without the password.
    # But I can check if the user exists via the admin API (requires SERVICE_KEY)
    service_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_key:
        print("SUPABASE_NOT_CONFIGURED")
        return

    admin_url = f"{url}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(admin_url, headers=headers)
            if resp.status_code == 200:
                users = resp.json()
                if isinstance(users, list):
                    user = next((u for u in users if u.get("email") == email), None)
                else:
                    # Some versions return { "users": [...] }
                    user_list = users.get("users", [])
                    user = next((u for u in user_list if u.get("email") == email), None)

                if user:
                    print(f"SUPABASE_USER_FOUND: {user.get('email')}")
                    print(f"ID: {user.get('id')}")
                else:
                    print("SUPABASE_USER_NOT_FOUND")
            else:
                print(f"SUPABASE_ERROR: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"FETCH_ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_supabase_auth())
