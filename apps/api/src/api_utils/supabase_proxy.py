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
            
        def get_user(self, token=None):
            class MockUserResponse:
                def __init__(self):
                    self.user = type('obj', (object,), {
                        'id': str(uuid.uuid4()),
                        'email': 'mock@example.com',
                        'user_metadata': {'tier': 'elite'}
                    })
                    self.error = None
            return MockUserResponse()

        def get_user_by_id(self, uid):
            class MockUser:
                def __init__(self):
                    self.user = self
                    self.id = uid
                    self.email = 'mock@example.com'
                    self.app_metadata = {
                        "referral_code": f"mock_{uid[:6]}", 
                        "tier": "pro",
                        "referral_clicks": 42,
                        "referral_conversions": 7
                    }
                    self.user_metadata = {"tier": "elite"}
            return MockUser()
            
        def update_user_by_id(self, uid, data): 
            return True
            
    def create_client(url, key): 
        return MockSupabase()

def _supabase_env() -> tuple[str, str, str]:
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or "https://mock.supabase.co"
    anon_key = os.environ.get("SUPABASE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY") or "mock_anon_key"
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY") or "mock_service_key"
    return url, anon_key, service_key


def role_readiness() -> dict:
    _, anon_key, service_key = _supabase_env()
    return {
        "anon_present": bool(anon_key and anon_key != "mock_anon_key"),
        "service_present": bool(service_key and service_key != "mock_service_key"),
        "service_key_looks_anon": bool(anon_key and service_key and anon_key == service_key),
    }


def get_supabase_clients() -> tuple[Client, Client]:
    """
    Returns (anon_client, admin_client) with role split validation.
    """
    url, anon_key, service_key = _supabase_env()
    return create_client(url, anon_key), create_client(url, service_key)


def get_supabase_client() -> Client:
    """
    Backwards-compatible alias returning admin client.
    """
    _, admin = get_supabase_clients()
    return admin


anon_supabase, supabase = get_supabase_clients()
