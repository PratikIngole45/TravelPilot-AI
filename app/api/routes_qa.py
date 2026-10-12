from fastapi import APIRouter
from app.schemas.retrieval import QARequest, QAResponse, SourceCitation
from app.schemas.common import GroundingStatus

router = APIRouter(prefix="/api/v1/qa", tags=["Q&A"])


@router.post("", response_model=QAResponse)
def answer_travel_question(request: QARequest):
    """
    Evidence-grounded travel question answering endpoint.
    Will invoke RAG retriever and citation validation.
    """
    # Baseline handler before RAG service is instantiated
    from app.services.travel_qa import TravelQAService
    qa_service = TravelQAService()
    return qa_service.answer_question(request)
