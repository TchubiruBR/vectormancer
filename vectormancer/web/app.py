from __future__ import annotations
import os, shutil
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from vectormancer import Vectormancer
from vectormancer.indexer.fetcher import fetch_url

PERSIST_DIR = os.path.expanduser("~/.vectormancer/index")
DEFAULT_CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples"))

app = FastAPI(title="Vectormancer API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# Single long-lived engine with persistence
vm = Vectormancer(persist_dir=PERSIST_DIR)

class IndexReq(BaseModel):
    path: str = DEFAULT_CORPUS
    rebuild: bool = False

class QueryReq(BaseModel):
    question: str
    top_k: int = 5
    window: int = 1200

class FetchReq(BaseModel):
    url: str
    dest: str = DEFAULT_CORPUS
    rebuild: bool = False

@app.post("/index")
def index(req: IndexReq):
    if req.rebuild:
        shutil.rmtree(PERSIST_DIR, ignore_errors=True)
    vm.index(req.path)
    return {"status": "ok", "indexed": os.path.abspath(req.path)}

@app.post("/query")
def query(req: QueryReq):
    hits = vm.query(req.question, top_k=req.top_k, show_sources=True, window=req.window)
    if hits is None:
        raise HTTPException(500, "Query failed")
    return {"hits": hits}

@app.post("/fetch")
def fetch(req: FetchReq):
    if req.rebuild:
        shutil.rmtree(PERSIST_DIR, ignore_errors=True)
    saved = fetch_url(req.url, req.dest)
    vm.index(req.dest)
    return {"saved": str(saved), "indexed": os.path.abspath(req.dest)}

# Serve static UI at /
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
