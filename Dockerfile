FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git git-lfs ffmpeg libsm6 libxext6 cmake rsync libgl1-mesa-glx libgl1 libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY frontend.py api.py setup_spacy.py requirements.txt symptom_matching.py pubmed_fetch.py tabnet_model.py biobert_utils.py data/ /app/

# Make start.sh executable
RUN chmod +x start.sh

# Expose port 7860
EXPOSE 7860

# Run start.sh
CMD ["./start.sh"]