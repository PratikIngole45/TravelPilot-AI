class TravelPilotException(Exception):
    """Base exception for TravelPilot AI application errors."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConstraintViolationError(TravelPilotException):
    """Raised when itinerary constraints (budget, time, duplicates) are violated."""
    pass


class DestinationNotFoundError(TravelPilotException):
    """Raised when destination is unknown or unsupported."""
    pass


class ProviderUnavailableError(TravelPilotException):
    """Raised when an external LLM or database provider cannot be reached."""
    pass


class IngestionError(TravelPilotException):
    """Raised during document ingestion or indexing failures."""
    pass
