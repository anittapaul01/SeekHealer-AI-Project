#!/bin/bash

# Ensure single instance
LOCK_FILE=/tmp/seekhealer.lock
if [ -e "$LOCK_FILE" ]; then
    echo "Another instance is running. Exiting."
    exit 1
fi
touch "$LOCK_FILE"

# Clean up lock file on exit
trap 'rm -f "$LOCK_FILE"; exit' SIGINT SIGTERM EXIT

# Log function
log() {
    echo "[INFO] $1"
}

# Check and free port
free_port() {
    PORT=$1
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        log "Killing process $PID on port $PORT"
        kill -9 $PID
        sleep 1
    fi
}

# Free ports 7860 and 8000
log "Checking ports 7860 and 8000"
free_port 7860
free_port 8000

# Run SpaCy setup
log "Running SpaCy setup"
python setup_spacy.py
if [ $? -ne 0 ]; then
    log "SpaCy setup failed"
    exit 1
fi

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