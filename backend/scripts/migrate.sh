#!/bin/bash
# Database migration helper script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$BACKEND_DIR"

case "$1" in
    up|upgrade)
        echo "Running migrations..."
        alembic upgrade head
        echo "Migrations complete."
        ;;
    down|downgrade)
        echo "Rolling back last migration..."
        alembic downgrade -1
        echo "Rollback complete."
        ;;
    new|create)
        if [ -z "$2" ]; then
            echo "Usage: $0 new 'migration description'"
            exit 1
        fi
        echo "Creating new migration: $2"
        alembic revision -m "$2"
        ;;
    auto|autogenerate)
        if [ -z "$2" ]; then
            echo "Usage: $0 auto 'migration description'"
            exit 1
        fi
        echo "Auto-generating migration: $2"
        alembic revision --autogenerate -m "$2"
        ;;
    history)
        alembic history
        ;;
    current)
        alembic current
        ;;
    *)
        echo "Database Migration Script"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  up, upgrade           Run all pending migrations"
        echo "  down, downgrade       Rollback last migration"
        echo "  new, create 'msg'     Create a new empty migration"
        echo "  auto, autogenerate 'msg'  Auto-generate migration from models"
        echo "  history               Show migration history"
        echo "  current               Show current migration version"
        ;;
esac
