from typing import List, Tuple
from app.schemas.itinerary import DayPlan, BudgetSummary
from app.schemas.common import Pace


class ItineraryValidator:
    """
    Deterministic validator enforcing schedule, budget, pace, and exclusion constraints.
    """

    MAX_MINUTES_BY_PACE = {
        Pace.RELAXED: 360,   # 6 hours
        Pace.BALANCED: 480,  # 8 hours
        Pace.PACKED: 600     # 10 hours
    }

    @classmethod
    def validate_itinerary_constraints(
        cls,
        days: List[DayPlan],
        budget_summary: BudgetSummary,
        pace: Pace = Pace.BALANCED,
        excluded_activities: List[str] | None = None
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validates:
        1. No duplicate activities.
        2. Daily duration limits per pace.
        3. Excluded activity compliance.
        4. Budget limit compliance.

        Returns: (is_valid, errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []
        excluded_lower = [e.strip().lower() for e in (excluded_activities or []) if e.strip()]

        seen_activities = set()
        max_minutes = cls.MAX_MINUTES_BY_PACE.get(pace, 480)

        for day in days:
            day_minutes = 0
            for act in day.activities:
                act_key = act.name.strip().lower()
                if act_key in seen_activities:
                    errors.append(f"Duplicate activity scheduled: '{act.name}' on Day {day.day_number}.")
                seen_activities.add(act_key)

                # Duration
                day_minutes += act.duration_minutes

                # Exclusions check
                act_category_lower = act.category.lower()
                for excl in excluded_lower:
                    if excl in act_key or excl in act_category_lower:
                        errors.append(
                            f"Excluded activity violation: '{act.name}' ({act.category}) matches excluded preference '{excl}'."
                        )

            if day_minutes > max_minutes:
                errors.append(
                    f"Day {day.day_number} scheduled time ({day_minutes} mins) exceeds maximum pace limit for {pace.value} ({max_minutes} mins)."
                )

        # Budget hard constraint
        if budget_summary.is_over_budget:
            errors.append(
                f"Budget exceeded: Estimated total {budget_summary.currency} {budget_summary.known_estimated_total:,.2f} exceeds limit {budget_summary.currency} {budget_summary.budget_limit:,.2f}."
            )

        is_valid = len(errors) == 0
        return is_valid, errors, warnings
