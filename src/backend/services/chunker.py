import re
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks for embeddings or analysis.
    
    Args:
        text: The input document text.
        chunk_size: Number of characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    # 1. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 2. Create chunks
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:  # skip empty chunks
            chunks.append(chunk)
        start += chunk_size - overlap
    
    return chunks
