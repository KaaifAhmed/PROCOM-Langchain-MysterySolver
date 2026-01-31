import whisper
import os
import warnings
import time

# --- CONFIGURATION ---
# "base" is fast. Use "medium" if you have a good GPU for higher accuracy.
MODEL_TYPE = "base" 
EVIDENCE_DIR = "Evidence_Transcripts"

# Suppress warnings to keep your terminal clean
warnings.filterwarnings("ignore")

class ForensicInvestigator:
    def __init__(self):
        print(f"🕵️  Initializing AI Investigator ({MODEL_TYPE})...")
        # Load the model ONCE (Cached)
        try:
            self.model = whisper.load_model(MODEL_TYPE)
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Could not load model. Is FFmpeg installed? Error: {e}")
            return

        # Create a folder for your evidence if it doesn't exist
        if not os.path.exists(EVIDENCE_DIR):
            os.makedirs(EVIDENCE_DIR)
        print("✅ System Ready. Awaiting evidence files.")

    def process_evidence(self, file_path):
        """
        Handles hearing, fixing punctuation, and translating to English.
        """
        start_time = time.time()
        print(f"\n🎧 Analyzing: {os.path.basename(file_path)}...")

        # Transcribe & Translate in one go
        # task="translate" ensures output is always English (Rules req this)
        result = self.model.transcribe(file_path, task="translate")
        
        text = result["text"].strip()
        language = result.get("language", "unknown")
        
        duration = time.time() - start_time
        
        return text, language, duration

    def save_log(self, filename, text):
        """
        Saves the evidence to a text file for Stage 2 usage.
        """
        base_name = os.path.basename(filename)
        save_path = os.path.join(EVIDENCE_DIR, f"{base_name}.txt")
        
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"SOURCE FILE: {base_name}\n")
            f.write("-" * 30 + "\n")
            f.write(text)
        
        return save_path

# --- MAIN LOOP ---
if __name__ == "__main__":
    investigator = ForensicInvestigator()

    while True:
        print("\n" + "="*50)
        # We capture raw input first to handle the PowerShell '&' symbol
        raw_input = input("📂 Drag & Drop Audio File (or type 'exit'): ").strip()

        if raw_input.lower() == "exit":
            print("Shutting down investigation.")
            break

        # --- FIX FOR POWERSHELL DRAG & DROP ---
        # 1. Remove the leading '& ' if it exists (PowerShell artifact)
        if raw_input.startswith("& "):
            raw_input = raw_input[2:]
        
        raw_input = raw_input.strip()

        # 2. Handle Single Quotes (PowerShell escapes ' as '')
        if raw_input.startswith("'") and raw_input.endswith("'"):
            # Remove outer quotes and fix the internal double-quotes
            file_path = raw_input[1:-1].replace("''", "'")
        # 3. Handle Double Quotes
        elif raw_input.startswith('"') and raw_input.endswith('"'):
            file_path = raw_input[1:-1]
        else:
            file_path = raw_input
        # ---------------------------------------

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            print("   (Check if the path has a double extension like .m4a.m4a)")
            continue

        try:
            # 1. Run the AI Pipeline
            transcript, lang, time_taken = investigator.process_evidence(file_path)

            # 2. Display 'Sahi' Output
            print("\n" + "-"*15 + " FORENSIC REPORT " + "-"*15)
            print(f"🗣️  Detected Language: {lang.upper()}")
            print(f"⏱️  Processing Time: {time_taken:.2f}s")
            print("-" * 47)
            print(transcript)
            print("-" * 47)

            # 3. Save for the team
            saved_loc = investigator.save_log(file_path, transcript)
            print(f"✅ Evidence saved to: {saved_loc}")

        except Exception as e:
            print(f"❌ Critical Error: {e}")