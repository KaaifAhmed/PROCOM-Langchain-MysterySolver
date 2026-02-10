"""Utility functions for LangChain operations and text processing."""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from validation import clean_output

logger = logging.getLogger(__name__)


def build_chain(system_prompt: str, template: str, llm):
    """Build a LangChain chain from system prompt and template."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", template)
    ])
    return prompt | llm | StrOutputParser()


def split_text_into_chunks(text: str, chunk_size: int, chunk_overlap: int, separators: list) -> list:
    """Split text into chunks using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators
    )
    return splitter.split_text(text)


def invoke_chain_with_retry(chain, input_data: dict, max_retries: int = 3) -> str:
    """Invoke a chain with exponential backoff retry logic."""
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            return chain.invoke(input_data)
        except Exception as e:
            backoff = 1.5 ** attempt
            logger.warning("Attempt %d failed: %s. Backing off %.1fs", attempt, e, backoff)
            time.sleep(backoff)
    logger.error("Failed after %d attempts", max_retries)
    return "[]"


def process_chunk_in_parallel(
    chunks: list,
    chain,
    input_key_mapping: dict,
    max_workers: int = 6,
    retries: int = 3
) -> list:
    """
    Process multiple chunks in parallel using ThreadPoolExecutor.
    
    Args:
        chunks: List of text chunks
        chain: LangChain chain to invoke
        input_key_mapping: Dict mapping chain input keys to values (or functions that take chunk)
        max_workers: Max concurrent workers
        retries: Number of retries per chunk
    
    Returns:
        List of parsed JSON results from all chunks
    """
    def _process_chunk(idx, chunk_text):
        attempt = 0
        while attempt < retries:
            attempt += 1
            try:
                input_data = {}
                for key, value in input_key_mapping.items():
                    input_data[key] = value(chunk_text) if callable(value) else value
                
                result = chain.invoke(input_data)
                cleaned = clean_output(result)
                parsed = json.loads(cleaned) if cleaned else []
                
                if isinstance(parsed, list):
                    logger.debug("Chunk %d: parsed %d items", idx + 1, len(parsed))
                    return parsed
                return []
            except Exception as e:
                backoff = 1.5 ** attempt
                logger.warning("Chunk %d: attempt %d failed: %s", idx + 1, attempt, e)
                time.sleep(backoff)
        return []

    all_results = []
    max_workers = min(max_workers, max(1, (os.cpu_count() or 4)))
    
    with ThreadPoolExecutor(max_workers=max_workers) as exe:
        futures = {exe.submit(_process_chunk, i, c): i for i, c in enumerate(chunks)}
        for fut in as_completed(futures):
            try:
                data = fut.result()
                if data:
                    all_results.extend(data)
            except Exception as e:
                logger.error("Error processing chunk: %s", e)

    return all_results
