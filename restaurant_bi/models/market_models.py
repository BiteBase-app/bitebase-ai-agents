from typing import List, Optional
from pydantic import BaseModel, Field
from .api_models import LocationInput, TimeframeInput, PaginationParams, SortParams

class MarketAnalysisParameters(BaseModel):
    radius_meters: int = Field(..., gt=0, le=50000)
    cuisine_type: Optional[str] = None
    price_range: Optional[List[str]] = Field(None, description="List of price ranges e.g. ['$$', '$$$']")
    include_demographics: bool = False
    include_competition: bool = False

class MarketAnalysisRequest(BaseModel):
    location: LocationInput
    parameters: MarketAnalysisParameters
    timeframe: TimeframeInput

class RestaurantSearchQuery(BaseModel):
    text: str
    semantic_boost: float = Field(0.5, ge=0.0, le=1.0)

class RestaurantSearchFilters(BaseModel):
    cuisine: Optional[List[str]] = None
    price_range: Optional[List[str]] = None
    features: Optional[List[str]] = None
    rating_min: Optional[float] = Field(None, ge=0.0, le=5.0)
    open_now: Optional[bool] = None

class RestaurantSearchRequest(BaseModel):
    query: RestaurantSearchQuery
    filters: Optional[RestaurantSearchFilters] = None
    location: LocationInput
    pagination: Optional[PaginationParams] = None
    sort: Optional[SortParams] = None

class SimilarityWeights(BaseModel):
    cuisine_weight: float = Field(..., ge=0.0, le=1.0)
    price_weight: float = Field(..., ge=0.0, le=1.0)
    location_weight: float = Field(..., ge=0.0, le=1.0)
    ambiance_weight: float = Field(..., ge=0.0, le=1.0)

    @validator('cuisine_weight', 'price_weight', 'location_weight', 'ambiance_weight')
    def weights_must_sum_to_one(cls, v, values):
        if len(values) == 3:  # On the last field
            total = v + sum(values.values())
            if not 0.99 <= total <= 1.01:  # Allow for floating point imprecision
                raise ValueError('weights must sum to 1.0')
        return v

class SimilarityFilters(BaseModel):
    min_similarity_score: float = Field(0.7, ge=0.0, le=1.0)
    max_distance_km: float = Field(10, gt=0)

class SimilarRestaurantsRequest(BaseModel):
    similarity_criteria: SimilarityWeights
    filters: SimilarityFilters
    limit: int = Field(10, ge=1, le=100)