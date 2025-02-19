"""
API endpoints for geospatial pricing and customer engagement
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..pricing.geospatial_pricing import GeospatialPricing
from ..chatbot.engagement_bot import EngagementBot
from ..config import Config

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/engagement", tags=["engagement"])

# Initialize components
config = Config()
pricing = GeospatialPricing(config)
bot = EngagementBot(config)

# Pydantic models
class LocationData(BaseModel):
    lat: float
    lng: float
    radius_km: Optional[float] = 1.0

class PricingFeatures(BaseModel):
    customer_count: int
    competition_density: float
    avg_income: float
    peak_hour: bool
    weekend: bool

class DynamicPriceRequest(BaseModel):
    base_price: float
    current_demand: int
    time_of_day: int
    day_of_week: int
    special_events: Optional[List[str]] = None

class CustomerMessage(BaseModel):
    customer_id: str
    message: str
    location: Optional[Dict[str, float]] = None
    phone_number: Optional[str] = None

class CustomerActivity(BaseModel):
    customer_id: str
    activity_type: str
    activity_data: Dict
    timestamp: Optional[datetime] = None

# API Routes
@router.post("/pricing/analyze")
def analyze_location_pricing(data: LocationData):
    """Analyze pricing for a location"""
    try:
        analysis = pricing.analyze_competition(
            location={"lat": data.lat, "lng": data.lng},
            radius_km=data.radius_km
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing location pricing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/pricing/optimize")
def get_optimal_price(data: PricingFeatures):
    """Get optimal price prediction"""
    try:
        prediction = pricing.predict_optimal_price(
            features=data.dict()
        )
        return prediction
    except Exception as e:
        logger.error(f"Error predicting optimal price: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/pricing/dynamic")
def get_dynamic_price(request: DynamicPriceRequest):
    """Get dynamic price adjustment"""
    try:
        adjustment = pricing.get_dynamic_price_adjustment(
            base_price=request.base_price,
            current_demand=request.current_demand,
            time_of_day=request.time_of_day,
            day_of_week=request.day_of_week,
            special_events=request.special_events
        )
        return adjustment
    except Exception as e:
        logger.error(f"Error calculating dynamic price: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.get("/pricing/heatmap")
def get_price_heatmap(location: LocationData):
    """Generate price heatmap"""
    try:
        heatmap = pricing.generate_price_heatmap(
            location={"lat": location.lat, "lng": location.lng},
            radius_km=location.radius_km
        )
        return {"heatmap_data": heatmap._repr_html_()}
    except Exception as e:
        logger.error(f"Error generating price heatmap: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/bot/message")
def handle_customer_message(message: CustomerMessage):
    """Handle customer message"""
    try:
        response = bot.handle_customer_message(
            message=message.message,
            customer_data={"id": message.customer_id},
            location=message.location
        )
        
        # Send offer via WhatsApp if available
        if response.get('offer') and message.phone_number:
            bot.send_whatsapp_message(
                to_number=message.phone_number,
                message=response['offer']['offer_text']
            )
            
        return response
    except Exception as e:
        logger.error(f"Error handling customer message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/bot/activity")
def process_customer_activity(
    activity: CustomerActivity,
    background_tasks: BackgroundTasks
):
    """Process customer activity"""
    try:
        # Process activity in background
        background_tasks.add_task(
            bot.process_customer_activity,
            customer_id=activity.customer_id,
            activity_type=activity.activity_type,
            activity_data=activity.activity_data
        )
        
        return {
            "status": "accepted",
            "message": "Activity queued for processing",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing customer activity: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )