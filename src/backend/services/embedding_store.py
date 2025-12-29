# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from typing import List, Tuple


# class EmbeddingStore:
#     """Simple embedding store using SentenceTransformers + FAISS.

#     This class is intentionally minimal and suitable for tests and small datasets.
#     """

#     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
#         import logging
#         self.logger = logging.getLogger(__name__)
#         self.model = SentenceTransformer(model_name)
#         self.dim = self.model.get_sentence_embedding_dimension()
#         # Flat L2 index for simplicity (no persistence here)
#         self.index = faiss.IndexFlatL2(self.dim)
#         self.texts: List[str] = []

#     def add_texts(self, texts: List[str]) -> None:
#         if not texts:
#             self.logger.debug("No texts provided to add_texts; skipping.")
#             return
#         try:
#             embs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
#             embs = embs.astype("float32")
#             self.index.add(embs)
#             self.texts.extend(texts)
#             self.logger.debug("Added %d texts to the index", len(texts))
#         except Exception as e:
#             self.logger.exception("Error creating embeddings: %s", e)
#             raise RuntimeError("Failed to create embeddings") from e

#     def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
#         try:
#             q_emb = self.model.encode([query], convert_to_numpy=True).astype("float32")
#         except Exception as e:
#             self.logger.exception("Failed to create query embedding: %s", e)
#             return []

#         if self.index.ntotal == 0:
#             self.logger.debug("Index is empty; returning no results")
#             return []

#         try:
#             distances, indices = self.index.search(q_emb, top_k)
#             results: List[Tuple[str, float]] = []
#             for dist, idx in zip(distances[0], indices[0]):
#                 if idx < len(self.texts):
#                     results.append((self.texts[idx], float(dist)))
#             self.logger.debug("Search returned %d results for query '%s'", len(results), query)
#             return results
#         except Exception as e:
#             self.logger.exception("FAISS search failed: %s", e)
#             return []

# if __name__ == "__main__":
#     # Demo / test block — guarded so imports won't execute this on module import
#     store = EmbeddingStore()

#     # Example chunks (replace with your actual chunks or call store.add_texts from elsewhere)
#     chunks = [
#         "This is a sample document used by tests.",
#         "It contains a few lines of text to verify the document loader and chunker.",
#         "The quick brown fox jumps over the lazy dog."
#     ]

#     store.add_texts(chunks)

#     # Test search
#     query = "risk factors"
#     results = store.search(query, top_k=3)

#     print("Search results for query:", query)
#     for text, distance in results:
#         print(f"Distance: {distance:.4f}, Text: {text[:100]}...")
import faiss
import numpy as np
from typing import List, Tuple
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# 🔒 Load ONCE (prevents HuggingFace retries)
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

