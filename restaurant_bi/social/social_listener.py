"""
Social media listening and analysis module
Handles multi-source data collection and sentiment analysis
"""
from typing import Dict, List, Optional
import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime, timedelta
from transformers import pipeline
import logging
from bertopic import BERTopic
from neo4j import GraphDatabase
from ..config import Config

logger = logging.getLogger(__name__)

class SocialListener:
    """Handles social media data collection and analysis"""
    
    def __init__(self, config: Config):
        """
        Initialize the social listener
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Initialize sentiment analysis model
        self.sentiment_model = pipeline(
            "text-classification",
            model="cardiffnlp/twitter-roberta-base-sentiment"
        )
        
        # Initialize topic modeling
        self.topic_model = BERTopic(language="english")
        
        # Initialize Neo4j connection
        self.neo4j_driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        
    def collect_social_data(
        self,
        restaurant_name: str,
        days_back: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """
        Collect social media posts about a restaurant
        
        Args:
            restaurant_name: Name of the restaurant
            days_back: Number of days to look back
            limit: Maximum number of posts to collect
            
        Returns:
            List of social media posts
        """
        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        query = f'"{restaurant_name}" since:{since_date}'
        
        posts = []
        try:
            # Collect tweets
            for tweet in sntwitter.TwitterSearchScraper(query).get_items():
                if len(posts) >= limit:
                    break
                    
                posts.append({
                    'date': tweet.date,
                    'text': tweet.rawContent,
                    'username': tweet.user.username,
                    'platform': 'twitter',
                    'likes': tweet.likeCount,
                    'retweets': tweet.retweetCount
                })
                
            logger.info(f"Collected {len(posts)} social posts for {restaurant_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting social data: {str(e)}")
            return []
    
    def analyze_sentiment(self, texts: List[str]) -> List[Dict]:
        """
        Perform deep sentiment analysis on texts
        
        Args:
            texts: List of text content to analyze
            
        Returns:
            List of sentiment analysis results
        """
        try:
            results = []
            for text in texts:
                sentiment = self.sentiment_model(text)[0]
                results.append({
                    'text': text,
                    'sentiment': sentiment['label'],
                    'confidence': sentiment['score']
                })
            return results
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return []
    
    def detect_trends(self, texts: List[str]) -> Dict:
        """
        Detect trending topics in social media content
        
        Args:
            texts: List of social media posts
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            # Fit topic model
            topics, _ = self.topic_model.fit_transform(texts)
            
            # Get topic information
            topic_info = self.topic_model.get_topic_info()
            
            # Extract top topics
            top_topics = []
            for _, row in topic_info.iterrows():
                if row['Topic'] != -1:  # Skip outlier topic
                    top_topics.append({
                        'topic_id': row['Topic'],
                        'words': self.topic_model.get_topic(row['Topic']),
                        'count': row['Count']
                    })
            
            return {
                'total_topics': len(top_topics),
                'topics': top_topics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting trends: {str(e)}")
            return {
                'total_topics': 0,
                'topics': [],
                'error': str(e)
            }
    
    def build_social_graph(
        self,
        restaurant_name: str,
        social_data: List[Dict]
    ) -> None:
        """
        Build knowledge graph from social media data
        
        Args:
            restaurant_name: Name of the restaurant
            social_data: List of social media posts
        """
        try:
            with self.neo4j_driver.session() as session:
                # Create restaurant node
                session.run("""
                MERGE (r:Restaurant {name: $name})
                """, name=restaurant_name)
                
                # Create user and post nodes
                for post in social_data:
                    session.run("""
                    MERGE (u:User {username: $username})
                    CREATE (p:Post {
                        text: $text,
                        date: $date,
                        platform: $platform,
                        engagement: $engagement
                    })
                    MERGE (r:Restaurant {name: $restaurant})
                    CREATE (u)-[:POSTED]->(p)
                    CREATE (p)-[:ABOUT]->(r)
                    """,
                    username=post['username'],
                    text=post['text'],
                    date=post['date'].isoformat(),
                    platform=post['platform'],
                    engagement=post.get('likes', 0) + post.get('retweets', 0),
                    restaurant=restaurant_name
                    )
                
            logger.info(f"Built social graph for {restaurant_name}")
            
        except Exception as e:
            logger.error(f"Error building social graph: {str(e)}")
    
    def get_social_insights(
        self,
        restaurant_name: str,
        days_back: int = 30
    ) -> Dict:
        """
        Get comprehensive social media insights
        
        Args:
            restaurant_name: Name of the restaurant
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing social insights
        """
        try:
            # Collect social data
            social_data = self.collect_social_data(
                restaurant_name,
                days_back=days_back
            )
            
            if not social_data:
                return {
                    "status": "error",
                    "message": "No social data available"
                }
            
            # Extract texts
            texts = [post['text'] for post in social_data]
            
            # Analyze sentiment
            sentiment_results = self.analyze_sentiment(texts)
            
            # Detect trends
            trends = self.detect_trends(texts)
            
            # Build social graph
            self.build_social_graph(restaurant_name, social_data)
            
            # Calculate metrics
            total_engagement = sum(
                post.get('likes', 0) + post.get('retweets', 0)
                for post in social_data
            )
            
            sentiment_counts = {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
            for result in sentiment_results:
                sentiment_counts[result['sentiment'].lower()] += 1
            
            return {
                "total_posts": len(social_data),
                "total_engagement": total_engagement,
                "sentiment_distribution": sentiment_counts,
                "trending_topics": trends['topics'][:5],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting social insights: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }