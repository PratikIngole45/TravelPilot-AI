import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "llm_provider" in data


def test_get_destinations():
    response = client.get("/api/v1/destinations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("Goa" in d["name"] for d in data)


def test_plan_trip_valid_payload():
    payload = {
        "destination": "Goa, India",
        "duration_days": 2,
        "party_size": 2,
        "budget": {
            "amount": 10000,
            "currency": "INR",
            "scope": "local_trip_only"
        },
        "interests": ["beaches", "history", "local_food"],
        "pace": "relaxed",
        "traveller_profile": "couple",
        "excluded_activities": ["nightclub"]
    }
    response = client.post("/api/v1/trips/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Goa, India"
    assert data["duration_days"] == 2
    assert len(data["days"]) == 2
    assert "budget_summary" in data
    assert data["budget_summary"]["known_estimated_total"] > 0
    assert data["budget_summary"]["budget_limit"] == 10000


def test_plan_trip_invalid_negative_budget():
    payload = {
        "destination": "Goa, India",
        "duration_days": 2,
        "party_size": 2,
        "budget": {
            "amount": -500,  # Negative!
            "currency": "INR"
        }
    }
    response = client.post("/api/v1/trips/plan", json=payload)
    assert response.status_code == 422  # Unprocessable Entity
