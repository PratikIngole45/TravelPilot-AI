import re
from typing import List, Dict, Any
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    content: str
    metadata: Dict[str, Any]


class DocumentChunker:
    """
    Splits documents into overlapping chunks while preserving metadata and heading context.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, content: str, doc_id: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        cleaned_text = content.strip()

        if len(cleaned_text) <= self.chunk_size:
            chunk = DocumentChunk(
                chunk_id=f"{doc_id}_chunk_0",
                doc_id=doc_id,
                content=cleaned_text,
                metadata=metadata
            )
            return [chunk]

        # Break text into paragraphs or sentences
        paragraphs = re.split(r"\n\s*\n", cleaned_text)
        current_chunk_parts: List[str] = []
        current_len = 0
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_len = len(para)
            if current_len + para_len > self.chunk_size and current_chunk_parts:
                chunk_text = "\n\n".join(current_chunk_parts)
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc_id}_chunk_{chunk_idx}",
                        doc_id=doc_id,
                        content=chunk_text,
                        metadata=metadata
                    )
                )
                chunk_idx += 1
                
                # Keep overlap if possible
                overlap_text = current_chunk_parts[-1] if len(current_chunk_parts[-1]) <= self.chunk_overlap else ""
                current_chunk_parts = [overlap_text, para] if overlap_text else [para]
                current_len = sum(len(p) for p in current_chunk_parts)
            else:
                current_chunk_parts.append(para)
                current_len += para_len

        if current_chunk_parts:
            chunk_text = "\n\n".join(current_chunk_parts)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc_id}_chunk_{chunk_idx}",
                    doc_id=doc_id,
                    content=chunk_text,
                    metadata=metadata
                )
            )

        return chunks
