import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('Starting test Streamlit app')

try:
    st.set_page_config(page_title='Test App', layout='wide')
    logger.info('Test page config set')
    st.title('Test Streamlit App')
    logger.info('Test title rendered')
    st.write('This is a test app to verify Streamlit.')
    logger.info('Test write completed')
except Exception as e:
    logger.error(f'Test Streamlit app failed: {e}')
    raise