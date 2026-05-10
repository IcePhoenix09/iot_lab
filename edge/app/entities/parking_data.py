from datetime import datetime
from pydantic import BaseModel, field_validator, Field

class GpsData(BaseModel):
    latitude: float
    longitude: float

class ParkingData(BaseModel):
    parking_id: int
    empty_count: int
    gps: GpsData
    timestamp: datetime = Field(alias="time")

    @classmethod
    @field_validator("timestamp", mode="before")
    def parse_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format."
            )