#!/usr/bin/env bash

python manage.py migrate

python manage.py collectstatic --noinput

uvicorn app.asgi:application --host 0.0.0.0 --port 8000 --reload --reload-dir /app &
# uvicorn app.asgi:application --host 0.0.0.0 --port 8000 --reload --reload-dir /app &
# /wait-for-it.sh -t 60 localhost:8000 -- echo "Django server is ready"
# # Run your custom command
# python manage.py sync-bot
# # Keep the script running to keep the container alive
# tail -f /dev/null