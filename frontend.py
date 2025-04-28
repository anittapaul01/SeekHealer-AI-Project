"""Frontend Using Streamlit."""

import streamlit as st
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info('Starting Streamlit app')

    st.set_page_config(page_title="Seek Healer", page_icon="🩺", layout="wide")
    logger.info('Streamlit page config set')

    st.markdown("""
        <style>
        /* General layout */
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f7fa;
        }

        /* Title */
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }

        /* Description */
        .description {
            color: GreenYellow;
            font-size: 18px;
            text-align: center;
            max-width: 600px;
            margin: 0 auto 30px;
        }

        /* Input box */
        .stTextInput input {
            border: 2px solid #3498db;
            border-radius: 5px;
            padding: 8px;
            font-size: 14px;
            font-family: cursive, 'Arial', sans-serif;
            width: 100%;
        }

        /* Button */
        .stButton button {
            background-color: #3498db;
            color: white;
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 14px;
            border: none;
            display: block;
            margin: 10px auto;
        }
        .stButton button:hover {
            background-color: #2980b9;
        }

        /* Results header */
        .results-header {
            color: YellowGreen;
            font-size: 20px;
            font-weight: bold;
            font-family: cursive, 'Arial', sans-serif;
            margin: 20px 0;
            text-align: center;
        }

        /* Result card */
        .result-card {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Disease name */
        .disease-name {
            color: #e74c3c;
            font-size: 18px;
            font-weight: bold;
            font-family: cursive, 'Arial', sans-serif;
            margin-bottom: 5px;
        }

        /* Disease description */
        .disease-desc {
            color: #34495e;
            font-size: 14px;
        }

        /* Results footer */
        .results-footer {
            color: Red;
            font-size: 14px;
            text-align: center;
            margin-top: 20px;
        }

        /* Error and warning */
        .stAlert {
            border-radius: 5px;
            padding: 10px;
        }

        /* Footer */
        .footer {
            color: #7f8c8d;
            font-size: 12px;
            text-align: center;
            margin-top: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    logger.info('Styles rendered')

    # Main app container
    st.title("Seek Healer")

    logger.info('Title rendered')

    # App description
    st.markdown("""
        <div class='description'>
        Discover the power of AI with our Disease Predicting App— Seek Healer! Share your symptoms with ease, and our advanced AI tool will analyze them to predict the top 3 potential conditions you may have. Every prediction comes with a short, concise, clear and reliable description drawn from PubMed, a trusted database of over 36 million biomedical and life sciences articles, managed by the National Library of Medicine at the NIH. The NIH, a leading federal agency in the U.S., drives medical research and innovation to improve public health, making it a cornerstone of reliable health knowledge. Take the first step toward understanding your health, type your symptoms and explore the possibilities with confidence! Gain clarity about your health in seconds— start by entering your symptoms below!
        </div>
    """, unsafe_allow_html=True)

    logger.info('Description rendered')

    # Input form
    symptoms = st.text_input("Symptoms (comma-seperated, e.g., fever, cough, fatigue):", placeholder="Type your symptoms here...", key="symptoms_input")

    logger.info('Input form rendered')

    if st.button("Predict"):
        logger.info('Predict button clicked')
        if symptoms:
            try:
                BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
                logger.info(f"Sending request to FastAPI: {symptoms}")
                response = requests.post(f"{BACKEND_URL}/predict", json={'symptoms': symptoms}, timeout=10)
                response.raise_for_status()
                logger.info(f"FastAPI response: {response.json()}")
                results = response.json()['response']
            
                st.markdown('<div class="results-header">Top Predicted Conditions</div>', unsafe_allow_html=True)
                st.markdown(results, unsafe_allow_html=True)
        
            except requests.exceptions.RequestException as e:
                logger.error(f"Error in prediction: {e}")
                st.error(f"Error connecting to the server: {str(e)}")
        else:
            st.warning("Please enter symptoms.")

    logger.info('Button logic completed')

    # Footer
    st.markdown("""
        <div class='footer'>
            Powered by AI | © 2025 Seek Healer
        </div>
    """, unsafe_allow_html=True)

    logger.info('Footer rendered')

except Exception as e:
    logger.error(f'Streamlit app failed: {e}')
    raise