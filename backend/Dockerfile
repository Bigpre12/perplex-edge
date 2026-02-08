FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Run migrations and then start the application
# First stamp the database to the latest migration (fixes missing revision issues)
# Then run upgrade to ensure we're at heads
CMD ["sh", "-c", "alembic stamp 20260207_010000 2>/dev/null || true && alembic upgrade heads && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
