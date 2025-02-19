"""
Restaurant data ETL pipeline DAG
Handles data collection, processing, and storage across multiple databases
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from restaurant_bi.scrapers.restaurant_scraper import RestaurantScraper
from restaurant_bi.vectorstore.embedding_store import RestaurantEmbeddingStore
from restaurant_bi.market_analysis_agent import RestaurantMarketAnalysisAgent
from restaurant_bi.config import Config

import logging
import pandas as pd
from typing import Dict, List
import json

# Initialize logging
logger = logging.getLogger(__name__)

# Default DAG arguments
default_args = {
    'owner': 'restaurant_bi',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def scrape_restaurant_data(**context):
    """Task to scrape restaurant data from multiple sources"""
    config = Config()
    scraper = RestaurantScraper(config)
    agent = RestaurantMarketAnalysisAgent()
    
    # Get default location from config
    location = config.DEFAULT_LOCATION
    
    try:
        # Scrape data from multiple sources
        logger.info(f"Starting restaurant data collection for location: {location}")
        
        # Get Google Maps data
        gmaps_data = agent.search_restaurants(location)
        
        # Get Yelp data
        location_str = f"{location['lat']},{location['lng']}"
        yelp_data = scraper.scrape_yelp(location_str)
        cleaned_yelp = scraper.clean_data(yelp_data)
        
        # Combine data
        all_data = gmaps_data + cleaned_yelp
        
        # Push to XCom for next task
        context['task_instance'].xcom_push(key='restaurant_data', value=json.dumps(all_data))
        logger.info(f"Successfully collected data for {len(all_data)} restaurants")
        
    except Exception as e:
        logger.error(f"Error scraping restaurant data: {str(e)}")
        raise

def process_and_store_data(**context):
    """Task to process scraped data and store in databases"""
    config = Config()
    vector_store = RestaurantEmbeddingStore()
    
    try:
        # Get data from previous task
        data_str = context['task_instance'].xcom_pull(key='restaurant_data')
        restaurant_data = json.loads(data_str)
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(restaurant_data)
        
        # Basic data cleaning
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['price_level'] = pd.to_numeric(df['price_level'], errors='coerce')
        
        # Store in vector database
        vector_store.add_restaurants(restaurant_data)
        logger.info("Successfully stored data in vector database")
        
        # Return processed data count
        return len(df)
        
    except Exception as e:
        logger.error(f"Error processing and storing data: {str(e)}")
        raise

def update_embeddings(**context):
    """Task to update vector embeddings for semantic search"""
    vector_store = RestaurantEmbeddingStore()
    
    try:
        # Get data from previous task
        data_str = context['task_instance'].xcom_pull(key='restaurant_data')
        restaurant_data = json.loads(data_str)
        
        # Update embeddings in ChromaDB
        vector_store.add_restaurants(restaurant_data)
        logger.info(f"Successfully updated embeddings for {len(restaurant_data)} restaurants")
        
    except Exception as e:
        logger.error(f"Error updating embeddings: {str(e)}")
        raise

# Create DAG
dag = DAG(
    'restaurant_data_etl',
    default_args=default_args,
    description='ETL pipeline for restaurant market data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['restaurant_bi', 'etl']
)

# Define tasks
scrape_data = PythonOperator(
    task_id='scrape_restaurant_data',
    python_callable=scrape_restaurant_data,
    provide_context=True,
    dag=dag,
)

process_data = PythonOperator(
    task_id='process_and_store_data',
    python_callable=process_and_store_data,
    provide_context=True,
    dag=dag,
)

update_vectors = PythonOperator(
    task_id='update_embeddings',
    python_callable=update_embeddings,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
scrape_data >> process_data >> update_vectors