'''Main application to run FastAPI and Streamlit.'''

import streamlit as st
import requests
import subprocess
import logging
import os
import psutil
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_port(port):
    """Check if a port is in use without terminating processes."""
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.pid:
                logger.info(f"Port {port} is in use by PID {conn.pid}")
                return True
        logger.info(f"Port {port} is free")
        return False
    except Exception as e:
        logger.error(f"Error checking port {port}: {e}")
        return False

def run_fastapi():
    """Run FastAPI server."""
    logger.info("Starting FastAPI on port 8000")
    try:
        result = subprocess.run(
            ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
            capture_output=True,
            text=True
        )
        logger.info(f"FastAPI output: {result.stdout}")
        logger.error(f"FastAPI error: {result.stderr}")
    except Exception as e:
        logger.error(f"Error running FastAPI: {e}")

def run_streamlit():
    """Run Streamlit server."""
    logger.info("Starting Streamlit on port 8501")
    try:
        # Check if ports are free
        if check_port(8501):
            logger.warning("Port 8501 in use, may cause conflicts")
        if check_port(8000):
            logger.warning("Port 8000 in use, may cause conflicts")
        
        subprocess.run(
            ["streamlit", "run", "frontend.py", "--server.port", "8501", "--server.address", "0.0.0.0"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Streamlit failed: {e}")
    except Exception as e:
        logger.error(f"Error running Streamlit: {e}")

if __name__ == "__main__":
    try:
        logger.info("Running SpaCy setup")
        subprocess.run(["python", "setup_spacy.py"], check=True)
        logger.info("Starting application")
        
        # Run FastAPI in a subprocess
        fastapi_proc = subprocess.Popen(
            ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"FastAPI started with PID {fastapi_proc.pid}")
        
        # Run Streamlit in the main process
        run_streamlit()
        
        # Clean up FastAPI process on exit
        fastapi_proc.terminate()
        fastapi_proc.wait()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        if 'fastapi_proc' in locals():
            fastapi_proc.terminate()
            fastapi_proc.wait()