"""
Restaurant Market Analysis Agent
Handles data collection and analysis of restaurant market data
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from typing import TypedDict
from geopy.geocoders import Nominatim
from datetime import datetime
import pandas as pd
import numpy as np
import folium
from .config import Config
from .vectorstore.embedding_store import RestaurantEmbeddingStore

class RestaurantMarketAnalysisAgent:
    """Agent for analyzing restaurant market data and competition"""
    
    def __init__(self):
        """Initialize the agent with necessary API clients"""
        self.config = Config()
        self.config.validate()
        self.geolocator = Nominatim(user_agent="restaurant_bi")
        
        # Initialize vector store (using sentence-transformers under the hood)
        self.vector_store = RestaurantEmbeddingStore()
        
        # Initialize Google Maps client if API key is available
        if hasattr(self.config, 'GOOGLE_MAPS_API_KEY'):
            import googlemaps
            self.gmaps = googlemaps.Client(key=self.config.GOOGLE_MAPS_API_KEY)
        else:
            self.gmaps = None
            
        self.cached_data = {}

    def search_restaurants(
        self, 
        location: Dict[str, float],
        radius: int = None,
        keyword: str = 'restaurant'
    ) -> List[Dict]:
        """
        Search for restaurants in a given area
        
        Args:
            location: Dict containing 'lat' and 'lng' keys
            radius: Search radius in meters
            keyword: Search keyword (default: 'restaurant')
            
        Returns:
            List of restaurant data dictionaries
        """
        radius = radius or self.config.DEFAULT_SEARCH_RADIUS
        
        try:
            if not self.gmaps:
                return []

            places_result = self.gmaps.places_nearby(
                location=f"{location['lat']},{location['lng']}",
                radius=radius,
                keyword=keyword
            )
                
            restaurants = places_result.get('results', [])
            
            # Get detailed data for each restaurant
            detailed_results = []
            for restaurant in restaurants:
                try:
                    details = self.gmaps.place(restaurant['place_id'],
                        fields=['name', 'rating', 'user_ratings_total',
                               'price_level', 'formatted_address',
                               'opening_hours', 'reviews'])
                    detailed_results.append(details['result'])
                except Exception as e:
                    print(f"Error getting details for {restaurant['name']}: {str(e)}")
                    continue
            
            # Store detailed results in vector database
            self.vector_store.add_restaurants(detailed_results)
            
            return detailed_results
            
        except Exception as e:
            print(f"Error fetching restaurant data: {str(e)}")
            return []

    def _get_location_string(self, location: Dict[str, float]) -> str:
        """Convert coordinates to location string"""
        try:
            result = self.gmaps.reverse_geocode((location['lat'], location['lng']))
            if result:
                address = result[0]
                city = next((component['long_name'] 
                    for component in address['address_components']
                    if 'locality' in component['types']), '')
                state = next((component['short_name']
                    for component in address['address_components']
                    if 'administrative_area_level_1' in component['types']), '')
                return f"{city}, {state}"
        except Exception as e:
            print(f"Error getting location string: {str(e)}")
            return f"{location['lat']}, {location['lng']}"

    def analyze_competition(
        self,
        location: Dict[str, float],
        radius: int = None
    ) -> Dict:
        """
        Analyze competition in a given area
        
        Args:
            location: Dict containing 'lat' and 'lng' keys
            radius: Analysis radius in meters
            
        Returns:
            Dictionary containing competition analysis results
        """
        restaurants = self.search_restaurants(location, radius)
        
        if not restaurants:
            return {
                "status": "error",
                "message": "No restaurant data available for analysis"
            }
        
        # Get semantic insights about restaurant types
        cuisine_insights = self.vector_store.semantic_search(
            "Find restaurants by cuisine type",
            n_results=len(restaurants)
        )
        
        cuisine_categories = [r['categories'] for r in cuisine_insights if 'categories' in r]
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(restaurants)
        
        # Basic competition metrics
        analysis = {
            "total_restaurants": len(df),
            "avg_rating": df['rating'].mean() if 'rating' in df else None,
            "price_level_distribution": df['price_level'].value_counts().to_dict() if 'price_level' in df else {},
            "high_rated_competitors": len(df[df['rating'] >= 4.0]) if 'rating' in df else 0,
            "timestamp": datetime.now().isoformat(),
            "cuisine_analysis": {
                "total_cuisines": len(set([cat for cats in cuisine_categories for cat in cats])),
                "top_cuisines": pd.Series([cat for cats in cuisine_categories for cat in cats]).value_counts().head().to_dict()
            }
        }
        
        return analysis

    def generate_heatmap(
        self,
        location: Dict[str, float],
        radius: int = None
    ) -> folium.Map:
        """
        Generate a heatmap visualization of restaurant density
        
        Args:
            location: Dict containing 'lat' and 'lng' keys
            radius: Analysis radius in meters
            
        Returns:
            Folium map object with restaurant heatmap
        """
        restaurants = self.search_restaurants(location, radius)
        
        # Create base map
        m = folium.Map(
            location=[location['lat'], location['lng']],
            zoom_start=14
        )
        
        # Add restaurant markers
        for restaurant in restaurants:
            if 'geometry' in restaurant and 'location' in restaurant['geometry']:
                loc = restaurant['geometry']['location']
                folium.Marker(
                    [loc['lat'], loc['lng']],
                    popup=restaurant.get('name', 'Unknown'),
                    tooltip=f"{restaurant.get('name', 'Unknown')} - Rating: {restaurant.get('rating', 'N/A')}"
                ).add_to(m)
        
        return m

    def get_market_insights(
        self,
        location: Dict[str, float],
        radius: int = None,
        cuisine_type: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive market insights for a location
        
        Args:
            location: Dict containing 'lat' and 'lng' keys
            radius: Analysis radius in meters
            cuisine_type: Optional cuisine type to analyze
            
        Returns:
            Dictionary containing market insights
        """
        # Get base competition data
        competition_data = self.analyze_competition(location, radius)    

        # Get semantic insights if cuisine type specified
        cuisine_insights = None
        if cuisine_type:
            cuisine_insights = self.vector_store.semantic_search(
                f"Find {cuisine_type} restaurants",
                n_results=10,
                filter_criteria={
                    "min_rating": 3.5
                }
            )
        
        if competition_data.get("status") == "error":
            return competition_data
        
        # Calculate market saturation score (0-100)
        total_restaurants = competition_data['total_restaurants']
        avg_rating = competition_data['avg_rating']
        
        market_saturation = min(100, (total_restaurants / 20) * 100)
        
        insights = {
            "market_data": competition_data,
            "market_saturation_score": market_saturation,
            "market_quality_score": avg_rating * 20 if avg_rating else None,
            "cuisine_specific_insights": {
                "matching_restaurants": len(cuisine_insights) if cuisine_insights else None,
                "avg_rating": np.mean([r['rating'] for r in cuisine_insights if r['rating']]) if cuisine_insights else None
            } if cuisine_type else None,
            "similar_successful_venues": self._find_similar_successful_venues(competition_data),
            "recommendations": self._generate_recommendations(competition_data),
            "timestamp": datetime.now().isoformat()
        }
        
        return insights
        
    def _find_similar_successful_venues(self, competition_data: Dict) -> List[Dict]:
        """Find successful venues in the area"""
        try:
            return self.vector_store.semantic_search(
                "Find highly rated and successful restaurants",
                n_results=5,
                filter_criteria={"min_rating": 4.5}
            )
        except Exception:
            return []

    def _generate_recommendations(self, competition_data: Dict) -> List[str]:
        """
        Generate recommendations based on competition analysis
        
        Args:
            competition_data: Dictionary containing competition analysis results
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        total_restaurants = competition_data['total_restaurants']
        avg_rating = competition_data.get('avg_rating')
        high_rated = competition_data.get('high_rated_competitors', 0)
        
        # Market saturation recommendations
        if total_restaurants < 10:
            recommendations.append("Low market saturation - good opportunity for new entrants")
        elif total_restaurants > 30:
            recommendations.append("High market saturation - consider differentiation strategy")
        
        # Quality level recommendations
        if avg_rating and avg_rating < 3.5:
            recommendations.append("Low average quality in area - opportunity for high-quality establishment")
        elif avg_rating and avg_rating > 4.2:
            recommendations.append("High quality expectations in area - ensure premium service")
        
        # Competition recommendations
        if high_rated > total_restaurants * 0.5:
            recommendations.append("High concentration of quality competitors - needs strong unique selling proposition")
        
        return recommendations
