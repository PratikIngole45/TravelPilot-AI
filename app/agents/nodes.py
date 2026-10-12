import uuid
from typing import Dict, Any, List
from datetime import timedelta, date
from app.agents.state import AgentState
from app.agents.tools import TravelAgentTools
from app.schemas.trip import TripPlanRequest
from app.schemas.itinerary import ItineraryResponse, DayPlan, Activity, BudgetSummary
from app.schemas.common import TimeBlock, Pace, BudgetScope
from app.services.budget_calculator import BudgetCalculator
from app.services.itinerary_validator import ItineraryValidator
from app.services.transit_router import TransitRouterService
from app.core.logging import logger
from app.core.config import settings

tools = TravelAgentTools()


def validate_request_node(state: AgentState) -> Dict[str, Any]:
    """Node 1: Validates incoming request schema and sets defaults."""
    req_dict = state["request"]
    req = TripPlanRequest(**req_dict)
    logger.info(f"[Node: validate_request] Destination={req.destination}, duration={req.duration_days}")
    return {
        "request": req.model_dump(),
        "revision_count": 0,
        "validation_errors": [],
        "warnings": []
    }


def retrieve_context_node(state: AgentState) -> Dict[str, Any]:
    """Node 2: Retrieves verified context chunks from vector store."""
    req = TripPlanRequest(**state["request"])
    query = f"{req.destination} {' '.join(req.interests)} travel guide and attractions"
    docs = tools.search_destination_knowledge(query, destination=req.destination)
    logger.info(f"[Node: retrieve_context] Retrieved {len(docs)} documents")
    return {"retrieved_docs": docs}


def query_knowledge_graph_node(state: AgentState) -> Dict[str, Any]:
    """Node 3: Retrieves graph relationships if configured or demo categories."""
    req = TripPlanRequest(**state["request"])
    # If Neo4j enabled, query graph; otherwise return category graph relationships
    graph_context = [
        {"relation": "HAS_ATTRACTION", "destination": req.destination, "category": cat}
        for cat in req.interests
    ]
    return {"graph_context": graph_context}


def select_candidates_node(state: AgentState) -> Dict[str, Any]:
    """Node 4: Ranks candidate attractions using preferences and constraints."""
    req = TripPlanRequest(**state["request"])
    candidates = tools.rec_engine.rank_candidates(req)
    candidate_dicts = [c.model_dump() for c in candidates]
    logger.info(f"[Node: select_candidates] Ranked {len(candidate_dicts)} candidates")
    return {"candidate_attractions": candidate_dicts}


def build_itinerary_node(state: AgentState) -> Dict[str, Any]:
    """Node 5: Builds structured itinerary days and calculates exact budget."""
    req = TripPlanRequest(**state["request"])
    candidates = state["candidate_attractions"]

    if req.pace == Pace.RELAXED:
        acts_per_day = 2
        allowed_blocks = [TimeBlock.MORNING, TimeBlock.AFTERNOON]
    elif req.pace == Pace.PACKED:
        acts_per_day = 3
        allowed_blocks = [TimeBlock.MORNING, TimeBlock.AFTERNOON, TimeBlock.EVENING]
    else:
        acts_per_day = 2
        allowed_blocks = [TimeBlock.MORNING, TimeBlock.AFTERNOON]

    days: List[DayPlan] = []
    idx = 0
    total = len(candidates)
    start_dt = req.start_date

    for day_num in range(1, (req.duration_days or 1) + 1):
        curr_date = (start_dt + timedelta(days=day_num - 1)) if start_dt else None
        day_acts: List[Activity] = []

        for slot_idx in range(acts_per_day):
            if total > 0:
                c = candidates[idx % total]
                idx += 1
                block = allowed_blocks[slot_idx % len(allowed_blocks)]

                reason = f"Matches preference in {c['category']}."
                act = Activity(
                    name=c["name"],
                    category=c["category"],
                    time_block=block,
                    duration_minutes=c["estimated_duration_minutes"],
                    estimated_cost_per_person=c.get("estimated_cost_per_person"),
                    estimated_group_cost=None,
                    cost_status=c.get("cost_status", "demo_data"),
                    reason=reason,
                    source_ids=[c.get("source_id", "demo-doc-01")]
                )
                day_acts.append(act)

        days.append(DayPlan(day_number=day_num, date=curr_date, activities=day_acts))

    # Calculate exact budget in code
    updated_days, summary, b_warnings = BudgetCalculator.compute_itinerary_budget(
        days=days,
        party_size=req.party_size,
        budget_limit=req.budget.amount,
        currency=req.budget.currency
    )

    return {
        "days": [d.model_dump() for d in updated_days],
        "budget_summary": summary.model_dump(),
        "warnings": state.get("warnings", []) + b_warnings
    }


def validate_itinerary_node(state: AgentState) -> Dict[str, Any]:
    """Node 6: Validates hard constraints (schedule, budget, pace, exclusions)."""
    req = TripPlanRequest(**state["request"])
    res = tools.validate_itinerary_constraints(
        days_data=state["days"],
        budget_summary_data=state["budget_summary"],
        pace_str=req.pace.value,
        excluded_activities=req.excluded_activities
    )
    is_valid = res["is_valid"]
    errors = res["errors"]
    warnings = state.get("warnings", []) + res["warnings"]

    logger.info(f"[Node: validate_itinerary] is_valid={is_valid}, errors={len(errors)}")
    return {
        "is_valid": is_valid,
        "validation_errors": errors,
        "warnings": warnings
    }


def revise_plan_node(state: AgentState) -> Dict[str, Any]:
    """Node 7: Bounded repair step if constraints are violated."""
    current_revisions = state["revision_count"] + 1
    logger.info(f"[Node: revise_plan] Repair attempt #{current_revisions}")

    # Remove the most expensive activity or reduce pace
    days_data = state["days"]
    for day in days_data:
        if len(day.get("activities", [])) > 1:
            # Drop last activity of the day to reduce duration/cost
            day["activities"].pop()
            break

    # Recalculate budget
    req = TripPlanRequest(**state["request"])
    day_plans = [DayPlan(**d) for d in days_data]
    updated_days, summary, b_warn = BudgetCalculator.compute_itinerary_budget(
        days=day_plans,
        party_size=req.party_size,
        budget_limit=req.budget.amount,
        currency=req.budget.currency
    )

    return {
        "days": [d.model_dump() for d in updated_days],
        "budget_summary": summary.model_dump(),
        "revision_count": current_revisions,
        "warnings": state.get("warnings", []) + [f"Itinerary adjusted during revision #{current_revisions}"]
    }


def finalize_output_node(state: AgentState) -> Dict[str, Any]:
    """Node 8: Compiles final verified ItineraryResponse."""
    req = TripPlanRequest(**state["request"])
    days = [DayPlan(**d) for d in state["days"]]
    summary = BudgetSummary(**state["budget_summary"])

    assumptions = [
        f"Budget scope: {req.budget.scope.value}. Intercity travel excluded.",
        f"Tempo paced at {req.pace.value} tempo.",
        "Attraction prices and durations are sourced from demonstration knowledge base."
    ]
    all_warnings = list(dict.fromkeys(state.get("warnings", [])))  # Deduplicate

    if state.get("validation_errors"):
        for err in state["validation_errors"]:
            all_warnings.append(f"Constraint notice: {err}")

    transit_guidance = None
    if req.origin_city:
        transit_guidance = TransitRouterService.get_transit_guidance(
            origin_city=req.origin_city,
            destination=req.destination,
            party_size=req.party_size
        )

    response = ItineraryResponse(
        plan_id=f"plan-agent-{uuid.uuid4().hex[:8]}",
        destination=req.destination,
        origin_city=req.origin_city,
        duration_days=req.duration_days or 1,
        currency=req.budget.currency,
        budget_scope=req.budget.scope,
        transit_guidance=transit_guidance,
        days=days,
        budget_summary=summary,
        assumptions=assumptions,
        warnings=all_warnings
    )
    return {"final_itinerary": response.model_dump()}
