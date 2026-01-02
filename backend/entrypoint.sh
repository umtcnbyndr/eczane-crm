#!/bin/bash
set -e

echo "Running database migrations..."

# First try to fake-initial if tables exist
python manage.py migrate --fake-initial --noinput 2>/dev/null || true

# Then run normal migrate to apply any pending
python manage.py migrate --noinput

echo "Migrations completed successfully"

# Start gunicorn
exec gunicorn --bind 0.0.0.0:8000 --workers 2 smartpharmacy.wsgi:application
