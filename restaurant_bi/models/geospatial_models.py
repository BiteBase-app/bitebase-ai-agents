from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, validator
from .api_models import LocationInput

class LocationMetadata(BaseModel):
    revenue: Optional[float] = None
    customer_count: Optional[int] = None

class WeightedLocation(LocationInput):
    weight: float = Field(1.0, ge=0.0)
    metadata: Optional[LocationMetadata] = None

class ClusteringParameters(BaseModel):
    eps_km: Optional[float] = Field(None, gt=0)
    min_samples: Optional[int] = Field(None, ge=1)
    max_clusters: Optional[int] = Field(None, ge=1)

class GeoBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)

    @validator('south')
    def south_must_be_less_than_north(cls, v, values):
        if 'north' in values and v >= values['north']:
            raise ValueError('south must be less than north')
        return v

    @validator('west')
    def west_must_be_less_than_east(cls, v, values):
        if 'east' in values and v >= values['east']:
            raise ValueError('west must be less than east')
        return v

class ClusterAnalysisRequest(BaseModel):
    analysis_type: Literal['dbscan', 'kmeans', 'hierarchical']
    parameters: ClusteringParameters
    locations: List[WeightedLocation]
    include_demographics: bool = False
    visualization_format: Literal['geojson', 'h3', 'svg'] = 'geojson'

class HeatmapParameters(BaseModel):
    resolution: int = Field(8, ge=1, le=15)
    smoothing_factor: float = Field(0.5, ge=0.0, le=1.0)
    color_scheme: str = 'viridis'

class HeatmapFilters(BaseModel):
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    exclude_outliers: bool = False

    @validator('max_value')
    def max_value_must_be_greater_than_min(cls, v, values):
        if v is not None and 'min_value' in values and values['min_value'] is not None:
            if v <= values['min_value']:
                raise ValueError('max_value must be greater than min_value')
        return v

class HeatmapRequest(BaseModel):
    type: Literal['density', 'price', 'popularity', 'revenue']
    parameters: HeatmapParameters
    bounds: GeoBounds
    filters: Optional[HeatmapFilters] = None
    output_format: Literal['geojson', 'png', 'svg'] = 'geojson'