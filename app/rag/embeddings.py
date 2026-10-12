from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging import logger


class EmbeddingGenerator:
    """
    Embedding generator using SentenceTransformers with normalized vectors.
    """

    _model = None

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL

    def _get_model(self) -> SentenceTransformer:
        if EmbeddingGenerator._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                # Prefer local cached files to avoid network latency and rate limits
                EmbeddingGenerator._model = SentenceTransformer(self.model_name, local_files_only=True)
            except Exception:
                EmbeddingGenerator._model = SentenceTransformer(self.model_name)
        return EmbeddingGenerator._model

    def encode(self, texts: List[str]) -> np.ndarray:
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # Normalize to unit length for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        normalized = embeddings / norms
        return normalized.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        return self.encode([query])[0]
