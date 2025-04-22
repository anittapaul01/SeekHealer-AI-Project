"""BioBert embeddings for symptoms matching."""

import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch


try:
    tokenizer = AutoTokenizer.from_pretrained('dmis-lab/biobert-base-cased-v1.1')
    model_emb = AutoModel.from_pretrained('dmis-lab/biobert-base-cased-v1.1')
    symptom_embeddings = np.load('data/symptom_embeddings.npy')

except Exception as e:
    raise RuntimeError(f'Failed to load BioBert or embeddings: {e}')


def get_embedding(text, max_length=128):
    """Getting BioBert embedding for text (user input).
    
    Args:
        text (str): Input text for embedding.
        max_length (int): Maximum token length. Defaults to 128.

    Returns:
        np.ndarray: Embedding vector.

    Raises:
        ValueError: If text is empty or invalid.
    """
    if not text or not isinstance(text, str):
        raise ValueError(f'Text must be a non-empty string')
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=max_length)
        with torch.no_grad():
            outputs = model_emb(**inputs)
        # Use [CLS] token embedding
        return outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    except Exception as e:
        raise RuntimeError(f'Embedding generation failed: {e}')