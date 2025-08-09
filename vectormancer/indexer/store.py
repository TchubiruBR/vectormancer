# Minimal FAISS-backed store (with numpy fallback if faiss missing)
from typing import List, Dict, Any
import numpy as np

try:
    import faiss
except Exception:
    faiss = None

class VectorStore:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.texts: List[str] = []
        self.ids: List[str] = []
        self.vectors = None  # numpy array
        if faiss is not None:
            self.index = faiss.IndexFlatIP(dim)
        else:
            self.index = None

    def add(self, doc_id: str, text: str, vector: list):
        vec = np.array(vector, dtype="float32").reshape(1, -1)
        if self.vectors is None:
            self.vectors = vec
        else:
            self.vectors = np.vstack([self.vectors, vec])
        self.texts.append(text)
        self.ids.append(doc_id)
        if self.index is not None:
            self.index.add(vec)

    def search(self, qvec: list, top_k: int = 5) -> List[Dict[str, Any]]:
        q = np.array(qvec, dtype="float32").reshape(1, -1)
        if self.index is not None:
            scores, idxs = self.index.search(q, top_k)
            idxs = idxs[0]
            scores = scores[0]
        else:
            # Cosine sim via numpy as fallback
            if self.vectors is None or len(self.texts) == 0:
                return []
            A = self.vectors / (np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-9)
            qn = q / (np.linalg.norm(q) + 1e-9)
            sims = (A @ qn.T).reshape(-1)
            idxs = np.argsort(-sims)[:top_k]
            scores = sims[idxs]
        results = []
        for i, s in zip(idxs, scores):
            if i < 0 or i >= len(self.texts):
                continue
            results.append({
                "id": self.ids[i],
                "text": self.texts[i][:400],
                "score": float(s),
                "path": self.ids[i],
                "snippet": self.texts[i][:200]
            })
        return results