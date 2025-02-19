# Restaurant BI System

Open-source Business Intelligence system for restaurant market analysis using AI and vector search capabilities.

## Features

- 🌐 Multi-source data collection (Google Maps, Yelp)
- 🔍 Semantic search using ChromaDB and Sentence-BERT
- 📊 Advanced analytics with POS integration
- 🗺️ Interactive visualization with Streamlit
- 🤖 LLM-powered insights (GPT-4 or Llama-2)
- ⚡ Real-time analytics with Kafka
- 📱 Social media listening and analysis
- 💰 AI-powered dynamic pricing
- 💬 Real-time customer engagement chatbot
- 🔮 AI-powered demand forecasting
- 👥 Customer migration tracking
- 📈 Restaurant competition analysis
- 🎯 AI-powered recommendations

## Technology Stack

- **Data Collection**: Scrapy, BeautifulSoup, Google Maps API
- **Vector Search**: ChromaDB, Sentence-BERT
- **Data Processing**: Pandas, spaCy
- **Visualization**: Streamlit, Folium
- **Database**: PostgreSQL, ChromaDB (vector store)
- **LLM Integration**: OpenAI GPT-4 or Llama-2
- **Real-time Streaming**: Apache Kafka
- **Machine Learning**: XGBoost, LightGBM, Prophet
- **Storage**: MinIO (S3-compatible)
- **Graph Database**: Neo4j
- **ETL**: Apache Airflow
- **Sentiment Analysis**: RoBERTa, VADER
- **Geospatial**: H3, Folium
- **Chat Integration**: Twilio WhatsApp API
- **Emotion Detection**: DistilBERT for emotions
- **Topic Modeling**: BERTopic
- **Version Control**: Git-sync for Airflow DAGs

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd restaurant-bi
```

### Option 1: Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root:
```env
GOOGLE_MAPS_API_KEY=your_api_key_here
DATABASE_URL=postgresql://localhost:5432/restaurant_bi
OPENAI_API_KEY=your-openai-key  # For GPT-4
TWILIO_ACCOUNT_SID=your-twilio-sid  # For WhatsApp integration
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_NUMBER=your-whatsapp-number
```

### Option 2: Docker Deployment

1. Start all services:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL (localhost:5432)
- MinIO (localhost:9000, console: 9001)
- Neo4j (localhost:7474, 7687)
- ChromaDB (localhost:8000)
- Streamlit Dashboard (localhost:8501)
- REST API (localhost:8080/docs)
- Apache Airflow (localhost:8081)
- Apache Kafka (localhost:9092)
- Zookeeper (localhost:2181)

## Advanced Analytics Features

### POS Data Integration
```python
from restaurant_bi.analytics.advanced_analytics import AdvancedAnalytics

analytics = AdvancedAnalytics(config)

# Get POS insights
insights = analytics.get_pos_insights(
    restaurant_id="restaurant_001",
    date_range=(start_date, end_date)
)
```

### Dynamic Pricing
```python
from restaurant_bi.pricing.geospatial_pricing import GeospatialPricing

pricing = GeospatialPricing(config)

# Get optimal price for location
optimal_price = pricing.predict_optimal_price({
    'customer_count': 50,
    'competition_density': 3,
    'avg_income': 75000,
    'peak_hour': True,
    'weekend': False
})

# Generate price heatmap
heatmap = pricing.generate_price_heatmap(
    location={'lat': 51.5074, 'lng': -0.1278},
    radius_km=1.0
)
```

### Real-Time Customer Engagement
```python
from restaurant_bi.chatbot.engagement_bot import EngagementBot

bot = EngagementBot(config)

# Handle customer message
response = bot.handle_customer_message(
    message="What's good near me?",
    customer_data={"id": "customer_001"},
    location={'lat': 51.5074, 'lng': -0.1278}
)

# Send offer via WhatsApp
bot.send_whatsapp_message(
    to_number="+1234567890",
    message="Special offer just for you!"
)
```

### Emotion Analysis
```python
# Analyze customer emotions
emotions = analytics.analyze_customer_emotions(
    texts=["Great service!", "Food was cold"]
)
```

### Customer Migration Tracking
```python
# Track customer movement patterns
patterns = analytics.track_customer_migration(
    restaurant_id="restaurant_001",
    timeframe_days=90
)
```

### Social Media Analysis
```python
from restaurant_bi.social.social_listener import SocialListener

listener = SocialListener(config)

# Collect and analyze social data
data = listener.collect_social_data(
    restaurant_name="Restaurant Name",
    days_back=30
)

# Analyze trends
trends = listener.detect_trends(texts)
```

## API Endpoints

The system provides a REST API with comprehensive documentation at http://localhost:8080/docs

### Market Analysis
- `POST /market/analyze` - Get market analysis for a location
- `GET /market/heatmap` - Generate restaurant density heatmap

### Restaurant Search
- `POST /search/semantic` - Semantic search for restaurants
- `POST /restaurants/similar/{restaurant_id}` - Find similar restaurants
- `GET /restaurants/top` - Get top-rated restaurants

### Social Media Analysis
- `POST /social/analyze` - Get comprehensive social media analysis
- `POST /social/sentiment` - Analyze text sentiment
- `POST /social/trends` - Detect trending topics
- `POST /social/graph` - Build social knowledge graph

### Dynamic Pricing & Engagement
- `POST /pricing/optimize` - Get optimal price prediction
- `POST /pricing/dynamic` - Get dynamic price adjustment
- `POST /bot/message` - Handle customer message
- `POST /bot/activity` - Process customer activity

### Advanced Analytics
- `POST /advanced/pos/insights` - Get POS data insights
- `POST /advanced/emotions/analyze` - Analyze customer emotions
- `POST /advanced/customers/migration` - Track customer migration
- `POST /advanced/demand/forecast` - Generate demand forecasts

## Project Structure

```
restaurant_bi/
├── __init__.py
├── config.py               # Configuration settings
├── market_analysis_agent.py # Main analysis logic
├── analytics/             # Advanced analytics
├── demo.py                # Streamlit demo
├── api/                   # REST API
│   └── main.py           # FastAPI implementation
├── llm/                   # LLM integration
│   └── insights_generator.py # AI insights generation
├── social/               # Social media analysis
│   └── social_listener.py # Social data processing
├── streaming/            # Real-time processing
│   └── realtime_processor.py # Kafka streaming
├── pricing/             # Dynamic pricing
│   └── geospatial_pricing.py # Location-based pricing
├── chatbot/             # Customer engagement
│   └── engagement_bot.py # Real-time chat bot
├── dags/                  # Airflow DAG definitions
├── scrapers/
│   └── restaurant_scraper.py # Multi-source data collection
└── vectorstore/
    └── embedding_store.py   # Vector search implementation
```

## Development

### Running Tests
```bash
pytest
```

### Code Style
We follow PEP 8 guidelines for Python code.

### Docker Services Management

Stop all services:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f [service-name]
```

Rebuild services:
```bash
docker-compose up -d --build
