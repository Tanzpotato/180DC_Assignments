from fastapi import FastAPI, Body
import uuid

# ✅ Use package imports (works when running `uvicorn backend.app.main:app --reload`)
from .models import rag_lawyer, chaos_lawyer
from .generator import generate_case
from .retrieval import load_corpus

app = FastAPI()

# Store active sessions in memory
DEBATE_SESSIONS = {}

# Load case corpus (adjust path if needed)
DOCS = load_corpus("Metadata/cases.jsonl")


# -----------------------------
# Endpoints
# -----------------------------
@app.get("/")
def root():
    return {"message": "Legal Debate API is running"}


@app.post("/generate_case")
def get_case():
    """Return a randomly generated case."""
    case = generate_case()
    return {"case": case}


@app.post("/debate")
def debate(case: dict):
    """Simulate a multi-round debate and store session (no AI judge decision)."""
    rag_turns = []
    chaos_turns = []
    case_text = case["case"]

    # Simulate 3 rounds of back-and-forth
    for round_num in range(3):
        rag_argument = rag_lawyer(case_text, round_num)
        chaos_argument = chaos_lawyer(case_text, round_num)

        rag_turns.append({"round": round_num + 1, "argument": rag_argument})
        chaos_turns.append({"round": round_num + 1, "argument": chaos_argument})

    # Store session without judge decision
    session_id = str(uuid.uuid4())
    DEBATE_SESSIONS[session_id] = {
        "case": case_text,
        "rag_lawyer": rag_turns,
        "chaos_lawyer": chaos_turns,
        "judge_decision": None,  # ✅ Left empty for the user to decide later
    }

    return {
        "session_id": session_id,
        "case": case_text,
        "rag_lawyer": rag_turns,
        "chaos_lawyer": chaos_turns,
        "judge_decision": None,
    }


@app.post("/judge_decision")
def judge_decision(
    session_id: str = Body(...),
    verdict: str = Body(...),
):
    """User sets the final verdict (acts as the judge)."""
    if session_id not in DEBATE_SESSIONS:
        return {"error": "Invalid session_id"}

    session = DEBATE_SESSIONS[session_id]
    session["judge_decision"] = f"Judge rules in favor of {verdict}"

    return {
        "session_id": session_id,
        "judge_decision": session["judge_decision"],
    }
