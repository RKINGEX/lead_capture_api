#!/bin/sh

set -e

echo "Running database migrations..."

alembic -c /app/alembic.ini upgrade head

echo "Starting API"

exec uvicorn codigo_fuente.main:app --host 0.0.0.0 --port 8000 