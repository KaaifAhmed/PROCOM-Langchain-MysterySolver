import logging
import sys
import os

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("Sherlock_Bridge")

# --- IMPORT THE ENGINE ---
try:
    # This imports the solve_mystery function from your 'engine.py' file
    from engine import solve_mystery
except ImportError as e:
    solve_mystery = None
    logger.error(f"❌ CRITICAL IMPORT ERROR: {e}")
    print(f"❌ CRITICAL: Could not import 'engine.py'. Details: {e}")

def solve_case(audio_log, doc_log, clues_log=""):
    """
    The Bridge Function.
    It takes raw text logs from the Dashboard (Frontend) and feeds them 
    into your sophisticated backend Engine.
    """
    
    # 1. Safety Check: Did the modules load?
    if not solve_mystery:
        return "❌ ERROR: Backend Modules Missing.\n\nMake sure these files are in your folder:\n- engine.py\n- config.py\n- prompts.py\n- utils.py\n- validation.py", ""

    try:
        # 2. Prepare Inputs (Handle empty data)
        if not audio_log: audio_log = "No audio evidence collected."
        if not doc_log: doc_log = "No document evidence collected."
        if not clues_log: clues_log = "No additional clues provided."

        logger.info("🧠 Brain Activated. Feeding data to Forensic Engine...")
        
        # 3. CALL THE BACKEND (This triggers your full multi-file pipeline)
        # 🚨 CRITICAL UPDATE: Unpacking the tuple (Report, Context)
        final_verdict, full_context = solve_mystery(audio_log, doc_log, clues_log)
        
        # 4. Return Output
        # Now passing the full_context so your Chatbot knows the details
        return final_verdict, full_context
        
    except Exception as e:
        logger.exception("Brain Execution Failed")
        return f"❌ BRAIN ERROR: {str(e)}\n\nCheck the terminal for full error logs.", ""