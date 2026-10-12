import pytest
from app.graphdb.neo4j_client import Neo4jClient
from app.graphdb.queries import TravelGraphQueries


def test_neo4j_client_offline_fallback():
    # Client with invalid host or disabled flag
    client = Neo4jClient(uri="bolt://127.0.0.1:9999", enabled=False)
    assert client.connect() is False
    res = client.execute_query("MATCH (n) RETURN n")
    assert res == []


def test_graph_queries_fallback_destination_attractions():
    queries = TravelGraphQueries(client=Neo4jClient(enabled=False))
    results = queries.get_attractions_by_destination("Goa, India")
    assert len(results) >= 5
    assert any("Fort Aguada" in a["name"] for a in results)


def test_graph_queries_fallback_nearby_attractions():
    queries = TravelGraphQueries(client=Neo4jClient(enabled=False))
    # Fort Aguada id: goa-attr-01
    nearby = queries.get_nearby_attractions("goa-attr-01", limit=2)
    assert len(nearby) > 0
    # Must not contain itself
    assert all(a["id"] != "goa-attr-01" for a in nearby)


def test_graph_queries_for_profile():
    queries = TravelGraphQueries(client=Neo4jClient(enabled=False))
    couples = queries.get_attractions_for_profile("couple")
    assert len(couples) > 0
