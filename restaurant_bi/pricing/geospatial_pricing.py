"""
Geospatial pricing optimization module using H3 hexagonal grid
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import h3
import folium
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import logging
from ..config import Config

logger = logging.getLogger(__name__)

class GeospatialPricing:
    """Handles dynamic pricing based on location and competition"""
    
    def __init__(self, config: Config):
        """
        Initialize the geospatial pricing module
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        
        # H3 resolution (7 is approximately 1km hexagons)
        self.h3_resolution = 7
    
    def get_location_hex(
        self,
        lat: float,
        lng: float
    ) -> str:
        """
        Get H3 hexagon index for a location
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            H3 index string
        """
        return h3.geo_to_h3(lat, lng, self.h3_resolution)
    
    def analyze_competition(
        self,
        location: Dict[str, float],
        radius_km: float = 1.0
    ) -> Dict:
        """
        Analyze competition in an area
        
        Args:
            location: Dictionary with lat/lng
            radius_km: Radius to analyze in kilometers
            
        Returns:
            Dictionary containing competition analysis
        """
        try:
            # Get central hexagon
            center_hex = self.get_location_hex(
                location['lat'],
                location['lng']
            )
            
            # Get neighboring hexagons
            hex_ring = h3.k_ring(center_hex, int(radius_km))
            
            # TODO: Get actual competitor data from database
            # For now, return sample data
            return {
                "center_hex": center_hex,
                "nearby_hexagons": list(hex_ring),
                "competitor_count": len(hex_ring),
                "avg_price": 15.0,
                "price_range": (10.0, 25.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competition: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def train_pricing_model(
        self,
        training_data: pd.DataFrame
    ) -> None:
        """
        Train the pricing model
        
        Args:
            training_data: DataFrame with features for price prediction
        """
        try:
            features = [
                'customer_count',
                'competition_density',
                'avg_income',
                'peak_hour',
                'weekend'
            ]
            
            X = training_data[features]
            y = training_data['price']
            
            self.model.fit(X, y)
            logger.info("Successfully trained pricing model")
            
        except Exception as e:
            logger.error(f"Error training pricing model: {str(e)}")
            raise
    
    def predict_optimal_price(
        self,
        features: Dict[str, float]
    ) -> Dict:
        """
        Predict optimal price based on features
        
        Args:
            features: Dictionary containing pricing features
            
        Returns:
            Dictionary containing price predictions
        """
        try:
            # Convert features to array
            feature_array = np.array([[
                features.get('customer_count', 0),
                features.get('competition_density', 0),
                features.get('avg_income', 0),
                features.get('peak_hour', 0),
                features.get('weekend', 0)
            ]])
            
            # Get prediction and confidence
            predicted_price = self.model.predict(feature_array)[0]
            
            # Get price ranges using tree variance
            predictions = []
            for estimator in self.model.estimators_:
                predictions.append(estimator.predict(feature_array)[0])
            
            confidence_interval = np.percentile(predictions, [5, 95])
            
            return {
                "optimal_price": float(predicted_price),
                "price_range": {
                    "min": float(confidence_interval[0]),
                    "max": float(confidence_interval[1])
                },
                "confidence": float(np.std(predictions)),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting price: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def generate_price_heatmap(
        self,
        location: Dict[str, float],
        radius_km: float = 1.0
    ) -> folium.Map:
        """
        Generate price heatmap for an area
        
        Args:
            location: Dictionary with lat/lng
            radius_km: Radius to analyze in kilometers
            
        Returns:
            Folium map with price heatmap
        """
        try:
            # Create base map
            m = folium.Map(
                location=[location['lat'], location['lng']],
                zoom_start=14
            )
            
            # Get hexagons in area
            center_hex = self.get_location_hex(
                location['lat'],
                location['lng']
            )
            hex_ring = h3.k_ring(center_hex, int(radius_km))
            
            # Generate sample prices for visualization
            # TODO: Replace with actual price predictions
            for hex_id in hex_ring:
                # Get hexagon boundaries
                boundaries = h3.h3_to_geo_boundary(hex_id)
                
                # Predict price for this hexagon
                predicted_price = self.predict_optimal_price({
                    'customer_count': 50,
                    'competition_density': 3,
                    'avg_income': 75000,
                    'peak_hour': 0,
                    'weekend': 0
                })
                
                # Add polygon to map
                folium.Polygon(
                    locations=boundaries,
                    popup=f"Optimal Price: ${predicted_price['optimal_price']:.2f}",
                    color='blue',
                    fill=True,
                    fill_color=self._get_price_color(predicted_price['optimal_price']),
                    fill_opacity=0.6
                ).add_to(m)
            
            return m
            
        except Exception as e:
            logger.error(f"Error generating price heatmap: {str(e)}")
            raise
    
    def _get_price_color(self, price: float) -> str:
        """Get color for price visualization"""
        if price < 10:
            return 'green'
        elif price < 20:
            return 'yellow'
        elif price < 30:
            return 'orange'
        else:
            return 'red'
    
    def get_dynamic_price_adjustment(
        self,
        base_price: float,
        current_demand: int,
        time_of_day: int,
        day_of_week: int,
        special_events: Optional[List[str]] = None
    ) -> Dict:
        """
        Get dynamic price adjustment based on current conditions
        
        Args:
            base_price: Base menu price
            current_demand: Current customer demand
            time_of_day: Hour of day (0-23)
            day_of_week: Day of week (0-6, 0=Monday)
            special_events: List of special events happening
            
        Returns:
            Dictionary containing price adjustments
        """
        try:
            # Base adjustment factors
            demand_factor = min(current_demand / 50.0, 2.0)  # Cap at 2x
            time_factor = 1.0 + (0.2 if 17 <= time_of_day <= 21 else 0)  # Peak hours
            weekend_factor = 1.1 if day_of_week >= 5 else 1.0  # Weekend premium
            
            # Event adjustment
            event_factor = 1.0
            if special_events:
                event_factor = 1.2  # 20% premium during special events
            
            # Calculate final price
            adjusted_price = base_price * demand_factor * time_factor * weekend_factor * event_factor
            
            # Round to nearest 0.49 or 0.99
            final_price = round(adjusted_price * 2) / 2 - 0.01
            
            return {
                "original_price": base_price,
                "adjusted_price": final_price,
                "adjustments": {
                    "demand_factor": demand_factor,
                    "time_factor": time_factor,
                    "weekend_factor": weekend_factor,
                    "event_factor": event_factor
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating dynamic price: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
