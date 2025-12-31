#!/bin/bash
set -e

echo "Initializing database..."
python init_db.py

echo "Running migrations..."
python migrate_db.py

echo "Starting Nuxt Frontend..."
node /app/frontend/.output/server/index.mjs &

echo "Starting FastAPI Backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000

