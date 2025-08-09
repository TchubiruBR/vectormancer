# Vectormancer

**Local-first vector search for your files, notes, and code.**  
Index PDFs, Markdown, docs, and source code; query with natural language; keep your data private.


## Why Vectormancer?

- **Private by default**: runs locally; no data leaves your machine.
- **Zero-config quickstart**: point it at a folder and search.
- **Flexible backends**: FAISS or ChromaDB; choose your embedding model (open-source or API).
- **Continuous sync**: watches your filesystem for changes and re-indexes incrementally.
- **CLI + Python API**: use it in scripts, terminals, or build a tiny app/UI.

## Features (MVP)

- Index local folders (PDF, TXT, MD, DOCX, HTML, PY, JS, TS, JSON)
- Pluggable embedding models (`sentence-transformers`, OpenAI, etc.)
- Vector stores: FAISS (default) or Chroma
- Simple CLI: `vectormancer index <path>` and `vectormancer query "<question>"`
- File-watcher for incremental updates
- Export/import index snapshots

## Installation

```bash
# From source
git clone https://github.com/you/vectormancer.git
cd vectormancer
pip install -e .
```

### Optional system deps
- poppler (for robust PDF text extraction) or `pypdf` fallback
- `tesseract` if you want OCR for scanned PDFs (future plugin)

## Quickstart

```bash
# 1) Index a folder
vectormancer index ~/Notes

# 2) Ask questions
vectormancer query "What did I write about retrieval augmented generation?"

# 3) Show sources and snippets
vectormancer query --top-k 5 "UE5 behavior trees vs decision transformers"


```


## Configuration

Create `~/.vectormancer/config.yaml` or use `--config`:

```yaml
embeddings:
  provider: sentence-transformers
  model: all-MiniLM-L6-v2     # or 'text-embedding-3-small' (OpenAI)

vector_store:
  backend: faiss               # or 'chroma'
  path: ~/.vectormancer/index

indexing:
  include_ext: [".md", ".txt", ".pdf", ".py", ".ipynb", ".json", ".js", ".ts"]
  exclude_dirs: [".git", "node_modules", "__pycache__"]
  chunk_size: 800
  chunk_overlap: 120

watcher:
  enabled: true
```

## CLI

```bash
vectormancer index <PATH> [--config CONFIG] [--rebuild]
vectormancer query "<QUESTION>" [--top-k K] [--show-sources] [--config CONFIG]
vectormancer daemon start [--config CONFIG]   # optional file-watcher service
```

CLI Usage:

```bash
# Index a folder of .txt or .py files:
vectormancer index ./examples

# Query the index:
vectormancer query "high frequency trading in NASDAQ" --top-k 3

# Query with extended context windows (good for RAG)
vectormancer query "high frequency trading in NASDAQ" --top-k 3 --window 1000

# Rebuild the index from scratch
vectormancer index ./examples --rebuild

```

## Python API

```python
from vectormancer import Vectormancer

vm = Vectormancer(config_path="~/.vectormancer/config.yaml")
vm.index("/path/to/folder")
hits = vm.query("notes about PPO vs DPO", top_k=5, show_sources=True)
for h in hits:
    print(h.score, h.path, h.snippet)
```

Most updated:
```python
from vectormancer import Vectormancer

# Create engine
vm = Vectormancer()

# Index files
vm.index("./examples")

# Query
results = vm.query("capital of France", top_k=3)

for r in results:
    print(r["path"], r["score"], r["snippet"])

```
## Architecture (MVP)

```
+--------------------+       +-------------------+
|  File Scanner      |  -->  |  Text Extractors  |  (pdf/md/docx/code)
+--------------------+       +-------------------+
           |                           |
           v                           v
   Chunker & Normalizer         Embedding Model
           |                           |
           +-------------> Vector Store (FAISS/Chroma)
                                   |
                                   v
                               Query Engine
```

### Packages & Components

- `vectormancer.indexer` — scanning, extraction, chunking, embeddings, vector DB I/O
- `vectormancer.cli` — CLI entry points
- `vectormancer.ui` — optional Streamlit UI (later)
- `examples/` — runnable samples
- `tests/` — unit tests for parser, embedder, retrieval

## Roadmap

- [ ] OCR plugin (Tesseract) for scanned PDFs
- [ ] RAG-ready: return citations + context windows
- [ ] Lightweight Streamlit UI
- [ ] Code-aware chunking (AST-based)
- [ ] Multi-repo indexing and Git history awareness
- [ ] Embedding cache with fingerprints
- [ ] Incremental compaction / pruning

## Contributing

PRs welcome! Please open an issue to discuss bigger changes.

## License

MIT © 2025 Zhafira Elham