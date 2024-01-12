#!/bin/sh

# Wait for any other initialization steps
sleep 10

# Apply migrations
python manage.py migrate

# Start the Django application
exec "$@"