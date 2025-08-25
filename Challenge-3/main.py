import uuid
import os
import time
import logging
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from fastapi import FastAPI, Body, HTTPException

# Unified interface functions from models.py
from backend.app.models import (
    rag_lawyer_wrapper as rag_lawyer,
    chaos_lawyer_wrapper as chaos_lawyer,
    summarize_verdict_llm as summarize_verdict,
    judge_random_event as judge
)
from backend.app.generator import generate_case
from backend.app.retrieval import load_corpus

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ----------------------------
# FastAPI App
# ----------------------------
app = FastAPI(title="⚖️ AI Legal Debate API")

# In-memory session store
DEBATE_SESSIONS: Dict[str, Any] = {}

# Thread pool for enforcing LLM timeouts
executor = ThreadPoolExecutor(max_workers=5)

# Timeout in seconds (default 120)
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

# ----------------------------
# Timeout wrapper
# ----------------------------
def call_with_timeout(fn, fallback: str, timeout: int = LLM_TIMEOUT) -> str:
    start = time.time()
    future = executor.submit(fn)
    try:
        result = future.result(timeout=timeout)
        elapsed = round(time.time() - start, 2)
        logger.info(f"⏱️ LLM call finished in {elapsed}s")
        return result
    except FuturesTimeout:
        logger.warning(f"⚠️ LLM call timed out after {timeout}s")
        return f"{fallback} (⚠️ timed out)"
    except Exception as e:
        logger.error(f"⚠️ LLM call error: {e}")
        return f"{fallback} (⚠️ error: {e})"

# ----------------------------
# Startup: Load Corpus
# ----------------------------
try:
    DOCS: List[Dict[str, Any]] = load_corpus("Metadata/cases.jsonl")
    logger.info(f"✅ Loaded {len(DOCS)} cases into memory.")
except Exception as e:
    logger.warning(f"⚠️ Could not load corpus: {e}")
    DOCS = []

# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "✅ Legal Debate API is running with MOCK LLM"}

@app.post("/generate_case")
def get_case() -> Dict[str, Any]:
    try:
        case = generate_case()
        title = case.get("title") or case.get("text", "Unknown Case")
        logger.info(f"🎲 Generated case: {title}")
        return {"case": case}
    except Exception as e:
        logger.error(f"⚠️ Case generation failed: {e}")
        raise HTTPException(status_code=500, detail="Case generation failed")

@app.post("/debate")
def debate(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    try:
        inbound = payload.get("case", payload)
        case_dict = inbound if isinstance(inbound, dict) else {"text": str(inbound)}
        case_text = case_dict.get("text", str(case_dict))

        logger.info("🚀 Debate started for case: %s", case_text)

        prosecution_turns, defense_turns, judge_events = [], [], []

        for round_num in range(3):
            logger.info(f"⚖️ Starting round {round_num+1}...")

            # Prosecution
            pros_arg = call_with_timeout(
                lambda: rag_lawyer(case_text, round_num),
                fallback="Prosecution argument unavailable"
            )
            prosecution_turns.append({"round": round_num + 1, "argument": pros_arg})

            # Defense
            cons_arg = call_with_timeout(
                lambda: chaos_lawyer(case_text, round_num),
                fallback="Defense argument unavailable"
            )
            defense_turns.append({"round": round_num + 1, "argument": cons_arg})

            # Judge events
            event = call_with_timeout(
                lambda: judge(case_text, prosecution_turns, defense_turns),
                fallback="Judge event unavailable"
            )
            judge_events.append({"round": round_num + 1, "event": event})

        session_id = str(uuid.uuid4())
        debate_obj = {
            "session_id": session_id,
            "case": case_dict,
            "case_text": case_text,
            "prosecution": prosecution_turns,
            "defense": defense_turns,
            "judge_events": judge_events,
        }

        DEBATE_SESSIONS[session_id] = debate_obj
        logger.info("🏁 Debate finished successfully. Session ID: %s", session_id)
        return debate_obj

    except Exception as e:
        logger.error(f"⚠️ Debate failed: {e}")
        raise HTTPException(status_code=500, detail="Debate execution failed")

@app.post("/summarize_verdict")
def summarize_verdict_route(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    try:
        case = payload.get("case", {})
        pros = payload.get("prosecution", [])
        defs = payload.get("defense", [])
        verdict = payload.get("judge_decision", "No decision provided")

        summary = call_with_timeout(
            lambda: summarize_verdict(case, pros, defs, verdict),
            fallback="Summary unavailable"
        )

        logger.info("📜 Verdict summarized: %s", verdict)
        return {"summary": summary}

    except Exception as e:
        logger.error(f"⚠️ Verdict summarization failed: {e}")
        raise HTTPException(status_code=500, detail="Verdict summarization failed")
