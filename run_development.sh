#!/bin/bash
cp -v .env.dev .env
export $(xargs < .env)
docker-compose -f docker-compose.dev.yml up --build -d api-database
python manage.py runserver