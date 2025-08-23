from fastapi import FastAPI
from .models import CaseScenario, DebateTurn, JudgeInput
from .retrieval import load_corpus, HybridRetriever
from .generator import rag_argument, chaos_argument
import random, uuid

app = FastAPI(title="AI Legal Debate")

CASES = [
    "A man sues a parrot for defamation.",
    "A robot barista refuses service; customer sues for discrimination.",
    "A landlord sues a ghost for unpaid rent."
]

DOCS = load_corpus("backend/data/cases.jsonl")
RETRIEVER = HybridRetriever(DOCS)
SESSIONS = {}

@app.post("/generate_case")
def generate_case(payload: CaseScenario | None = None):
    case = payload.case if payload and payload.case else random.choice(CASES)
    return {"case": case}

@app.post("/debate", response_model=DebateTurn)
def debate(payload: CaseScenario):
    top_docs, hints = RETRIEVER.search(payload.case, extra_hints=payload.metadata_hints)
    rag = rag_argument(payload.case, top_docs, hints)
    chaos = chaos_argument(payload.case)
    turn = {
        "case": payload.case,
        "rag_lawyer": rag,
        "chaos_lawyer": chaos,
        "judge_decision": "Pending user input."
    }
    sid = str(uuid.uuid4())
    SESSIONS[sid] = turn
    turn["session_id"] = sid
    return turn

@app.post("/judge_decision")
def judge_decision(inp: JudgeInput):
    sid = inp.session_id
    if sid and sid in SESSIONS:
        if inp.verdict:
            SESSIONS[sid]["judge_decision"] = inp.verdict
        if inp.new_evidence:
            base = SESSIONS[sid]["case"] + " New evidence: " + inp.new_evidence
            top_docs, hints = RETRIEVER.search(base)
            SESSIONS[sid]["rag_lawyer"] = rag_argument(base, top_docs, hints)
            SESSIONS[sid]["chaos_lawyer"] = chaos_argument(base)
            SESSIONS[sid]["case"] = base
        if inp.role_reversal:
            SESSIONS[sid]["rag_lawyer"], SESSIONS[sid]["chaos_lawyer"] = \
                SESSIONS[sid]["chaos_lawyer"], SESSIONS[sid]["rag_lawyer"]
        return SESSIONS[sid]
    return {"error": "Unknown session_id"}
