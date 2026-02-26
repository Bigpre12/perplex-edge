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
 && pip install --no-cache-dir pywebpush cryptography

# Copy the entire backend application into the container
COPY . .

# Expose port 8080 logic (Google Cloud Run default port)
EXPOSE 8080

# Command to run the application using Hypercorn/Uvicorn
# Binding to 0.0.0.0 and port 8080 to satisfy Cloud Run listener constraints
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
