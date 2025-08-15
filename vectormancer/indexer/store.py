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

        # Core data
        self.texts: List[str] = []     # chunk text
        self.ids: List[str] = []       # doc path per chunk
        self.spans: List[tuple] = []   # (start, end) in original doc
        self.vectors: Optional[np.ndarray] = None

        # Full doc cache for RAG windows
        self.doc_texts: Dict[str, str] = {}

        # FAISS index (optional)
        if faiss is not None:
            self.index = faiss.IndexFlatIP(dim)
        else:
            self.index = None

    # ---------- Add / Search ----------
    def add(self, doc_id: str, text: str, vector: list, span: tuple, *, full_doc_text: Optional[str] = None):
        vec = np.array(vector, dtype="float32").reshape(1, -1)
        self.vectors = vec if self.vectors is None else np.vstack([self.vectors, vec])
        self.texts.append(text)
        self.ids.append(doc_id)
        self.spans.append((int(span[0]), int(span[1])))
        if self.index is not None:
            self.index.add(vec)
        if full_doc_text is not None:
            # cache once per doc
            if doc_id not in self.doc_texts:
                self.doc_texts[doc_id] = full_doc_text

    def search(self, qvec: list, top_k: int = 5) -> List[Dict[str, Any]]:
        if (self.vectors is None) or (len(self.texts) == 0):
            return []
        q = np.array(qvec, dtype="float32").reshape(1, -1)

        if self.index is not None:
            scores, idxs = self.index.search(q, top_k)
            idxs = idxs[0]
            scores = scores[0]
        else:
            A = self.vectors / (np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-9)
            qn = q / (np.linalg.norm(q) + 1e-9)
            sims = (A @ qn.T).reshape(-1)
            idxs = np.argsort(-sims)[:top_k]
            scores = sims[idxs]

        results = []
        for i, s in zip(idxs, scores):
            if i < 0 or i >= len(self.texts):
                continue
            start, end = self.spans[i]
            doc_id = self.ids[i]
            results.append({
                "id": doc_id,
                "path": doc_id,
                "text": self.texts[i][:400],
                "score": float(s),
                "start": int(start),
                "end": int(end),
            })
        return results

    # ---------- RAG helpers ----------
    def get_doc_text(self, doc_id: str) -> str:
        return self.doc_texts.get(doc_id, "")

    # ---------- Persistence ----------
    def _paths(self):
        os.makedirs(self.persist_dir, exist_ok=True)
        return (
            os.path.join(self.persist_dir, "meta.json"),
            os.path.join(self.persist_dir, "vectors.npy"),
            os.path.join(self.persist_dir, "index.faiss"),
            os.path.join(self.persist_dir, "docs.json"),
        )

    def save(self):
        meta, vecs, faiss_idx, docs = self._paths()
        with open(meta, "w", encoding="utf-8") as f:
            json.dump({
                "ids": self.ids,
                "texts": self.texts,
                "spans": self.spans,
                "dim": self.dim
            }, f)
        if self.vectors is not None:
            np.save(vecs, self.vectors)
        if self.index is not None and hasattr(faiss, "write_index"):
            faiss.write_index(self.index, faiss_idx)
        with open(docs, "w", encoding="utf-8") as f:
            json.dump(self.doc_texts, f)

    def load(self) -> bool:
        meta, vecs, faiss_idx, docs = self._paths()
        if not os.path.exists(meta):
            return False
        try:
            with open(meta, "r", encoding="utf-8") as f:
                m = json.load(f)
            self.ids   = m.get("ids", [])
            self.texts = m.get("texts", [])
            self.spans = [tuple(x) for x in m.get("spans", [])]
            self.dim   = int(m.get("dim", self.dim))

            if os.path.exists(vecs):
                self.vectors = np.load(vecs)
            if self.index is not None and os.path.exists(faiss_idx):
                self.index = faiss.read_index(faiss_idx)

            if os.path.exists(docs):
                with open(docs, "r", encoding="utf-8") as f:
                    self.doc_texts = json.load(f)
            else:
                self.doc_texts = {}
            return True
        except Exception:
            return False


    def stats(self) -> dict:
        meta, vecs, faiss_idx, docs = self._paths()
        size_bytes = 0
        for p in (meta, vecs, faiss_idx, docs):
            if os.path.exists(p):
                size_bytes += os.path.getsize(p)
        return {
            "persist_dir": self.persist_dir,
            "num_chunks": len(self.texts),
            "num_docs": len(set(self.ids)),
            "dim": self.dim,
            "faiss_enabled": bool(self.index is not None),
            "files_on_disk": {
                "meta": os.path.exists(meta),
                "vectors": os.path.exists(vecs),
                "faiss": os.path.exists(faiss_idx),
                "docs": os.path.exists(docs),
            },
            "disk_usage_bytes": size_bytes,
        }
