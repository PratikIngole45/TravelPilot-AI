import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.common import BudgetScope, CostStatus, TimeBlock


class Activity(BaseModel):
    name: str = Field(..., description="Attraction or activity name")
    category: str = Field(..., description="Category, e.g. beaches, history, dining")
    time_block: TimeBlock = Field(..., description="Time of day: morning, afternoon, evening")
    duration_minutes: int = Field(..., ge=15, le=480, description="Approximate duration in minutes")
    estimated_cost_per_person: Optional[float] = Field(None, ge=0, description="Per-person cost if known")
    estimated_group_cost: Optional[float] = Field(None, ge=0, description="Total group cost if known")
    cost_status: CostStatus = Field(default=CostStatus.DEMO_DATA, description="Provenance status of the cost")
    reason: str = Field(..., description="Explanation matching traveler preferences")
    source_ids: List[str] = Field(default_factory=list, description="IDs of documents or records supporting this venue")


class DayPlan(BaseModel):
    day_number: int = Field(..., ge=1, description="Sequential day number")
    date: Optional[datetime.date] = Field(None, description="Actual date if known")
    activities: List[Activity] = Field(default_factory=list, description="Activities planned for this day")
    estimated_day_total: float = Field(default=0.0, ge=0, description="Sum of known group costs for this day")


class BudgetSummary(BaseModel):
    known_estimated_total: float = Field(..., ge=0, description="Calculated total for all known activity costs")
    budget_limit: float = Field(..., ge=0, description="User specified budget limit")
    currency: str = Field(..., description="Currency code")
    remaining_budget: float = Field(..., description="budget_limit - known_estimated_total")
    cost_completeness: str = Field(..., description="'complete' if all costs known, 'partial' if some unknown")
    is_over_budget: bool = Field(default=False, description="True if known total exceeds budget limit")


class ItineraryResponse(BaseModel):
    plan_id: str = Field(..., description="Unique ID for the generated itinerary")
    destination: str = Field(..., description="Destination")
    duration_days: int = Field(..., ge=1, description="Total days")
    currency: str = Field(..., description="Currency")
    budget_scope: BudgetScope = Field(..., description="Scope of the budget")
    days: List[DayPlan] = Field(..., description="Day-by-day plan")
    budget_summary: BudgetSummary = Field(..., description="Deterministic budget summary")
    assumptions: List[str] = Field(default_factory=list, description="Explicit assumptions made by planner")
    warnings: List[str] = Field(default_factory=list, description="Warnings (budget, incomplete data, etc.)")
