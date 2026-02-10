"""Configuration and LLM initialization."""

import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

logger.info("Loading the LLMs...")

# --- MODEL SPECIALIZATION ---
# 1. THE SMART ONE (Llama 3.3 70B): For Logic, Extraction, and Verdicts.
SMART_LLM = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

# 2. THE FAST ONE (Llama 3.1 8B): For Organizing, Sorting, and Summarizing.
FAST_LLM = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# --- EXTRACTION CONFIGURATION ---
EXTRACTION_CONFIG = {
    "chunk_size": 16000,
    "chunk_overlap": 400,
    "separators": ["\n\n", "\n", ".", " ", ""],
    "max_workers": 6,
    "retries": 3,
}
