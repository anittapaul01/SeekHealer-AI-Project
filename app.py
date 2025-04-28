'''Setup script for SpaCy and FastAPI.'''

import subprocess
import logging
import fcntl
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def acquire_lock():
    '''Ensure single instance using a lock file.'''
    lock_file = '/tmp/seekhealer.lock'
    try:
        fd = open(lock_file, 'w')
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except IOError:
        logger.error('Another instance is already running. Exiting.')
        sys.exit(1)

def run_spacy_setup():
    '''Run the SpaCy model setup.'''
    logger.info('Running SpaCy setup script')
    try:
        subprocess.run(['python', 'setup_spacy.py'], check=True)
        logger.info('SpaCy setup completed successfully')
    except subprocess.CalledProcessError as e:
        logger.error(f'SpaCy setup failed: {e}')
        raise

if __name__ == '__main__':
    # Acquire lock to prevent multiple instances
    lock_fd = acquire_lock()
    
    try:
        # Run SpaCy setup
        run_spacy_setup()
        
        # Start FastAPI on port 7860
        logger.info('Starting FastAPI')
        subprocess.run([
            'uvicorn', 'api:app',
            '--host', '0.0.0.0',
            '--port', '7860',
            '--log-level', 'warning'
        ])
        
    except Exception as e:
        logger.error(f'Error in main execution: {e}')
        raise
    finally:
        # Release lock
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
        lock_fd.close()