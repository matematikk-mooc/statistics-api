#!/bin/bash

echo -e "\n\n\n[1/4] Copy and import .env variables to the current shell"
echo -e "##############################################################\n"
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .docker/.env.template .env
fi

set -o allexport
while IFS='=' read -r key value; do
  if [[ ! "$key" =~ ^# ]] && [[ -n "$key" ]]; then
    value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//')
    value=$(echo "$value" | sed -e "s/^'//" -e "s/'$//")

    if [[ -z "${!key}" ]]; then
      export "$key=$value"
      echo "- IMPORTED: $key"
    else
      echo "- ERROR: $key"
    fi
  fi
done < "$ENV_FILE"
set +o allexport

echo -e "\n\n\n[2/4] Install PIP packages"
echo -e "##############################################################\n"
pip3 --cache-dir=/app/.cache install -r requirements.txt

echo -e "\n\n\n[3/4] Apply Django migrations"
echo -e "##############################################################\n"
python manage.py migrate

echo -e "\n\n\n[4/4] Start Django server"
echo -e "##############################################################\n"
python manage.py runserver 0.0.0.0:8000
