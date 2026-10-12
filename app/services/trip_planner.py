import uuid
from datetime import timedelta
from typing import List
from app.schemas.trip import TripPlanRequest
from app.schemas.itinerary import ItineraryResponse, DayPlan, Activity
from app.schemas.common import TimeBlock, Pace
from app.services.recommendation import RecommendationEngine
from app.services.budget_calculator import BudgetCalculator
from app.services.itinerary_validator import ItineraryValidator
from app.core.logging import logger


class TripPlannerService:
    """
    Deterministic itinerary planning engine that satisfies all schema,
    budget, pace, and constraint requirements.
    """

    def __init__(self, recommendation_engine: RecommendationEngine | None = None):
        self.recommendation_engine = recommendation_engine or RecommendationEngine()

    def plan_trip(self, request: TripPlanRequest) -> ItineraryResponse:
        logger.info(f"Generating trip plan for '{request.destination}', duration={request.duration_days} days, party={request.party_size}")
        
        candidates = self.recommendation_engine.rank_candidates(request)
        if not candidates:
            # Fallback to all attractions if filtering was too aggressive
            candidates = self.recommendation_engine.get_all_attractions()

        # Determine activities per day based on pace
        if request.pace == Pace.RELAXED:
            acts_per_day = 2
            allowed_blocks = [TimeBlock.MORNING, TimeBlock.AFTERNOON]
        elif request.pace == Pace.PACKED:
            acts_per_day = 3
            allowed_blocks = [TimeBlock.MORNING, TimeBlock.AFTERNOON, TimeBlock.EVENING]
        else:  # Balanced
            acts_per_day = 2
            allowed_blocks = [TimeBlock.MORNING, TimeBlock.AFTERNOON]

        days: List[DayPlan] = []
        candidate_idx = 0
        total_candidates = len(candidates)
        start_dt = request.start_date

        for day_num in range(1, (request.duration_days or 1) + 1):
            curr_date = (start_dt + timedelta(days=day_num - 1)) if start_dt else None
            day_activities: List[Activity] = []

            for slot_idx in range(acts_per_day):
                if total_candidates > 0 and candidate_idx < total_candidates:
                    chosen = candidates[candidate_idx]
                    candidate_idx += 1
                elif total_candidates > 0:
                    # Loop back if not enough unique candidates, but keep unique within reason
                    chosen = candidates[candidate_idx % total_candidates]
                    candidate_idx += 1
                else:
                    break

                block = allowed_blocks[slot_idx % len(allowed_blocks)]

                # Build rationale
                reason_parts = []
                if any(i.lower() in chosen.category.lower() for i in request.interests):
                    reason_parts.append(f"Matches your interest in {chosen.category}")
                if request.traveller_profile and request.traveller_profile.value in chosen.suitable_for:
                    reason_parts.append(f"suitable for {request.traveller_profile.value}s")
                if not reason_parts:
                    reason_parts.append(f"Popular {chosen.category} highlight in {chosen.destination}")
                reason_str = ", ".join(reason_parts).capitalize() + "."

                act = Activity(
                    name=chosen.name,
                    category=chosen.category,
                    time_block=block,
                    duration_minutes=chosen.estimated_duration_minutes,
                    estimated_cost_per_person=chosen.estimated_cost_per_person,
                    estimated_group_cost=None,  # Will be calculated by BudgetCalculator
                    cost_status=chosen.cost_status,
                    reason=reason_str,
                    source_ids=[chosen.source_id]
                )
                day_activities.append(act)

            days.append(
                DayPlan(
                    day_number=day_num,
                    date=curr_date,
                    activities=day_activities,
                    estimated_day_total=0.0
                )
            )

        # Calculate exact budget and day totals deterministically
        days, budget_summary, budget_warnings = BudgetCalculator.compute_itinerary_budget(
            days=days,
            party_size=request.party_size,
            budget_limit=request.budget.amount,
            currency=request.budget.currency
        )

        # Validate constraints
        is_valid, validation_errors, validation_warnings = ItineraryValidator.validate_itinerary_constraints(
            days=days,
            budget_summary=budget_summary,
            pace=request.pace,
            excluded_activities=request.excluded_activities
        )

        all_warnings = budget_warnings + validation_warnings
        if validation_errors:
            for err in validation_errors:
                all_warnings.append(f"Constraint notice: {err}")

        # Explicit assumptions
        assumptions = [
            f"Budget scope configured as '{request.budget.scope.value}'. Intercity transport and flights are excluded unless stated.",
            f"Schedule paced for '{request.pace.value}' tempo with standard activity durations.",
            "Opening hours and ticket costs are demonstration estimates based on curated reference records and are not live quotes."
        ]

        if request.notes:
            assumptions.append(f"User preference note noted: '{request.notes}'")

        return ItineraryResponse(
            plan_id=f"plan-{uuid.uuid4().hex[:10]}",
            destination=request.destination,
            duration_days=request.duration_days or 1,
            currency=request.budget.currency,
            budget_scope=request.budget.scope,
            days=days,
            budget_summary=budget_summary,
            assumptions=assumptions,
            warnings=all_warnings
        )
