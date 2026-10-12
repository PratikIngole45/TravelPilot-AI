import pytest
from app.schemas.itinerary import DayPlan, Activity
from app.schemas.common import TimeBlock, CostStatus
from app.services.budget_calculator import BudgetCalculator


def test_budget_calculator_exact_totals_for_group():
    # 2 activities, party of 3:
    # Act 1: 150.00 * 3 = 450.00
    # Act 2: 250.50 * 3 = 751.50
    # Total = 1201.50
    act1 = Activity(
        name="Heritage Walk",
        category="history",
        time_block=TimeBlock.MORNING,
        duration_minutes=90,
        estimated_cost_per_person=150.0,
        reason="Cultural",
        source_ids=["src-1"]
    )
    act2 = Activity(
        name="Spice Plantation Tour",
        category="local_food",
        time_block=TimeBlock.AFTERNOON,
        duration_minutes=120,
        estimated_cost_per_person=250.5,
        reason="Food",
        source_ids=["src-2"]
    )
    day = DayPlan(day_number=1, activities=[act1, act2])

    days, summary, warnings = BudgetCalculator.compute_itinerary_budget(
        days=[day],
        party_size=3,
        budget_limit=2000.0,
        currency="INR"
    )

    assert summary.known_estimated_total == 1201.5
    assert summary.remaining_budget == 798.5
    assert summary.cost_completeness == "complete"
    assert not summary.is_over_budget
    assert len(warnings) == 0


def test_budget_calculator_over_budget_flag():
    act = Activity(
        name="Private Yacht Cruise",
        category="leisure",
        time_block=TimeBlock.EVENING,
        duration_minutes=180,
        estimated_cost_per_person=5000.0,
        reason="Luxury",
        source_ids=["src-yacht"]
    )
    day = DayPlan(day_number=1, activities=[act])

    days, summary, warnings = BudgetCalculator.compute_itinerary_budget(
        days=[day],
        party_size=2,
        budget_limit=8000.0,
        currency="INR"
    )

    # 5000 * 2 = 10,000 > 8,000
    assert summary.known_estimated_total == 10000.0
    assert summary.remaining_budget == -2000.0
    assert summary.is_over_budget is True
    assert any("exceeds budget limit" in w for w in warnings)


def test_budget_calculator_unknown_cost_handling():
    # Unknown cost must remain None and not count as 0
    act_known = Activity(
        name="Museum Visit",
        category="history",
        time_block=TimeBlock.MORNING,
        duration_minutes=60,
        estimated_cost_per_person=100.0,
        reason="History",
        source_ids=["src-3"]
    )
    act_unknown = Activity(
        name="Local Village Walk",
        category="nature",
        time_block=TimeBlock.AFTERNOON,
        duration_minutes=90,
        estimated_cost_per_person=None,
        cost_status=CostStatus.UNKNOWN,
        reason="Explore",
        source_ids=[]
    )
    day = DayPlan(day_number=1, activities=[act_known, act_unknown])

    days, summary, warnings = BudgetCalculator.compute_itinerary_budget(
        days=[day],
        party_size=2,
        budget_limit=500.0,
        currency="INR"
    )

    assert summary.known_estimated_total == 200.0
    assert summary.cost_completeness == "partial"
    assert any("unknown pricing" in w for w in warnings)
    assert act_unknown.estimated_group_cost is None
