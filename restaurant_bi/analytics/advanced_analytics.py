"""
Advanced analytics module for restaurant BI system
Handles POS integration, emotion detection, customer tracking, and predictive analytics
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from prophet import Prophet
from transformers import pipeline
import psycopg2
from neo4j import GraphDatabase
import logging
from ..config import Config

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """Advanced analytics for restaurant business intelligence"""
    
    def __init__(self, config: Config):
        """
        Initialize the advanced analytics module
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Initialize emotion detection model
        self.emotion_model = pipeline(
            "text-classification",
            model="bhadresh-savani/distilbert-emotion"
        )
        
        # Initialize database connections
        self.pos_conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
        
        self.neo4j_driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        
    def get_pos_insights(
        self,
        restaurant_id: str,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict:
        """
        Get insights from POS data
        
        Args:
            restaurant_id: Restaurant identifier
            date_range: Optional date range tuple (start, end)
            
        Returns:
            Dictionary containing POS insights
        """
        if not date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            date_range = (start_date, end_date)
            
        try:
            cursor = self.pos_conn.cursor()
            
            # Get top selling items
            cursor.execute("""
                SELECT menu_item, COUNT(*) as orders, SUM(price) as revenue
                FROM transactions
                WHERE restaurant_id = %s
                AND transaction_date BETWEEN %s AND %s
                GROUP BY menu_item
                ORDER BY orders DESC
                LIMIT 10
            """, (restaurant_id, date_range[0], date_range[1]))
            
            top_items = cursor.fetchall()
            
            # Get busiest hours
            cursor.execute("""
                SELECT EXTRACT(HOUR FROM transaction_date) as hour,
                       COUNT(*) as transactions
                FROM transactions
                WHERE restaurant_id = %s
                AND transaction_date BETWEEN %s AND %s
                GROUP BY hour
                ORDER BY transactions DESC
            """, (restaurant_id, date_range[0], date_range[1]))
            
            busy_hours = cursor.fetchall()
            
            return {
                "top_selling_items": [
                    {
                        "item": item[0],
                        "orders": item[1],
                        "revenue": float(item[2])
                    } for item in top_items
                ],
                "peak_hours": [
                    {
                        "hour": int(hour[0]),
                        "transactions": hour[1]
                    } for hour in busy_hours
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting POS insights: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def analyze_customer_emotions(
        self,
        texts: List[str]
    ) -> List[Dict]:
        """
        Perform deep emotion analysis on customer feedback
        
        Args:
            texts: List of customer feedback texts
            
        Returns:
            List of emotion analysis results
        """
        try:
            results = []
            for text in texts:
                emotion = self.emotion_model(text)[0]
                results.append({
                    "text": text,
                    "emotion": emotion["label"],
                    "confidence": emotion["score"]
                })
            return results
        except Exception as e:
            logger.error(f"Error analyzing emotions: {str(e)}")
            return []
    
    def track_customer_migration(
        self,
        restaurant_id: str,
        timeframe_days: int = 90
    ) -> Dict:
        """
        Track customer migration patterns
        
        Args:
            restaurant_id: Restaurant identifier
            timeframe_days: Number of days to analyze
            
        Returns:
            Dictionary containing migration patterns
        """
        try:
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (r1:Restaurant {id: $restaurant_id})
                    MATCH (c:Customer)-[v1:VISITS]->(r1)
                    MATCH (c)-[v2:VISITS]->(r2:Restaurant)
                    WHERE r1 <> r2
                    AND v2.date > v1.date
                    AND v2.date >= datetime() - duration('P' + $days + 'D')
                    RETURN r2.name as next_restaurant,
                           COUNT(DISTINCT c) as customer_count,
                           AVG(v2.date - v1.date) as avg_days_between
                    ORDER BY customer_count DESC
                    LIMIT 10
                """, restaurant_id=restaurant_id, days=str(timeframe_days))
                
                migration_data = []
                for record in result:
                    migration_data.append({
                        "restaurant": record["next_restaurant"],
                        "customer_count": record["customer_count"],
                        "avg_days_between": record["avg_days_between"].days
                    })
                
                return {
                    "migration_patterns": migration_data,
                    "timeframe_days": timeframe_days,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error tracking customer migration: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def forecast_demand(
        self,
        restaurant_id: str,
        forecast_days: int = 30
    ) -> Dict:
        """
        Forecast demand using historical data and events
        
        Args:
            restaurant_id: Restaurant identifier
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary containing demand forecast
        """
        try:
            # Get historical data
            cursor = self.pos_conn.cursor()
            cursor.execute("""
                SELECT DATE(transaction_date) as date,
                       COUNT(*) as transactions,
                       SUM(total_amount) as revenue
                FROM transactions
                WHERE restaurant_id = %s
                GROUP BY DATE(transaction_date)
                ORDER BY date
            """, (restaurant_id,))
            
            data = cursor.fetchall()
            
            # Prepare data for Prophet
            df = pd.DataFrame(data, columns=['ds', 'y'])
            
            # Add event data
            events_df = self._get_local_events(restaurant_id)
            
            # Train model
            model = Prophet()
            if not events_df.empty:
                model.add_regressor('event_impact')
                df = df.merge(events_df, on='ds', how='left')
                df['event_impact'] = df['event_impact'].fillna(0)
            
            model.fit(df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=forecast_days)
            if not events_df.empty:
                future_events = self._get_future_events(restaurant_id, forecast_days)
                future = future.merge(future_events, on='ds', how='left')
                future['event_impact'] = future['event_impact'].fillna(0)
            
            forecast = model.predict(future)
            
            return {
                "forecast": [
                    {
                        "date": row['ds'].strftime('%Y-%m-%d'),
                        "predicted_transactions": int(row['yhat']),
                        "lower_bound": int(row['yhat_lower']),
                        "upper_bound": int(row['yhat_upper'])
                    }
                    for _, row in forecast.tail(forecast_days).iterrows()
                ],
                "seasonality": {
                    "weekly_pattern": model.weekly.iloc[-7:].to_dict(),
                    "yearly_pattern": model.yearly.iloc[-12:].to_dict()
                }
            }
            
        except Exception as e:
            logger.error(f"Error forecasting demand: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _get_local_events(self, restaurant_id: str) -> pd.DataFrame:
        """Get historical local events data"""
        # TODO: Implement event data collection
        return pd.DataFrame(columns=['ds', 'event_impact'])
    
    def _get_future_events(
        self,
        restaurant_id: str,
        days: int
    ) -> pd.DataFrame:
        """Get upcoming local events data"""
        # TODO: Implement future event data collection
        return pd.DataFrame(columns=['ds', 'event_impact'])
    
    def get_personalized_recommendations(
        self,
        customer_id: str
    ) -> Dict:
        """
        Generate personalized recommendations for a customer
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Dictionary containing personalized recommendations
        """
        try:
            cursor = self.pos_conn.cursor()
            
            # Get customer's order history
            cursor.execute("""
                SELECT menu_item, COUNT(*) as order_count
                FROM transactions
                WHERE customer_id = %s
                GROUP BY menu_item
                ORDER BY order_count DESC
                LIMIT 5
            """, (customer_id,))
            
            favorites = cursor.fetchall()
            
            # Get customer's visit patterns
            cursor.execute("""
                SELECT EXTRACT(DOW FROM transaction_date) as day_of_week,
                       COUNT(*) as visits
                FROM transactions
                WHERE customer_id = %s
                GROUP BY day_of_week
                ORDER BY visits DESC
                LIMIT 1
            """, (customer_id,))
            
            preferred_day = cursor.fetchone()
            
            return {
                "favorite_items": [
                    {"item": item[0], "order_count": item[1]}
                    for item in favorites
                ],
                "preferred_day": int(preferred_day[0]) if preferred_day else None,
                "recommendations": [
                    {
                        "type": "discount",
                        "item": favorites[0][0] if favorites else None,
                        "offer": "20% off your favorite item!"
                    },
                    {
                        "type": "timing",
                        "day": preferred_day[0] if preferred_day else None,
                        "offer": f"Visit us on your favorite day ({preferred_day[0]}) for a special treat!"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }