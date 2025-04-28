'''Setup script for SpaCy and FastAPI.'''

import subprocess
import logging
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_spacy_setup():
    """Run the SpaCy model setup."""
    logger.info("Running SpaCy setup script")
    try:
        subprocess.run(["python", "setup_spacy.py"], check=True)
        logger.info("SpaCy setup completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"SpaCy setup failed: {e}")
        raise


def start_services():
    '''Start FastAPI and Streamlit as subprocesses.'''
    fastapi_cmd = ['uvicorn', 'api:app', '--host', '0.0.0.0', '--port', '8000', '--log-level', 'warning']
    streamlit_cmd = ['streamlit', 'run', 'frontend.py', '--server.port', '7860', '--server.address', '0.0.0.0', '--server.headless', 'true', '--logger.level', 'info']
    
    # Start FastAPI
    logger.info('Starting FastAPI')
    fastapi_proc = subprocess.Popen(fastapi_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait to ensure FastAPI starts
    time.sleep(5)
    
    # Start Streamlit
    logger.info('Starting Streamlit frontend')
    streamlit_proc = subprocess.Popen(streamlit_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Monitor processes
    try:
        for proc in [fastapi_proc, streamlit_proc]:
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                logger.error(f'Process failed: {stderr}')
    except KeyboardInterrupt:
        logger.info('Shutting down services')
        for proc in [fastapi_proc, streamlit_proc]:
            proc.terminate()
            proc.wait()

if __name__ == '__main__':
    try:
        # Run SpaCy setup
        run_spacy_setup()
        
        # Start services
        start_services()
        
    except Exception as e:
        logger.error(f'Error in main execution: {e}')
        raise