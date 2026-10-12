import os
import re
from typing import List, Dict, Any
from app.rag.chunking import DocumentChunker, DocumentChunk
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore
from app.core.logging import logger


class DocumentIngestionPipeline:
    """
    Ingests raw travel documents, extracts frontmatter, chunks content,
    generates embeddings, and stores them in the vector index.
    """

    def __init__(
        self,
        raw_dir: str = "data/raw",
        processed_dir: str = "data/processed/vector_index",
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore(index_dir=processed_dir)

    def _parse_frontmatter(self, file_content: str) -> tuple[Dict[str, Any], str]:
        """
        Parses YAML-style frontmatter headers between --- markers.
        """
        metadata: Dict[str, Any] = {}
        content = file_content

        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", file_content, re.DOTALL)
        if frontmatter_match:
            header_text = frontmatter_match.group(1)
            content = frontmatter_match.group(2)
            for line in header_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    metadata[key.strip()] = val.strip()

        return metadata, content

    def run_ingestion(self) -> int:
        if not os.path.exists(self.raw_dir):
            logger.warning(f"Raw documents directory '{self.raw_dir}' does not exist.")
            return 0

        all_chunks: List[DocumentChunk] = []

        for filename in sorted(os.listdir(self.raw_dir)):
            if not (filename.endswith(".md") or filename.endswith(".txt")):
                continue

            filepath = os.path.join(self.raw_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            metadata, body = self._parse_frontmatter(raw_text)
            doc_id = metadata.get("id", os.path.splitext(filename)[0])
            metadata["filename"] = filename

            chunks = self.chunker.chunk_document(body, doc_id=doc_id, metadata=metadata)
            all_chunks.extend(chunks)
            logger.info(f"Parsed '{filename}': {len(chunks)} chunks created.")

        if not all_chunks:
            logger.warning("No chunks generated from raw documents.")
            return 0

        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
        texts = [chunk.content for chunk in all_chunks]
        embeddings = self.embedder.encode(texts)

        logger.info("Building vector index...")
        self.vector_store.build_index(all_chunks, embeddings)
        self.vector_store.save()
        logger.info("Ingestion complete.")
        return len(all_chunks)
