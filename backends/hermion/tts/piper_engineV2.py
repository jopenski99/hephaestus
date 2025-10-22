import wave
from piper import PiperVoice
from hermion.core.config import settings
from datetime import datetime

class PiperEngine:
    def __init__(self):
        self.voice = PiperVoice.load(settings.ROOT_DIR /"models"/ settings.MODEL_NAME)
        self.ouput = settings.OUTPUT_DIR
    def synthesize(self, text: str):
        now = datetime.now()
        datetime_str = now.strftime("%m/%d/%Y-%I:%M%p")
        print(datetime_str)
        with wave.open("output.wav", "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file)
        return "output.wav"
    
def main(text: str):
    engine = PiperEngine()
    output_file = engine.synthesize(text)
    print(f"Synthesis successful: {output_file}")

if __name__ == "__main__":
    main("Welcome to the world of speech synthesis!")
