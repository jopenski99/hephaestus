from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from hermion.tts.piper_engineV2 import PiperEngine

import base64
import shutil
print("🧩 Piper path resolved to:", shutil.which("piper"))
router = APIRouter()
engine = PiperEngine()

class TTSRequest(BaseModel):
    text: str
    base64: bool = False

@router.post("/tts")
async def synthesize(req: TTSRequest):
    #try:
    output_path = engine.synthesize(req.text)
    
    return {"audio_path": output_path}
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail=str(e))
