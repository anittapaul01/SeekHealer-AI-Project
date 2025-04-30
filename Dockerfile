FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git-lfs libjpeg-dev zlib1g-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# Create a non-root user and set up permissions
RUN useradd -m appuser && \
    mkdir -p /home/appuser/.cache && \
    chown -R appuser:appuser /home/appuser/.cache

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies as appuser
USER appuser
ENV HOME=/home/appuser
ENV PIP_CACHE_DIR=/home/appuser/.cache/pip
ENV HUGGINGFACE_HUB_CACHE=/home/appuser/.cache/huggingface
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir spacy
RUN python -m spacy download en_core_web_sm

# Switch back to root for file copying and permissions
USER root

# Copy application files
COPY frontend.py api.py requirements.txt symptom_matching.py pubmed_fetch.py tabnet_model.py biobert_utils.py start.sh .gitattributes /app/
COPY data/ /app/data/

# Make start.sh executable and set permissions
RUN chmod +x /app/start.sh && \
    chown -R appuser:appuser /app

# Expose ports
EXPOSE 8000 7860

# Run as appuser
USER appuser

# Run start.sh 
CMD ["/app/start.sh"]