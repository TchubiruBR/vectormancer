from pathlib import Path
from .indexer.scanner import scan_paths
from .indexer.embedder import embed_texts
from .indexer.store import VectorStore
from .indexer.chunker import chunk_text
from .indexer.extract import extract_text
from typing import List, Dict, Any
from typing import Optional
import os

class Vectormancer:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.store = VectorStore()

    def index(self, path: str):
        files = scan_paths([Path(path)])
        for f in files:
            text = extract_text(f)
            for chunk in chunk_text(text):
                vec = embed_texts([chunk])[0]
                self.store.add(doc_id=str(f), text=chunk, vector=vec)

    def query(self, question: str, top_k: int = 5, show_sources: bool = True) -> List[Dict[str, Any]]:
        qvec = embed_texts([question])[0]
        hits = self.store.search(qvec, top_k=top_k)
        if show_sources:
            return hits
        return [{"score": h["score"], "text": h["text"]} for h in hits]