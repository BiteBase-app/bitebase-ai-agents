from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, validator
from .api_models import TimeframeInput

class RestaurantPricing(BaseModel):
    current_prices: Dict[str, float]
    costs: Dict[str, float]

    @validator('current_prices', 'costs')
    def validate_prices(cls, v):
        if not all(price > 0 for price in v.values()):
            raise ValueError('all prices must be positive')
        return v

class MarketConditions(BaseModel):
    customer_count: int = Field(..., ge=0)
    competition_density: float = Field(..., ge=0)
    avg_income: Optional[float] = Field(None, ge=0)
    events_nearby: Optional[List[str]] = None

class TimeFactors(BaseModel):
    peak_hour: bool = False
    weekend: bool = False
    season: str

class OptimizationGoals(BaseModel):
    revenue_weight: float = Field(..., ge=0.0, le=1.0)
    volume_weight: float = Field(..., ge=0.0, le=1.0)
    min_margin_percent: float = Field(..., ge=0.0, le=100.0)

    @validator('volume_weight')
    def weights_must_sum_to_one(cls, v, values):
        if 'revenue_weight' in values:
            if not 0.99 <= (v + values['revenue_weight']) <= 1.01:
                raise ValueError('weights must sum to 1.0')
        return v

class PriceOptimizationRequest(BaseModel):
    restaurant_data: RestaurantPricing
    market_conditions: MarketConditions
    time_factors: TimeFactors
    optimization_goals: OptimizationGoals

class AnalysisType(str):
    ITEM_PERFORMANCE = "item_performance"
    CATEGORY_ANALYSIS = "category_analysis"
    PRICE_ELASTICITY = "price_elasticity"
    CROSS_SELLING = "cross_selling"
    DAYPART_ANALYSIS = "daypart_analysis"

class Metric(str):
    REVENUE = "revenue"
    PROFIT_MARGIN = "profit_margin"
    ORDER_FREQUENCY = "order_frequency"
    CUSTOMER_SATISFACTION = "customer_satisfaction"

class MenuAnalysisRequest(BaseModel):
    restaurant_id: str
    timeframe: TimeframeInput
    analysis_types: List[AnalysisType]
    metrics: List[Metric]
    segmentation: Dict[str, bool] = Field(
        default_factory=lambda: {
            "by_daypart": False,
            "by_customer_type": False,
            "by_season": False
        }
    )

class CustomerAnalysisType(str):
    SEGMENTATION = "segmentation"
    LIFETIME_VALUE = "lifetime_value"
    CHURN_RISK = "churn_risk"
    PREFERENCE_ANALYSIS = "preference_analysis"

class CustomerAnalysisRequest(BaseModel):
    restaurant_id: str
    analysis_types: List[CustomerAnalysisType]
    timeframe: TimeframeInput
    segmentation_criteria: Dict[str, bool] = Field(
        default_factory=lambda: {
            "visit_frequency": True,
            "spending_patterns": True,
            "menu_preferences": True,
            "demographic": True
        }
    )

class StreamAnalyticsRequest(BaseModel):
    subscriptions: List[str] = Field(..., min_items=1)
    aggregation_interval: str = Field(
        "1m",
        regex="^[1-9][0-9]*(s|m|h)$"
    )
    filters: Dict[str, Union[float, List[str]]] = Field(default_factory=dict)