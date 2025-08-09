from pathlib import Path
from typing import List, Dict, Any, Optional
from .indexer.scanner import scan_paths
from .indexer.embedder import embed_texts
from .indexer.store import VectorStore
from .indexer.chunker import chunk_text
from .indexer.extract import extract_text

class Vectormancer:
    def __init__(self, config_path: Optional[str] = None, persist_dir: Optional[str] = None):
        self.config_path = config_path
        self.store = VectorStore(persist_dir=persist_dir)
        self.store.load()

    def index(self, path: str):
        files = scan_paths([Path(path)])
        for f in files:
            full = extract_text(f)
            if not full.strip():
                continue
            abs_id = str(f.resolve())
            for chunk, start, end in chunk_text(full):
                vec = embed_texts([chunk])[0]
                self.store.add(doc_id=abs_id, text=chunk, vector=vec, span=(start, end), full_doc_text=full)
        self.store.save()

    def query(self, question: str, top_k: int = 5, show_sources: bool = True, window: int = 1200) -> List[Dict[str, Any]]:
        qvec = embed_texts([question])[0]
        hits = self.store.search(qvec, top_k=top_k)
        if not show_sources:
            return [{"score": h["score"], "text": h["text"]} for h in hits]

        # RAG-style: merge to a context window per hit with citation
        out = []
        for h in hits:
            doc = self.store.get_doc_text(h["path"])
            if not doc:
                out.append(h)
                continue
            center = (h["start"] + h["end"]) // 2
            half = window // 2
            span_start = max(0, center - half)
            span_end   = min(len(doc), center + half)
            context = doc[span_start:span_end]
            out.append({
                **h,
                "context": context,
                "citation": {
                    "path": h["path"],
                    "offset": int(span_start),
                    "length": int(span_end - span_start)
                }
            })
        return out
