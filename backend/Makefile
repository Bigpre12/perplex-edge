.PHONY: help install dev migrate migrate-down migrate-new run test lint clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make migrate      - Run all pending migrations"
	@echo "  make migrate-down - Rollback last migration"
	@echo "  make migrate-new  - Create new migration (usage: make migrate-new MSG='description')"
	@echo "  make migrate-auto - Auto-generate migration from models (usage: make migrate-auto MSG='description')"
	@echo "  make run          - Run production server"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo "  make clean        - Clean cache files"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Database migrations
migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

migrate-new:
	alembic revision -m "$(MSG)"

migrate-auto:
	alembic revision --autogenerate -m "$(MSG)"

migrate-history:
	alembic history

migrate-current:
	alembic current

# Testing
test:
	pytest -v

# Linting
lint:
	ruff check app/

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
