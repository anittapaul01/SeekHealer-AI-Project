FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git git-lfs cmake rsync libjpeg-dev zlib1g-dev lsof \
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
COPY frontend.py api.py setup_spacy.py requirements.txt symptom_matching.py pubmed_fetch.py tabnet_model.py biobert_utils.py data/ start.sh /app/

# Make start.sh executable
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 7860 8000

# Run start.sh
CMD ["/app/start.sh"]