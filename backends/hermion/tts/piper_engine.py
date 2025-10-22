import subprocess
import uuid
import os
from pathlib import Path
from hermion.core.config import settings

class PiperEngine:
    def __init__(self):
        self.model_path = str(settings.ROOT_DIR / "models" / settings.MODEL_NAME)
        self.config_path = str(settings.ROOT_DIR / "models" / settings.CONFIG_PATH)
        self.output_dir = str(settings.OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)
        self.piper_exe =  r"C:\Dev\hephaestus\venv\Scripts\piper.exe"

    def synthesize(self, text: str) -> str:
        if not text.strip():
            raise ValueError("Input text is empty!")

        output_file = os.path.join(self.output_dir, f"{uuid.uuid4()}.wav")

        cmd = [
            self.piper_exe,
            "-m", self.model_path,
            "-c", self.config_path,
            "-f", output_file,
            "-" 
        ]

        print(f"\n🔊 Synthesizing text: {repr(text)}")
        print(f"💻 Running command: {' '.join(cmd)}")
        print("📂 Current working directory:", os.getcwd())

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # ensure consistent working dir
            text=True,                   # auto-handle text encoding (UTF-8)
            universal_newlines=True
        )
        stdout, stderr = process.communicate(input=text)

        print("📤 Piper stdout:", stdout)
        print("📥 Piper stderr:", stderr)

        if process.returncode != 0:
            raise RuntimeError(f"Piper TTS failed (code {process.returncode}). See logs above.")

        print(f"✅ Synthesis successful: {output_file}")
        return output_file
