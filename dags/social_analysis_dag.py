"""
Airflow DAG for scheduled social media analysis
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from restaurant_bi.social.social_listener import SocialListener
from restaurant_bi.llm.insights_generator import InsightsGenerator
from restaurant_bi.config import Config

import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'restaurant_bi',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def get_monitored_restaurants() -> List[str]:
    """Get list of restaurants to monitor"""
    # TODO: Get this from database or configuration
    return [
        "McDonald's",
        "Burger King",
        "KFC",
        "Pizza Hut",
        "Subway"
    ]

def collect_social_data(**context):
    """Collect social media data for monitored restaurants"""
    config = Config()
    social_listener = SocialListener(config)
    
    restaurants = get_monitored_restaurants()
    all_social_data = {}
    
    for restaurant in restaurants:
        try:
            social_data = social_listener.collect_social_data(
                restaurant_name=restaurant,
                days_back=1  # Get last 24 hours
            )
            
            all_social_data[restaurant] = social_data
            logger.info(f"Collected {len(social_data)} posts for {restaurant}")
            
        except Exception as e:
            logger.error(f"Error collecting data for {restaurant}: {str(e)}")
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(
        key='social_data',
        value=json.dumps(all_social_data)
    )
    
    return len(all_social_data)

def analyze_social_data(**context):
    """Analyze collected social media data"""
    config = Config()
    social_listener = SocialListener(config)
    insights_generator = InsightsGenerator(config)
    
    # Get data from previous task
    ti = context['task_instance']
    all_social_data = json.loads(
        ti.xcom_pull(task_ids='collect_social_data', key='social_data')
    )
    
    analysis_results = {}
    
    for restaurant, social_data in all_social_data.items():
        try:
            # Extract texts for analysis
            texts = [post['text'] for post in social_data]
            
            # Analyze sentiment
            sentiment_results = social_listener.analyze_sentiment(texts)
            
            # Detect trends
            trends = social_listener.detect_trends(texts)
            
            # Generate AI insights
            ai_insights = insights_generator.generate_restaurant_summary(
                restaurant,
                "\n".join(texts)
            )
            
            analysis_results[restaurant] = {
                'sentiment_analysis': sentiment_results,
                'trend_analysis': trends,
                'ai_insights': ai_insights
            }
            
            logger.info(f"Analyzed {len(texts)} posts for {restaurant}")
            
        except Exception as e:
            logger.error(f"Error analyzing data for {restaurant}: {str(e)}")
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(
        key='analysis_results',
        value=json.dumps(analysis_results)
    )
    
    return len(analysis_results)

def update_knowledge_graph(**context):
    """Update Neo4j knowledge graph with social data"""
    config = Config()
    social_listener = SocialListener(config)
    
    # Get data from previous tasks
    ti = context['task_instance']
    all_social_data = json.loads(
        ti.xcom_pull(task_ids='collect_social_data', key='social_data')
    )
    
    for restaurant, social_data in all_social_data.items():
        try:
            social_listener.build_social_graph(restaurant, social_data)
            logger.info(f"Updated social graph for {restaurant}")
            
        except Exception as e:
            logger.error(f"Error updating graph for {restaurant}: {str(e)}")
    
    return len(all_social_data)

def store_insights(**context):
    """Store analysis results in database"""
    # Get analysis results from previous task
    ti = context['task_instance']
    analysis_results = json.loads(
        ti.xcom_pull(task_ids='analyze_social_data', key='analysis_results')
    )
    
    # TODO: Store results in appropriate databases
    logger.info(f"Stored analysis results for {len(analysis_results)} restaurants")
    
    return len(analysis_results)

# Create DAG
dag = DAG(
    'social_media_analysis',
    default_args=default_args,
    description='Scheduled social media analysis for restaurants',
    schedule_interval=timedelta(hours=12),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['restaurant_bi', 'social_media', 'analytics']
)

# Define tasks
collect_data = PythonOperator(
    task_id='collect_social_data',
    python_callable=collect_social_data,
    provide_context=True,
    dag=dag,
)

analyze_data = PythonOperator(
    task_id='analyze_social_data',
    python_callable=analyze_social_data,
    provide_context=True,
    dag=dag,
)

update_graph = PythonOperator(
    task_id='update_knowledge_graph',
    python_callable=update_knowledge_graph,
    provide_context=True,
    dag=dag,
)

store_results = PythonOperator(
    task_id='store_insights',
    python_callable=store_insights,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
collect_data >> analyze_data >> [update_graph, store_results]