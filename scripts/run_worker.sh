#!/bin/bash

# Script to run the worker with virtual display on Ubuntu

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run worker with Xvfb (virtual display for headless browser)
echo "Starting worker with virtual display..."
xvfb-run python3 src/vm/worker.py

echo "Worker finished."
