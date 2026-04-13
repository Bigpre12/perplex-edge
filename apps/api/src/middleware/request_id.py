from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import contextvars

request_id_ctx_var = contextvars.ContextVar("request_id", default=None)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        token = request_id_ctx_var.set(request_id)
        
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response
        finally:
            request_id_ctx_var.reset(token)

def get_request_id():
    return request_id_ctx_var.get()
