from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import logging

from ..services.document_loader import load_document
from ..services.chunker import chunk_text
from ..services.embedding_store import EmbeddingStore
from ..services.insight_generator import generate_insights

# Import sanitize_filename from utils (sibling of backend)
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
try:
    from utils.file_utils import sanitize_filename
except ImportError:
    # Fallback if sys.path doesn't work
    def sanitize_filename(name: str) -> str:
        """Fallback: basename and remove unsafe characters."""
        import re
        base = os.path.basename(name)
        return re.sub(r"[^A-Za-z0-9._-]", "_", base)

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def analyze_document(file: UploadFile = File(...)):
    # 1. Validate file type
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )

    # 2. Save uploaded file (sanitize filename to avoid path traversal)
    safe_name = sanitize_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    try:
        with open(file_path, "wb") as buffer:
            file.file.seek(0)
            shutil.copyfileobj(file.file, buffer)
        logger.info("Saved uploaded file %s to %s", safe_name, file_path)
    except Exception as e:
        logger.exception("Failed to save uploaded file %s: %s", safe_name, e)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    # Process the file with guarded steps and clear logging
    try:
        # 3. Load document
        text = load_document(file_path)
        logger.debug("Loaded document %s (length=%d)", safe_name, len(text))

        # 4. Chunk document
        chunks = chunk_text(text)
        if not chunks:
            logger.warning("Document %s produced no chunks", safe_name)
            raise HTTPException(status_code=400, detail="Document is empty or contained no text")

        # 5. Create embedding store and add texts
        store = EmbeddingStore()
        try:
            store.add_texts(chunks)
        except Exception as e:
            logger.exception("Failed to create embeddings for %s: %s", safe_name, e)
            raise HTTPException(status_code=500, detail="Failed to create embeddings")

        # 6. Retrieve top chunks for insights
        retrieved = store.search("key insights and risks", top_k=5)
        retrieved_chunks = [text for text, _ in retrieved]

        if not retrieved_chunks:
            logger.warning("No relevant chunks retrieved for %s", safe_name)

        # 7. Generate structured insights
        try:
            insights = generate_insights(retrieved_chunks)
        except Exception as e:
            logger.exception("Insight generation failed for %s: %s", safe_name, e)
            raise HTTPException(status_code=500, detail="Insight generation failed")

        return {
            "filename": safe_name,
            "num_chunks": len(chunks),
            "insights": insights
        }

    except HTTPException:
        # Re-raise HTTPExceptions so FastAPI can handle them
        raise
    except Exception as e:
        logger.exception("Unexpected error analyzing %s: %s", safe_name, e)
        raise HTTPException(status_code=500, detail="Unexpected server error")
