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
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'bitebase-db-cluster.cluster-c36ga22k8s51.us-east-1.rds.amazonaws.com')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'database_admin')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'Data1234!*')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'bitebaseDB')
    DATABASE_URL = os.getenv('DATABASE_URL', 
        f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}')

    # Neo4j settings
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

    # MinIO settings
    MINIO_HOST = os.getenv('MINIO_HOST', 'localhost')
    MINIO_PORT = int(os.getenv('MINIO_PORT', '9000'))
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'database_admin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'Data1234!*')
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
    
    # BiteBase 4P Analytics Configuration
    
    # 1. Product Analytics
    PRODUCT_ANALYTICS = {
        'menu_insights': {
            'popularity_threshold': 0.1,     # Top 10% items
            'cost_margin_alert': 0.15,      # 15% minimum margin
            'seasonal_correlation': 0.7,     # Correlation threshold for seasonal items
            'trend_detection': {
                'window_size': '90d',
                'confidence_level': 0.95
            }
        },
        'sales_tracking': {
            'update_frequency': '5m',        # Real-time sales tracking
            'trend_analysis_window': '90d',
            'performance_metrics': [
                'revenue', 'quantity', 'profit_margin', 'reorder_rate'
            ]
        },
        'inventory': {
            'low_stock_threshold': 0.2,      # 20% of max stock
            'reorder_point_buffer': 1.5,     # Safety stock multiplier
            'forecast_horizon': '14d',       # 2-week forecast
            'stock_rotation_alert': '48h'    # Alert for items close to expiry
        }
    }

    # 2. Place Analytics
    PLACE_ANALYTICS = {
        'market_analysis': {
            'demographic_radius': 5000,      # meters
            'competitor_radius': 2000,       # meters
            'factors': {
                'income_level': 0.3,
                'population_density': 0.2,
                'competition_density': 0.2,
                'foot_traffic': 0.3
            }
        },
        'location_optimization': {
            'delivery_radius': 5000,         # meters
            'hotspot_threshold': 0.7,        # Minimum density for delivery hotspot
            'route_optimization': {
                'max_delivery_time': '30m',
                'batch_size': 3              # Maximum orders per batch
            }
        },
        'expansion_planning': {
            'market_potential_factors': {
                'demographics': 0.3,
                'competition': 0.2,
                'real_estate': 0.2,
                'accessibility': 0.3
            },
            'risk_assessment_window': '365d'
        }
    }

    # 3. Price Analytics
    PRICE_ANALYTICS = {
        'dynamic_pricing': {
            'max_adjustment': 0.2,           # Maximum 20% price adjustment
            'factors': {
                'demand': 0.4,
                'competition': 0.3,
                'inventory': 0.2,
                'time_of_day': 0.1
            },
            'update_frequency': '1h'
        },
        'revenue_optimization': {
            'target_margin': 0.3,            # 30% target profit margin
            'price_elasticity_window': '90d',
            'bundle_discount_threshold': 0.15 # 15% discount for bundles
        },
        'forecasting': {
            'methods': ['prophet', 'arima', 'lstm'],
            'horizon': '90d',
            'confidence_interval': 0.95,
            'seasonality_modes': ['daily', 'weekly', 'monthly']
        }
    }

    # 4. Promotion Analytics
    PROMOTION_ANALYTICS = {
        'campaign_management': {
            'channel_mix': {
                'email': 0.3,
                'sms': 0.2,
                'push': 0.2,
                'social': 0.3
            },
            'effectiveness_metrics': [
                'conversion_rate', 'roi', 'customer_acquisition_cost'
            ],
            'ab_testing': {
                'min_sample_size': 1000,
                'confidence_level': 0.95,
                'test_duration': '14d'
            }
        },
        'customer_insights': {
            'segmentation': {
                'rfm_weights': {
                    'recency': 0.35,
                    'frequency': 0.35,
                    'monetary': 0.3
                },
                'update_frequency': '7d',
                'min_transaction_count': 3
            },
            'loyalty_program': {
                'points_multiplier': 1.0,
                'tier_thresholds': [100, 500, 1000],
                'reward_ratio': 0.1          # 10% back in points
            }
        },
        'sentiment_analysis': {
            'sources': ['reviews', 'social_media', 'surveys'],
            'update_frequency': '1h',
            'alert_threshold': -0.2,         # Alert on negative sentiment
            'min_review_count': 10
        }
    }

    # Geospatial pricing settings (original pricing settings maintained for compatibility)
    PRICING_SETTINGS = {
        'h3_resolution': 7,  # H3 hexagon resolution
        'max_discount': 30,  # Maximum discount percentage
        'base_discount': 10, # Base discount percentage
        'peak_hours': [11, 12, 13, 17, 18, 19, 20],  # Peak hours (24h format)
        'weekend_premium': 1.1,  # Weekend price multiplier
        'event_premium': 1.2,  # Special event price multiplier
        'max_price_range': 2.0  # Maximum price multiplier
    }

    # Vector store settings
    VECTOR_STORE_DIR = os.path.join(
        '/app/data/vector_store' if IS_CONTAINER else
        os.path.join(pathlib.Path(__file__).parent.parent.absolute(), 'data', 'vector_store')
    )
    
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

    # Performance settings
    REALTIME_METRICS = {
        'sales_window': '24h',
        'trend_window': '7d',
        'alert_thresholds': {
            'sales_drop': -15,  # Percentage
            'stock_low': 20,    # Percentage
            'rating_drop': -0.5 # Absolute
        }
    }
    
    # Analytics settings
    ANALYTICS_CONFIG = {
        'product_insights': {
            'trend_period': '90d',
            'min_orders': 10,
            'seasonality_window': '365d'
        },
        'customer_segments': {
            'recency_weight': 0.35,
            'frequency_weight': 0.35,
            'monetary_weight': 0.3,
            'segment_count': 5
        },
        'promotion_analysis': {
            'roi_threshold': 1.5,
            'min_campaign_duration': '7d',
            'significance_level': 0.95
        }
    }
    
    # Data storage paths
    BASE_DIR = pathlib.Path(__file__).parent.parent.absolute()
    DATA_DIR = '/app/data' if IS_CONTAINER else os.path.join(BASE_DIR, 'data')
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
    
    # Health check endpoints
    HEALTH_CHECK_ENDPOINTS = {
        'kafka': f"{KAFKA_BOOTSTRAP_SERVERS}/_health",
        'postgres': f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
    }
    
    # Monitoring settings
    PROMETHEUS_PORT = 9090
    GRAFANA_PORT = 3000
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_THRESHOLD = 5
    CIRCUIT_BREAKER_TIMEOUT = 60
    
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
        os.makedirs(cls.VECTOR_STORE_DIR, exist_ok=True)
        
    @classmethod
    def get_vector_store_settings(cls) -> Dict:
        """Get vector store settings"""
        return {
            "persist_directory": cls.VECTOR_STORE_DIR,
            "embedding_model": cls.VECTOR_SEARCH['embedding_model'],
            "min_similarity_score": cls.VECTOR_SEARCH['min_similarity_score']
        }
