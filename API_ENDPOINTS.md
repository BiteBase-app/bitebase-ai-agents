# Restaurant BI System API Endpoints

Base URL: `https://api.bitebase.app/agents/v1`

## Authentication
All endpoints require an `Authorization` header:
```http
Authorization: Bearer <your_api_token>
```

## Common Response Format
All endpoints follow a standard response format:
```json
{
    "status": "success|error",
    "data": {},
    "message": "Optional message",
    "timestamp": "2024-02-19T06:45:00Z"
}
```

## Market Analysis Endpoints

### Analyze Market
```http
POST /market/analyze
```
Comprehensive market analysis for a location
```json
{
    "location": {
        "lat": 51.5074,
        "lng": -0.1278,
        "address": "Optional full address"
    },
    "parameters": {
        "radius_meters": 5000,
        "cuisine_type": "italian",
        "price_range": ["$$", "$$$"],
        "include_demographics": true,
        "include_competition": true
    },
    "timeframe": {
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-02-19T00:00:00Z"
    }
}
```

### Search Restaurants
```http
POST /restaurants/search
```
Advanced semantic search with filtering
```json
{
    "query": {
        "text": "cozy italian restaurant with outdoor seating",
        "semantic_boost": 0.7
    },
    "filters": {
        "cuisine": ["italian", "mediterranean"],
        "price_range": ["$$", "$$$"],
        "features": ["outdoor_seating", "wheelchair_accessible"],
        "rating_min": 4.0,
        "open_now": true
    },
    "location": {
        "lat": 51.5074,
        "lng": -0.1278,
        "radius_meters": 5000
    },
    "pagination": {
        "limit": 10,
        "offset": 0
    },
    "sort": {
        "by": "rating|distance|popularity",
        "order": "desc"
    }
}
```

### Similar Restaurants
```http
POST /restaurants/{restaurant_id}/similar
```
Find similar restaurants with customizable criteria
```json
{
    "similarity_criteria": {
        "cuisine_weight": 0.3,
        "price_weight": 0.2,
        "location_weight": 0.2,
        "ambiance_weight": 0.3
    },
    "filters": {
        "min_similarity_score": 0.7,
        "max_distance_km": 10
    },
    "limit": 10
}
```

## Geospatial Analysis Endpoints

### Analyze Clusters
```http
POST /geospatial/clusters
```
Advanced clustering analysis
```json
{
    "analysis_type": "dbscan|kmeans|hierarchical",
    "parameters": {
        "eps_km": 0.5,
        "min_samples": 5,
        "max_clusters": 10
    },
    "locations": [
        {
            "lat": 51.5074,
            "lng": -0.1278,
            "weight": 1.0,
            "metadata": {
                "revenue": 50000,
                "customer_count": 1000
            }
        }
    ],
    "include_demographics": true,
    "visualization_format": "geojson|h3|svg"
}
```

### Generate Heatmap
```http
POST /geospatial/heatmap
```
Customizable heatmap generation
```json
{
    "type": "density|price|popularity|revenue",
    "parameters": {
        "resolution": 8,
        "smoothing_factor": 0.5,
        "color_scheme": "viridis"
    },
    "bounds": {
        "north": 51.5074,
        "south": 51.4074,
        "east": -0.1178,
        "west": -0.1378
    },
    "filters": {
        "min_value": 0,
        "max_value": 100,
        "exclude_outliers": true
    },
    "output_format": "geojson|png|svg"
}
```

## Dynamic Pricing Endpoints

### Optimize Price
```http
POST /pricing/optimize
```
AI-driven price optimization
```json
{
    "restaurant_data": {
        "id": "rest_123",
        "current_prices": {
            "item_1": 15.99,
            "item_2": 12.99
        },
        "costs": {
            "item_1": 5.50,
            "item_2": 4.20
        }
    },
    "market_conditions": {
        "customer_count": 50,
        "competition_density": 3,
        "avg_income": 75000,
        "events_nearby": ["concert", "game_day"]
    },
    "time_factors": {
        "peak_hour": true,
        "weekend": false,
        "season": "summer"
    },
    "optimization_goals": {
        "revenue_weight": 0.6,
        "volume_weight": 0.4,
        "min_margin_percent": 20
    }
}
```

## Analytics Endpoints

### Menu Performance
```http
POST /analytics/menu
```
Comprehensive menu analysis
```json
{
    "restaurant_id": "rest_123",
    "timeframe": {
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-02-19T00:00:00Z",
        "compare_to_previous": true
    },
    "analysis_types": [
        "item_performance",
        "category_analysis",
        "price_elasticity",
        "cross_selling",
        "daypart_analysis"
    ],
    "metrics": [
        "revenue",
        "profit_margin",
        "order_frequency",
        "customer_satisfaction"
    ],
    "segmentation": {
        "by_daypart": true,
        "by_customer_type": true,
        "by_season": true
    }
}
```

### Customer Analytics
```http
POST /analytics/customers
```
Advanced customer behavior analysis
```json
{
    "restaurant_id": "rest_123",
    "analysis_types": [
        "segmentation",
        "lifetime_value",
        "churn_risk",
        "preference_analysis"
    ],
    "timeframe": {
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-02-19T00:00:00Z"
    },
    "segmentation_criteria": {
        "visit_frequency": true,
        "spending_patterns": true,
        "menu_preferences": true,
        "demographic": true
    }
}
```

## Streaming Endpoints

### Real-time Analytics Stream
```http
GET /stream/analytics
```
WebSocket connection for real-time analytics
```json
{
    "subscriptions": [
        "orders",
        "revenue",
        "customer_feedback",
        "kitchen_status"
    ],
    "aggregation_interval": "1m",
    "filters": {
        "min_order_value": 10,
        "locations": ["loc_123", "loc_124"]
    }
}
```

## Rate Limits
- Free tier: 1000 requests/day
- Professional tier: 10000 requests/day
- Enterprise tier: Unlimited

## Versioning
- Current version: v1
- Deprecation notice: 6 months
- Legacy version support: 12 months