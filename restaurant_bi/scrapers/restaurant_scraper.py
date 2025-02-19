"""
Restaurant data scraping module integrating multiple data sources
"""
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess
import requests
from datetime import datetime

class YelpSpider(scrapy.Spider):
    """Spider for scraping restaurant data from Yelp"""
    name = 'yelp_spider'
    
    def __init__(self, location: str, *args, **kwargs):
        super(YelpSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            f'https://www.yelp.com/search?find_desc=Restaurants&find_loc={location}'
        ]
        self.results = []

    def parse(self, response):
        """Parse Yelp search results page"""
        # Extract restaurant listings
        restaurants = response.css('div.businessName__09f24__EYQC3')
        
        for restaurant in restaurants:
            yield {
                'name': restaurant.css('a::text').get(),
                'url': restaurant.css('a::attr(href)').get(),
                'rating': restaurant.css('div[aria-label*="rating"]::attr(aria-label)').get(),
                'reviews': restaurant.css('span.reviewCount__09f24__EUXPZ::text').get(),
                'price_range': restaurant.css('span.priceRange__09f24__mmOuH::text').get(),
                'categories': restaurant.css('span.css-1ip2op1::text').getall(),
                'scraped_at': datetime.now().isoformat()
            }

class RestaurantScraper:
    """Unified scraper for collecting restaurant data from multiple sources"""
    
    def __init__(self, config=None):
        """Initialize the scraper with configuration"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        
    def scrape_yelp(self, location: str) -> List[Dict]:
        """
        Scrape restaurant data from Yelp
        
        Args:
            location: Location string (e.g., 'New York, NY')
            
        Returns:
            List of restaurant dictionaries
        """
        process = CrawlerProcess(settings={
            'USER_AGENT': 'Mozilla/5.0 (compatible; RestaurantBI/1.0)',
            'LOG_LEVEL': 'ERROR'
        })
        
        spider = YelpSpider(location=location)
        process.crawl(spider)
        process.start()
        
        return spider.results
    
    def scrape_social_data(self, restaurant_name: str, location: str) -> Dict:
        """
        Scrape social media mentions and reviews
        
        Args:
            restaurant_name: Name of the restaurant
            location: Location string
            
        Returns:
            Dictionary containing social media data
        """
        # TODO: Implement social media scraping using snscrape
        # This is a placeholder for future implementation
        return {
            "mentions": [],
            "sentiment": None,
            "scraped_at": datetime.now().isoformat()
        }
    
    def clean_data(self, data: List[Dict]) -> List[Dict]:
        """
        Clean and normalize scraped data
        
        Args:
            data: List of raw restaurant dictionaries
            
        Returns:
            List of cleaned restaurant dictionaries
        """
        cleaned = []
        for item in data:
            if not item.get('name'):
                continue
                
            # Normalize ratings to 5-star scale
            rating = item.get('rating', '')
            if isinstance(rating, str) and 'rating' in rating.lower():
                try:
                    rating = float(rating.split()[0])
                except (ValueError, IndexError):
                    rating = None
                    
            # Normalize price ranges
            price_range = item.get('price_range', '')
            if price_range:
                price_range = len(price_range.replace('$', ''))
                
            cleaned.append({
                'name': item['name'],
                'url': item.get('url', ''),
                'rating': rating,
                'review_count': item.get('reviews', '0').replace(' reviews', ''),
                'price_level': price_range,
                'categories': item.get('categories', []),
                'source': 'yelp',
                'scraped_at': item.get('scraped_at', datetime.now().isoformat())
            })
            
        return cleaned