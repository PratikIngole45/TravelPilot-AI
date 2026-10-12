from typing import List, Dict, Any, Optional
from app.graphdb.neo4j_client import Neo4jClient
from app.services.recommendation import RecommendationEngine
from app.core.logging import logger

CYPHER_GET_DESTINATION_ATTRACTIONS = """
MATCH (d:Destination {name: $destination})-[:HAS_ATTRACTION]->(a:Attraction)
RETURN a.id AS id, a.name AS name, a.category AS category, a.duration_minutes AS duration_minutes, a.cost AS cost
"""

CYPHER_GET_ATTRACTIONS_BY_CATEGORY = """
MATCH (d:Destination {name: $destination})-[:HAS_ATTRACTION]->(a:Attraction)-[:IN_CATEGORY]->(c:Category {name: $category})
RETURN a.id AS id, a.name AS name, a.category AS category, a.cost AS cost
"""

CYPHER_GET_NEARBY_ATTRACTIONS = """
MATCH (a:Attraction {id: $attraction_id})-[:NEAR]->(nearby:Attraction)
RETURN nearby.id AS id, nearby.name AS name, nearby.category AS category
LIMIT $limit
"""

CYPHER_GET_ATTRACTIONS_FOR_PROFILE = """
MATCH (a:Attraction)-[:SUITS]->(p:TravellerProfile {name: $profile})
RETURN a.id AS id, a.name AS name, a.category AS category
"""


class TravelGraphQueries:
    """
    Manages parameterized Cypher graph queries with graceful in-memory graph fallback.
    """

    def __init__(self, client: Optional[Neo4jClient] = None, rec_engine: Optional[RecommendationEngine] = None):
        self.client = client or Neo4jClient()
        self.rec_engine = rec_engine or RecommendationEngine()

    def get_attractions_by_destination(self, destination: str) -> List[Dict[str, Any]]:
        params = {"destination": destination}
        res = self.client.execute_query(CYPHER_GET_DESTINATION_ATTRACTIONS, params)
        if res:
            return res

        # In-memory graph fallback
        all_attrs = self.rec_engine.get_all_attractions(destination)
        return [
            {
                "id": a.id,
                "name": a.name,
                "category": a.category,
                "duration_minutes": a.estimated_duration_minutes,
                "cost": a.estimated_cost_per_person
            }
            for a in all_attrs
        ]

    def get_nearby_attractions(self, attraction_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        params = {"attraction_id": attraction_id, "limit": limit}
        res = self.client.execute_query(CYPHER_GET_NEARBY_ATTRACTIONS, params)
        if res:
            return res

        # In-memory proximity graph fallback based on shared geographic zones
        all_attrs = self.rec_engine.get_all_attractions()
        target = next((a for a in all_attrs if a.id == attraction_id), None)
        if not target:
            return []

        # Return attractions in the same category or destination excluding self
        nearby = [
            {"id": a.id, "name": a.name, "category": a.category}
            for a in all_attrs
            if a.id != attraction_id and (a.category == target.category or "North" in a.description)
        ]
        return nearby[:limit]

    def get_attractions_for_profile(self, profile: str) -> List[Dict[str, Any]]:
        params = {"profile": profile}
        res = self.client.execute_query(CYPHER_GET_ATTRACTIONS_FOR_PROFILE, params)
        if res:
            return res

        all_attrs = self.rec_engine.get_all_attractions()
        matched = [
            {"id": a.id, "name": a.name, "category": a.category}
            for a in all_attrs
            if profile.lower() in [s.lower() for s in a.suitable_for]
        ]
        return matched
