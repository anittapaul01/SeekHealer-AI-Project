"""TabNet model for the disease predictions"""

import pandas as pd
import numpy as np
from pytorch_tabnet.tab_model import TabNetClassifier


try:
    aug_df = pd.read_csv('data/aug_df.csv')
    disease_classes = pd.factorize(aug_df['Prognosis'])[1]
    symptoms_col = aug_df.columns[1:]
    model_tab = TabNetClassifier()
    model_tab.load_model('data/tabnet_model.zip')
except FileNotFoundError as e:
    raise FileNotFoundError(f'Failed to load dataset or mode: {e}')


# Retrieve top k diseases using TabNet

def retrieve_top_diseases(ip_vec, top_k=3):
    '''Predict top diseases based on symptom vector.

    Args:
        ip_vec (np.ndarray): Input symptom vector.
        top_k (int): No. of top predictions to return, Defaut set to 3.

    Returns:
        list: List of (disease, probability) tuples.

    Raises:
        ValueError: If input vector shape is incorrect.    
    '''
    if ip_vec.shape[-1] != len(symptoms_col):
        raise ValueError(f'Input vector size {ip_vec.shape[-1]} does not match {len(symptoms_col)} symptoms')
    try:
        ip_vec = ip_vec.reshape(1, -1)
        pred_prob = model_tab.predict_proba(ip_vec)
        top_k_ind = np.argsort(pred_prob[0])[::-1][:top_k]
        top_k_prob = pred_prob[0][top_k_ind]
        top_k_diseases = disease_classes[top_k_ind]
        return list(zip(top_k_diseases, top_k_prob))
    except Exception as e:
        raise RuntimeError(f'Prediction failed: {e}')