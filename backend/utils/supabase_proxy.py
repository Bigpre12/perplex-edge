import os
import uuid

try:
    from supabase import create_client, Client
except ImportError:
    # MOCK FOR LOCAL ENVIRONMENTS WITHOUT SUPABASE BINARIES
    class Client: pass
    
    class MockSupabase:
        def __init__(self):
            self.auth = self
            self.admin = self
            
        def list_users(self):
            class MockUsers:
                def __init__(self): 
                    self.users = []
            return MockUsers()
            
        def get_user_by_id(self, uid):
            class MockUser:
                def __init__(self):
                    self.user = self
                    self.app_metadata = {
                        "referral_code": f"mock_{uid[:6]}", 
                        "tier": "pro",
                        "referral_clicks": 42,
                        "referral_conversions": 7
                    }
            return MockUser()
            
        def update_user_by_id(self, uid, data): 
            return True
            
    def create_client(url, key): 
        return MockSupabase()

def get_supabase_client():
    """
    Initializes a Supabase client using environment variables.
    Provides a fallback mock client if the library is missing or config is incomplete.
    """
    url = os.environ.get("SUPABASE_URL", "https://mock.supabase.co")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "mock_service_key")
    return create_client(url, key)

# Export a singleton instance
supabase: Client = get_supabase_client()
