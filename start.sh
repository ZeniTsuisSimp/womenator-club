#!/bin/bash
set -e

# Run migrations
python manage.py migrate --run-syncdb

# Create superuser if it doesn't exist
python manage.py createsuperuser --no-input 2>/dev/null || true

# Start gunicorn
exec gunicorn womenator_project.wsgi:application --bind 0.0.0.0:7860 --workers 2 --timeout 120
