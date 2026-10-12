import pytest
from app.schemas.itinerary import DayPlan, Activity, BudgetSummary
from app.schemas.common import TimeBlock, Pace
from app.services.itinerary_validator import ItineraryValidator


def test_validator_detects_duplicate_activities():
    act1 = Activity(
        name="Fort Aguada",
        category="history",
        time_block=TimeBlock.MORNING,
        duration_minutes=90,
        estimated_cost_per_person=50.0,
        reason="Test",
        source_ids=[]
    )
    act2 = Activity(
        name="Fort Aguada",  # Duplicate!
        category="history",
        time_block=TimeBlock.AFTERNOON,
        duration_minutes=90,
        estimated_cost_per_person=50.0,
        reason="Test duplicate",
        source_ids=[]
    )
    days = [DayPlan(day_number=1, activities=[act1, act2])]
    summary = BudgetSummary(
        known_estimated_total=100.0,
        budget_limit=1000.0,
        currency="INR",
        remaining_budget=900.0,
        cost_completeness="complete",
        is_over_budget=False
    )

    is_valid, errors, warnings = ItineraryValidator.validate_itinerary_constraints(
        days=days,
        budget_summary=summary,
        pace=Pace.BALANCED
    )

    assert is_valid is False
    assert any("Duplicate activity" in err for err in errors)


def test_validator_detects_excluded_activity():
    act = Activity(
        name="Club Cabana Nightclub",
        category="nightlife",
        time_block=TimeBlock.EVENING,
        duration_minutes=120,
        estimated_cost_per_person=1000.0,
        reason="Clubbing",
        source_ids=[]
    )
    days = [DayPlan(day_number=1, activities=[act])]
    summary = BudgetSummary(
        known_estimated_total=1000.0,
        budget_limit=5000.0,
        currency="INR",
        remaining_budget=4000.0,
        cost_completeness="complete",
        is_over_budget=False
    )

    is_valid, errors, warnings = ItineraryValidator.validate_itinerary_constraints(
        days=days,
        budget_summary=summary,
        pace=Pace.BALANCED,
        excluded_activities=["nightclub", "casinos"]
    )

    assert is_valid is False
    assert any("Excluded activity violation" in err for err in errors)


def test_validator_detects_excessive_duration_for_relaxed_pace():
    # Relaxed pace max is 360 mins (6h). Let's schedule 400 mins.
    act = Activity(
        name="Full Day Jungle Safari",
        category="nature",
        time_block=TimeBlock.MORNING,
        duration_minutes=420,
        estimated_cost_per_person=800.0,
        reason="Long excursion",
        source_ids=[]
    )
    days = [DayPlan(day_number=1, activities=[act])]
    summary = BudgetSummary(
        known_estimated_total=800.0,
        budget_limit=5000.0,
        currency="INR",
        remaining_budget=4200.0,
        cost_completeness="complete",
        is_over_budget=False
    )

    is_valid, errors, warnings = ItineraryValidator.validate_itinerary_constraints(
        days=days,
        budget_summary=summary,
        pace=Pace.RELAXED
    )

    assert is_valid is False
    assert any("exceeds maximum pace limit" in err for err in errors)
