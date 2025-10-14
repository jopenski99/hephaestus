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
    EMBEDDER_NAME: str = "all-mpnet-base-v2"
    LLM_NAME: str = "phi3:mini"

    # === Security ===
    JWT_SECRET: str = "dev_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === Directories ===
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
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
