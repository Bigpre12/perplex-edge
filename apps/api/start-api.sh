#!/bin/bash
# apps/api/start-api.sh
# Production start script with Gunicorn and Uvicorn workers

echo "🚀 Starting Lucrix API with Gunicorn..."

# Run migrations if needed (optional but recommended)
python src/tmp_migration.py || echo "⚠️ Migration script failed or not found, skipping..."

# Start Gunicorn
# -w 4: 4 worker processes
# -k uvicorn.workers.UvicornWorker: Use Uvicorn workers for ASGI support
# --bind 0.0.0.0:$PORT: Bind to all interfaces on the specified port
# --timeout 120: Increase timeout for LLM calls
# --access-logfile -: Log to stdout

exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:${PORT:-8080} \
     --timeout 120 \
     --access-logfile - \
     src.main:app
