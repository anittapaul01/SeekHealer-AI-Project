# Seek Healer

Seek Healer is an AI-powered disease prediction app that analyzes user-input symptoms to predict the top 3 potential medical conditions, with descriptions sourced from PubMed. Built with Streamlit (frontend), FastAPI (backend), and a TabNet model with BioBERT embeddings.

## Features
- Input symptoms via a user-friendly Streamlit interface.
- Predicts top 3 diseases with probabilities using a TabNet model.
- Fetches reliable medical descriptions from PubMed Using RAG Technique.
- Uses BioBERT and SpaCy for symptom matching.

## Project Structure
- `frontend.py`: Streamlit frontend for user interaction.
- `api.py`: FastAPI backend for prediction API.
- `biobert_utils.py`: BioBERT embeddings for symptom matching.
- `symptom_matching.py`: Symptom processing and matching.
- `tabnet_model.py`: TabNet model for disease prediction.
- `pubmed_fetch.py`: Fetch PubMed medical information.
- `preprocess.py`: Dataset preprocessing (reference only).
- `data/`: Contains datasets (`training.csv`, `testing.csv`, etc.).

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/anittapaul01/SeekHealer-AI-Project.git
   cd SeekHealer-AI-Project