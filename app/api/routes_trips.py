from fastapi import APIRouter, HTTPException
from app.schemas.trip import TripPlanRequest
from app.schemas.itinerary import ItineraryResponse
from app.services.trip_planner import TripPlannerService
from app.agents.graph import build_travel_agent_graph
from app.core.exceptions import TravelPilotException
from app.core.logging import logger

router = APIRouter(prefix="/api/v1/trips", tags=["Trips"])
planner_service = TripPlannerService()
agent_graph = build_travel_agent_graph()


@router.post("/plan", response_model=ItineraryResponse)
def plan_trip(request: TripPlanRequest):
    """
    Generate a validated, multi-day, budget-aware itinerary based on user preferences
    using the bounded LangGraph agent workflow with deterministic constraint validation.
    """
    try:
        # Execute LangGraph Agent State Workflow
        initial_state = {
            "request": request.model_dump(),
            "retrieved_docs": [],
            "candidate_attractions": [],
            "graph_context": [],
            "days": [],
            "budget_summary": None,
            "validation_errors": [],
            "warnings": [],
            "revision_count": 0,
            "is_valid": False,
            "final_itinerary": None
        }
        
        final_state = agent_graph.invoke(initial_state)
        if final_state.get("final_itinerary"):
            return ItineraryResponse(**final_state["final_itinerary"])

        # Fallback to direct deterministic service
        logger.warning("Agent graph produced no final itinerary, using fallback planner")
        return planner_service.plan_trip(request)
        
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except TravelPilotException as te:
        raise HTTPException(status_code=400, detail={"message": te.message, "details": te.details})
    except Exception as e:
        logger.error(f"Error in trip planning endpoint: {e}")
        # Fallback to direct planner if graph had any unexpected failure
        try:
            return planner_service.plan_trip(request)
        except Exception as inner_e:
            raise HTTPException(status_code=500, detail=f"Planning service error: {str(inner_e)}")
