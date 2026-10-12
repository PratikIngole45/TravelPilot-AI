from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """
    Explicit typed state schema for the LangGraph agent workflow.
    """
    request: Dict[str, Any]
    retrieved_docs: List[Dict[str, Any]]
    candidate_attractions: List[Dict[str, Any]]
    graph_context: List[Dict[str, Any]]
    days: List[Dict[str, Any]]
    budget_summary: Optional[Dict[str, Any]]
    validation_errors: List[str]
    warnings: List[str]
    revision_count: int
    is_valid: bool
    final_itinerary: Optional[Dict[str, Any]]
