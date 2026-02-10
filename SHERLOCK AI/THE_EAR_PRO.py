import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

class AdvancedForensicEar:
    def __init__(self):
        print(f"   ...Initializing Audio Forensics (Groq Whisper)...")
        try:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        except Exception as e:
            print(f"❌ Groq API Error: {e}")
            self.client = None

    def process(self, file_path):
        if not self.client: return "❌ Audio Engine not loaded."
        
        print(f"   ...Transcribing {os.path.basename(file_path)}...")
        
        # KEYWORD PRIMING: Helps Whisper spell names correctly
        case_keywords = "BioGenix, Dr. Richard Castellano, Sarah Chen, Marcus Reid, Project Helix, Cyanide, Potassium, Lab 2-B"
        
        try:
            start = time.time()
            with open(file_path, "rb") as file:
                # Read file content safely
                file_content = file.read()
                
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(file_path), file_content), # Send (Name, Bytes)
                    model="whisper-large-v3",
                    prompt=case_keywords, # 🧠 SMART MOVE: Primes the model with case context
                    response_format="text",
                    language="en",
                    temperature=0.0 # Strict accuracy
                )
            
            duration = round(time.time() - start, 2)
            print(f"   ✅ Transcribed in {duration}s")
            return transcription.strip()
            
        except Exception as e:
            return f"❌ Transcription Error: {e}"