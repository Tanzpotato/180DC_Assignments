# backend/app/main.py
from .models import rag_lawyer, chaos_lawyer, judge
from .generator import generate_case
from .retrieval import load_corpus
