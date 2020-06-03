#!/usr/bin/env bash
venv/bin/./python3 manage.py makemigrations statistics_api
venv/bin/./python3 manage.py migrate
venv/bin/./python3 manage.py runserver 0.0.0.0:"${STATISTICS_API_PORT}"
