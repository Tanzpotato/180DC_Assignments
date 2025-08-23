import json, re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util

def load_corpus(path="backend/data/cases.jsonl"):
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs

def tokenize(text):
    return re.findall(r"[A-Za-z']+", text.lower())

class HybridRetriever:
    def __init__(self, docs):
        self.docs = docs
        self.corpus_texts = [ (d["title"] + " " + d["text"]).strip() for d in docs ]
        self.corpus_tokens = [ tokenize(t) for t in self.corpus_texts ]
        self.bm25 = BM25Okapi(self.corpus_tokens)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.doc_embs = self.model.encode(self.corpus_texts, normalize_embeddings=True)

    def metadata_hint(self, query):
        q = query.lower()
        m = {}
        if "defamation" in q: m["case_type"]="defamation"
        if "contract" in q: m["case_type"]="contract"
        if "tort" in q or "negligence" in q: m["case_type"]="tort"
        if "uk" in q: m["jurisdiction"]="UK"
        if "us" in q: m["jurisdiction"]="US"
        return m

    def meta_score(self, doc, hints):
        score = 0.0
        if not hints: return score
        if "case_type" in hints and doc.get("case_type")==hints["case_type"]: score += 1.0
        if "jurisdiction" in hints and doc.get("jurisdiction")==hints["jurisdiction"]: score += 0.5
        return score

    def search(self, query, k=3, extra_hints=None):
        hints = {**self.metadata_hint(query), **(extra_hints or {})}
        kw_scores = self.bm25.get_scores(tokenize(query))
        q_emb = self.model.encode([query], normalize_embeddings=True)[0]
        sem_scores = util.cos_sim(q_emb, self.doc_embs).cpu().numpy().ravel()

        def norm(x): 
            x = np.array(x)
            return (x - x.min()) / (x.max() - x.min() + 1e-9)

        kw_n, sem_n = norm(kw_scores), norm(sem_scores)

        combined = []
        for i, d in enumerate(self.docs):
            meta = self.meta_score(d, hints)
            score = 0.3*kw_n[i] + 0.4*sem_n[i] + 0.3*meta
            combined.append((score, i))
        combined.sort(reverse=True)
        top = [ self.docs[i] for _, i in combined[:k] ]
        return top, hints
