import subprocess, tempfile, os, time
from promethion.api.core.config import settings
from fastapi.responses import FileResponse, JSONResponse

class TTSClient:
    def __init__(self, config: dict):
        self.name = config["name"]
        self.config = config["config"]
        
    def generate(self, text: str):
        
        model = settings.TTS_DIR / self.name
        config = settings.TTS_DIR / self.config
        #output = settings.ROOT_DIR / "generated_audio/"
        
        if not os.path.exists(model) or not os.path.exists(config):
            return JSONResponse(
                status_code=404,
                content={"error": f"Model {self.name} not found in {settings.TTS_DIR}"}
            )
            
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        
        try:
        # Run Piper subprocess
            process = subprocess.run(
                [
                    "piper",
                    "-m", model,
                    "-c", config,
                    "-f", output_path
                ],
                input=text.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120
            )

            if process.returncode != 0:
                raise RuntimeError(process.stderr.decode("utf-8"))

            return FileResponse(output_path, media_type="audio/wav")

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})


    