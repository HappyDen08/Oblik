#!/bin/bash

# Exit on error
set -e

echo "Starting Project Rita..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/Update dependencies
echo "Checking dependencies..."
pip install -r requirements.txt

# Default to bot if no argument provided
COMMAND=${1:-bot}

echo "Running $COMMAND..."
python3 main.py "$COMMAND"
