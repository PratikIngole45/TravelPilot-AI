from typing import List, Dict, Any, Optional
from app.rag.retriever import TravelRetriever
from app.services.recommendation import RecommendationEngine
from app.services.budget_calculator import BudgetCalculator
from app.services.itinerary_validator import ItineraryValidator
from app.schemas.itinerary import DayPlan, BudgetSummary, Activity
from app.schemas.common import Pace, TimeBlock


class TravelAgentTools:
    """
    Bounded, validated tool interface for the agent workflow.
    No arbitrary shell, network, or code execution is permitted.
    """

    def __init__(
        self,
        retriever: TravelRetriever | None = None,
        rec_engine: RecommendationEngine | None = None
    ):
        self.retriever = retriever or TravelRetriever()
        self.rec_engine = rec_engine or RecommendationEngine()

    def search_destination_knowledge(self, query: str, destination: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves relevant travel passages and guide notes from verified vector store.
        """
        chunks = self.retriever.retrieve(query=query, top_k=3, destination_filter=destination)
        return [
            {
                "chunk_id": c.chunk_id,
                "doc_id": c.doc_id,
                "title": c.metadata.get("title", ""),
                "content": c.content,
                "data_status": c.metadata.get("data_status", "demo_data")
            }
            for c in chunks
        ]

    def get_attractions(
        self,
        destination: str,
        categories: Optional[List[str]] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Returns structured attraction records for a destination filtered by category.
        """
        all_attrs = self.rec_engine.get_all_attractions(destination)
        if categories:
            cats_lower = [c.lower() for c in categories]
            all_attrs = [a for a in all_attrs if a.category.lower() in cats_lower]
        return [a.model_dump() for a in all_attrs[:max_results]]

    def get_attraction_details(self, attraction_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns complete details of a specific attraction by ID.
        """
        all_attrs = self.rec_engine.get_all_attractions()
        for a in all_attrs:
            if a.id == attraction_id:
                return a.model_dump()
        return None

    def estimate_trip_cost(
        self,
        days_activities: List[Dict[str, Any]],
        party_size: int,
        budget_limit: float,
        currency: str = "INR"
    ) -> Dict[str, Any]:
        """
        Calculates group totals deterministically using BudgetCalculator.
        """
        day_plans: List[DayPlan] = []
        for d in days_activities:
            activities = [Activity(**act) for act in d.get("activities", [])]
            day_plans.append(DayPlan(day_number=d.get("day_number", 1), activities=activities))

        updated_days, summary, warnings = BudgetCalculator.compute_itinerary_budget(
            days=day_plans,
            party_size=party_size,
            budget_limit=budget_limit,
            currency=currency
        )
        return {
            "days": [d.model_dump() for d in updated_days],
            "budget_summary": summary.model_dump(),
            "warnings": warnings
        }

    def validate_itinerary_constraints(
        self,
        days_data: List[Dict[str, Any]],
        budget_summary_data: Dict[str, Any],
        pace_str: str = "balanced",
        excluded_activities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validates schedule, duplicate activities, pace durations, and budget constraints.
        """
        days = [DayPlan(**d) for d in days_data]
        summary = BudgetSummary(**budget_summary_data)
        pace = Pace(pace_str) if pace_str in [p.value for p in Pace] else Pace.BALANCED

        is_valid, errors, warnings = ItineraryValidator.validate_itinerary_constraints(
            days=days,
            budget_summary=summary,
            pace=pace,
            excluded_activities=excluded_activities
        )
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
