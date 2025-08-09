def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120):
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = max(start + chunk_size - overlap, end)
    return chunks