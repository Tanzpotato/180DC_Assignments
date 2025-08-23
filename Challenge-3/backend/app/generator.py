import random

def format_citation(d):
    return f'{d["title"]}, {d["year"]} ({d["jurisdiction"]})'

def rag_argument(query, top_docs, hints):
    if not top_docs:
        return {
            "argument": "No relevant precedent found; by default, non-human actors cannot be held liable unless statute applies.",
            "citations": [],
            "metadata": hints
        }
    d = top_docs[0]
    arg = (
        f'Under {d["case_type"]} principles '
        f'({", ".join(d.get("principles", []))}), '
        f'precedent in {d["jurisdiction"]} suggests {d["outcome"]}. '
        f'In {format_citation(d)}, the court reasoned: {d["text"][:150]}...'
    )
    return {
        "argument": arg,
        "citations": [format_citation(x) for x in top_docs],
        "metadata": {
            "case_type": d.get("case_type"),
            "jurisdiction": d.get("jurisdiction"),
            "key_legal_principles": d.get("principles", []),
            "outcome": d.get("outcome")
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
