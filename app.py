'''Main application to run FastAPI and Streamlit.'''

import subprocess
import logging
import os
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
    """Run Streamlit server if not already running."""
    port = 8501
    logger.info(f"Checking Streamlit on port {port}")
    pid = check_port(port)
    
    if pid:
        logger.warning(f"Port {port} is in use by PID {pid}, assuming container's Streamlit instance")
        return
    
    logger.info(f"Starting Streamlit on port {port}")
    try:
        subprocess.run(
            ["streamlit", "run", "frontend.py", "--server.port", str(port), "--server.address", "0.0.0.0"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Streamlit failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error running Streamlit: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Running SpaCy setup")
        subprocess.run(["python", "setup_spacy.py"], check=True)
        
        logger.info("Starting application")
        # Check FastAPI port
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
        
        # Run Streamlit
        run_streamlit()
        
        # Clean up FastAPI process on exit
        fastapi_proc.terminate()
        fastapi_proc.wait()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        if 'fastapi_proc' in locals():
            fastapi_proc.terminate()
            fastapi_proc.wait()
        raise