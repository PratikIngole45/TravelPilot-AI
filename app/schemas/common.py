from enum import Enum


class BudgetScope(str, Enum):
    LOCAL_TRIP_ONLY = "local_trip_only"
    INCLUDING_INTERCITY_TRAVEL = "including_intercity_travel"
    UNSPECIFIED = "unspecified"


class Pace(str, Enum):
    RELAXED = "relaxed"
    BALANCED = "balanced"
    PACKED = "packed"


class CostStatus(str, Enum):
    VERIFIED = "verified"
    SOURCED_ESTIMATE = "sourced_estimate"
    DEMO_DATA = "demo_data"
    UNKNOWN = "unknown"


class GroundingStatus(str, Enum):
    GROUNDED = "grounded"
    PARTIAL = "partial"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class TravellerProfile(str, Enum):
    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    GROUP = "group"


class TimeBlock(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
