# Multi-stage build for minimal image size
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Render sets PORT dynamically via env var
ENV PORT=8000

EXPOSE ${PORT}

# Health check for Render / UptimeRobot keep-alive
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.getenv(\"PORT\",8000)}/immediate/status')" || exit 1

# Start with 2 workers for free tier (512MB RAM)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2 --timeout-keep-alive 30"]
