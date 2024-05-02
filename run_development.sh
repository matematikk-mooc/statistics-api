#!/bin/bash

# Install python3 if not installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed. Attempting to install..."

    # Check if the system uses apt package manager
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3
    else
        echo "Unsupported package manager. Please install Python 3 manually."
        exit 1
    fi

    # Check if installation was successful
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Failed to install Python 3. Please install it manually."
        exit 1
    else
        echo "Python 3 has been installed successfully."
    fi
else
    echo "Python 3 is already installed."
fi

# Install python3-venv if not installed
if ! command -v python3 -m venv >/dev/null 2>&1; then
    echo "Python 3 venv module is not installed. Attempting to install..."

    # Check if the system uses apt package manager
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-venv
    else
        echo "Unsupported package manager. Please install python3-venv manually."
        exit 1
    fi

    # Check if installation was successful
    if ! command -v python3 -m venv >/dev/null 2>&1; then
        echo "Failed to install python3-venv. Please install it manually."
        exit 1
    else
        echo "python3-venv has been installed successfully."
    fi
else
    echo "Python 3 venv module is already installed."
fi

# Check if pip is available
if ! command -v pip >/dev/null 2>&1; then
    echo "pip is not installed. Attempting to install..."

    # Install pip 
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-pip
    else
        echo "Unsupported package manager. Please install pip manually."
        exit 1
    fi

    # Check if installation was successful
    if ! command -v pip >/dev/null 2>&1; then
        echo "Failed to install pip. Please install it manually."
        exit 1
    else
        echo "pip has been installed successfully."
    fi
fi

# Create and activate the virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Check if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "Checking if dependencies listed in requirements.txt are installed..."

    # Install dependencies using pip if not installed
    if ! pip install -r requirements.txt >/dev/null 2>&1; then
        echo "Installing missing dependencies..."
        pip install -r requirements.txt
        echo "Dependencies installed successfully."
    else
        echo "requirements.txt not found. Skipping dependency installation."
    fi
fi

cp -v .env.dev .env
export $(xargs < .env)
docker-compose -f docker-compose.dev.yml up --build -d api-database
python3 manage.py runserver