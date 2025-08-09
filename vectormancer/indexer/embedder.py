# Minimal stub using sentence-transformers
from typing import List
import numpy as np

_model = None

def _load_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model = None
    return _model

def embed_texts(texts: List[str]) -> List[list]:
    m = _load_model()
    if m is None:
        # Fallback: random vectors for skeleton demo
        return [np.random.rand(384).tolist() for _ in texts]
    vecs = m.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vecs]