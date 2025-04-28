'''FastAPI backend for disease prediction.'''

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pubmed_fetch import fetch_medical_info
from symptom_matching import match_symptoms
from tabnet_model import retrieve_top_diseases
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
logger.info("FastAPI initialized")


class UserInput(BaseModel):
    '''User input model.'''
    symptoms: str


def generate_response(user_input, top_diseases):
    '''Generate HTML-formatted response for top 3 predictions.

    Args:
        user_input (str): User input symptoms.
        top_diseases (list of tuples): Predicted diseases with their probabilties.

    Returns:
        str: HTML-Formatted response string.
    '''
    try:
        top_diseases = [(disease, proba * 100) for disease, proba in top_diseases]
        # Header
        response = (
            f"<div class='results-header'>"
            f"For your symptoms  —  {user_input}  —  here are the top "
            f"3 possible conditions:"
            f"</div>"
        )
        # Concise disease info
        for i, (disease, proba) in enumerate(top_diseases[:3], 1):
            info = fetch_medical_info(disease, user_input)
            response += (
                f"<div class='result-card'>"
                f"<div class='disease-name'>{i}. {disease.title()} ({proba:.1f}% chance)</div>"
                f"<div class='disease-desc'>What it is: {info}</div>"
                f"</div>"
            )
        # Footer
        response += (
            "<div class='results-footer'>"
            "⚠️ Heads Up: This is an AI guess. Check with a doctor for certainty."
            "</div>"
        )
        return response
    except Exception as e:
        raise RuntimeError(f'Response generation failed: {e}')
    

@app.post('/predict')
async def predict_disease(user_input: UserInput):
    '''Predict diseases from user symptoms.

    Args:
        user_input (UserInput): User input data.

    Returns:
        dict: Predicton response.

    Raises:
        HTTPException: If prediction fails.
    '''
    logger.info(f"Received predict request: {user_input}")
    try:
        ip_vec = match_symptoms(user_input.symptoms)
        top_diseases = retrieve_top_diseases(ip_vec)
        response = generate_response(user_input.symptoms, top_diseases)
        return {'response': response}
    except Exception as e:
        logger.error(f"Error in predict: {e}")
        raise HTTPException(status_code=500, detail=f'Prediction failed: {str(e)}')
    

