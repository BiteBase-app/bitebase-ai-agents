"""
Vector storage and semantic search implementation using ChromaDB and Sentence-BERT
"""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime

class RestaurantEmbeddingStore:
    """Manages restaurant data embeddings and semantic search"""
    
    def __init__(self, persist_directory: str = "./data/chroma"):
        """
        Initialize the embedding store
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Initialize Sentence-BERT model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create or get collections
        self.restaurant_collection = self.client.get_or_create_collection(
            name="restaurant_data",
            metadata={"description": "Restaurant information and reviews"}
        )
        
    def add_restaurants(self, restaurants: List[Dict]) -> None:
        """
        Add restaurant data to the vector store
        
        Args:
            restaurants: List of restaurant dictionaries
        """
        documents = []
        metadatas = []
        ids = []
        
        for restaurant in restaurants:
            # Create a combined text representation for embedding
            text_content = f"{restaurant['name']} - {' '.join(restaurant.get('categories', []))}"
            if 'reviews' in restaurant:
                text_content += f" Reviews: {restaurant['reviews']}"
                
            # Store complete restaurant data in metadata
            metadata = {
                'name': restaurant['name'],
                'rating': restaurant.get('rating'),
                'price_level': restaurant.get('price_level'),
                'categories': json.dumps(restaurant.get('categories', [])),
                'source': restaurant.get('source', 'unknown'),
                'added_at': datetime.now().isoformat()
            }
            
            documents.append(text_content)
            metadatas.append(metadata)
            ids.append(f"restaurant_{hash(restaurant['name'] + text_content)}")
            
        # Generate embeddings and add to ChromaDB
        self.restaurant_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
    def semantic_search(
        self, 
        query: str, 
        n_results: int = 10,
        filter_criteria: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform semantic search on restaurant data
        
        Args:
            query: Search query string
            n_results: Number of results to return
            filter_criteria: Optional filtering criteria
            
        Returns:
            List of matching restaurant dictionaries
        """
        # Convert natural language query to embedding
        query_embedding = self.model.encode(query)
        
        # Prepare filter if provided
        where_clause = None
        if filter_criteria:
            where_clause = {}
            if 'min_rating' in filter_criteria:
                where_clause["rating"] = {"$gte": filter_criteria['min_rating']}
            if 'price_level' in filter_criteria:
                where_clause["price_level"] = filter_criteria['price_level']
        
        # Perform search
        results = self.restaurant_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        for idx, metadata in enumerate(results['metadatas'][0]):
            result = {
                'name': metadata['name'],
                'rating': metadata.get('rating'),
                'price_level': metadata.get('price_level'),
                'categories': json.loads(metadata.get('categories', '[]')),
                'source': metadata.get('source'),
                'relevance_score': results['distances'][0][idx],
                'matched_text': results['documents'][0][idx]
            }
            formatted_results.append(result)
            
        return formatted_results
    
    def get_similar_restaurants(
        self, 
        restaurant_name: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Find similar restaurants based on name and description
        
        Args:
            restaurant_name: Name of the restaurant to find similar ones for
            n_results: Number of similar restaurants to return
            
        Returns:
            List of similar restaurant dictionaries
        """
        # First, try to find the exact restaurant
        results = self.restaurant_collection.query(
            query_texts=[restaurant_name],
            n_results=1
        )
        
        if not results['documents'][0]:
            return []
            
        # Use the full text content to find similar restaurants
        return self.semantic_search(
            results['documents'][0][0],
            n_results=n_results + 1  # Add 1 to account for the query restaurant
        )[1:]  # Exclude the first result (the query restaurant)