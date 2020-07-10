#!/usr/bin/env bash
# These commands are run as appuser
set -e
source venv/bin/activate
python manage.py migrate
python manage.py migrate enrollment_activity
python manage.py import_school_teacher_counts_from_csv data/primary_schools_data.csv
python manage.py import_county_teacher_counts_from_csv data/county_data.csv
if [ "$PULL_MEMBER_COUNTS_FROM_CANVAS_ON_STARTUP" = "True" ]
then
  python manage.py pull_course_member_counts_from_canvas
fi
gunicorn --bind 0.0.0.0:"${WEBSITES_PORT}" --timeout "${GUNICORN_TIMEOUT}" statistics_api.wsgi:application --log-level debug --access-logfile - --error-logfile -
