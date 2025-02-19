"""
Advanced geospatial analysis and location optimization module
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import geopandas as gpd
import h3
import osmnx as ox
from sklearn.cluster import DBSCAN
from prophet import Prophet
import folium
from datetime import datetime, timedelta
import numpy as np
from geopy.distance import geodesic
import logging
from ..config import Config

logger = logging.getLogger(__name__)

class LocationOptimizer:
    """Handles advanced geospatial analysis and location optimization"""
    
    def __init__(self, config: Config):
        """
        Initialize the location optimizer
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.h3_resolution = 7  # Neighborhood level
        
    def analyze_restaurant_clusters(
        self,
        locations: List[Dict],
        eps_km: float = 0.5,
        min_samples: int = 5
    ) -> Dict:
        """
        Analyze restaurant clusters using DBSCAN
        
        Args:
            locations: List of restaurant locations
            eps_km: Maximum distance between points in km
            min_samples: Minimum points to form a cluster
            
        Returns:
            Dictionary containing cluster analysis
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(locations)
            
            # Apply DBSCAN clustering
            coords = df[['latitude', 'longitude']].values
            kms_per_radian = 6371.0
            epsilon = eps_km / kms_per_radian
            
            clustering = DBSCAN(
                eps=epsilon,
                min_samples=min_samples,
                metric='haversine'
            ).fit(np.radians(coords))
            
            # Add cluster labels
            df['cluster'] = clustering.labels_
            
            # Analyze clusters
            cluster_stats = []
            for cluster_id in set(clustering.labels_):
                if cluster_id == -1:
                    continue  # Skip noise points
                    
                cluster_points = df[df['cluster'] == cluster_id]
                center = cluster_points[['latitude', 'longitude']].mean()
                
                cluster_stats.append({
                    'cluster_id': int(cluster_id),
                    'center_lat': float(center['latitude']),
                    'center_lng': float(center['longitude']),
                    'restaurant_count': len(cluster_points),
                    'avg_rating': float(cluster_points.get('rating', 0).mean()),
                    'points': cluster_points[['latitude', 'longitude']].values.tolist()
                })
            
            return {
                'total_clusters': len(cluster_stats),
                'noise_points': int((df['cluster'] == -1).sum()),
                'clusters': cluster_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing clusters: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def generate_price_heatmap(
        self,
        restaurants: List[Dict],
        center: Dict[str, float],
        zoom: int = 12
    ) -> folium.Map:
        """
        Generate price heatmap using H3 hexagons
        
        Args:
            restaurants: List of restaurant data
            center: Center point for map
            zoom: Initial zoom level
            
        Returns:
            Folium map with price heatmap
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(restaurants)
            
            # Add H3 indices
            df['h3_index'] = df.apply(
                lambda row: h3.geo_to_h3(
                    row['latitude'],
                    row['longitude'],
                    self.h3_resolution
                ),
                axis=1
            )
            
            # Calculate average prices per hexagon
            price_zones = df.groupby('h3_index').agg({
                'price_level': 'mean',
                'latitude': 'mean',
                'longitude': 'mean',
                'restaurant_name': 'count'
            }).reset_index()
            
            # Create map
            m = folium.Map(
                location=[center['lat'], center['lng']],
                zoom_start=zoom
            )
            
            # Add hexagons
            for _, row in price_zones.iterrows():
                hex_boundary = h3.h3_to_geo_boundary(row['h3_index'])
                
                # Color based on price level
                color = self._get_price_color(row['price_level'])
                
                folium.Polygon(
                    locations=hex_boundary,
                    popup=f"Average Price: ${row['price_level']:.2f}<br>"
                          f"Restaurants: {row['restaurant_name']}",
                    color=color,
                    fill=True,
                    fill_opacity=0.6
                ).add_to(m)
            
            return m
            
        except Exception as e:
            logger.error(f"Error generating price heatmap: {str(e)}")
            raise
    
    def analyze_population_impact(
        self,
        location: Dict[str, float],
        radius_km: float = 1.0
    ) -> Dict:
        """
        Analyze population impact on restaurant success
        
        Args:
            location: Center point location
            radius_km: Analysis radius in kilometers
            
        Returns:
            Dictionary containing population analysis
        """
        try:
            # Get area boundary
            north = location['lat'] + (radius_km / 111.32)
            south = location['lat'] - (radius_km / 111.32)
            east = location['lng'] + (radius_km / (111.32 * np.cos(np.radians(location['lat']))))
            west = location['lng'] - (radius_km / (111.32 * np.cos(np.radians(location['lat']))))
            
            # Get OSM data
            area_data = ox.geometries_from_bbox(
                north, south, east, west,
                tags={'building': True, 'population': True}
            )
            
            # Calculate statistics
            total_buildings = len(area_data)
            population_data = area_data[area_data['population'].notna()]
            estimated_population = population_data['population'].sum()
            
            return {
                'estimated_population': int(estimated_population),
                'building_count': total_buildings,
                'area_km2': radius_km * radius_km * np.pi,
                'population_density': int(estimated_population / (radius_km * radius_km * np.pi)),
                'bounds': {
                    'north': north,
                    'south': south,
                    'east': east,
                    'west': west
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing population impact: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def predict_growth_zones(
        self,
        historical_data: pd.DataFrame,
        prediction_days: int = 365
    ) -> Dict:
        """
        Predict future restaurant growth zones
        
        Args:
            historical_data: DataFrame with historical restaurant openings
            prediction_days: Number of days to predict
            
        Returns:
            Dictionary containing growth predictions
        """
        try:
            # Prepare data for Prophet
            df = historical_data.copy()
            df['ds'] = pd.to_datetime(df['date'])
            df['y'] = df['new_restaurants']
            
            # Train model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False
            )
            model.fit(df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=prediction_days)
            forecast = model.predict(future)
            
            # Extract key metrics
            predictions = []
            for _, row in forecast.tail(prediction_days).iterrows():
                predictions.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_openings': float(row['yhat']),
                    'lower_bound': float(row['yhat_lower']),
                    'upper_bound': float(row['yhat_upper'])
                })
            
            return {
                'predictions': predictions,
                'trend_direction': 'up' if forecast['trend'].iloc[-1] > forecast['trend'].iloc[0] else 'down',
                'peak_season': self._get_peak_season(forecast),
                'forecast_period': {
                    'start': forecast['ds'].min().strftime('%Y-%m-%d'),
                    'end': forecast['ds'].max().strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting growth zones: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _get_price_color(self, price_level: float) -> str:
        """Get color for price visualization"""
        if price_level < 10:
            return 'green'
        elif price_level < 25:
            return 'yellow'
        elif price_level < 50:
            return 'orange'
        else:
            return 'red'
    
    def _get_peak_season(self, forecast: pd.DataFrame) -> Dict:
        """Analyze seasonal patterns in forecast"""
        # Group by month and get average predicted values
        monthly_avg = forecast.groupby(forecast['ds'].dt.month)['yhat'].mean()
        peak_month = monthly_avg.idxmax()
        
        return {
            'peak_month': int(peak_month),
            'peak_value': float(monthly_avg[peak_month]),
            'monthly_pattern': monthly_avg.to_dict()
        }