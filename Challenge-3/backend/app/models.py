# backend/app/models.py

from typing import List, Dict, Any, Union
from backend.app.llm import (
    rag_lawyer,
    chaos_lawyer,
    summarize_verdict as summarize_verdict_llm,  # alias to keep old name
    judge as judge_random_event,
)


# -------------------------------------------------------------------
# Unified interface wrappers for main.py and other modules
# -------------------------------------------------------------------

def rag_lawyer_wrapper(case_text: str, round_num: int, context: str = "") -> str:
    """
    Prosecution lawyer (RAG) wrapper.
    Delegates to backend.app.llm.rag_lawyer.
    """
    return rag_lawyer(case_text, round_num, context)


def chaos_lawyer_wrapper(case_text: str, round_num: int) -> str:
    """
    Defense lawyer (chaotic/random style) wrapper.
    Delegates to backend.app.llm.chaos_lawyer.
    """
    return chaos_lawyer(case_text, round_num)


def summarize_verdict(
    case: Union[Dict[str, Any], str],
    pros: List[Dict[str, str]],
    cons: List[Dict[str, str]],
    verdict: str
) -> str:
    """
    Summarize the debate outcome and verdict using the LLM.
    """
    return summarize_verdict_llm(case, pros, cons, verdict)


def judge(
    case: Union[Dict[str, Any], str],
    rag_turns: List[Dict[str, str]],
    chaos_turns: List[Dict[str, str]]
) -> str:
    """
    Generate a random but plausible courtroom event.
    Does NOT decide the verdict – user provides the final decision.
    """
    return judge_random_event(case, rag_turns, chaos_turns)
