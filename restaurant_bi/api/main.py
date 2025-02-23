"""
FastAPI-based REST API for Restaurant BI System
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from . import advanced_endpoints, engagement_endpoints, geospatial_endpoints
from typing import List, Dict, Optional
from datetime import datetime
import logging

from ..market_analysis_agent import RestaurantMarketAnalysisAgent
from ..llm.insights_generator import InsightsGenerator
from ..social.social_listener import SocialListener
from ..streaming.realtime_processor import RealtimeProcessor
from ..vectorstore.embedding_store import RestaurantEmbeddingStore
from ..config import Config

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Restaurant BI API",
    description="API for restaurant market analysis and AI insights",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(advanced_endpoints.router)
app.include_router(engagement_endpoints.router)
app.include_router(geospatial_endpoints.router)

# Initialize components
config = Config()
market_agent = RestaurantMarketAnalysisAgent()
insights_generator = InsightsGenerator(config)
social_listener = SocialListener(config)
realtime_processor = RealtimeProcessor(config)
vector_store = RestaurantEmbeddingStore()

# Pydantic models
class LocationQuery(BaseModel):
    lat: float
    lng: float
    radius: Optional[int] = None
    cuisine_type: Optional[str] = None

class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict] = None
    limit: Optional[int] = 10

class ReviewData(BaseModel):
    restaurant_name: str
    review_text: str
    rating: float
    source: str

class MarketInsightRequest(BaseModel):
    location: Dict[str, float]
    cuisine_type: Optional[str] = None
    competitors: Optional[List[str]] = None

# # Add caching for expensive operations
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache.decorator import cache

# @app.on_event("startup")
# async def startup():
#     redis = aioredis.from_url("redis://localhost", encoding="utf8")
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# API Routes
@app.get("/")
def read_root():
    """API health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/market/analyze")
# @cache(expire=3600)  # Cache for 1 hour
async def analyze_market(query: LocationQuery):
    """Get market analysis for a location"""
    try:
        insights = market_agent.get_market_insights(
            location={"lat": query.lat, "lng": query.lng},
            radius=query.radius,
            cuisine_type=query.cuisine_type
        )
        return insights
    except Exception as e:
        logger.error(f"Error analyzing market: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@app.post("/search/semantic")
def semantic_search(query: SearchQuery):
    """Perform semantic search for restaurants"""
    try:
        results = vector_store.semantic_search(
            query=query.query,
            n_results=query.limit,
            filter_criteria=query.filters
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Error performing semantic search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@app.post("/restaurants/similar/{restaurant_id}")
def find_similar_restaurants(restaurant_id: str, limit: int = 5):
    """Find similar restaurants"""
    try:
        similar = vector_store.get_similar_restaurants(
            restaurant_id,
            n_results=limit
        )
        return {"similar_restaurants": similar}
    except Exception as e:
        logger.error(f"Error finding similar restaurants: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@app.post("/insights/generate")
def generate_insights(request: MarketInsightRequest):
    """Generate AI insights for market data"""
    try:
        market_data = market_agent.analyze_competition(request.location)
        insights = insights_generator.generate_market_insights(
            market_data,
            f"{request.location['lat']}, {request.location['lng']}"
        )
        return {
            "market_data": market_data,
            "ai_insights": insights
        }
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@app.post("/stream/review")
def stream_review(review: ReviewData, background_tasks: BackgroundTasks):
    """Stream a new restaurant review"""
    try:
        # Process review in background
        background_tasks.add_task(
            realtime_processor.stream_review,
            {
                "restaurant_name": review.restaurant_name,
                "review_text": review.review_text,
                "rating": review.rating,
                "source": review.source
            }
        )
        return {"status": "accepted", "message": "Review queued for processing"}
    except Exception as e:
        logger.error(f"Error streaming review: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@app.get("/restaurants/top")
def get_top_restaurants(location: Optional[Dict[str, float]] = None, limit: int = 10):
    """Get top-rated restaurants in an area"""
    try:
        restaurants = market_agent.search_restaurants(
            location=location or config.DEFAULT_LOCATION
        )
        # Sort by rating and take top N
        top_restaurants = sorted(
            restaurants,
            key=lambda x: x.get('rating', 0),
            reverse=True
        )[:limit]
        return {"top_restaurants": top_restaurants}
    except Exception as e:
        logger.error(f"Error getting top restaurants: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )

@app.get("/market/heatmap")
def generate_heatmap(query: LocationQuery):
    """Generate restaurant density heatmap"""
    try:
        heatmap = market_agent.generate_heatmap(
            location={"lat": query.lat, "lng": query.lng},
            radius=query.radius
        )
        return {"heatmap_data": heatmap._repr_html_()}
    except Exception as e:
        logger.error(f"Error generating heatmap: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "timestamp": datetime.now().isoformat()}
        )
