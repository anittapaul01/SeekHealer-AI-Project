#!/bin/bash

# Set PATH to include user-specific bin directory
export PATH="/home/appuser/.local/bin:$PATH"

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

# Check for python, uvicorn and streamlit
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
uvicorn api:app --host 0.0.0.0 --port 8000 --log-level debug > /app/fastapi.log 2>&1 &
FASTAPI_PID=$!
sleep 15
if ! ps -p $FASTAPI_PID > /dev/null; then
    error "FastAPI failed to start. Check /app/fastapi.log for details."
    cat /app/fastapi.log
    exit 1
fi
# Verify port 8000 is listening
if ! lsof -i:8000 > /dev/null; then
    error "Port 8000 not in use. FastAPI may have failed. Check /app/fastapi.log."
    cat /app/fastapi.log
    exit 1
fi

# Start Streamlit
log "Starting Streamlit"
streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0 --server.headless true --logger.level info > /app/streamlit.log 2>&1 &
STREAMLIT_PID=$!
sleep 10
if ! ps -p $STREAMLIT_PID > /dev/null; then
    error "Streamlit failed to start. Check /app/streamlit.log for details."
    cat /app/streamlit.log
    exit 1
fi

# Keep container running
wait