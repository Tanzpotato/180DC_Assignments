import random
from typing import List, Dict, Any

# ----------------------------
# Mock LLM for testing
# ----------------------------

# Predefined templates for Prosecution and Defense
PROSECUTION_TEMPLATES = [
    "Based on precedent, I argue that {case_text} strongly supports our position.",
    "Considering the facts and relevant legal principles, {case_text} clearly favors the prosecution.",
    "Examining the case details, it is evident that {case_text} warrants a favorable outcome for the prosecution.",
]

DEFENSE_TEMPLATES = [
    "While the facts suggest otherwise, {case_text} allows room for a creative defense.",
    "Taking a broader view, {case_text} presents unique angles that favor the defense.",
    "Considering all aspects, {case_text} may support an alternative interpretation favoring the defense.",
]

JUDGE_EVENTS = [
    "The judge allows additional evidence to be submitted.",
    "The judge raises a procedural objection.",
    "A surprise witness enters the courtroom.",
    "The judge requests clarifications from both sides.",
    "The courtroom experiences a brief recess."
]

# ----------------------------
# LLM Functions
# ----------------------------

def rag_lawyer(case_text: str, round_num: int, context: str = "") -> str:
    """
    Prosecution lawyer using mock RAG logic.
    Uses templates with optional context injection.
    """
    base = random.choice(PROSECUTION_TEMPLATES)
    ctx = f" Context: {context}" if context else ""
    return (base.format(case_text=case_text) + ctx).strip()

def chaos_lawyer(case_text: str, round_num: int) -> str:
    """
    Defense lawyer: unpredictable, creative, sometimes absurd but persuasive.
    """
    return random.choice(DEFENSE_TEMPLATES).format(case_text=case_text).strip()

def judge(case: str, pros: List[Dict[str, str]], cons: List[Dict[str, str]]) -> str:
    """
    Judge introduces a random courtroom twist or procedural event.
    Chooses an event and slightly personalizes it based on the current round.
    """
    event = random.choice(JUDGE_EVENTS)
    round_num = len(pros)
    return f"Round {round_num}: {event}"

def summarize_verdict(case: Dict[str, Any], pros: List[Dict[str, str]], cons: List[Dict[str, str]], verdict: str) -> str:
    """
    Summarize the debate and the Judge’s decision in 3-5 sentences.
    """
    case_title = case.get("title") or "Untitled Case"
    summary_lines = [
        f"The case '{case_title}' was debated over {len(pros)} rounds.",
        f"The prosecution argued: " + "; ".join([p["argument"] for p in pros]),
        f"The defense argued: " + "; ".join([c["argument"] for c in cons]),
        f"The judge ultimately ruled in favor of: {verdict}.",
        "This conclusion considers the arguments presented by both sides."
    ]
    return " ".join(summary_lines)
