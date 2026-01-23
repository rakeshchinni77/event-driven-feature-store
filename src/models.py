from pydantic import BaseModel, Field, validator
from typing import Dict, Any
from datetime import datetime


# Raw Kafka Event Model (Untrusted Input)
class RawEvent(BaseModel):
    """
    Represents a raw event consumed from Kafka.
    This is the most critical validation layer.
    """

    entity_id: str = Field(..., min_length=1, description="Unique entity identifier (e.g., user_id)")
    action: str = Field(..., min_length=1, description="Action performed by the entity")
    timestamp: datetime = Field(..., description="Event timestamp in ISO 8601 format")

    @validator("entity_id", "action")
    def must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field must not be empty or whitespace")
        return value


# Feature Model (Internal Representation)
class Feature(BaseModel):
    """
    Represents a single computed feature.
    Used internally before persisting to PostgreSQL.
    """

    entity_id: str
    feature_name: str
    feature_value: str
    timestamp: datetime


# API Response Model (Stable Contract)
class FeatureResponse(BaseModel):
    """
    Response model for GET /features/{entity_id}
    """

    entity_id: str
    features: Dict[str, Any]
    last_updated: datetime
