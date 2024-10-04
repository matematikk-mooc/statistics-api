#!/bin/bash

if [ -z "$ENV_FILE_PATH" ]; then
    echo "ERROR: ENV_FILE_PATH is not set. Please define ENV_FILE_PATH before running the script."
    exit 1
fi

if [ ! -f "$ENV_FILE_PATH" ]; then
    echo "WARNING: .env file not found at $ENV_FILE_PATH. Skipping import."
    exit 1
fi

echo -e "INFO: Importing environment variables from $ENV_FILE_PATH\n"
set -o allexport

while IFS='=' read -r key value; do
  if [[ ! "$key" =~ ^# ]] && [[ -n "$key" ]]; then
    value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//')
    value=$(echo "$value" | sed -e "s/^'//" -e "s/'$//")

    if [[ -z "${!key}" ]]; then
      export "$key=$value"
      echo "    - IMPORTED: $key"
    else
      echo "    - ERROR: $key"
    fi
  fi
done < "$ENV_FILE_PATH"

set +o allexport
echo -e "\nINFO: Environment variables import completed."
