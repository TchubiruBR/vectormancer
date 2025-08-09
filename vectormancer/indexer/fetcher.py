from __future__ import annotations
import os, re, hashlib
from pathlib import Path
from urllib.parse import urlparse
import requests

def _safe_name_from_url(url: str, fallback_ext: str) -> str:
    parsed = urlparse(url)
    tail = os.path.basename(parsed.path) or ""
    if not tail:
        tail = "download"
    # strip query
    tail = tail.split("?")[0].split("#")[0]
    # ensure extension
    if "." not in tail:
        tail += fallback_ext
    # extra safety
    tail = re.sub(r"[^A-Za-z0-9._-]+", "_", tail)
    return tail

def fetch_url(url: str, dest_dir: str | Path) -> Path:
    dest = Path(dest_dir).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)

    # stream to avoid huge memory
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()

    ctype = r.headers.get("content-type", "").lower()
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        fname = _safe_name_from_url(url, ".pdf")
    elif "html" in ctype or url.lower().endswith((".html", ".htm")):
        fname = _safe_name_from_url(url, ".html")
    else:
        # generic text or unknown -> save as .txt (still indexable)
        fname = _safe_name_from_url(url, ".txt")

    # avoid collisions: append short hash if file exists
    target = dest / fname
    if target.exists():
        h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
        stem = target.stem
        ext = target.suffix
        target = dest / f"{stem}-{h}{ext}"

    with open(target, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 14):
            if chunk:
                f.write(chunk)

    return target

