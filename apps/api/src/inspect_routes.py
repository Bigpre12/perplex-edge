import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from main import app
from fastapi.routing import APIRoute

print("--- LISTING ALL REGISTERED API ROUTES ---")
for route in app.routes:
    if isinstance(route, APIRoute):
        methods = ",".join(route.methods)
        print(f"[{methods}] {route.path} -> {route.name}")
print("--- END OF LIST ---")
