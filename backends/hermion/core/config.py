from pathlib import Path
from pydantic_settings  import BaseSettings

class Settings(BaseSettings):
    # === App Info ===
    MODEL_NAME: str = "en_US-amy-low.onnx"
    CONFIG_PATH: str = "en_US-amy-low.onnx.json"

    # === External Services ===
    ROOT_DIR:Path = Path(__file__).resolve().parent.parent
    OUTPUT_DIR:Path = ROOT_DIR / "output"
    PORT: int = "8003"

    # === Models ===
    
     

settings = Settings()
