'''Setup script for SpaCy and FastAPI.'''

import subprocess
import logging
import time
import psutil
import threading
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_port(port):
    """Check if a port is in use and return PID if occupied."""
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.pid:
                logger.info(f"Port {port} is in use by PID {conn.pid}")
                return conn.pid
        logger.info(f"Port {port} is free")
        return None
    except Exception as e:
        logger.error(f"Error checking port {port}: {e}")
        return None

def run_fastapi():
    """Run the FastAPI server."""
    logger.info("Starting FastAPI")
    os.system("uvicorn api:app --host 0.0.0.0 --port 8000 --log-level warning")

def run_streamlit():
    """Run the Streamlit frontend."""
    logger.info("Starting Streamlit frontend")
    os.system("streamlit run frontend.py --server.port 7860 --server.headless true")

def run_spacy_setup():
    """Run the SpaCy model setup."""
    logger.info("Running SpaCy setup script")
    try:
        subprocess.run(["python", "setup_spacy.py"], check=True)
        logger.info("SpaCy setup completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"SpaCy setup failed: {e}")
        raise

if __name__ == "__main__":
    try:
        # Step 1: Setup SpaCy
        run_spacy_setup()

        # Step 2: Check if FastAPI port is already occupied
        if check_port(8000):
            logger.warning("Port 8000 already in use, may cause FastAPI conflicts")

        # Step 3: Start FastAPI backend in a separate thread
        threading.Thread(target=run_fastapi).start()

        # Step 4: Wait a little to ensure FastAPI is ready
        time.sleep(5)

        # Step 5: Start Streamlit frontend
        run_streamlit()

    except Exception as e:
        logger.error(f"Error in main execution: {e}")