import pytest
from decimal import Decimal
from app.services.transit_router import TransitRouterService
from app.schemas.itinerary import TransitGuidance


def test_transit_guidance_mumbai_goa():
    guidance = TransitRouterService.get_transit_guidance("Mumbai", "Goa, India", party_size=2)
    assert guidance is not None
    assert isinstance(guidance, TransitGuidance)
    assert guidance.origin_city == "Mumbai"
    assert guidance.approximate_distance_km == 590
    assert len(guidance.options) >= 3

    # Check modes
    modes = [opt.mode for opt in guidance.options]
    assert "air" in modes
    assert "train" in modes
    assert "road_bus" in modes
    assert "cab" in modes

    # Check group calculation for 2 travelers
    for opt in guidance.options:
        if opt.mode == "cab":
            # For 2 people, 1 vehicle is needed: group cost = cost_pp * 1
            assert opt.estimated_group_cost == opt.estimated_cost_per_person
        else:
            # For 2 people, per person * 2
            assert opt.estimated_group_cost == opt.estimated_cost_per_person * 2


def test_transit_guidance_delhi_shimla():
    # User specific scenario: Delhi to Shimla
    guidance = TransitRouterService.get_transit_guidance("Delhi", "Shimla, India", party_size=4)
    assert guidance is not None
    assert guidance.approximate_distance_km == 350
    assert "Toy Train" in guidance.recommended_mode or "Volvo Bus" in guidance.recommended_mode

    # Check Toy Train route mentioned
    train_opts = [opt for opt in guidance.options if opt.mode == "train"]
    assert len(train_opts) > 0
    assert "Kalka" in train_opts[0].route_summary

    # Check advisories mention snow or monsoon
    advisories_str = " ".join(guidance.weather_or_seasonal_advisories)
    assert "snow" in advisories_str.lower() or "monsoon" in advisories_str.lower()


def test_transit_guidance_empty_origin():
    guidance = TransitRouterService.get_transit_guidance("", "Goa, India", party_size=2)
    assert guidance is None

    guidance_none = TransitRouterService.get_transit_guidance(None, "Goa, India", party_size=2)
    assert guidance_none is None


def test_transit_guidance_unmapped_fallback():
    guidance = TransitRouterService.get_transit_guidance("Hyderabad", "Kochi", party_size=3)
    assert guidance is not None
    assert guidance.origin_city == "Hyderabad"
    assert guidance.destination == "Kochi"
    assert len(guidance.options) >= 2
    assert guidance.options[0].estimated_group_cost == guidance.options[0].estimated_cost_per_person * 3
