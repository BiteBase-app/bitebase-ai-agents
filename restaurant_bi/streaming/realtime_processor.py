"""
Real-time data streaming processor using Kafka
Handles streaming restaurant data and generates real-time insights
"""
from typing import Callable, Dict, Optional
from kafka import KafkaProducer, KafkaConsumer
import json
import logging
from datetime import datetime
import time
from ..config import Config
from ..llm.insights_generator import InsightsGenerator

logger = logging.getLogger(__name__)

class RealtimeProcessor:
    """Processes real-time restaurant data streams"""
    
    def __init__(self, config: Config):
        """
        Initialize the real-time processor
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        self.insights_generator = InsightsGenerator(config)
        
        self.batch_size = 100
        self.batch_timeout = 30  # seconds
        self._batch = []
        self._last_flush = time.time()
    
    async def stream_review(self, review_data: Dict) -> bool:
        """
        Stream a new restaurant review
        
        Args:
            review_data: Dictionary containing review information
            
        Returns:
            bool: Success status
        """
        try:
            # Add timestamp
            review_data['timestamp'] = datetime.now().isoformat()
            
            # Generate AI insights if enabled
            if self.config.ENABLE_REALTIME_INSIGHTS:
                insights = self.insights_generator.generate_restaurant_summary(
                    review_data['restaurant_name'],
                    review_data['review_text']
                )
                review_data['ai_insights'] = insights
            
            # Improved batched streaming with automatic flush
            self._batch.append(review_data)
            
            should_flush = (
                len(self._batch) >= self.batch_size or
                time.time() - self._last_flush > self.batch_timeout
            )
            
            if should_flush:
                await self._flush_batch()
            
            return True
            
        except Exception as e:
            logger.error(f"Error streaming review: {str(e)}")
            return False
    
    async def _flush_batch(self):
        """Flush batched reviews to Kafka"""
        if not self._batch:
            return
            
        self.producer.send('restaurant_reviews', self._batch)
        self.producer.flush()
        self._batch = []
        self._last_flush = time.time()
    
    def stream_market_update(self, market_data: Dict) -> bool:
        """
        Stream market analysis updates
        
        Args:
            market_data: Dictionary containing market analysis data
            
        Returns:
            bool: Success status
        """
        try:
            # Add timestamp
            market_data['timestamp'] = datetime.now().isoformat()
            
            # Generate market insights if enabled
            if self.config.ENABLE_REALTIME_INSIGHTS:
                insights = self.insights_generator.generate_market_insights(
                    market_data,
                    market_data.get('location', 'Unknown')
                )
                market_data['ai_insights'] = insights
            
            # Send to Kafka
            self.producer.send('market_updates', market_data)
            self.producer.flush()
            
            logger.info(f"Successfully streamed market update for {market_data.get('location', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error streaming market update: {str(e)}")
            return False
    
    def consume_stream(
        self,
        topic: str,
        handler: Callable[[Dict], None],
        filters: Optional[Dict] = None
    ) -> None:
        """
        Consume streaming data from a topic
        
        Args:
            topic: Kafka topic to consume from
            handler: Callback function to process messages
            filters: Optional filters for messages
        """
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.config.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True
        )
        
        try:
            for message in consumer:
                data = message.value
                
                # Apply filters if provided
                if filters and not self._apply_filters(data, filters):
                    continue
                
                # Process message
                handler(data)
                
        except Exception as e:
            logger.error(f"Error consuming stream: {str(e)}")
            consumer.close()
            
    def _apply_filters(self, data: Dict, filters: Dict) -> bool:
        """Apply filters to streaming data"""
        for key, value in filters.items():
            if key not in data or data[key] != value:
                return False
        return True
    
    def close(self):
        """Close Kafka connections"""
        if hasattr(self, 'producer'):
            self.producer.close()

# Example usage:
"""
config = Config()
processor = RealtimeProcessor(config)

# Stream a review
review = {
    'restaurant_name': 'Pizza Place',
    'review_text': 'Great pizza and service!',
    'rating': 5
}
processor.stream_review(review)

# Consume reviews
def handle_review(review_data):
    print(f"New review for {review_data['restaurant_name']}: {review_data['review_text']}")

# Start consuming in a separate thread
import threading
threading.Thread(
    target=processor.consume_stream,
    args=('restaurant_reviews', handle_review),
    daemon=True
).start()
"""
