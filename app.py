'''Main application to run FastAPI and Streamlit.'''

import subprocess
import os
import signal
import sys
import logging
import psutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def kill_port(port):
    """Kill processes using the specified port."""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.net_connections():
                    if conn.laddr.port == port:
                        logger.info(f"Terminating process {proc.pid} on port {port}")
                        proc.terminate()
                        proc.wait(timeout=3)
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Error killing port {port}: {e}")

def run_streamlit():
    """Run Streamlit app."""
    logger.info("Starting Streamlit on port 8501")
    subprocess.run(["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"])

def run_fastapi():
    """Run FastAPI backend."""
    logger.info("Starting FastAPI on port 8000")
    subprocess.run(["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"])

def signal_handler(sig, frame):
    """Handle termination signals."""
    logger.info("Terminating Streamlit and FastAPI...")
    os._exit(0)

if __name__ == "__main__":
    # Kill any existing processes on ports 8501 and 8000
    kill_port(8501)
    kill_port(8000)

    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start Streamlit and FastAPI in separate processes
    from multiprocessing import Process
    streamlit_process = Process(target=run_streamlit)
    fastapi_process = Process(target=run_fastapi)

    try:
        streamlit_process.start()
        fastapi_process.start()
        streamlit_process.join()
        fastapi_process.join()
    except Exception as e:
        logger.error(f"Error running processes: {e}")
        os._exit(1)