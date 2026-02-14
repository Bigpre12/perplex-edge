FROM python:3.11-slim

WORKDIR /app

# Install only essential dependencies
RUN pip install fastapi uvicorn

# Copy only what we need
COPY app/ ./app/

# Simplest possible startup
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
