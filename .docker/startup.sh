#!/bin/bash

echo -e "\n\n\n[1/4] Copy and import .env variables to the current shell"
echo -e "##############################################################\n"
ENV_FILE_PATH="/app/.env"
ENV_SCRIPT_PATH="/var/www/html/.docker/env.sh"
TEMPLATE_PATH="/app/.docker/.env.template"

if [ ! -f "$ENV_FILE_PATH" ]; then
    cp $TEMPLATE_PATH $ENV_FILE_PATH
fi

echo "export ENV_FILE_PATH=\"$ENV_FILE_PATH\" && source $ENV_SCRIPT_PATH" >> /root/.bashrc
chmod +x /root/.bashrc
source /root/.bashrc

echo -e "\n\n\n[2/4] Install PIP packages"
echo -e "##############################################################\n"
pip3 --cache-dir=/app/.cache install -r requirements.txt

echo -e "\n\n\n[3/4] Apply Django migrations"
echo -e "##############################################################\n"
python manage.py migrate

echo -e "\n\n\n[4/4] Start Django server"
echo -e "##############################################################\n"
python manage.py runserver 0.0.0.0:8000
