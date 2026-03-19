from dataclasses import dataclass
from datetime import datetime

@dataclass
class Accelerometer:
    x: int
    y: int
    z: int

@dataclass
class Gps:
    longitude: float
    latitude: float

@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    time: datetime

@dataclass
class Parking:
    empty_count: int
    gps: Gps