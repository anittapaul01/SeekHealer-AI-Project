'''Main application to run FastAPI and Streamlit.'''

import streamlit as st
import requests
import multiprocessing
import psutil
import subprocess
import logging
import os
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_terminate_port(port):
    logger.info(f"Checking for processes on port {port}")
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port:
            logger.info(f"Terminating process {conn.pid} on port {port}")
            psutil.Process(conn.pid).terminate()

def run_fastapi():
    logger.info("Starting FastAPI on port 8000")
    result = subprocess.run(["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"], capture_output=True, text=True)
    logger.info(f"FastAPI output: {result.stdout}")
    logger.error(f"FastAPI error: {result.stderr}")

def run_streamlit():
    logger.info("Starting Streamlit on port 8501")
    check_and_terminate_port(8501)
    check_and_terminate_port(8000)
    subprocess.run(["streamlit", "run", "frontend.py", "--server.port", "8501", "--server.address", "0.0.0.0"])

if __name__ == "__main__":
    try:
        logger.info("Running SpaCy setup")
        subprocess.run(["python", "setup_spacy.py"])
        logger.info("Starting FastAPI process")
        if threading.current_thread() is threading.main_thread():
            fastapi_process = multiprocessing.Process(target=run_fastapi)
            fastapi_process.start()
        else:
            logger.warning("Not in main thread, skipping FastAPI process")
        logger.info("Starting Streamlit process")
        run_streamlit()
    except Exception as e:
        logger.error(f"Error in main: {e}")