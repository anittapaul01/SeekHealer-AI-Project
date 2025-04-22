# Seek Healer

Seek Healer is an AI-powered disease prediction app that analyzes user-input symptoms to predict the top 3 potential medical conditions, with descriptions sourced from PubMed. Built with Streamlit (frontend), FastAPI (backend), and a TabNet model with BioBERT embeddings.

## Features
- Input symptoms via a user-friendly Streamlit interface.
- Predicts top 3 diseases with probabilities using a TabNet model.
- Fetches reliable medical descriptions from PubMed Using RAG Technique.
- Uses BioBERT and SpaCy for symptom matching.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/seek-healer.git
   cd seek-healer