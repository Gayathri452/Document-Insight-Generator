import os
try:
    # Prefer pypdf (actively maintained). Fall back to PyPDF2 if pypdf is not installed.
    from pypdf import PdfReader  # type: ignore
except Exception:
    from PyPDF2 import PdfReader  # type: ignore


import logging


def load_pdf(file_path: str) -> str:
    """
    Load text from a PDF file.
    """
    logger = logging.getLogger(__name__)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            # extract_text() is available in both pypdf and PyPDF2
            extracted = page.extract_text() or ""
            text += extracted
    logger.debug("Loaded PDF %s (length=%d)", file_path, len(text))
    return text


def load_txt(file_path: str) -> str:
    """
    Load text from a TXT file safely (ignore bad bytes).
    """
    logger = logging.getLogger(__name__)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()
    logger.debug("Loaded TXT %s (length=%d)", file_path, len(data))
    return data

def load_document(file_path: str) -> str:
    """
    Detect file type and load content.
    """
    if file_path.lower().endswith(".pdf"):
        return load_pdf(file_path)
    elif file_path.lower().endswith(".txt"):
        return load_txt(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and TXT are supported.")
