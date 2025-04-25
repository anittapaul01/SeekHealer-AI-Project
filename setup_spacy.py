'''Setting up SpaCy- en_core_web_sm for smooth workflow.'''

import spacy
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Installing en_core_web_sm")
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    spacy.load('en_core_web_sm')
    logger.info("en_core_web_sm installed and loaded")
except Exception as e:
    logger.error(f"Error installing en_core_web_sm: {e}")