"""Core forensic analysis engine."""

import json
import logging

from utils import build_chain, split_text_into_chunks, process_chunk_in_parallel
from prompts import (
    EXTRACTION_SYSTEM_PROMPT, EXTRACTION_TEMPLATE,
    TIMELINE_SYSTEM_PROMPT, TIMELINE_TEMPLATE,
    CONTRADICTION_SYSTEM_PROMPT, CONTRADICTION_TEMPLATE,
    VERDICT_SYSTEM_PROMPT, VERDICT_TEMPLATE
)
from config import SMART_LLM, FAST_LLM, EXTRACTION_CONFIG

logger = logging.getLogger(__name__)


def extract_structured_data(raw_text: str, data_type: str) -> str:
    """
    Extract structured forensic data from raw text using parallel chunk processing.
    
    Args:
        raw_text: Full text to extract from
        data_type: 'FACTS' or 'CLAIMS'
    
    Returns:
        JSON string of extracted items
    """
    logger.info("Processing %s (chunk_size=%s)...", data_type, EXTRACTION_CONFIG["chunk_size"])

    # Split into chunks
    chunks = split_text_into_chunks(
        raw_text,
        EXTRACTION_CONFIG["chunk_size"],
        EXTRACTION_CONFIG["chunk_overlap"],
        EXTRACTION_CONFIG["separators"]
    )
    logger.info("Split into %d chunks", len(chunks))

    # Build extraction chain
    chain = build_chain(EXTRACTION_SYSTEM_PROMPT, EXTRACTION_TEMPLATE, SMART_LLM)

    # Process chunks in parallel
    all_extracted = process_chunk_in_parallel(
        chunks,
        chain,
        {"text": lambda chunk: chunk, "dtype": data_type},
        EXTRACTION_CONFIG["max_workers"],
        EXTRACTION_CONFIG["retries"]
    )

    logger.info("Total Extracted Items: %d", len(all_extracted))
    return json.dumps(all_extracted, indent=2)


def create_timeline(facts: str, claims: str) -> str:
    """
    Merge facts and claims into a chronological timeline.
    
    Args:
        facts: JSON string of facts
        claims: JSON string of claims
    
    Returns:
        Timeline as a formatted string
    """
    logger.info("Constructing Master Timeline...")
    
    chain = build_chain(TIMELINE_SYSTEM_PROMPT, TIMELINE_TEMPLATE, FAST_LLM)
    return chain.invoke({"facts": facts, "claims": claims})


def find_contradictions(timeline: str) -> str:
    """
    Analyze timeline for lies and contradictions.
    
    Args:
        timeline: Formatted timeline string
    
    Returns:
        Analysis of contradictions found
    """
    logger.info("Detecting inconsistencies...")
    
    chain = build_chain(CONTRADICTION_SYSTEM_PROMPT, CONTRADICTION_TEMPLATE, SMART_LLM)
    return chain.invoke({"timeline": timeline})


def get_final_verdict(contradictions: str, clues: str, timeline: str) -> str:
    """
    Determine the killer based on all evidence.
    
    Args:
        contradictions: Analysis of contradictions
        clues: Additional clues
        timeline: Master timeline
    
    Returns:
        Final verdict with killer identification
    """
    logger.info("Delivering final verdict...")
    
    chain = build_chain(VERDICT_SYSTEM_PROMPT, VERDICT_TEMPLATE, SMART_LLM)
    return chain.invoke({
        "contradictions": contradictions,
        "clues": clues,
        "timeline": timeline
    })


def solve_mystery(audio_text: str, doc_text: str, clue_text: str) -> str:
    """
    Main orchestration function to solve a mystery case.
    
    Args:
        audio_text: Transcribed audio/witness statements
        doc_text: Document/log data
        clue_text: Additional clues
    
    Returns:
        Final verdict string
    """
    # Phase 1: Extract structured data
    logger.info("=== PHASE 1: EXTRACTING DATA ===")
    facts = extract_structured_data(doc_text, "FACTS")
    claims = extract_structured_data(audio_text, "CLAIMS")

    # Phase 2: Build timeline
    logger.info("=== PHASE 2: BUILDING TIMELINE ===")
    master_timeline = create_timeline(facts, claims)
    logger.info("--- MASTER TIMELINE ---\n%s\n-----------------------", master_timeline)

    # Phase 3: Detect contradictions
    logger.info("=== PHASE 3: DETECTING CONTRADICTIONS ===")
    logic_analysis = find_contradictions(master_timeline)
    logger.info("--- DETECTIVE'S NOTES ---\n%s\n-------------------------", logic_analysis)

    # Phase 4: Deliver verdict
    logger.info("=== PHASE 4: FINAL VERDICT ===")
    final_result = get_final_verdict(logic_analysis, clue_text, master_timeline)
    
    return final_result
