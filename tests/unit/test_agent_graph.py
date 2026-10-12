import pytest
from app.agents.graph import build_travel_agent_graph
from app.schemas.trip import TripPlanRequest
from app.schemas.itinerary import ItineraryResponse


def test_agent_graph_compiles_and_executes_end_to_end():
    graph = build_travel_agent_graph()

    request_payload = {
        "destination": "Goa, India",
        "duration_days": 2,
        "party_size": 2,
        "budget": {
            "amount": 10000,
            "currency": "INR",
            "scope": "local_trip_only"
        },
        "interests": ["beaches", "history"],
        "pace": "relaxed",
        "traveller_profile": "couple",
        "excluded_activities": []
    }

    initial_state = {
        "request": request_payload,
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

    final_state = graph.invoke(initial_state)

    assert "final_itinerary" in final_state
    assert final_state["final_itinerary"] is not None

    itinerary = ItineraryResponse(**final_state["final_itinerary"])
    assert itinerary.destination == "Goa, India"
    assert len(itinerary.days) == 2
    assert itinerary.budget_summary.known_estimated_total > 0
    assert itinerary.budget_summary.budget_limit == 10000


def test_agent_graph_bounded_repair_on_tight_budget():
    graph = build_travel_agent_graph()

    # Extremely low budget of ₹200 for 2 days to trigger budget constraint violation & repair
    request_payload = {
        "destination": "Goa, India",
        "duration_days": 2,
        "party_size": 2,
        "budget": {
            "amount": 200,
            "currency": "INR",
            "scope": "local_trip_only"
        },
        "interests": ["history"],
        "pace": "relaxed",
        "excluded_activities": []
    }

    initial_state = {
        "request": request_payload,
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

    final_state = graph.invoke(initial_state)

    # Must complete and not loop indefinitely
    assert final_state["final_itinerary"] is not None
    itinerary = ItineraryResponse(**final_state["final_itinerary"])
    assert itinerary.budget_summary.budget_limit == 200
    assert any("revision" in w.lower() or "budget" in w.lower() for w in itinerary.warnings)
