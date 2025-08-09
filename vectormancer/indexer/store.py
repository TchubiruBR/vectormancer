# Minimal FAISS-backed store (with numpy fallback if faiss missing)
from typing import List, Dict, Any, Optional
import os, json, numpy as np

try:
    import faiss  # type: ignore
except Exception:
    faiss = None

DEFAULT_DIR = os.path.expanduser("~/.vectormancer/index")

class VectorStore:
    def __init__(self, dim: int = 384, persist_dir: Optional[str] = None):
        self.dim = dim
        self.persist_dir = os.path.expanduser(persist_dir or DEFAULT_DIR)
        self.texts: List[str] = []
        self.ids: List[str] = []
        self.vectors: Optional[np.ndarray] = None

        # Build a FAISS index if available
        if faiss is not None:
            self.index = faiss.IndexFlatIP(dim)
        else:
            self.index = None

    def add(self, doc_id: str, text: str, vector: list):
        vec = np.array(vector, dtype="float32").reshape(1, -1)
        # keep vectors in memory either way (for saving & numpy fallback)
        self.vectors = vec if self.vectors is None else np.vstack([self.vectors, vec])
        self.texts.append(text)
        self.ids.append(doc_id)
        if self.index is not None:
            self.index.add(vec)

    def search(self, qvec: list, top_k: int = 5) -> List[Dict[str, Any]]:
        if (self.vectors is None) or (len(self.texts) == 0):
            return []
        q = np.array(qvec, dtype="float32").reshape(1, -1)

        if self.index is not None:
            scores, idxs = self.index.search(q, top_k)
            idxs = idxs[0]
            scores = scores[0]
        else:
            # cosine similarity in numpy as fallback
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

    # ---------- Persistence ----------
    def _paths(self):
        os.makedirs(self.persist_dir, exist_ok=True)
        meta = os.path.join(self.persist_dir, "meta.json")
        vecs = os.path.join(self.persist_dir, "vectors.npy")
        faiss_idx = os.path.join(self.persist_dir, "index.faiss")
        return meta, vecs, faiss_idx

    def save(self):
        meta, vecs, faiss_idx = self._paths()
        with open(meta, "w", encoding="utf-8") as f:
            json.dump({"ids": self.ids, "texts": self.texts, "dim": self.dim}, f)
        if self.vectors is not None:
            np.save(vecs, self.vectors)
        if self.index is not None and hasattr(faiss, "write_index"):
            faiss.write_index(self.index, faiss_idx)

    def load(self) -> bool:
        meta, vecs, faiss_idx = self._paths()
        if not os.path.exists(meta):
            return False
        try:
            with open(meta, "r", encoding="utf-8") as f:
                m = json.load(f)
            self.ids = m.get("ids", [])
            self.texts = m.get("texts", [])
            self.dim = int(m.get("dim", self.dim))
            self.vectors = None
            if os.path.exists(vecs):
                self.vectors = np.load(vecs)
            if self.index is not None and os.path.exists(faiss_idx):
                self.index = faiss.read_index(faiss_idx)
            elif self.index is None and self.vectors is not None:
                # no FAISS, will use numpy fallback
                pass
            return True
        except Exception:
            return False
