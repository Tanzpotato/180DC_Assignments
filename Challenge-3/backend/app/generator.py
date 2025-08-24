import json
import os
import random
from typing import Dict, Any

# Path to your JSONL corpus
CORPUS_PATH = os.path.join("Metadata", "cases.jsonl")


def load_cases() -> list[Dict[str, Any]]:
    """Load all cases from the JSONL file."""
    if not os.path.exists(CORPUS_PATH):
        raise FileNotFoundError(f"Corpus not found at {CORPUS_PATH}")

    cases = []
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # skip blank lines
                try:
                    cases.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"⚠️ Skipping invalid line: {e}")
    return cases


def generate_case() -> Dict[str, Any]:
    """Return a random case from the JSONL corpus as a dict."""
    cases = load_cases()
    if not cases:
        # Fallback: return a dummy case if no data found
        return {
            "id": 0,
            "title": "Dummy Case",
            "year": 2023,
            "jurisdiction": "Unknown",
            "tags": ["test"],
            "text": "This is a placeholder case since no valid cases were found."
        }
    return random.choice(cases)


# For quick testing
if __name__ == "__main__":
    print(generate_case())
