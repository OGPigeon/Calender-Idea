#!/bin/bash
# Start both the Flask API and the React dev server

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting Flask API on http://localhost:5001 ..."
source "$ROOT/venv/bin/activate"
python "$ROOT/Src/api.py" &
FLASK_PID=$!

echo "Starting React frontend on http://localhost:5173 ..."
export PATH="/opt/homebrew/bin:$PATH"
cd "$ROOT/frontend" && npm run dev &
REACT_PID=$!

trap "kill $FLASK_PID $REACT_PID 2>/dev/null" EXIT INT TERM
wait
