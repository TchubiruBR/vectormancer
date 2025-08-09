from pathlib import Path

def extract_text(path: Path) -> str:
    # Minimal stub; real impl would branch on suffix and use pypdf / bs4 etc.
    try:
        if path.suffix.lower() in {'.md', '.txt', '.py', '.json', '.js', '.ts'}:
            return path.read_text(encoding='utf-8', errors='ignore')
        if path.suffix.lower() == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            return "\n".join([p.extract_text() or "" for p in reader.pages])
    except Exception as e:
        return f""
    return ""