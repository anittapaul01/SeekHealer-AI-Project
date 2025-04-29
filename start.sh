#!/bin/bash

# Check if bash is available
if ! command -v bash >/dev/null 2>&1; then
    echo "[ERROR] Bash not found. Exiting." >&2
    exit 1
fi

# Ensure single instance
LOCK_FILE=/tmp/seekhealer.lock
if [ -e "$LOCK_FILE" ]; then
    echo "[ERROR] Another instance is running. Exiting." >&2
    exit 1
fi
touch "$LOCK_FILE"

# Clean up lock file on exit
trap 'rm -f "$LOCK_FILE"; exit' SIGINT SIGTERM EXIT

# Log function
log() {
    echo "[INFO] $1"
}

# Error log function
error() {
    echo "[ERROR] $1" >&2
}

# Check and free port
free_port() {
    PORT=$1
    if ! command -v lsof >/dev/null 2>&1; then
        error "lsof not found. Cannot check port $PORT."
        exit 1
    fi
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        log "Killing process $PID on port $PORT"
        kill -9 $PID
        sleep 1
    fi
}

# Check for python and uvicorn
if ! command -v python >/dev/null 2>&1; then
    error "Python not found. Exiting."
    exit 1
fi
if ! command -v uvicorn >/dev/null 2>&1; then
    error "Uvicorn not found. Exiting."
    exit 1
fi
if ! command -v streamlit >/dev/null 2>&1; then
    error "Streamlit not found. Exiting."
    exit 1
fi

# Free ports 7860 and 8000
log "Checking ports 7860 and 8000"
free_port 7860
free_port 8000

# Start FastAPI
log "Starting FastAPI"
uvicorn api:app --host 0.0.0.0 --port 8000 --log-level warning &

# Wait to ensure FastAPI starts
sleep 5

# Start Streamlit
log "Starting Streamlit"
streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0 --server.headless true --logger.level info &

# Keep container running
wait