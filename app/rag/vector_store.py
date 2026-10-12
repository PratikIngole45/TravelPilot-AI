import os
import json
from typing import List, Tuple, Dict, Any
import numpy as np
from app.rag.chunking import DocumentChunk
from app.core.logging import logger

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


class VectorStore:
    """
    Lightweight vector store supporting FAISS IndexFlatIP with automatic
    numpy Cosine-Similarity fallback.
    """

    def __init__(self, index_dir: str = "data/processed/vector_index"):
        self.index_dir = index_dir
        self.chunks: List[DocumentChunk] = []
        self.embeddings: np.ndarray | None = None
        self.faiss_index = None
        self.dimension: int = 384

    def build_index(self, chunks: List[DocumentChunk], embeddings: np.ndarray):
        self.chunks = chunks
        self.embeddings = embeddings.astype(np.float32)
        self.dimension = embeddings.shape[1]

        if HAS_FAISS:
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
            self.faiss_index.add(self.embeddings)
            logger.info(f"Built FAISS IndexFlatIP with {len(chunks)} vectors of dim {self.dimension}")
        else:
            logger.info(f"Built NumPy vector store with {len(chunks)} vectors of dim {self.dimension}")

    def save(self):
        os.makedirs(self.index_dir, exist_ok=True)
        # Save chunks metadata
        chunks_data = [chunk.model_dump() for chunk in self.chunks]
        with open(os.path.join(self.index_dir, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

        # Save embeddings
        if self.embeddings is not None:
            np.save(os.path.join(self.index_dir, "embeddings.npy"), self.embeddings)

        # Save FAISS index
        if HAS_FAISS and self.faiss_index is not None:
            faiss.write_index(self.faiss_index, os.path.join(self.index_dir, "index.faiss"))

        logger.info(f"Saved VectorStore index to {self.index_dir}")

    def load(self) -> bool:
        chunks_file = os.path.join(self.index_dir, "chunks.json")
        embeddings_file = os.path.join(self.index_dir, "embeddings.npy")
        faiss_file = os.path.join(self.index_dir, "index.faiss")

        if not os.path.exists(chunks_file):
            logger.warning(f"No vector store chunks found at {chunks_file}")
            return False

        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)
            self.chunks = [DocumentChunk(**c) for c in chunks_data]

        if os.path.exists(embeddings_file):
            self.embeddings = np.load(embeddings_file)
            self.dimension = self.embeddings.shape[1]

        if HAS_FAISS and os.path.exists(faiss_file):
            self.faiss_index = faiss.read_index(faiss_file)
        elif self.embeddings is not None and HAS_FAISS:
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
            self.faiss_index.add(self.embeddings)

        logger.info(f"Loaded VectorStore with {len(self.chunks)} items from {self.index_dir}")
        return True

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        if not self.chunks:
            return []

        query = query_vector.reshape(1, -1).astype(np.float32)

        if HAS_FAISS and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(query, min(top_k, len(self.chunks)))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.chunks):
                    results.append((self.chunks[idx], float(score)))
            return results

        # NumPy fallback
        if self.embeddings is not None:
            similarities = np.dot(self.embeddings, query.T).flatten()
            top_indices = np.argsort(similarities)[::-1][:top_k]
            results = [(self.chunks[idx], float(similarities[idx])) for idx in top_indices]
            return results

        return []
