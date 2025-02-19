"""
API endpoints for advanced geospatial analysis
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import logging

from ..geospatial.location_optimizer import LocationOptimizer
from ..config import Config

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/geospatial", tags=["geospatial"])

# Initialize components
config = Config()
optimizer = LocationOptimizer(config)

# Pydantic models
class LocationPoint(BaseModel):
    lat: float
    lng: float

class ClusterAnalysisRequest(BaseModel):
    locations: List[Dict]
    eps_km: Optional[float] = 0.5
    min_samples: Optional[int] = 5

class HeatmapRequest(BaseModel):
    restaurants: List[Dict]
    center: LocationPoint
    zoom: Optional[int] = 12

class PopulationAnalysisRequest(BaseModel):
    location: LocationPoint
    radius_km: Optional[float] = 1.0

class GrowthPredictionRequest(BaseModel):
    historical_data: List[Dict]
    prediction_days: Optional[int] = 365

# API Routes
@router.post("/clusters/analyze")
def analyze_clusters(request: ClusterAnalysisRequest):
    """Analyze restaurant clusters using DBSCAN"""
    try:
        analysis = optimizer.analyze_restaurant_clusters(
            locations=request.locations,
            eps_km=request.eps_km,
            min_samples=request.min_samples
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing clusters: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/prices/heatmap")
def generate_price_heatmap(request: HeatmapRequest):
    """Generate price heatmap using H3 hexagons"""
    try:
        center = {"lat": request.center.lat, "lng": request.center.lng}
        heatmap = optimizer.generate_price_heatmap(
            restaurants=request.restaurants,
            center=center,
            zoom=request.zoom
        )
        return {"heatmap_data": heatmap._repr_html_()}
    except Exception as e:
        logger.error(f"Error generating price heatmap: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/population/analyze")
def analyze_population(request: PopulationAnalysisRequest):
    """Analyze population impact on restaurant success"""
    try:
        analysis = optimizer.analyze_population_impact(
            location={"lat": request.location.lat, "lng": request.location.lng},
            radius_km=request.radius_km
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing population: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@router.post("/growth/predict")
def predict_growth(request: GrowthPredictionRequest):
    """Predict future restaurant growth zones"""
    try:
        # Convert list of dicts to DataFrame
        df = pd.DataFrame(request.historical_data)
        
        predictions = optimizer.predict_growth_zones(
            historical_data=df,
            prediction_days=request.prediction_days
        )
        return predictions
    except Exception as e:
        logger.error(f"Error predicting growth: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )