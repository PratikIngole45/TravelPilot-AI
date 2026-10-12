import json
import os
from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.retrieval import DestinationSummary, AttractionRecord
from app.services.recommendation import RecommendationEngine

router = APIRouter(prefix="/api/v1/destinations", tags=["Destinations"])
rec_engine = RecommendationEngine()


@router.get("", response_model=List[DestinationSummary])
def get_destinations():
    """
    Returns only destinations supported in the current data source.
    """
    dest_path = "data/demo/destinations.json"
    if not os.path.exists(dest_path):
        return []
    with open(dest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [DestinationSummary(**d) for d in data]


@router.get("/{destination_id}", response_model=DestinationSummary)
def get_destination(destination_id: str):
    """
    Returns details for a specific destination.
    """
    dest_path = "data/demo/destinations.json"
    if not os.path.exists(dest_path):
        raise HTTPException(status_code=404, detail="Destination data not found")
    with open(dest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for d in data:
        if d.get("destination_id") == destination_id or destination_id.lower() in d.get("name", "").lower():
            return DestinationSummary(**d)
    raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")


@router.get("/{destination_id}/attractions", response_model=List[AttractionRecord])
def get_destination_attractions(destination_id: str):
    """
    Returns attractions for a given destination.
    """
    attractions = rec_engine.get_all_attractions(destination_id)
    if not attractions:
        # Check if generic Goa
        if "goa" in destination_id.lower():
            attractions = rec_engine.get_all_attractions()
    return attractions
