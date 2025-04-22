import streamlit as st
import os
import subprocess

# Run FastAPI backend in the background
subprocess.Popen(["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"])

# Run Streamlit frontend
os.system("streamlit run frontend.py")