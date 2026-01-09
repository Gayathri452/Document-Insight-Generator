import faiss
import numpy as np
from typing import List, Tuple
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Load ONCE (prevents HuggingFace retries)
try:
    EMBEDDING_MODEL = SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu",
        local_files_only=True
    )
except Exception as e:
    logger.exception("Failed to load embedding model")
    raise RuntimeError("Embedding model could not be loaded") from e


class EmbeddingStore:
    """Simple embedding store using SentenceTransformers + FAISS."""

    def __init__(self):
        self.logger = logger
        self.model = EMBEDDING_MODEL
        self.dim = self.model.get_sentence_embedding_dimension()

        self.index = faiss.IndexFlatL2(self.dim)
        self.texts: List[str] = []

    def add_texts(self, texts: List[str]) -> None:
        if not texts:
            return

        try:
            embs = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False
            ).astype("float32")

            self.index.add(embs)
            self.texts.extend(texts)

        except Exception:
            self.logger.exception("Error creating embeddings")
            raise RuntimeError("Failed to create embeddings")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if self.index.ntotal == 0:
            return []

        try:
            q_emb = self.model.encode([query], convert_to_numpy=True).astype("float32")
            distances, indices = self.index.search(q_emb, top_k)

            return [
                (self.texts[idx], float(dist))
                for dist, idx in zip(distances[0], indices[0])
                if idx < len(self.texts)
            ]

        except Exception:
            self.logger.exception("FAISS search failed")
            return []

