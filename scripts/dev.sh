#!/usr/bin/env bash
# Dev script to run FastAPI + Vite concurrently with frozen demo DB

set -e

# Kill all background jobs on exit
trap 'kill 0' EXIT

# Get absolute path to project root (handle being called from any directory)
# Use BASH_SOURCE[0] instead of $0 for reliability when script is sourced or called with bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Demo DB path (absolute)
DEMO_DB="$PROJECT_ROOT/data/demo.sqlite3"

# Create demo DB if it doesn't exist
if [ ! -f "$DEMO_DB" ]; then
    echo "Demo database not found. Building frozen demo DB..."
    python "$PROJECT_ROOT/scripts/build_demo_db.py"
    echo "✓ Demo database created"
fi

# Export DB path for demo mode (absolute path)
export DEAL_HAWK_DB_PATH="$DEMO_DB"
echo "Using demo database: $DEMO_DB"

echo "Starting FastAPI on port 8000 (using demo DB: $DEMO_DB)..."
uvicorn backend.api.main:app --reload --port 8000 &

echo "Starting Vite dev server on port 5173..."
cd frontend
npm run dev &

# Wait for all background processes
wait

