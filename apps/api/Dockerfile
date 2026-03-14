# Use the official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependency list
COPY requirements.txt .

# Install Python dependencies
# Also forcefully ensure pywebpush is installed (for web push notifications)
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pywebpush cryptography gunicorn uvicorn

# Copy the entire backend application into the container
COPY . .

# Set the Python path to include the src directory
ENV PYTHONPATH=/app/src

# Expose port 8080 logic (Google Cloud Run default port)
EXPOSE 8080

# Ensure startup script is executable
RUN chmod +x start-api.sh

# Command to run the application using the startup script (Gunicorn + Uvicorn)
CMD ["./start-api.sh"]
