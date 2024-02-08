#!/usr/bin/env bash

python manage.py migrate

python manage.py collectstatic --noinput

uvicorn app.asgi:application --host 0.0.0.0 --port 8000 --reload --reload-dir /app
