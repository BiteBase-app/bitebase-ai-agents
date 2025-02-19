"""
Advanced analytics API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from ..analytics.advanced_analytics import AdvancedAnalytics
from ..config import Config

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/advanced", tags=["advanced"])

# Initialize components
config = Config()
analytics = AdvancedAnalytics(config)

# Pydantic models
class POSRequest(BaseModel):
    restaurant_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class EmotionRequest(BaseModel):
    texts: List[str]

class MigrationRequest(BaseModel):
    restaurant_id: str
    timeframe_days: Optional[int] = 90

class ForecastRequest(BaseModel):
    restaurant_id: str
    forecast_days: Optional[int] = 30

class RecommendationRequest(BaseModel):
    customer_id: str

# API Routes
@router.post("/pos/insights")
def get_pos_insights(request: POSRequest):
    """Get insights from POS data"""
    try:
        date_range = None
        if request.start_date and request.end_date:
            date_range = (request.start_date, request.end_date)
            
        insights = analytics.get_pos_insights(
            restaurant_id=request.restaurant_id,
            date_range=date_range
        )
        return insights
    except Exception as e:
        logger.error(f"Error getting POS insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/emotions/analyze")
def analyze_emotions(request: EmotionRequest):
    """Analyze customer emotions from feedback"""
    try:
        results = analytics.analyze_customer_emotions(request.texts)
        return {"emotion_analysis": results}
    except Exception as e:
        logger.error(f"Error analyzing emotions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/customers/migration")
def track_migration(request: MigrationRequest):
    """Track customer migration patterns"""
    try:
        patterns = analytics.track_customer_migration(
            restaurant_id=request.restaurant_id,
            timeframe_days=request.timeframe_days
        )
        return patterns
    except Exception as e:
        logger.error(f"Error tracking migration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/demand/forecast")
def forecast_demand(request: ForecastRequest):
    """Generate demand forecast"""
    try:
        forecast = analytics.forecast_demand(
            restaurant_id=request.restaurant_id,
            forecast_days=request.forecast_days
        )
        return forecast
    except Exception as e:
        logger.error(f"Error forecasting demand: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/customers/recommendations")
def get_recommendations(request: RecommendationRequest):
    """Get personalized customer recommendations"""
    try:
        recommendations = analytics.get_personalized_recommendations(
            customer_id=request.customer_id
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )