"""Process user input for symptom matching."""

import pandas as pd
import numpy as np
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from biobert_utils import get_embedding, symptom_embeddings
import os


# Normalize input using spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError as e:
    raise OSError(f"Ensure en_core_web_sm is installed via setup_spacy.py: {e}")

try:
    aug_df = pd.read_csv(os.path.join('data', 'aug_df.csv'))
    symptoms_col = aug_df.columns[1:]
except FileNotFoundError as e:
    raise FileNotFoundError(f"Ensure aug_df.csv exists in data/: {e}")


def normalize_user_input(user_input):
    """Normalizes user symptom inputs.

    Args:
        user_input (str): Raw user symptom string.

    Returns:
        list: Normalized symptom terms.
    
    Raises:
        ValueError: If input is empty or invalid.
    """
    if not user_input.strip() or not isinstance(user_input, str):
        raise ValueError(f'User input must be a non-empty string.')
    try:
        doc = nlp(user_input)
        terms = [token.text.lower() for token in doc if not token.is_stop and len(token.text) > 2]
        return terms if terms else [user_input.lower().strip()]
    except Exception as e:
        raise RuntimeError(f'Normalization failed: {e}')
    

def match_symptoms(user_ip, top_k=10, threshold=0.7):
    """Match user symptoms to dataset symptoms.

    Args:
        user_ip (str): User symptom input.
        top_k (int): Maximum symptoms to match, Default set to 10.
        threshold (float): Similarity threshold, Defaults to 0.7.

    Returns:
        np.ndarray: Binary symptom vector.

    Raises:
        ValueError: If input is invalid.
    """
    try:
        user_symptoms = normalize_user_input(user_ip)
        matched_symptoms = []
        for symptom in user_symptoms:
            user_emb = get_embedding(symptom).reshape(1, -1)
            similarities = cosine_similarity(user_emb, symptom_embeddings)[0]
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            if best_score >= threshold:
                matched_symptoms.append(symptoms_col[best_idx])

        matched_symptoms = list(dict.fromkeys(matched_symptoms))[:top_k]

        # Create one-hot input vector
        ip_vec = np.zeros(len(symptoms_col))
        for match in matched_symptoms:
            ip_vec[list(symptoms_col).index(match)] = 1

        return ip_vec
    except Exception as e:
        raise RuntimeError(f'Symptom matching failed: {e}')
    