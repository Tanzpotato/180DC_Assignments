import random
import json
import os 

from .retrieval import load_corpus

def format_citation(d):
    return f'{d["title"]}, {d["year"]} ({d["jurisdiction"]})'

def rag_argument(query, top_docs, hints):
    if not top_docs:
        return {
            "argument": "No relevant precedent found; default rules apply.",
            "citations": [],
            "metadata": hints
        }
    d = top_docs[0]
    arg = (
        f'Precedent in {d.get("jurisdiction", "Unknown jurisdiction")} '
        f'suggests possible outcome. '
        f'In {d.get("title", "Unknown case")} ({d.get("year", "n.d.")}), '
        f'the court reasoned: {d.get("text", "")[:150]}...'
    )
    return {
        "argument": arg,
        "citations": [d.get("title", "Unknown case")] + [x.get("title", "Unknown") for x in top_docs[1:]],
        "metadata": {
            "jurisdiction": d.get("jurisdiction"),
            "tags": d.get("tags", []),
            "year": d.get("year")
        }
    }

CHAOS_STYLES = [
    "wild analogy", "jurisdictional loophole", "what-if escalation"
]

def chaos_argument(query):
    style = random.choice(CHAOS_STYLES)
    riffs = {
        "wild analogy": "If a voicemail can defame, why not a parrot? It’s just a feathered voicemail!",
        "jurisdictional loophole": "Under the Avian Rights Act (totally made up), parrots enjoy free speech.",
        "what-if escalation": "What if the parrot was bribed? Follow the cracker money!"
    }
    arg = f"As defense, I argue ({style}): {riffs[style]}"
    return {"argument": arg, "rhetoric": "Absurd, exaggerated counter-logic."}

def generate_case():
    """Pick a random case from Metadata/cases.jsonl."""
    # Go up TWO levels: backend/app/ → backend/ → project root
    path = os.path.join(os.path.dirname(__file__), "..", "..", "Metadata", "cases.jsonl")
    path = os.path.abspath(path)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Cases file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        cases = []
        for line in f:
            line = line.strip()
            if not line:  # skip empty lines
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON line in cases.jsonl: {line}") from e

    return random.choice(cases)
