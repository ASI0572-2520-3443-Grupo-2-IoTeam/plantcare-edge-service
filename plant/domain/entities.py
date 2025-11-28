from dataclasses import dataclass
from datetime import datetime


@dataclass
class Plant:
    """
    Represents a plant entity, including the device ID.
    """
    id: int
    device_id: str
    temperature: float
    humidity: float
    light: int
    soil_humidity: int
    created_at: datetime
