from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator
from app.schemas.common import BudgetScope, Pace, TravellerProfile


class BudgetInput(BaseModel):
    amount: float = Field(..., gt=0, description="Total budget amount")
    currency: str = Field(default="INR", max_length=10, description="Currency code, e.g., INR, USD, EUR")
    scope: BudgetScope = Field(default=BudgetScope.LOCAL_TRIP_ONLY, description="Scope of the budget")


class TripPlanRequest(BaseModel):
    origin_city: Optional[str] = Field(None, max_length=100, description="Origin or starting city (e.g. Pune, Delhi, Mumbai, Bengaluru)")
    destination: str = Field(..., min_length=2, max_length=100, description="Destination city/region")
    duration_days: Optional[int] = Field(None, ge=1, le=30, description="Trip duration in days (1-30)")
    start_date: Optional[date] = Field(None, description="Start date of the trip")
    end_date: Optional[date] = Field(None, description="End date of the trip")
    party_size: int = Field(default=1, ge=1, le=50, description="Number of travelers")
    budget: BudgetInput = Field(..., description="Budget details")
    interests: List[str] = Field(default_factory=list, description="List of interests e.g. beaches, history, food")
    pace: Pace = Field(default=Pace.BALANCED, description="Pace of travel: relaxed, balanced, or packed")
    traveller_profile: Optional[TravellerProfile] = Field(None, description="solo, couple, family, group")
    dietary_preferences: List[str] = Field(default_factory=list, description="Dietary preferences or restrictions")
    accessibility_needs: List[str] = Field(default_factory=list, description="Accessibility requirements")
    preferred_transport: Optional[str] = Field(None, max_length=100)
    accommodation_preference: Optional[str] = Field(None, max_length=100)
    excluded_activities: List[str] = Field(default_factory=list, description="Activities or venues to exclude")
    notes: Optional[str] = Field(None, max_length=500, description="Additional context or notes")

    @model_validator(mode="after")
    def validate_duration_and_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be greater than or equal to start_date")
            calculated_days = (self.end_date - self.start_date).days + 1
            if self.duration_days is None:
                self.duration_days = calculated_days
            elif self.duration_days != calculated_days:
                # Align duration with explicit date span
                self.duration_days = calculated_days

        if self.duration_days is None:
            raise ValueError("Either duration_days or both start_date and end_date must be provided.")

        return self
