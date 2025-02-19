"""
LLM-powered restaurant insights generator
Supports both OpenAI GPT and open-source Llama models
"""
from typing import List, Dict, Optional, Union
import openai
from transformers import pipeline
import logging
from ..config import Config

logger = logging.getLogger(__name__)

class InsightsGenerator:
    """Generates AI-powered insights for restaurant data"""
    
    def __init__(self, config: Config):
        """
        Initialize the insights generator
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.model_type = config.LLM_MODEL_TYPE
        
        if self.model_type == 'openai':
            openai.api_key = config.OPENAI_API_KEY
            self.model = None
        else:
            # Initialize Llama model
            self.model = pipeline(
                "text-generation",
                model=config.LLAMA_MODEL_PATH,
                device=config.LLM_DEVICE
            )
    
    def generate_restaurant_summary(
        self,
        restaurant_name: str,
        reviews: Union[str, List[str]]
    ) -> str:
        """
        Generate a summary of restaurant reviews
        
        Args:
            restaurant_name: Name of the restaurant
            reviews: Review text or list of reviews
            
        Returns:
            Generated summary
        """
        if isinstance(reviews, list):
            reviews = "\n".join(reviews)
            
        prompt = f"""Analyze the following reviews for {restaurant_name} and provide a concise summary:

Reviews:
{reviews}

Please include:
1. Overall sentiment
2. Key strengths
3. Areas for improvement
4. Recommended target audience
"""
        
        try:
            if self.model_type == 'openai':
                return self._generate_gpt_summary(prompt)
            else:
                return self._generate_llama_summary(prompt)
        except Exception as e:
            logger.error(f"Error generating restaurant summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def generate_market_insights(
        self,
        market_data: Dict,
        location: str
    ) -> str:
        """
        Generate insights about market opportunities
        
        Args:
            market_data: Dictionary containing market analysis data
            location: Location string
            
        Returns:
            Generated market insights
        """
        prompt = f"""Analyze the following market data for {location} and provide strategic insights:

Market Data:
{market_data}

Please provide:
1. Market saturation analysis
2. Competitive advantages
3. Growth opportunities
4. Risk factors
"""
        
        try:
            if self.model_type == 'openai':
                return self._generate_gpt_summary(prompt)
            else:
                return self._generate_llama_summary(prompt)
        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")
            return f"Error generating insights: {str(e)}"
    
    def answer_query(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Answer a natural language query about restaurants or market data
        
        Args:
            query: User's question
            context: Optional context data
            
        Returns:
            AI-generated answer
        """
        prompt = f"""Question: {query}

{f'Context:\n{context}' if context else ''}

Please provide a detailed answer based on the available information.
"""
        
        try:
            if self.model_type == 'openai':
                return self._generate_gpt_summary(prompt)
            else:
                return self._generate_llama_summary(prompt)
        except Exception as e:
            logger.error(f"Error answering query: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    def _generate_gpt_summary(self, prompt: str) -> str:
        """Generate summary using OpenAI GPT"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI restaurant analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    
    def _generate_llama_summary(self, prompt: str) -> str:
        """Generate summary using Llama model"""
        response = self.model(
            prompt,
            max_length=500,
            temperature=0.7,
            top_p=0.9
        )
        return response[0]["generated_text"]