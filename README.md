---
title: Seek Healer
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Seek Healer

Seek Healer is an AI-powered disease prediction app that analyzes user-input symptoms to predict the top 3 potential medical conditions, with descriptions sourced from PubMed. Built with Streamlit (frontend), FastAPI (backend), and a TabNet model with BioBERT embeddings.

## Hosted on Hugging Face Spaces
[Open in Hugging Face Spaces](https://huggingface.co/spaces/anitta-paul/SeekHealer)

## Features
- Input symptoms via a user-friendly Streamlit interface.
- Predicts top 3 diseases with probabilities using a TabNet model.
- Fetches reliable medical descriptions from PubMed Using RAG Technique.
- Uses BioBERT and SpaCy for symptom matching.

## Project Structure
- `frontend.py`: Streamlit frontend for user interaction.
- `api.py`: FastAPI backend for prediction API.
- `start.sh`: Shell script to manage entry point, FastAPI (port 8000), and Streamlit (port 7860).
- `biobert_utils.py`: BioBERT embeddings for symptom matching.
- `symptom_matching.py`: Symptom processing and matching.
- `tabnet_model.py`: TabNet model for disease prediction.
- `pubmed_fetch.py`: Fetches PubMed medical information.
- `Dockerfile`: Defines the Docker container setup.
- `requirements.txt`: Python dependencies.
- `data/`: Contains datasets (`aug_df.csv`, `pubmed_medical_info.csv`, `tabnet_model.zip`, `symptom_embeddings.npy`).

## Setup
1. Clone the repository:
```bash
git clone https://github.com/anittapaul01/SeekHealer-AI-Project.git
cd SeekHealer-AI-Project
```
2. Build and run the Docker container:
```bash
docker build -t seekhealer .
docker run -p 7860:7860 -p 8000:8000 -e BACKEND_URL=http://localhost:8000 seekhealer
```
3. Access the app at `http://localhost:7860`.

## Deployment on Hugging Face Spaces
- The app is deployed using a `Dockerfile` with `start.sh` to manage services.
- Streamlit runs on port 7860 (exposed), FastAPI on port 8000 (internal).
- Ensure `data/` files are tracked with Git LFS.
