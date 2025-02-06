#!/bin/sh

echo "Waiting for MySQL..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL started"

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
if [ "$ENVIRONMENT" = "development" ]; then
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
