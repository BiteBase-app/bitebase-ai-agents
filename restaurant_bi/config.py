"""
Configuration settings for the Restaurant Market Analysis Agent
"""
from typing import Dict, Any
from dotenv import load_dotenv
import os
import pathlib
import logging

# Initialize logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings"""
    
    # API Keys
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

    # Container environment settings
    IS_CONTAINER = os.getenv('CONTAINER', 'false').lower() == 'true'
    
    # Database settings
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'supersecurepassword')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'restaurant_bi')
    DATABASE_URL = os.getenv('DATABASE_URL', 
        f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}')

    # Neo4j settings
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

    # MinIO settings
    MINIO_HOST = os.getenv('MINIO_HOST', 'localhost')
    MINIO_PORT = int(os.getenv('MINIO_PORT', '9000'))
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'admin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'supersecurepassword')
    MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').lower() == 'true'

    # LLM settings
    LLM_MODEL_TYPE = os.getenv('LLM_MODEL_TYPE', 'openai')  # 'openai' or 'llama'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    LLAMA_MODEL_PATH = os.getenv('LLAMA_MODEL_PATH', 'meta-llama/Llama-2-7b')
    LLM_DEVICE = os.getenv('LLM_DEVICE', 'cpu')  # 'cpu' or 'cuda'
    ENABLE_REALTIME_INSIGHTS = os.getenv('ENABLE_REALTIME_INSIGHTS', 'true').lower() == 'true'

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPICS = {
        'REVIEWS': 'restaurant_reviews',
        'MARKET_UPDATES': 'market_updates'
    }

    # Chatbot settings
    TWILIO_ENABLED = os.getenv('TWILIO_ENABLED', 'false').lower() == 'true'
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
    
    # Geospatial pricing settings
    PRICING_SETTINGS = {
        'h3_resolution': 7,  # H3 hexagon resolution
        'max_discount': 30,  # Maximum discount percentage
        'base_discount': 10, # Base discount percentage
        'peak_hours': [11, 12, 13, 17, 18, 19, 20],  # Peak hours (24h format)
        'weekend_premium': 1.1,  # Weekend price multiplier
        'event_premium': 1.2,  # Special event price multiplier
        'max_price_range': 2.0  # Maximum price multiplier
    }

    # ChromaDB settings
    CHROMA_HOST = os.getenv('CHROMA_HOST', 'localhost')
    CHROMA_PORT = int(os.getenv('CHROMA_PORT', '8000'))
    
    # Analysis settings
    DEFAULT_SEARCH_RADIUS = 5000  # meters
    MIN_RATINGS_THRESHOLD = 5
    COMPETITION_RADIUS = 1000  # meters
    DEFAULT_CACHE_TTL = 3600  # seconds
    
    # Location settings
    DEFAULT_LOCATION = {
        'lat': 51.5074,  # London as default
        'lng': -0.1278
    }
    
    # Data storage paths
    BASE_DIR = pathlib.Path(__file__).parent.parent.absolute()
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    CHROMA_DIR = os.path.join(DATA_DIR, 'chroma')
    
    # Adjust paths for containerized environment
    if IS_CONTAINER:
        DATA_DIR = '/app/data'
        CHROMA_DIR = '/app/data/chroma'
        
    MINIO_BUCKET = 'restaurant-data'
    
    # Scraping settings
    SCRAPER_SETTINGS = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; RestaurantBI/1.0)',
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1.0
    }
    
    # Vector search settings
    VECTOR_SEARCH = {
        'embedding_model': 'all-MiniLM-L6-v2',
        'min_similarity_score': 0.7,
        'max_results': 100
    }
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate required configuration settings"""
        missing_vars = []
        
        if not cls.GOOGLE_MAPS_API_KEY:
            missing_vars.append('GOOGLE_MAPS_API_KEY')
        
        # Check database connection
        if not all([cls.POSTGRES_USER, cls.POSTGRES_PASSWORD, cls.POSTGRES_HOST]):
            missing_vars.append('DATABASE_CREDENTIALS')
            
        # Check MinIO credentials
        if not all([cls.MINIO_ACCESS_KEY, cls.MINIO_SECRET_KEY]):
            missing_vars.append('MINIO_CREDENTIALS')
        
        # Check LLM configuration
        if cls.LLM_MODEL_TYPE == 'openai' and not cls.OPENAI_API_KEY:
            missing_vars.append('OPENAI_API_KEY')
        elif cls.LLM_MODEL_TYPE == 'llama' and not os.path.exists(cls.LLAMA_MODEL_PATH):
            logger.warning(
                f"Llama model not found at {cls.LLAMA_MODEL_PATH}. "
                "Will download from Hugging Face."
            )
            
        # Check Twilio configuration if enabled
        if cls.TWILIO_ENABLED and not all([
            cls.TWILIO_ACCOUNT_SID,
            cls.TWILIO_AUTH_TOKEN,
            cls.TWILIO_WHATSAPP_NUMBER
        ]):
            missing_vars.append('TWILIO_CREDENTIALS')
        
        # Create necessary directories
        cls._create_directories()
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return {
            "status": "valid",
            "database_url": cls.DATABASE_URL,
            "api_keys_configured": bool(cls.GOOGLE_MAPS_API_KEY),
            "data_dir_exists": os.path.exists(cls.DATA_DIR),
            "environment": "container" if cls.IS_CONTAINER else "local",
            "services": {
                "minio_endpoint": f"{'https' if cls.MINIO_SECURE else 'http'}://{cls.MINIO_HOST}:{cls.MINIO_PORT}"
            }
        }
    
    @classmethod
    def _create_directories(cls) -> None:
        """Create necessary data directories"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.CHROMA_DIR, exist_ok=True)
        
    @classmethod
    def get_chroma_settings(cls) -> Dict:
        """Get ChromaDB connection settings"""
        return {
            "host": cls.CHROMA_HOST,
            "port": cls.CHROMA_PORT
        } if cls.IS_CONTAINER else None