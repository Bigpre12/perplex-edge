#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting Lucrix backend..."
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
