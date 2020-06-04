#!/usr/bin/env bash
source venv/bin/activate
python manage.py makemigrations statistics_api
python manage.py migrate
gunicorn --bind 0.0.0.0:"${STATISTICS_API_PORT}" statistics_api.wsgi:application