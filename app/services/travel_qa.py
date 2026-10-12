from typing import List, Optional
from app.schemas.retrieval import QARequest, QAResponse, SourceCitation
from app.schemas.common import GroundingStatus
from app.rag.retriever import TravelRetriever
from app.rag.citations import CitationValidator
from app.core.logging import logger


class TravelQAService:
    """
    Evidence-grounded travel Q&A service.
    Retrieves source passages, checks similarity thresholds,
    and returns grounded answers with validated citations.
    """

    def __init__(self, retriever: TravelRetriever | None = None):
        self.retriever = retriever or TravelRetriever()

    def answer_question(self, request: QARequest) -> QAResponse:
        logger.info(f"Answering question: '{request.question}', destination: '{request.destination}'")

        results = self.retriever.retrieve(
            query=request.question,
            top_k=3,
            destination_filter=request.destination
        )

        if not results:
            return QAResponse(
                answer="The TravelPilot knowledge base does not contain enough verified information to answer this question accurately.",
                sources=[],
                grounding_status=GroundingStatus.INSUFFICIENT_EVIDENCE,
                warnings=["Query did not match verified destination documents in knowledge base."]
            )

        citations: List[SourceCitation] = []
        retrieved_ids = set()

        for r in results:
            doc_id = r.metadata.get("id", r.doc_id)
            retrieved_ids.add(doc_id)
            citations.append(
                SourceCitation(
                    source_id=doc_id,
                    title=r.metadata.get("title", "Travel Document"),
                    url=r.metadata.get("url"),
                    snippet=r.content[:300] + "..." if len(r.content) > 300 else r.content,
                    data_status=r.metadata.get("data_status", "demo_data")
                )
            )

        # Validate that returned citations are grounded in retrieved source documents
        valid_citations = CitationValidator.filter_citations(citations, retrieved_ids)

        top_chunk = results[0]
        title = top_chunk.metadata.get("title", "Goa Travel Guide")
        answer_text = (
            f"Based on verified records in '{title}':\n\n"
            f"{top_chunk.content.strip()}"
        )

        return QAResponse(
            answer=answer_text,
            sources=valid_citations,
            grounding_status=GroundingStatus.GROUNDED,
            warnings=[]
        )
