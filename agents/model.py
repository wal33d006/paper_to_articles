from langchain_google_genai import ChatGoogleGenerativeAI
from agents.config import config


def get_model():
    return ChatGoogleGenerativeAI(
        model=config.model_name,
        google_api_key=config.google_api_key,
        temperature=config.temperature
    )
