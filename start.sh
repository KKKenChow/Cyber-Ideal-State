#!/bin/bash
# Cyber-Ideal-State Start Script

set -e

echo "🏛️ Starting Cyber-Ideal-State..."
echo "================================="

# Kill any existing processes
pkill -f "server.py" || true

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start backend server
echo "🚀 Starting backend server..."
cd ui/backend
python3 server.py &
BACKEND_PID=$!

echo ""
echo "✅ Cyber-Ideal-State is running!"
echo ""
echo "Services:"
echo "  - Backend API: http://localhost:8080"
echo "  - Frontend UI: http://localhost:8080/ui"
echo ""
echo "Process ID:"
echo "  - Backend: $BACKEND_PID"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Wait for processes
wait $BACKEND_PID
