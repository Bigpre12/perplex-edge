FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc libffi-dev libssl-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Use specific COPY to handle both root and sub-dir contexts
# Railway often builds from root but we want our API dependencies
COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API source
# If building from root, we copy apps/api/ into .
# This flattens the structure so apps/api/src becomes /workspace/src
COPY apps/api/ .

# Fallback in case requirements was missed at root
COPY requirements.txt ./root_reqs.txt
RUN pip install --no-cache-dir -r root_reqs.txt || true

WORKDIR /workspace/src
ENV PYTHONPATH=/workspace/src:/workspace

# Production entry point
CMD ["sh", "-c", "gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 main:app"]
