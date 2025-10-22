from pathlib import Path
from pydantic_settings  import BaseSettings


class Settings(BaseSettings):
    # === App Info ===
    APP_NAME: str = "Hephaestus API"
    DEBUG: bool = True

    # === External Services ===
    AI_HOST: str = "http://localhost"
    AI_PORT: int = "11434"
    DATABASE_URL: str = "sqlite:///./hephaestus.db"

    # === Models ===
    
    # ==== Embedder =======
    EMBEDDER_NAME: str = "all-mpnet-base-v2"
    
    # ===== TTS ======
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent 
    TTS_DIR:Path = ROOT_DIR / "models/piper" 
    TTS_NAME: str = "en_US-danny-low.onnx"
    TTS_CONFIG: str = "en_US-danny-low.onnx.json" 
    
    # ==== LLM =======
    LLM_HOST: str = "http://localhost"
    LLM_NAME: str = "phi3:medium:Q4_K_M"
    
    # ==== Classifier =======
    CLASSIFIER_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    CLASSIFIER_NAME: str = "meta-llama/llama-3.2-3b-instruct:free"
    CLASSIFIER_KEY: str = "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"
    CLASSIFIER_PORT: str = ""
    # === Security ===
    JWT_SECRET: str = "dev_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === Directories ===
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    PROMTPS_DIR: Path = BASE_DIR / "prompts"
    UPLOAD_DIR: Path = DATA_DIR / "knowledge_files"
    DISPOSE_DIR: Path = DATA_DIR / "dump"

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")  
        env_file_encoding = "utf-8"


# instantiate once
settings = Settings()
# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DISPOSE_DIR.mkdir(parents=True, exist_ok=True)
