"""
Detective Test Data Loader
===========================
Helper module to easily load and access test case data for the hackathon detective program.

Usage:
    from detective_data_loader import load_case_data, get_audio_text, get_documents_text, get_clues_text
    
    # Load all data
    case_data = load_case_data()
    
    # Or get individual formatted sections
    audio = get_audio_text()
    documents = get_documents_text()
    clues = get_clues_text()
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_case_data(filepath: str = "detective_test_data.json") -> Dict[str, Any]:
    """
    Load the complete case data from JSON file.
    
    Args:
        filepath: Path to the JSON file (default: detective_test_data.json)
    
    Returns:
        Dictionary containing all case data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_audio_text(filepath: str = "detective_test_data.json") -> str:
    """
    Extract and format all audio transcripts into a single text string.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Formatted string containing all audio interview transcripts
    """
    data = load_case_data(filepath)
    
    audio_sections = []
    audio_sections.append("=" * 80)
    audio_sections.append("AUDIO TRANSCRIPTS - WITNESS INTERVIEWS")
    audio_sections.append("=" * 80)
    audio_sections.append("")
    
    for interview_id, interview_data in data["audio_transcripts"].items():
        audio_sections.append("-" * 80)
        audio_sections.append(f"INTERVIEW: {interview_id.replace('_', ' ').upper()}")
        audio_sections.append(f"Timestamp: {interview_data['timestamp']}")
        audio_sections.append(f"Duration: {interview_data['duration']}")
        audio_sections.append("-" * 80)
        audio_sections.append("")
        audio_sections.append(interview_data["transcript"])
        audio_sections.append("")
        if "notes" in interview_data:
            audio_sections.append(f"[DETECTIVE NOTES: {interview_data['notes']}]")
            audio_sections.append("")
    
    return "\n".join(audio_sections)


def get_documents_text(filepath: str = "detective_test_data.json") -> str:
    """
    Extract and format all document texts into a single string.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Formatted string containing all document contents
    """
    data = load_case_data(filepath)
    
    doc_sections = []
    doc_sections.append("=" * 80)
    doc_sections.append("DOCUMENTS AND RECORDS")
    doc_sections.append("=" * 80)
    doc_sections.append("")
    
    for doc_id, doc_data in data["documents"].items():
        doc_sections.append("-" * 80)
        doc_sections.append(f"DOCUMENT: {doc_id.replace('_', ' ').upper()}")
        doc_sections.append(f"Document ID: {doc_data.get('document_id', 'N/A')}")
        doc_sections.append(f"Date: {doc_data.get('date', 'N/A')}")
        doc_sections.append("-" * 80)
        doc_sections.append("")
        doc_sections.append(doc_data["content"])
        doc_sections.append("")
    
    return "\n".join(doc_sections)


def get_clues_text(filepath: str = "detective_test_data.json") -> str:
    """
    Extract and format all final clues into a single string.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Formatted string containing all final clues
    """
    data = load_case_data(filepath)
    
    clue_sections = []
    clue_sections.append("=" * 80)
    clue_sections.append("FINAL CLUES AND EVIDENCE")
    clue_sections.append("=" * 80)
    clue_sections.append("")
    
    for clue_id, clue_data in data["final_clues"].items():
        clue_sections.append("-" * 80)
        clue_sections.append(f"EVIDENCE: {clue_id.replace('_', ' ').upper()}")
        clue_sections.append("-" * 80)
        clue_sections.append("")
        clue_sections.append(clue_data["content"])
        clue_sections.append("")
    
    return "\n".join(clue_sections)


def get_all_text_combined(filepath: str = "detective_test_data.json") -> str:
    """
    Get all case data (audio, documents, clues) as one combined text.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Complete case file as formatted text
    """
    sections = []
    
    # Add case metadata
    data = load_case_data(filepath)
    sections.append("=" * 80)
    sections.append("CASE FILE - COMPLETE")
    sections.append("=" * 80)
    sections.append("")
    sections.append("CASE METADATA:")
    for key, value in data["case_metadata"].items():
        sections.append(f"  {key}: {value}")
    sections.append("")
    sections.append("")
    
    # Add all sections
    sections.append(get_audio_text(filepath))
    sections.append("\n\n")
    sections.append(get_documents_text(filepath))
    sections.append("\n\n")
    sections.append(get_clues_text(filepath))
    
    return "\n".join(sections)


def get_case_metadata(filepath: str = "detective_test_data.json") -> Dict[str, str]:
    """
    Get just the case metadata.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Dictionary with case metadata
    """
    data = load_case_data(filepath)
    return data["case_metadata"]


def print_data_statistics(filepath: str = "detective_test_data.json") -> None:
    """
    Print statistics about the test data.
    
    Args:
        filepath: Path to the JSON file
    """
    data = load_case_data(filepath)
    
    print("=" * 60)
    print("DETECTIVE TEST DATA STATISTICS")
    print("=" * 60)
    print(f"Number of audio interviews: {len(data['audio_transcripts'])}")
    print(f"Number of documents: {len(data['documents'])}")
    print(f"Number of final clues: {len(data['final_clues'])}")
    print()
    
    audio_text = get_audio_text(filepath)
    docs_text = get_documents_text(filepath)
    clues_text = get_clues_text(filepath)
    
    print(f"Total audio text length: {len(audio_text):,} characters")
    print(f"Total documents text length: {len(docs_text):,} characters")
    print(f"Total clues text length: {len(clues_text):,} characters")
    print(f"TOTAL DATA SIZE: {len(audio_text) + len(docs_text) + len(clues_text):,} characters")
    print()
    
    all_text = get_all_text_combined(filepath)
    word_count = len(all_text.split())
    print(f"Approximate word count: {word_count:,} words")
    print(f"Estimated tokens (rough): {int(word_count * 1.3):,} tokens")
    print("=" * 60)


# Example usage
if __name__ == "__main__":
    # Print statistics
    print_data_statistics()
    print()
    
    # Example of loading data
    print("EXAMPLE: Loading specific data sections")
    print("-" * 60)
    
    # Get case metadata
    metadata = get_case_metadata()
    print(f"Victim: {metadata['victim']}")
    print(f"Case Number: {metadata['case_number']}")
    print(f"Time of Death: {metadata['time_of_death']}")
    print()
    
    # Show how to access audio transcripts
    audio = get_audio_text()
    print("First 500 characters of audio transcripts:")
    print(audio[:500])
    print("...")
    print()
    
    # Show how to access documents
    docs = get_documents_text()
    print("First 500 characters of documents:")
    print(docs[:500])
    print("...")
