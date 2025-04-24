'''Main application to run FastAPI and Streamlit.'''

import streamlit as st
import os
import subprocess
import sys
import spacy
import time

# Install en_core_web_sm if not present
try:
    spacy.load("en_core_web_sm")
    print("en_core_web_sm is already installed.")
except OSError:
    print("Installing en_core_web_sm...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    print("en_core_web_sm installed successfully.")

# Start FastAPI backend
fastapi_process = subprocess.Popen(
    ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait briefly to check if FastAPI starts successfully
time.sleep(5)
if fastapi_process.poll() is not None:
    stdout, stderr = fastapi_process.communicate()
    print(f"FastAPI failed to start. Error: {stderr}")
    sys.exit(1)
else:
    print("FastAPI backend started successfully.")

# Run Streamlit frontend
os.system("streamlit run frontend.py --server.port 8501")