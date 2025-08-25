# backend/app/generator.py

import random
import logging
from typing import Dict, Any, List
from backend.app.retrieval import load_corpus

logger = logging.getLogger(__name__)

def generate_case(corpus_path: str = "Metadata/cases.jsonl", verbose: bool = True) -> Dict[str, Any]:
    """
    Generate a random legal case from the loaded corpus.
    
    Returns a dictionary with at least:
      - id
      - title
      - text
      - year
      - jurisdiction
      - tags
    """
    try:
        docs: List[Dict[str, Any]] = load_corpus(corpus_path, verbose=verbose)
        if not docs:
            logger.warning("⚠️ Corpus is empty, returning placeholder case.")
            return {
                "id": 0,
                "title": "No Cases Available",
                "year": "N/A",
                "jurisdiction": "Unknown",
                "tags": ["empty"],
                "text": "⚠️ No cases available in the corpus."
            }
        case = random.choice(docs)
        # Ensure required keys exist
        case.setdefault("id", 0)
        case.setdefault("title", "Untitled Case")
        case.setdefault("text", "No description available.")
        case.setdefault("year", "N/A")
        case.setdefault("jurisdiction", "Unknown")
        case.setdefault("tags", [])

        if verbose:
            logger.info(f"🎲 Selected case: {case.get('title')}")
        return case

    except Exception as e:
        logger.error(f"⚠️ Error generating case: {e}")
        return {
            "id": 0,
            "title": "Error Case",
            "year": "N/A",
            "jurisdiction": "Unknown",
            "tags": ["error"],
            "text": f"⚠️ An error occurred while generating a case: {e}"
        }
