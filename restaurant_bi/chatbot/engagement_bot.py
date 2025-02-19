"""
AI-powered chatbot for real-time customer engagement and offers
"""
from typing import Dict, List, Optional, Union
from datetime import datetime
import openai
from twilio.rest import Client
from geopy.distance import geodesic
import json
import logging
from ..config import Config
from ..pricing.geospatial_pricing import GeospatialPricing

logger = logging.getLogger(__name__)

class EngagementBot:
    """Handles real-time customer engagement and offers"""
    
    def __init__(self, config: Config):
        """
        Initialize the engagement bot
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Initialize OpenAI
        openai.api_key = config.OPENAI_API_KEY
        
        # Initialize Twilio for WhatsApp
        if config.TWILIO_ENABLED:
            self.twilio_client = Client(
                config.TWILIO_ACCOUNT_SID,
                config.TWILIO_AUTH_TOKEN
            )
        else:
            self.twilio_client = None
        
        # Initialize pricing module
        self.pricing = GeospatialPricing(config)
        
        # Load offer templates
        self.offer_templates = {
            "nearby": "🎉 Special offer just for you! {restaurant_name} is {distance}m away. "
                     "Get {discount}% off on {item} in the next {time_limit} minutes!",
            "loyalty": "👋 Welcome back to {restaurant_name}! As a valued customer, "
                      "enjoy {discount}% off your favorite {item} today!",
            "quiet_hours": "Beat the crowd! Visit {restaurant_name} in the next hour "
                          "and get {discount}% off on all menu items!",
            "weather": "☔ Perfect weather for {item}! Stop by {restaurant_name} and "
                      "get a special {discount}% discount today!"
        }
    
    def check_customer_proximity(
        self,
        customer_location: Dict[str, float],
        restaurant_location: Dict[str, float]
    ) -> float:
        """
        Check distance between customer and restaurant
        
        Args:
            customer_location: Dict with customer lat/lng
            restaurant_location: Dict with restaurant lat/lng
            
        Returns:
            Distance in meters
        """
        distance = geodesic(
            (customer_location['lat'], customer_location['lng']),
            (restaurant_location['lat'], restaurant_location['lng'])
        ).meters
        
        return distance
    
    def generate_personalized_offer(
        self,
        customer_id: str,
        restaurant_data: Dict,
        distance: float,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate personalized offer using AI
        
        Args:
            customer_id: Customer identifier
            restaurant_data: Restaurant information
            distance: Distance to restaurant in meters
            context: Additional context (weather, time, etc.)
            
        Returns:
            Dictionary containing offer details
        """
        try:
            # Generate offer prompt
            prompt = f"""Create a personalized restaurant offer with the following details:
Restaurant: {restaurant_data['name']}
Distance: {distance:.0f} meters
Cuisine: {restaurant_data.get('cuisine', 'various')}
Context: {json.dumps(context) if context else 'None'}

Generate a compelling offer that encourages immediate visit."""

            # Get AI response
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a restaurant marketing expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            offer_text = response["choices"][0]["message"]["content"]
            
            # Calculate dynamic discount
            base_discount = 10
            if distance < 200:  # Within 200m
                base_discount += 5
            if context and context.get('quiet_hours'):
                base_discount += 10
                
            return {
                "offer_text": offer_text,
                "discount_percent": min(base_discount, 30),  # Cap at 30%
                "valid_minutes": 30,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating offer: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def send_whatsapp_message(
        self,
        to_number: str,
        message: str
    ) -> Dict:
        """
        Send message via WhatsApp
        
        Args:
            to_number: Recipient's phone number
            message: Message text
            
        Returns:
            Dictionary containing send status
        """
        if not self.twilio_client:
            return {
                "status": "error",
                "message": "WhatsApp integration not configured"
            }
            
        try:
            # Send via Twilio
            message = self.twilio_client.messages.create(
                from_=f"whatsapp:{self.config.TWILIO_WHATSAPP_NUMBER}",
                body=message,
                to=f"whatsapp:{to_number}"
            )
            
            return {
                "status": "sent",
                "message_id": message.sid,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def handle_customer_message(
        self,
        message: str,
        customer_data: Dict,
        location: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Handle incoming customer message
        
        Args:
            message: Customer's message text
            customer_data: Customer information
            location: Optional customer location
            
        Returns:
            Dictionary containing response
        """
        try:
            # Generate response prompt
            prompt = f"""Customer message: {message}
Customer data: {json.dumps(customer_data)}
Location data: {json.dumps(location) if location else 'None'}

Generate a helpful response that includes restaurant recommendations if appropriate."""

            # Get AI response
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful restaurant assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            reply_text = response["choices"][0]["message"]["content"]
            
            # Generate offer if customer is near a restaurant
            offer = None
            if location:
                nearby_restaurants = self._find_nearby_restaurants(location)
                if nearby_restaurants:
                    restaurant = nearby_restaurants[0]
                    distance = self.check_customer_proximity(
                        location,
                        restaurant['location']
                    )
                    
                    if distance < 500:  # Within 500m
                        offer = self.generate_personalized_offer(
                            customer_data['id'],
                            restaurant,
                            distance
                        )
            
            return {
                "response_text": reply_text,
                "offer": offer,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _find_nearby_restaurants(
        self,
        location: Dict[str, float]
    ) -> List[Dict]:
        """Find restaurants near a location"""
        # TODO: Implement actual restaurant search
        # For now, return sample data
        return [{
            "name": "Sample Restaurant",
            "cuisine": "Italian",
            "location": {
                "lat": location['lat'] + 0.001,
                "lng": location['lng'] + 0.001
            }
        }]
    
    def process_customer_activity(
        self,
        customer_id: str,
        activity_type: str,
        activity_data: Dict
    ) -> None:
        """
        Process customer activity for engagement opportunities
        
        Args:
            customer_id: Customer identifier
            activity_type: Type of activity
            activity_data: Activity details
        """
        try:
            # Handle different activity types
            if activity_type == 'location_update':
                location = activity_data.get('location')
                if location:
                    nearby_restaurants = self._find_nearby_restaurants(location)
                    for restaurant in nearby_restaurants:
                        distance = self.check_customer_proximity(
                            location,
                            restaurant['location']
                        )
                        
                        if distance < 500:  # Within 500m
                            offer = self.generate_personalized_offer(
                                customer_id,
                                restaurant,
                                distance,
                                activity_data.get('context')
                            )
                            
                            if offer and activity_data.get('phone_number'):
                                message = self.offer_templates['nearby'].format(
                                    restaurant_name=restaurant['name'],
                                    distance=int(distance),
                                    discount=offer['discount_percent'],
                                    item=restaurant.get('specialty', 'your meal'),
                                    time_limit=offer['valid_minutes']
                                )
                                
                                self.send_whatsapp_message(
                                    activity_data['phone_number'],
                                    message
                                )
            
            elif activity_type == 'app_open':
                # Handle app opens
                pass
                
            elif activity_type == 'order_complete':
                # Handle order completions
                pass
                
        except Exception as e:
            logger.error(f"Error processing customer activity: {str(e)}")