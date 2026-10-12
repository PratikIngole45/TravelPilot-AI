import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graphdb.neo4j_client import Neo4jClient
from app.graphdb.seed_graph import seed_knowledge_graph
from app.core.logging import logger


def main():
    logger.info("Initializing Neo4j Seeding Script...")
    client = Neo4jClient()
    success = seed_knowledge_graph(client)
    if success:
        print("Neo4j database successfully seeded.")
    else:
        print("Neo4j is currently disabled or offline; in-memory graph fallback active.")


if __name__ == "__main__":
    main()
