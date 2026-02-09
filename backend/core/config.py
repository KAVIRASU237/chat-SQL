import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Offline NL-DB Assistant"
    DATABASE_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/sample.db"))
    VECTOR_STORE_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/faiss_index"))
    OLLAMA_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "mistral"
    
    class Config:
        case_sensitive = True

settings = Settings()
