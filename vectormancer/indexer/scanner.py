from pathlib import Path
from typing import Iterable, List
import os

DEFAULT_EXCLUDE = {".git", "__pycache__", "node_modules"}
INCLUDE_EXT = {".md", ".txt", ".pdf", ".py", ".json", ".js", ".ts", ".html", ".htm"}  # <- added .html/.htm

def scan_paths(paths: Iterable[Path]) -> List[Path]:
    out = []
    for p in paths:
        p = Path(p).expanduser().resolve()
        if p.is_file():
            if p.suffix.lower() in INCLUDE_EXT:
                out.append(p)
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE]
            for fn in files:
                fp = Path(root) / fn
                if fp.suffix.lower() in INCLUDE_EXT:
                    out.append(fp)
    return out