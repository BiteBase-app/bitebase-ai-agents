"""
Restaurant Embedding Store using FAISS
"""
from typing import List, Dict, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

class RestaurantEmbeddingStore:
    def __init__(self, index_path: str = "./data/embeddings"):
        """Initialize FAISS index and sentence transformer"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_path = index_path
        self.data_path = os.path.join(index_path, "metadata.pkl")
        
        # Create directory if it doesn't exist
        os.makedirs(index_path, exist_ok=True)
        
        # Initialize or load FAISS index
        self.dimension = 384  # Dimension of sentence-transformers embeddings
        if os.path.exists(os.path.join(index_path, "index.faiss")):
            self.index = faiss.read_index(os.path.join(index_path, "index.faiss"))
            with open(self.data_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def add_restaurants(self, restaurants: List[Dict]) -> None:
        """Add restaurant data to the vector store"""
        if not restaurants:
            return
            
        # Create document texts
        documents = []
        for restaurant in restaurants:
            doc_text = f"{restaurant.get('name', '')} {restaurant.get('formatted_address', '')} "
            doc_text += f"Rating: {restaurant.get('rating', 'N/A')} "
            if 'price_level' in restaurant:
                doc_text += f"Price Level: {'$' * restaurant['price_level']} "
            documents.append(doc_text)
        
        # Generate embeddings
        embeddings = self.model.encode(documents)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        self.metadata.extend(restaurants)
        
        # Save index and metadata
        faiss.write_index(self.index, os.path.join(self.index_path, "index.faiss"))
        with open(self.data_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def semantic_search(
        self,
        query: str,
        n_results: int = 10,
        filter_criteria: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for restaurants using semantic similarity"""
        # Generate query embedding
        query_embedding = self.model.encode([query])[0].astype('float32').reshape(1, -1)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, n_results)
        
        # Get metadata for results
        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                result = self.metadata[idx]
                # Apply filters if specified
                if filter_criteria:
                    if 'min_rating' in filter_criteria:
                        if result.get('rating', 0) < filter_criteria['min_rating']:
                            continue
                results.append(result)
                
        return results