from typing import Dict, Optional, Any

def build_headers(base: Dict[str, Any]) -> Dict[str, str]:
    """
    Safely build HTTP headers by removing None values and casting to strings.
    Prevents NoneType errors in libraries like httpx and requests.
    """
    return {str(k): str(v) for k, v in base.items() if v is not None}
