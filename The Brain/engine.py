"""Core forensic analysis engine."""

import json
import logging

from utils import build_chain, split_text_into_chunks, process_chunk_in_parallel
from prompts import (
    EXTRACTION_SYSTEM_PROMPT, EXTRACTION_TEMPLATE,
    TIMELINE_SYSTEM_PROMPT, TIMELINE_TEMPLATE,
    CONTRADICTION_SYSTEM_PROMPT, CONTRADICTION_TEMPLATE,
    VERDICT_SYSTEM_PROMPT, VERDICT_TEMPLATE,
    SUMMARIZATION_SYSTEM_PROMPT, SUMMARIZATION_TEMPLATE
)
from config import SMART_LLM, FAST_LLM, EXTRACTION_CONFIG, MAX_CONTEXT_TOKENS, ENABLE_CHECKPOINTS, CHECKPOINT_DIR
from utils import save_checkpoint

logger = logging.getLogger(__name__)




def summarize_text(text: str) -> str:
    """Summarize text if it exceeds the token limit."""
    if not text:
        return ""
        
    # Crude estimation: 1 token ~= 4 chars
    estimated_tokens = len(text) / 4
    
    if estimated_tokens < MAX_CONTEXT_TOKENS:
        return text

    logger.info("Text size (%.0f tokens) exceeds limit (%d). Summarizing...", estimated_tokens, MAX_CONTEXT_TOKENS)
    chain = build_chain(SUMMARIZATION_SYSTEM_PROMPT, SUMMARIZATION_TEMPLATE, FAST_LLM)
    
    # Split into large chunks for summarization (e.g., 12k chars ~ 3k tokens)
    chunks = split_text_into_chunks(text, 12000, 500, ["\n\n", "\n", ". "])
    
    if len(chunks) <= 1:
        return chain.invoke({"text": text})
    
    # Map-Reduce style summarization for very large inputs
    summaries = []
    for i, chunk in enumerate(chunks):
        logger.info("Summarizing chunk %d/%d...", i+1, len(chunks))
        try:
            summary = chain.invoke({"text": chunk})
            summaries.append(summary)
        except Exception as e:
            logger.error("Failed to summarize chunk %d: %s", i+1, e)
            summaries.append(chunk[:2000] + "... [Truncated due to error]")
            
    return "\n".join(summaries)


def extract_structured_data(raw_text: str, data_type: str) -> str:
    """Extract structured forensic data from raw text."""
    logger.info("Processing %s...", data_type)

    chunks = split_text_into_chunks(
        raw_text,
        EXTRACTION_CONFIG["chunk_size"],
        EXTRACTION_CONFIG["chunk_overlap"],
        EXTRACTION_CONFIG["separators"]
    )
    logger.info("Split into %d chunks", len(chunks))

    chain = build_chain(EXTRACTION_SYSTEM_PROMPT, EXTRACTION_TEMPLATE, SMART_LLM)
    all_extracted = process_chunk_in_parallel(
        chunks,
        chain,
        {"text": lambda chunk: chunk, "dtype": data_type},
        EXTRACTION_CONFIG["max_workers"],
        EXTRACTION_CONFIG["retries"]
    )

    logger.info("Extracted %d items", len(all_extracted))
    # Use compact JSON separators to save tokens
    return json.dumps(all_extracted, separators=(',', ':'))



def create_timeline(facts: str, claims: str) -> str:
    """Merge facts and claims into a chronological timeline."""
    logger.info("Building timeline...")
    
    # Summarize inputs if they are massive before timeline construction
    # Note: For timeline, we prefer not to summarize structured JSON, but if it's text, we might.
    # FACTS and CLAIMS from extract_structured_data are defined as JSON strings.
    # Summarizing JSON with a text summarizer will break the structure.
    # However, create_timeline takes the strings and passes them to the prompt.
    # If the JSON strings are too huge, we might context overflow.
    # Strategy: Prune or summarize the JSON list? Hard to do with text LLM efficiently without parsing.
    # For now, we rely on the large context of the model (8k/128k depending on model).
    # Llama 3.1 8B has 128k context, so it should handle raw JSON lists fine.
    # We will only summarize the *output* if needed, or the raw input text in extraction phase.
    
    chain = build_chain(TIMELINE_SYSTEM_PROMPT, TIMELINE_TEMPLATE, FAST_LLM)
    return chain.invoke({"facts": facts, "claims": claims})


def find_contradictions(timeline: str) -> str:
    """Analyze timeline for lies and contradictions."""
    logger.info("Detecting contradictions...")
    
    # If timeline is huge, standard contradiction finding might fail or be slow.
    # But usually timeline is the condensed version of facts.
    
    chain = build_chain(CONTRADICTION_SYSTEM_PROMPT, CONTRADICTION_TEMPLATE, SMART_LLM)
    return chain.invoke({"timeline": timeline})


def get_final_verdict(contradictions: str, clues: str, timeline: str) -> str:
    """Determine the killer based on all evidence."""
    logger.info("Generating final verdict...")
    
    # Optimization: Summarize inputs if they are too large
    timeline = summarize_text(timeline)
    contradictions = summarize_text(contradictions)
    clues = summarize_text(clues)

    chain = build_chain(VERDICT_SYSTEM_PROMPT, VERDICT_TEMPLATE, SMART_LLM)
    return chain.invoke({
        "contradictions": contradictions,
        "clues": clues,
        "timeline": timeline
    })


def solve_mystery(audio_text: str, doc_text: str, clue_text: str) -> str:
    """Main orchestration function to solve a mystery case."""
    # Phase 1: Extract structured data
    logger.info("=== PHASE 1: EXTRACTING DATA ===")
    facts = extract_structured_data(doc_text, "FACTS")
    claims = extract_structured_data(audio_text, "CLAIMS")
    
    save_checkpoint("1_facts.json", facts)
    save_checkpoint("2_claims.json", claims)

    # Phase 2: Build timeline

    logger.info("=== PHASE 2: BUILDING TIMELINE ===")
    master_timeline = create_timeline(facts, claims)
    logger.info("Timeline preview: %s...", master_timeline[:200])
    
    save_checkpoint("3_master_timeline.txt", master_timeline)

    # Phase 3: Detect contradictions
    logger.info("=== PHASE 3: DETECTING CONTRADICTIONS ===")
    logic_analysis = find_contradictions(master_timeline)
    
    save_checkpoint("4_contradictions.txt", logic_analysis)

    # Phase 4: Deliver verdict
    logger.info("=== PHASE 4: FINAL VERDICT ===")
    final_result = get_final_verdict(logic_analysis, clue_text, master_timeline)
    
    save_checkpoint("5_final_verdict.txt", final_result)
    
    return final_result