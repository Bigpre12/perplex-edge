"""
Emergency CORS Fix - Immediate resolution for CORS issues.

This module provides immediate CORS fixes when the brain hasn't detected
the issue yet or when manual intervention is needed.
"""

import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def apply_emergency_cors_fix():
    """Apply emergency CORS fix immediately."""
    try:
        fixes_applied = []
        
        # Fix 1: Force environment variables
        os.environ["CORS_ORIGINS"] = "*"
        os.environ["ALLOW_ALL_ORIGINS"] = "true"
        os.environ["ENABLE_WILDCARD_CORS"] = "true"
        
        fixes_applied.append("Forced wildcard CORS environment variables")
        
        # Fix 2: Update main.py with aggressive CORS
        main_py_path = Path(__file__).parent.parent / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r') as f:
                content = f.read()
            
            # Add emergency CORS middleware at the top
            emergency_cors_code = '''
# =============================================================================
# EMERGENCY CORS FIX - Applied immediately
# =============================================================================

class EmergencyCORSMiddleware:
    """Emergency CORS middleware that always allows all origins."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Handle CORS preflight requests
            if scope["method"] == "OPTIONS":
                await send({
                    'type': 'http.response.start',
                    'status': 200,
                    'headers': [
                        (b'access-control-allow-origin', b'*'),
                        (b'access-control-allow-methods', b'GET, POST, PUT, DELETE, OPTIONS, PATCH'),
                        (b'access-control-allow-headers', b'*'),
                        (b'access-control-allow-credentials', b'true'),
                        (b'access-control-max-age', b'600'),
                    ]
                })
                await send({'type': 'http.response.body', 'body': b''})
                return
        
        # Pass through to next middleware
        await self.app(scope, receive, send)

# Apply emergency CORS middleware immediately
app.add_middleware(EmergencyCORSMiddleware)

'''
            
            if "EMERGENCY CORS FIX" not in content:
                # Insert after FastAPI app creation
                app_creation_pos = content.find("app = FastAPI(")
                if app_creation_pos != -1:
                    # Find the end of the FastAPI constructor
                    end_pos = content.find(")", app_creation_pos)
                    if end_pos != -1:
                        content = content[:end_pos+1] + emergency_cors_code + content[end_pos+1:]
                        
                        with open(main_py_path, 'w') as f:
                            f.write(content)
                        
                        fixes_applied.append("Added emergency CORS middleware to main.py")
        
        # Fix 3: Create .env file with CORS settings
        env_path = Path(__file__).parent.parent / ".env"
        env_content = """
# Emergency CORS Fix
CORS_ORIGINS=*
ALLOW_ALL_ORIGINS=true
ENABLE_WILDCARD_CORS=true
FRONTEND_URL=https://perplex-edge-production.up.railway.app
BACKEND_URL=https://railway-engine-production.up.railway.app
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content.strip())
        
        fixes_applied.append("Created .env with emergency CORS settings")
        
        # Fix 4: Update production.py to force wildcard
        production_py_path = Path(__file__).parent.parent / "core" / "production.py"
        if production_py_path.exists():
            with open(production_py_path, 'r') as f:
                content = f.read()
            
            # Force wildcard CORS in production
            if "def get_cors_origins()" in content:
                # Replace the function to always return wildcard
                new_function = '''def get_cors_origins() -> List[str]:
    """Emergency CORS fix - always allow all origins."""
    logger.warning("EMERGENCY CORS: Forcing wildcard CORS for all requests")
    return ["*"]'''
                
                # Find and replace the function
                import re
                pattern = r'def get_cors_origins\(\) -> List\[str\]:.*?(?=\n\ndef|\nclass|\Z)'
                content = re.sub(pattern, new_function, content, flags=re.DOTALL)
                
                with open(production_py_path, 'w') as f:
                    f.write(content)
                
                fixes_applied.append("Forced wildcard CORS in production.py")
        
        logger.warning(f"[EMERGENCY CORS] Applied {len(fixes_applied)} emergency fixes: {', '.join(fixes_applied)}")
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "message": f"Emergency CORS fix applied: {len(fixes_applied)} fixes"
        }
        
    except Exception as e:
        logger.error(f"[EMERGENCY CORS] Failed to apply emergency fix: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Emergency CORS fix failed"
        }

def restart_backend_service():
    """Trigger backend service restart."""
    try:
        # In Railway, we can't directly restart, but we can trigger a redeploy
        # by touching a file that the build process depends on
        
        # Touch requirements.txt to trigger rebuild
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        if requirements_path.exists():
            import time
            current_time = time.time()
            os.utime(requirements_path, (current_time, current_time))
            
            logger.warning("[EMERGENCY CORS] Touched requirements.txt to trigger redeploy")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"[EMERGENCY CORS] Failed to trigger restart: {e}")
        return False

if __name__ == "__main__":
    """Apply emergency CORS fix immediately."""
    logging.basicConfig(level=logging.WARNING)
    
    result = apply_emergency_cors_fix()
    
    if result["success"]:
        print(f"✅ {result['message']}")
        print("🔄 Please redeploy the backend service now")
        
        # Try to trigger restart
        if restart_backend_service():
            print("🚀 Backend restart triggered")
        else:
            print("⚠️  Please manually redeploy the backend service")
    else:
        print(f"❌ Emergency CORS fix failed: {result.get('error', 'Unknown error')}")
