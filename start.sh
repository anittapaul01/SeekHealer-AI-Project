#!/bin/bash

export PATH="/home/appuser/.local/bin:$PATH"

# Set trap for clean exit
trap 'kill $(jobs -p)' EXIT

# Start FastAPI on 8000 in background
echo "[INFO] Starting FastAPI..."
uvicorn api:app --host 127.0.0.1 --port 8000 --log-level warning &
FASTAPI_PID=$!

# Wait for FastAPI to be ready (poll until it responds)
echo "[INFO] Waiting for FastAPI..."
until curl -s http://127.0.0.1:8000/docs > /dev/null; do
  sleep 1
done
echo "[INFO] FastAPI is up."

# Start Streamlit (this will hold the container open)
echo "[INFO] Starting Streamlit..."
streamlit run frontend.py \
  --server.port 7860 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --logger.level info
