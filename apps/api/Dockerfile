# ── Perplex Edge API — Railway Dockerfile ──
# Build context: repo root (railway.toml is at root)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (pg driver, ssl, curl for healthcheck)
RUN apt-get update && apt-get install -y \
    gcc libffi-dev libssl-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer cache)
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API application (flattens apps/api/ into /app/)
COPY apps/api/ .

# The FastAPI app lives in src/main.py → "main:app"
ENV PYTHONPATH=/app/src

# Railway injects $PORT automatically
EXPOSE ${PORT:-8000}

# Production: gunicorn + uvicorn workers
CMD ["sh", "-c", "gunicorn -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120 --access-logfile - main:app"]
