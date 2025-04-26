'''Setup script for SpaCy and FastAPI.'''

import subprocess
import logging
import time
import psutil

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

if __name__ == "__main__":
    try:
        # Run SpaCy setup
        logger.info("Running SpaCy setup")
        subprocess.run(["python", "setup_spacy.py"], check=True)
        
        # Check FastAPI port
        logger.info("Starting application")
        if check_port(8000):
            logger.warning("Port 8000 in use, may cause FastAPI conflicts")
        
        # Run FastAPI in a subprocess
        fastapi_proc = subprocess.Popen(
            ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"FastAPI started with PID {fastapi_proc.pid}")
        
        # Wait briefly to ensure FastAPI starts
        time.sleep(5)

        # Allow CMD to proceed to Streamlit
        logger.info("Proceeding to Streamlit")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        if 'fastapi_proc' in locals():
            fastapi_proc.terminate()
            fastapi_proc.wait()
        raise