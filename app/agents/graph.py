from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.nodes import (
    validate_request_node,
    retrieve_context_node,
    query_knowledge_graph_node,
    select_candidates_node,
    build_itinerary_node,
    validate_itinerary_node,
    revise_plan_node,
    finalize_output_node
)
from app.core.config import settings


def should_revise_or_finalize(state: AgentState) -> str:
    """
    Conditional edge evaluator:
    - If valid, proceed to finalize.
    - If invalid and retries remain, attempt revision.
    - If invalid and retries exhausted, finalize with warnings.
    """
    if state["is_valid"]:
        return "finalize"
    if state["revision_count"] < settings.MAX_AGENT_REVISIONS:
        return "revise"
    return "finalize"


def build_travel_agent_graph():
    """
    Compiles the LangGraph bounded travel planning agent state graph.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("validate_request", validate_request_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("query_knowledge_graph", query_knowledge_graph_node)
    workflow.add_node("select_candidates", select_candidates_node)
    workflow.add_node("build_itinerary", build_itinerary_node)
    workflow.add_node("validate_itinerary", validate_itinerary_node)
    workflow.add_node("revise_plan", revise_plan_node)
    workflow.add_node("finalize_output", finalize_output_node)

    # Add Edges
    workflow.add_edge(START, "validate_request")
    workflow.add_edge("validate_request", "retrieve_context")
    workflow.add_edge("retrieve_context", "query_knowledge_graph")
    workflow.add_edge("query_knowledge_graph", "select_candidates")
    workflow.add_edge("select_candidates", "build_itinerary")
    workflow.add_edge("build_itinerary", "validate_itinerary")

    # Conditional branching
    workflow.add_conditional_edges(
        "validate_itinerary",
        should_revise_or_finalize,
        {
            "finalize": "finalize_output",
            "revise": "revise_plan"
        }
    )

    # Revision leads back to validation
    workflow.add_edge("revise_plan", "validate_itinerary")
    workflow.add_edge("finalize_output", END)

    return workflow.compile()
