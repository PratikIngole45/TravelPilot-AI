from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.common import GroundingStatus, CostStatus


class SourceCitation(BaseModel):
    source_id: str = Field(..., description="Unique document/record identifier")
    title: str = Field(..., description="Document or place title")
    url: Optional[str] = Field(None, description="Source URL if available")
    snippet: str = Field(..., description="Relevant text excerpt or summary")
    data_status: str = Field(default="demo_data", description="verified, sourced_estimate, or demo_data")


class QARequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, description="User travel question")
    destination: Optional[str] = Field(None, max_length=100, description="Destination context if applicable")
    conversation_context: Optional[str] = Field(None, max_length=1000, description="Optional previous context")


class QAResponse(BaseModel):
    answer: str = Field(..., description="Evidence-grounded answer")
    sources: List[SourceCitation] = Field(default_factory=list, description="Citations used to formulate answer")
    grounding_status: GroundingStatus = Field(..., description="grounded, partial, or insufficient_evidence")
    warnings: List[str] = Field(default_factory=list, description="Warnings if knowledge base lacks details")


class AttractionRecord(BaseModel):
    id: str
    destination: str
    name: str
    category: str
    description: str
    estimated_duration_minutes: int
    estimated_cost_per_person: Optional[float] = None
    is_per_person_cost: bool = True
    best_time_of_day: str = "morning"  # morning, afternoon, evening
    suitable_for: List[str] = Field(default_factory=list)
    accessibility_features: List[str] = Field(default_factory=list)
    source_id: str
    cost_status: CostStatus = CostStatus.DEMO_DATA


class DestinationSummary(BaseModel):
    destination_id: str
    name: str
    country: str
    description: str
    attraction_count: int
    data_status: str = "demo_data"
