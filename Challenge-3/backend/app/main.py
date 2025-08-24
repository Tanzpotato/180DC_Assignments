from fastapi import FastAPI, Body
import uuid, random
from typing import Dict, Any

# ✅ Absolute imports since we run `uvicorn backend.app.main:app`
from backend.app.models import rag_lawyer, chaos_lawyer
from backend.app.generator import generate_case
from backend.app.retrieval import load_corpus

app = FastAPI()

# In-memory session storage
DEBATE_SESSIONS: Dict[str, Any] = {}

# Load case corpus once
try:
    DOCS = load_corpus("Metadata/cases.jsonl")
except Exception as e:
    print(f"⚠️ Could not load corpus: {e}")
    DOCS = []


# -----------------------------
# Endpoints
# -----------------------------

@app.get("/")
def root():
    return {"message": "✅ Legal Debate API is running"}


@app.post("/generate_case")
def get_case():
    """Return a randomly generated case from Metadata/cases.jsonl."""
    case = generate_case()
    return {"case": case}


@app.post("/debate")
def debate(case: Dict[str, Any]):
    """Simulate a multi-round debate. Returns arguments, but no judge decision."""
    case_text = case["case"] if isinstance(case, dict) and "case" in case else case

    prosecution_turns = []
    defense_turns = []

    # Simulate 3 rounds of arguments
    for round_num in range(3):
        prosecution_turns.append({
            "round": round_num + 1,
            "argument": rag_lawyer(case_text, round_num)
        })
        defense_turns.append({
            "round": round_num + 1,
            "argument": chaos_lawyer(case_text, round_num)
        })

    session_id = str(uuid.uuid4())
    debate_obj = {
        "session_id": session_id,
        "case": case_text,
        "prosecution": prosecution_turns,
        "defense": defense_turns,
    }

    DEBATE_SESSIONS[session_id] = debate_obj
    return debate_obj


@app.post("/summarize_verdict")
def summarize_verdict(payload: Dict[str, Any] = Body(...)):
    """
    Summarize the case, arguments, and final verdict.
    This is called after the user (judge) submits their decision.
    """
    case = payload.get("case", {})
    pros = payload.get("prosecution", [])
    defs = payload.get("defense", [])
    verdict = payload.get("judge_decision", "No decision provided")

    # Very simple summarization (replace with LLM call if needed)
    case_title = case.get("title") if isinstance(case, dict) else str(case)
    pros_points = "; ".join([p["argument"] for p in pros])
    defs_points = "; ".join([d["argument"] for d in defs])

    summary = (
        f"**Case:** {case_title}\n\n"
        f"**Prosecution argued:** {pros_points}\n\n"
        f"**Defense argued:** {defs_points}\n\n"
        f"**Final Verdict:** Judge ruled in favor of **{verdict}**."
    )

    return {"summary": summary}
