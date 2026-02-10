import os
import sys
import importlib.util

def print_status(component, status, message=""):
    icon = "✅" if status == "OK" else "❌"
    color = "\033[92m" if status == "OK" else "\033[91m"
    reset = "\033[0m"
    print(f"{icon} [{color}{status}{reset}] {component:<25} {message}")
    return status == "OK"

print("\n" + "="*60)
print("🕵️  SHERLOCK AI - SYSTEM DIAGNOSTICS")
print("="*60 + "\n")

all_passed = True

# 1. CHECK VIRTUAL ENVIRONMENT
is_venv = (sys.prefix != sys.base_prefix) or hasattr(sys, 'real_prefix')
if is_venv:
    print_status("Virtual Env", "OK", f"Active at: {sys.prefix}")
else:
    print_status("Virtual Env", "FAIL", "NOT ACTIVE! Activate your .venv first.")
    # We don't fail strictly here, just warn, as some use Conda/Global
    
# 2. CHECK .ENV & API KEYS
if os.path.exists(".env"):
    print_status(".env File", "OK", "Found")
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and groq_key.startswith("gsk_"):
            print_status("Groq API Key", "OK", "Valid Format (starts with gsk_)")
        else:
            print_status("Groq API Key", "FAIL", "Missing or Invalid in .env")
            all_passed = False
            
    except ImportError:
        print_status("dotenv Library", "FAIL", "Not installed")
        all_passed = False
else:
    print_status(".env File", "FAIL", "MISSING! Create it with GROQ_API_KEY")
    all_passed = False

# 3. CHECK CRITICAL LIBRARIES
print("-" * 60)
libraries = [
    "streamlit",
    "groq",
    "langchain_groq",
    "fitz", # PyMuPDF
    "PIL",  # Pillow
    "dotenv" # python-dotenv
]

for lib in libraries:
    if importlib.util.find_spec(lib) is not None:
        print_status(f"Library: {lib}", "OK")
    else:
        print_status(f"Library: {lib}", "FAIL", "Run: pip install -r requirements.txt")
        all_passed = False

# 4. CHECK PROJECT FILES
print("-" * 60)
required_files = [
    "dashboard.py",
    "THE_BRAIN_PRO.py",
    "THE_EAR_PRO.py",
    "THE_EYE_VISION_GROQ.py",
    "engine.py",
    "config.py",
    "prompts.py",
    "utils.py",
    "validation.py"
]

for f in required_files:
    if os.path.exists(f):
        print_status(f"File: {f}", "OK")
    else:
        print_status(f"File: {f}", "FAIL", "MISSING from folder!")
        all_passed = False

# 5. FINAL VERDICT
print("\n" + "="*60)
if all_passed:
    print("🚀 SYSTEMS GREEN. YOU ARE READY TO WIN.")
    print("   Run command: streamlit run dashboard.py")
else:
    print("⚠️  SYSTEM RED. FIX ERRORS ABOVE BEFORE STARTING.")
print("="*60 + "\n")
