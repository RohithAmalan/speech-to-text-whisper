#!/bin/bash
echo "🚀 Starting Voice Assistant..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to the project root (where run.sh is)
cd "$SCRIPT_DIR"

# Start the server
echo "Running on http://127.0.0.1:8000"
uvicorn assistant.api:app --reload
