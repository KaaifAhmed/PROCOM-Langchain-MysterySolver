import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

class AdvancedForensicEar:
    def __init__(self):
        print(f"   ...Initializing Audio Forensics (Cloud Engine)...")
        try:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        except Exception as e:
            print(f"❌ Groq API Error: {e}")
            self.client = None

    def process(self, file_path):
        if not self.client: return "❌ Audio Engine not loaded."
        
        print("   ...Uploading to Forensic Cloud (Groq Whisper)...")
        
        try:
            start = time.time()
            with open(file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(file_path, file.read()),
                    model="whisper-large-v3", # Much smarter than the local base model
                    response_format="text",
                    language="en",
                    temperature=0.0
                )
            return transcription.strip()
        except Exception as e:
            return f"❌ Transcription Error: {e}"