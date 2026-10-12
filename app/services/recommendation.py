import json
import os
from typing import List, Dict, Any
from app.schemas.retrieval import AttractionRecord
from app.schemas.trip import TripPlanRequest
from app.core.logging import logger


class RecommendationEngine:
    """
    Deterministic scoring and candidate attraction selection engine.
    """

    def __init__(self, demo_data_path: str = "data/demo/goa_attractions.json"):
        self.demo_data_path = demo_data_path
        self._attractions_cache: List[AttractionRecord] = []
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.demo_data_path):
            with open(self.demo_data_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                self._attractions_cache = [AttractionRecord(**item) for item in raw_data]
            logger.info(f"Loaded {len(self._attractions_cache)} attractions from {self.demo_data_path}")
        else:
            logger.warning(f"Demo data file not found at {self.demo_data_path}")
            self._attractions_cache = []

    def get_all_attractions(self, destination: str | None = None) -> List[AttractionRecord]:
        if not destination:
            return self._attractions_cache
        dest_clean = destination.lower()
        return [
            a for a in self._attractions_cache
            if dest_clean in a.destination.lower() or a.destination.lower() in dest_clean
        ]

    def score_attraction(self, attraction: AttractionRecord, request: TripPlanRequest) -> float:
        score = 1.0  # Base score

        user_interests = [i.strip().lower() for i in request.interests]
        # Match category or description keywords
        if attraction.category.lower() in user_interests:
            score += 3.0
        for interest in user_interests:
            if interest in attraction.description.lower() or interest in attraction.name.lower():
                score += 1.5

        # Profile suitability match
        if request.traveller_profile:
            profile_val = request.traveller_profile.value.lower()
            if profile_val in [s.lower() for s in attraction.suitable_for]:
                score += 1.0

        # Accessibility filtering/scoring
        for need in request.accessibility_needs:
            need_lower = need.lower()
            features_lower = [f.lower() for f in attraction.accessibility_features]
            if any(need_lower in f for f in features_lower):
                score += 2.0
            if "wheelchair" in need_lower and "strenuous_trek" in features_lower:
                score -= 10.0  # Major penalty for inaccessible options

        return score

    def rank_candidates(self, request: TripPlanRequest) -> List[AttractionRecord]:
        candidates = self.get_all_attractions(request.destination)
        excluded = [e.strip().lower() for e in request.excluded_activities if e.strip()]

        filtered: List[AttractionRecord] = []
        for a in candidates:
            name_lower = a.name.lower()
            cat_lower = a.category.lower()
            # Check exclusions
            if any(ex in name_lower or ex in cat_lower for ex in excluded):
                continue
            filtered.append(a)

        # Sort by score descending
        scored = sorted(
            filtered,
            key=lambda a: self.score_attraction(a, request),
            reverse=True
        )
        return scored
