#!/bin/bash

# Exit on any error
set -e

# Wait for database to be ready
echo "Waiting for database..."
max_retries=30
counter=0
until PGPASSWORD=postgres psql -h db -U postgres -d app_db -c '\q' 2>/dev/null; do
    counter=$((counter + 1))
    if [ $counter -eq $max_retries ]; then
        echo "Failed to connect to database after $max_retries attempts."
        exit 1
    fi
    echo "Postgres is unavailable - sleeping 1s ($counter/$max_retries)"
    sleep 1
done
echo "Database is ready!"

# Show current migration state
echo "Current migration state:"
poetry run alembic current

# Run migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Show migration state after upgrade
echo "Migration state after upgrade:"
poetry run alembic current

# Verify migrations
echo "Verifying database schema..."
PGPASSWORD=postgres psql -h db -U postgres -d app_db -c '\dt documents'
if [ $? -ne 0 ]; then
    echo "ERROR: Documents table was not created!"
    echo "Database tables:"
    PGPASSWORD=postgres psql -h db -U postgres -d app_db -c '\dt'
    echo "Checking alembic history:"
    poetry run alembic history
    exit 1
fi

echo "Database schema is ready!"

# Start the API
echo "Starting API server..."
poetry run uvicorn src.app.main:app --host 0.0.0.0 --port 8000 