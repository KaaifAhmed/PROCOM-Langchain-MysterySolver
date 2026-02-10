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

# --- CHECKPOINTING ---
# Save intermediate steps (facts, timeline, etc.) to disk for debugging/recovery
ENABLE_CHECKPOINTS = True
CHECKPOINT_DIR = "case_logs"


logger.info("Loading the LLMs...")

# --- MODEL SPECIALIZATION ---
# 1. THE SMART ONE (Llama 3.3 70B): For Logic, Extraction, and Verdicts.
SMART_LLM = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

# 2. THE FAST ONE (Llama 3.1 8B): For Organizing, Sorting, and Summarizing.
FAST_LLM = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# --- TOKEN LIMITS ---
# Llama 3.3 supports 128k context. We set this to 32k to be safe with Rate Limits (TPM).
# If you have a high-tier Groq account, you can increase this to 100,000.
MAX_CONTEXT_TOKENS = 32000  # Threshold to trigger summarization


# --- EXTRACTION CONFIGURATION ---
EXTRACTION_CONFIG = {
    # Reduced to 10,000 chars (~2,500 tokens) to increase parallelism
    # and reduce latency (smaller chunks = faster processing per chunk)
    "chunk_size": 10000, 
    "chunk_overlap": 500,
    "separators": ["\n\n", "\n", ".", " ", ""],
    "max_workers": 10, # Increased workers for higher concurrency
    "retries": 3,
}

