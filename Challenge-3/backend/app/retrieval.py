import os
import json
from typing import List, Dict, Any

def load_corpus(path: str = "Metadata/cases.jsonl", verbose: bool = False) -> List[Dict[str, Any]]:
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        if verbose:
            print(f"⚠️ Corpus file not found: {abs_path}")
        return [{
            "id": 0,
            "title": "No Corpus Found",
            "year": "N/A",
            "jurisdiction": "Unknown",
            "tags": ["missing"],
            "text": "⚠️ The corpus file could not be located."
        }]

    docs: List[Dict[str, Any]] = []
    if verbose:
        print(f"📄 Loading corpus from: {abs_path}")

    with open(abs_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    docs.append(obj)
                elif isinstance(obj, list):
                    docs.extend(obj)
                else:
                    docs.append({"id": i, "text": str(obj)})
            except json.JSONDecodeError as e:
                if verbose:
                    print(f"⚠️ Skipping invalid JSON at line {i}: {e}")

    if not docs:
        if verbose:
            print("⚠️ No valid cases loaded, adding placeholder.")
        docs.append({
            "id": 0,
            "title": "No Valid Cases",
            "year": "N/A",
            "jurisdiction": "Unknown",
            "tags": ["empty"],
            "text": "⚠️ No valid cases could be loaded from the corpus."
        })

    if verbose:
        print(f"✅ Loaded {len(docs)} cases successfully.")

    return docs
