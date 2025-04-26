FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git git-lfs ffmpeg libsm6 libxext6 cmake rsync libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir streamlit==1.44.1 uvicorn==0.34.2 psutil==7.0.0

# Copy application files
COPY frontend.py api.py app.py setup_spacy.py requirements.txt symptom_matching.py pubmed_fetch.py tabnet_model.py biobert_utils.py data/ /app

# Run setup and start FastAPI and Streamlit
CMD ["bash", "-c", "python app.py && streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0"]