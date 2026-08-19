from openai import OpenAI
from app.core.config import app_settings

client= OpenAI(
    api_key=app_settings.openai_api_key,
    base_url=app_settings.openai_api_base_url
)

