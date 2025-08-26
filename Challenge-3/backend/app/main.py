import uuid
import os
import time
from fastapi import FastAPI, Body
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from backend.app.models import rag_lawyer, chaos_lawyer, judge
from backend.app.generator import generate_case
from backend.app.retrieval import load_corpus
from backend.app.llm import summarize_verdict_llm,judge_random_event

app = FastAPI(title="⚖️ AI Legal Debate API")

DEBATE_SESSIONS: Dict[str, Any] = {}

executor = ThreadPoolExecutor(max_workers=5)

LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

def call_with_timeout(fn, fallback: Any, timeout: int = LLM_TIMEOUT) -> Any:
    start = time.time()
    future = executor.submit(fn)
    try:
        result = future.result(timeout=timeout)
        elapsed = round(time.time() - start, 2)
        print(f"⏱️ LLM call finished in {elapsed}s")
        return result
    except FuturesTimeout:
        return fallback if isinstance(fallback, dict) else {"argument": fallback}
    except Exception as e:
        return {"argument": f"{fallback} (⚠️ error: {e})"}

try:
    DOCS: List[Dict[str, Any]] = load_corpus("Metadata/cases.jsonl")
    print(f"✅ Loaded {len(DOCS)} cases into memory.")
except Exception as e:
    print(f"⚠️ Could not load corpus: {e}")
    DOCS = []

@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "✅ Legal Debate API is running"}

@app.post("/generate_case")
def get_case() -> Dict[str, Any]:
    case = generate_case()
    title = case.get("title") or case.get("text", "Unknown Case")
    print(f"🎲 Generated case: {title}")
    return {"case": case}

@app.post("/debate")
def debate(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    inbound = payload.get("case", payload)
    case_dict = inbound if isinstance(inbound, dict) else {"text": str(inbound)}
    case_text = case_dict.get("text", str(case_dict))

    print("🚀 Debate started for case:", case_text)

    prosecution_turns, defense_turns, judge_events = [], [], []

    for round_num in range(3):
        print(f"⚖️ Starting round {round_num+1}...")
        
        pros_arg = call_with_timeout(
            lambda: rag_lawyer(case_dict, round_num),
            fallback={"argument": "Prosecution argument unavailable"}
        )
        pros_text = pros_arg.get("argument", str(pros_arg))
        print(f"✅ Prosecution round {round_num+1}: {pros_text[:80]}")
        prosecution_turns.append(pros_arg)

        cons_arg = call_with_timeout(
            lambda: chaos_lawyer(case_dict, round_num),
            fallback={"argument": "Defense argument unavailable"}
        )
        cons_text = cons_arg.get("argument", str(cons_arg))
        print(f"✅ Defense round {round_num+1}: {cons_text[:80]}")
        defense_turns.append(cons_arg)

        event = call_with_timeout(
            lambda: judge_random_event(case_dict, round_num),
            fallback="Judge event unavailable"
        )

        print(f"✅ Judge round {round_num+1}: {str(event)[:80]}")

        judge_events.append({
            "round": round_num + 1,
            "argument": event.get("argument", "No event returned") if isinstance(event, dict) else str(event)
        })


    debate_obj = {
        "session_id": str(uuid.uuid4()),
        "case": case_dict,
        "case_text": case_text,
        "prosecution": prosecution_turns,
        "defense": defense_turns,
        "judge_events": judge_events,
    }

    DEBATE_SESSIONS[debate_obj["session_id"]] = debate_obj
    print("🏁 Debate finished successfully. Session ID:", debate_obj["session_id"])
    return debate_obj

@app.post("/summarize_verdict")
def summarize_verdict(payload: dict = Body(...)) -> str:
    case = payload.get("case", {})
    pros = payload.get("pros", [])
    defs = payload.get("defs", [])
    verdict = payload.get("verdict", "Prosecution")

    case_title = case.get("title", "Untitled Case")
    case_text = case.get("text", "")

    pros_args = [p.get("argument", "") for p in pros if isinstance(p, dict)]
    defs_args = [d.get("argument", "") for d in defs if isinstance(d, dict)]

    summary = (
        f"In the case of **{case_title}**, the court examined the matter of {case_text}. "
        f"The Prosecution argued forcefully, citing points such as {', '.join(pros_args[:2]) or 'general legal principles'}. "
        f"In contrast, the Defense countered with arguments including {', '.join(defs_args[:2]) or 'unconventional claims'}. "
        f"After weighing both sides, the Judge concluded that the {verdict} presented stronger reasoning and "
        f"was more persuasive in addressing the facts of the case. "
        f"This ultimately led to a verdict in favor of the **{verdict}**."
    )

    return summary

