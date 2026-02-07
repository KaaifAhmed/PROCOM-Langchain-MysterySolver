"""
Main entry point for the Mystery Solver.

This is a Langchain-based forensic analysis tool that:
1. Extracts structured facts and claims from documents and audio
2. Builds a chronological timeline
3. Detects contradictions and lies
4. Identifies the killer with confidence scoring
"""

import logging
from detective_data_loader import get_audio_text, get_documents_text, get_clues_text
from engine import solve_mystery

logger = logging.getLogger(__name__)


def main():
    """Load data and solve the mystery."""
    logger.info("Loading case data...")
    audio_input = get_audio_text()
    document_input = get_documents_text()
    clue_input = get_clues_text()

    logger.info("Starting mystery solver...")
    result = solve_mystery(audio_input, document_input, clue_input)
    
    logger.info("=== CASE CLOSED ===\n%s", result)
    return result


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Error running solver: %s", e)
