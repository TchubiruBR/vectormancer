from pathlib import Path

# old:
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
    
from pathlib import Path

def _extract_pdf_text_native(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        return "\n".join([(p.extract_text() or "") for p in reader.pages]).strip()
    except Exception:
        return ""

def _extract_pdf_text_ocr(pdf_path: Path) -> str:
    # Requires: apt install tesseract-ocr poppler-utils ; pip install pdf2image pytesseract
    try:
        from pdf2image import convert_from_path
        import pytesseract
        pages = convert_from_path(str(pdf_path), dpi=300)
        out = []
        for img in pages:
            out.append(pytesseract.image_to_string(img))
        return "\n".join(out).strip()
    except Exception:
        return ""

def extract_text(path: Path, enable_ocr: bool = True) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix in {".md", ".txt", ".py", ".json", ".js", ".ts"}:
            return path.read_text(encoding="utf-8", errors="ignore")

        if suffix == ".pdf":
            txt = _extract_pdf_text_native(path)
            if (not txt.strip()) and enable_ocr:
                # Image-only PDF -> OCR fallback
                txt = _extract_pdf_text_ocr(path)
            return txt
    except Exception:
        return ""
    return ""


#### test ####
from pathlib import Path

def _extract_pdf_text_pdfplumber(pdf_path: Path) -> str:
    try:
        import pdfplumber
        text = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for p in pdf.pages:
                text.append(p.extract_text() or "")
        return "\n".join(text).strip()
    except Exception:
        return ""

def _extract_pdf_text_ocr(pdf_path: Path) -> str:
    # OCR fallback for scanned PDFs
    try:
        from pdf2image import convert_from_path
        import pytesseract
        pages = convert_from_path(str(pdf_path), dpi=300)
        out = []
        for img in pages:
            out.append(pytesseract.image_to_string(img))
        return "\n".join(out).strip()
    except Exception:
        return ""

def extract_text(path: Path, enable_ocr: bool = True) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix in {".md", ".txt", ".py", ".json", ".js", ".ts"}:
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".pdf":
            txt = _extract_pdf_text_pdfplumber(path)
            if not txt and enable_ocr:
                txt = _extract_pdf_text_ocr(path)
            return txt
    except Exception:
        return ""
    return ""
