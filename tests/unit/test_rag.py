import pytest
from app.rag.chunking import DocumentChunker
from app.rag.citations import CitationValidator
from app.rag.retriever import TravelRetriever
from app.services.travel_qa import TravelQAService
from app.schemas.retrieval import QARequest, SourceCitation
from app.schemas.common import GroundingStatus


def test_chunker_preserves_metadata_and_generates_ids():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    sample_text = (
        "Old Goa is home to the Basilica of Bom Jesus, a UNESCO World Heritage site.\n\n"
        "It enshrines the mortal remains of St. Francis Xavier in a silver casket.\n\n"
        "Nearby is Se Cathedral, one of the largest churches in Asia."
    )
    chunks = chunker.chunk_document(
        content=sample_text,
        doc_id="test-doc-01",
        metadata={"destination": "Goa, India", "title": "Old Goa Guide"}
    )

    assert len(chunks) >= 2
    for idx, c in enumerate(chunks):
        assert c.doc_id == "test-doc-01"
        assert c.chunk_id == f"test-doc-01_chunk_{idx}"
        assert c.metadata["title"] == "Old Goa Guide"


def test_citation_validator_filters_hallucinations():
    valid_ids = {"demo-goa-guide-01", "demo-goa-guide-02"}
    claimed = ["demo-goa-guide-01", "hallucinated-doc-99", "fake-website-citation"]

    filtered = CitationValidator.validate_citations(claimed, valid_ids)
    assert filtered == ["demo-goa-guide-01"]
    assert "hallucinated-doc-99" not in filtered


def test_retriever_finds_relevant_chunks():
    retriever = TravelRetriever()
    results = retriever.retrieve("What churches are in Old Goa?", top_k=2)

    assert len(results) > 0
    top_content = results[0].content.lower()
    assert "basilica" in top_content or "church" in top_content or "cathedral" in top_content


def test_qa_service_handles_insufficient_evidence_cleanly():
    qa_service = TravelQAService()
    # Query unrelated to Goa or indexed data
    request = QARequest(
        question="What are the best ski resorts and snowfall depths in the Swiss Alps?",
        destination="Switzerland"
    )
    response = qa_service.answer_question(request)

    assert response.grounding_status == GroundingStatus.INSUFFICIENT_EVIDENCE
    assert len(response.sources) == 0
    assert "does not contain enough verified information" in response.answer
