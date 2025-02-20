from dataclasses import dataclass
from typing import Dict

@dataclass
class Location:
    lat: float
    lng: float

    def to_dict(self) -> Dict[str, float]:
        return {"lat": self.lat, "lng": self.lng}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Location':
        return cls(lat=data['lat'], lng=data['lng'])