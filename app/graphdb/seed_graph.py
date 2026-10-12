import json
import os
from typing import List, Dict, Any
from app.graphdb.neo4j_client import Neo4jClient
from app.core.logging import logger

CYPHER_SEED_STATEMENTS = """
// Create Constraints
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Destination) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (a:Attraction) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (p:TravellerProfile) REQUIRE p.name IS UNIQUE;

// Merge Destination
MERGE (d:Destination {id: 'dest-goa-01'})
SET d.name = 'Goa, India', d.country = 'India';

// Merge Categories
MERGE (c1:Category {name: 'history'})
MERGE (c2:Category {name: 'beaches'})
MERGE (c3:Category {name: 'local_food'})
MERGE (c4:Category {name: 'nature'})
MERGE (c5:Category {name: 'nightlife'});

// Merge Traveller Profiles
MERGE (p1:TravellerProfile {name: 'solo'})
MERGE (p2:TravellerProfile {name: 'couple'})
MERGE (p3:TravellerProfile {name: 'family'})
MERGE (p4:TravellerProfile {name: 'group'});
"""


def seed_knowledge_graph(client: Neo4jClient, attractions_file: str = "data/demo/goa_attractions.json") -> bool:
    """
    Idempotently seeds Neo4j with destinations, attractions, categories, and proximity relationships.
    """
    logger.info("Starting Neo4j knowledge graph seeding...")
    connected = client.connect()
    if not connected:
        logger.warning("Neo4j is not connected. Seeding script recorded graph structure for in-memory graph mode.")
        return False

    if not os.path.exists(attractions_file):
        logger.error(f"Attractions file not found at {attractions_file}")
        return False

    with open(attractions_file, "r", encoding="utf-8") as f:
        attractions = json.load(f)

    # 1. Run schema and baseline categories
    for stmt in CYPHER_SEED_STATEMENTS.strip().split(";"):
        cleaned = stmt.strip()
        if cleaned:
            client.execute_query(cleaned)

    # 2. Merge attractions and relationships
    for a in attractions:
        cypher_attr = """
        MERGE (a:Attraction {id: $id})
        SET a.name = $name,
            a.category = $category,
            a.description = $description,
            a.duration_minutes = $duration,
            a.cost = $cost,
            a.data_status = $status
        WITH a
        MATCH (d:Destination {id: 'dest-goa-01'})
        MERGE (d)-[:HAS_ATTRACTION]->(a)
        WITH a
        MERGE (c:Category {name: $category})
        MERGE (a)-[:IN_CATEGORY]->(c)
        """
        client.execute_query(cypher_attr, {
            "id": a["id"],
            "name": a["name"],
            "category": a["category"],
            "description": a["description"],
            "duration": a["estimated_duration_minutes"],
            "cost": a.get("estimated_cost_per_person", 0.0),
            "status": a.get("cost_status", "demo_data")
        })

        # Profiles
        for prof in a.get("suitable_for", []):
            client.execute_query("""
            MATCH (a:Attraction {id: $id}), (p:TravellerProfile {name: $prof})
            MERGE (a)-[:SUITS]->(p)
            """, {"id": a["id"], "prof": prof})

    # 3. Nearby relationships
    client.execute_query("""
    MATCH (a1:Attraction {id: 'goa-attr-01'}), (a2:Attraction {id: 'goa-attr-04'})
    MERGE (a1)-[:NEAR]->(a2);
    MATCH (a3:Attraction {id: 'goa-attr-02'}), (a4:Attraction {id: 'goa-attr-03'})
    MERGE (a3)-[:NEAR]->(a4);
    """)

    logger.info(f"Successfully seeded {len(attractions)} attractions into Neo4j graph database.")
    return True
