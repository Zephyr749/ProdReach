from app.ai.client import client
from app.core.config import app_settings
from typing import List


TEXT_EMBEDDING_MODEL = app_settings.text_embedding_model_name

def get_embedding(text:str) -> List[float]:
    """Converts a text string into a 1536-dimensional vector."""
    clean_text = text.replace("\n", " ")
    response = client.embeddings.create(
        input= clean_text,
        model= TEXT_EMBEDDING_MODEL
    )
    
    return response.data[0].embedding
