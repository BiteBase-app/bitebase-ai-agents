# Restaurant BI System API Endpoints

Complete documentation of all available API endpoints. Base URL: `http://your-domain:8080`

## Market Analysis Endpoints

### Base Market Analysis
```
POST /market/analyze
```
Analyze market data for a location
```json
{
    "lat": 51.5074,
    "lng": -0.1278,
    "radius": 5000,
    "cuisine_type": "italian"
}
```

### Restaurant Search
```
POST /search/semantic
```
Perform semantic search for restaurants
```json
{
    "query": "cozy italian restaurant",
    "filters": {"cuisine": "italian"},
    "limit": 10
}
```

### Similar Restaurants
```
POST /restaurants/similar/{restaurant_id}
```
Find similar restaurants based on features

### Top Restaurants
```
GET /restaurants/top?location={"lat":51.5074,"lng":-0.1278}&limit=10
```
Get top-rated restaurants in an area

### Market Heatmap
```
GET /market/heatmap
```
Generate restaurant density heatmap
```json
{
    "lat": 51.5074,
    "lng": -0.1278,
    "radius": 5000
}
```

## Geospatial Analysis Endpoints

### Restaurant Clusters
```
POST /geospatial/clusters/analyze
```
Analyze restaurant clusters using DBSCAN
```json
{
    "locations": [{"lat": 51.5074, "lng": -0.1278}],
    "eps_km": 0.5,
    "min_samples": 5
}
```

### Price Heatmap
```
POST /geospatial/prices/heatmap
```
Generate price heatmap using H3 hexagons
```json
{
    "restaurants": [...],
    "center": {"lat": 51.5074, "lng": -0.1278},
    "zoom": 12
}
```

### Population Analysis
```
POST /geospatial/population/analyze
```
Analyze population impact on restaurant success
```json
{
    "location": {"lat": 51.5074, "lng": -0.1278},
    "radius_km": 1.0
}
```

### Growth Prediction
```
POST /geospatial/growth/predict
```
Predict future restaurant growth zones
```json
{
    "historical_data": [...],
    "prediction_days": 365
}
```

## Dynamic Pricing Endpoints

### Optimize Price
```
POST /pricing/optimize
```
Get optimal price prediction
```json
{
    "customer_count": 50,
    "competition_density": 3,
    "avg_income": 75000,
    "peak_hour": true,
    "weekend": false
}
```

### Dynamic Price
```
POST /pricing/dynamic
```
Get dynamic price adjustment
```json
{
    "base_price": 15.99,
    "current_demand": 75,
    "time_of_day": 18,
    "day_of_week": 5,
    "special_events": ["concert", "game_day"]
}
```

## Customer Engagement Endpoints

### Handle Message
```
POST /bot/message
```
Handle customer message and generate response
```json
{
    "customer_id": "cust_123",
    "message": "What's good near me?",
    "location": {"lat": 51.5074, "lng": -0.1278},
    "phone_number": "+1234567890"
}
```

### Process Activity
```
POST /bot/activity
```
Process customer activity for engagement
```json
{
    "customer_id": "cust_123",
    "activity_type": "location_update",
    "activity_data": {
        "location": {"lat": 51.5074, "lng": -0.1278},
        "timestamp": "2024-02-19T12:00:00Z"
    }
}
```

## Advanced Analytics Endpoints

### POS Insights
```
POST /advanced/pos/insights
```
Get insights from POS data
```json
{
    "restaurant_id": "rest_123",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-02-19T00:00:00Z"
}
```

### Emotion Analysis
```
POST /advanced/emotions/analyze
```
Analyze customer emotions from feedback
```json
{
    "texts": [
        "Great service!",
        "Food was cold"
    ]
}
```

### Migration Tracking
```
POST /advanced/customers/migration
```
Track customer migration patterns
```json
{
    "restaurant_id": "rest_123",
    "timeframe_days": 90
}
```

### Demand Forecast
```
POST /advanced/demand/forecast
```
Generate demand forecast
```json
{
    "restaurant_id": "rest_123",
    "forecast_days": 30
}
```

### Menu Performance Analysis
```
POST /advanced/menu/performance
```
Analyze menu performance including costs and profitability
```json
{
    "restaurant_id": "rest_123",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-02-19T00:00:00Z"
}
```
Response includes:
- Top and low performing dishes
- Food cost analysis
- Seasonal trends
- Pricing recommendations
- Category performance

### Staff Efficiency Analysis
```
POST /advanced/staff/efficiency
```
Analyze staff performance and scheduling optimization
```json
{
    "restaurant_id": "rest_123",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-02-19T00:00:00Z"
}
```
Response includes:
- Individual staff metrics
- Peak hour analysis
- Labor cost efficiency
- Scheduling recommendations
- Performance trends

### Customer Recommendations
```
POST /advanced/customers/recommendations
```
Get personalized customer recommendations
```json
{
    "customer_id": "cust_123"
}
```

## Social Media Analysis Endpoints

### Analyze Social Data
```
POST /social/analyze
```
Get comprehensive social media analysis
```json
{
    "restaurant_name": "Restaurant Name",
    "days_back": 30,
    "limit": 100
}
```

### Sentiment Analysis
```
POST /social/sentiment
```
Analyze text sentiment
```json
{
    "texts": [
        "Great atmosphere and service!",
        "Will never come back here again"
    ]
}
```

### Trend Detection
```
POST /social/trends
```
Detect trending topics
```json
{
    "texts": [...],
    "min_topics": 3,
    "max_topics": 10
}
```

### Social Graph
```
POST /social/graph
```
Build social knowledge graph
```json
{
    "restaurant_name": "Restaurant Name",
    "social_data": [...]
}
```

## Streaming Endpoints

### Stream Review
```
POST /stream/review
```
Stream a new restaurant review
```json
{
    "restaurant_name": "Restaurant Name",
    "review_text": "Amazing food!",
    "rating": 5,
    "source": "google"
}
```

## Health Check
```
GET /
```
API health check endpoint
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-02-19T06:45:00Z"
}