# backend/app/__init__.py

# ----------------------------
# Import wrappers from models
# ----------------------------
from backend.app.models import (
    rag_lawyer_wrapper as rag_lawyer,
    chaos_lawyer_wrapper as chaos_lawyer,
    summarize_verdict,
    judge,
)

# ----------------------------
# Optional: expose generator and retrieval functions
# ----------------------------
from backend.app.generator import generate_case
from backend.app.retrieval import load_corpus

# ----------------------------
# Define __all__ for clarity
# ----------------------------
__all__ = [
    "rag_lawyer",
    "chaos_lawyer",
    "summarize_verdict",
    "judge",
    "generate_case",
    "load_corpus",
]
