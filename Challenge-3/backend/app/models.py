from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class CaseScenario(BaseModel):
    case: str = Field(..., example="A man sues a parrot for defamation.")
    metadata_hints: Optional[Dict[str, Any]] = None  

class DebateTurn(BaseModel):
    case: str
    rag_lawyer: Dict[str, Any]
    chaos_lawyer: Dict[str, Any]
    judge_decision: str = "Pending user input."

class JudgeInput(BaseModel):
    verdict: Optional[Literal["RAG", "Chaos", "Hung"]] = None
    new_evidence: Optional[str] = None
    role_reversal: Optional[bool] = False
    session_id: Optional[str] = None
