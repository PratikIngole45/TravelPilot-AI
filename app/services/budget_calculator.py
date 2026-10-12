from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple
from app.schemas.itinerary import Activity, DayPlan, BudgetSummary


class BudgetCalculator:
    """
    Deterministic budget calculator enforcing exact arithmetic in Python.
    Distinguishes unknown costs from zero costs.
    """

    @staticmethod
    def calculate_activity_group_cost(
        activity: Activity,
        party_size: int,
        is_per_person: bool = True
    ) -> Tuple[Activity, Decimal | None]:
        """
        Calculates and updates activity group cost based on party size.
        """
        if activity.estimated_cost_per_person is None:
            # Unknown cost must remain unknown, NOT converted to 0
            activity.estimated_group_cost = None
            return activity, None

        unit_cost = Decimal(str(activity.estimated_cost_per_person))
        if is_per_person:
            group_cost = (unit_cost * Decimal(party_size)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            group_cost = unit_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        activity.estimated_group_cost = float(group_cost)
        return activity, group_cost

    @staticmethod
    def compute_itinerary_budget(
        days: List[DayPlan],
        party_size: int,
        budget_limit: float,
        currency: str = "INR"
    ) -> Tuple[List[DayPlan], BudgetSummary, List[str]]:
        """
        Calculates exact day totals, grand total, completeness, and budget warnings.
        """
        warnings: List[str] = []
        grand_total = Decimal("0.00")
        total_activities = 0
        known_cost_activities = 0

        for day in days:
            day_total = Decimal("0.00")
            for act in day.activities:
                total_activities += 1
                if act.estimated_cost_per_person is not None:
                    known_cost_activities += 1
                    # Recalculate group cost deterministically
                    unit_cost = Decimal(str(act.estimated_cost_per_person))
                    group_cost = (unit_cost * Decimal(party_size)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    act.estimated_group_cost = float(group_cost)
                    day_total += group_cost
                else:
                    act.estimated_group_cost = None

            day.estimated_day_total = float(day_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            grand_total += day_total

        limit_dec = Decimal(str(budget_limit)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        remaining = limit_dec - grand_total
        is_over = grand_total > limit_dec

        if total_activities == 0:
            completeness = "complete"
        elif known_cost_activities == total_activities:
            completeness = "complete"
        elif known_cost_activities == 0:
            completeness = "unknown"
        else:
            completeness = "partial"

        if is_over:
            warnings.append(
                f"Itinerary total ({currency} {float(grand_total):,.2f}) exceeds budget limit of {currency} {budget_limit:,.2f} by {currency} {abs(float(remaining)):,.2f}."
            )

        if completeness == "partial":
            unknown_count = total_activities - known_cost_activities
            warnings.append(
                f"{unknown_count} activity/activities have unknown pricing. Actual expenditure may exceed calculated estimates."
            )
        elif completeness == "unknown":
            warnings.append(
                "Cost data for all planned activities is unknown. Stated budget cannot be verified against verified venue prices."
            )

        summary = BudgetSummary(
            known_estimated_total=float(grand_total),
            budget_limit=budget_limit,
            currency=currency,
            remaining_budget=float(remaining),
            cost_completeness=completeness,
            is_over_budget=is_over
        )

        return days, summary, warnings
