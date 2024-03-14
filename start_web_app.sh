#!/usr/bin/env bash
# These commands are run as appuser
set -e
source venv/bin/activate
python manage.py migrate
python manage.py import_school_teacher_counts_from_csv
python manage.py import_county_teacher_counts_from_csv

gunicorn --bind 0.0.0.0:"${WEBSITES_PORT}" --timeout "${GUNICORN_TIMEOUT}" statistics_api.wsgi:application --log-level "${GUNICORN_LOG_LEVEL}" --access-logfile - --error-logfile -
