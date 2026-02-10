"""Simple validation utilities for forensic analysis output."""

import json
import logging

logger = logging.getLogger(__name__)


def validate_json_list(json_str: str) -> list:
    """Parse and validate JSON list. Returns empty list on failure."""
    try:
        cleaned = json_str.strip().replace("```json", "").replace("```", "").strip()
        if not cleaned:
            return []
        data = json.loads(cleaned)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        logger.warning("Invalid JSON format")
        return []


def validate_timeline(timeline_str: str) -> bool:
    """Check if timeline has minimum required content."""
    return bool(timeline_str and len(timeline_str.strip()) > 50)


def validate_contradictions(analysis_str: str) -> bool:
    """Check if contradiction analysis has required sections."""
    required = ["Contradiction", "CLAIM", "FACT"]
    has_all = all(word in analysis_str for word in required)
    return bool(analysis_str and len(analysis_str.strip()) > 50 and has_all)


def validate_verdict(verdict_str: str) -> bool:
    """Check if verdict identifies killer with evidence."""
    required = ["KILLER", "Smoking Gun", "Confidence"]
    has_all = all(word in verdict_str for word in required)
    return bool(verdict_str and len(verdict_str.strip()) > 100 and has_all)


def clean_output(text: str) -> str:
    """Remove markdown code fences from LLM output."""
    if not isinstance(text, str):
        return ""
    return text.replace("```json", "").replace("```", "").strip()
