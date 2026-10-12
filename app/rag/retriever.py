from typing import List, Optional
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore
from app.rag.chunking import DocumentChunk
from app.core.logging import logger


class TravelRetriever:
    """
    Retriever for vector similarity search with metadata filtering and minimum score threshold.
    """

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedding_generator: EmbeddingGenerator | None = None,
        min_similarity_threshold: float = 0.38
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.min_similarity_threshold = min_similarity_threshold

        # Try auto-loading index
        if not self.vector_store.chunks:
            self.vector_store.load()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        destination_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[DocumentChunk]:
        if not self.vector_store.chunks:
            logger.warning("VectorStore is empty during retrieve call")
            return []

        query_vec = self.embedding_generator.encode_query(query)
        # Retrieve extra to allow filtering
        search_k = top_k * 3
        raw_results = self.vector_store.search(query_vec, top_k=search_k)

        filtered: List[DocumentChunk] = []
        for chunk, score in raw_results:
            if score < self.min_similarity_threshold:
                continue

            # Destination check
            if destination_filter:
                chunk_dest = chunk.metadata.get("destination", "").lower()
                if destination_filter.lower() not in chunk_dest and chunk_dest not in destination_filter.lower():
                    continue

            # Category check
            if category_filter:
                chunk_cat = chunk.metadata.get("category", "").lower()
                if category_filter.lower() != chunk_cat:
                    continue

            filtered.append(chunk)
            if len(filtered) >= top_k:
                break

        return filtered
