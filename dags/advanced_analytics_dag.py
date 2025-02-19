"""
Airflow DAG for advanced restaurant analytics
Handles POS data, emotions, customer tracking, and forecasting
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from restaurant_bi.analytics.advanced_analytics import AdvancedAnalytics
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
    # TODO: Get this from database
    return [
        "restaurant_001",
        "restaurant_002",
        "restaurant_003"
    ]

def process_pos_data(**context):
    """Process POS data and extract insights"""
    config = Config()
    analytics = AdvancedAnalytics(config)
    restaurants = get_monitored_restaurants()
    
    pos_insights = {}
    
    for restaurant_id in restaurants:
        try:
            insights = analytics.get_pos_insights(
                restaurant_id=restaurant_id,
                date_range=(
                    datetime.now() - timedelta(days=1),
                    datetime.now()
                )
            )
            pos_insights[restaurant_id] = insights
            logger.info(f"Processed POS data for {restaurant_id}")
            
        except Exception as e:
            logger.error(f"Error processing POS data for {restaurant_id}: {str(e)}")
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(
        key='pos_insights',
        value=json.dumps(pos_insights)
    )
    
    return len(pos_insights)

def analyze_customer_emotions(**context):
    """Analyze customer emotions from feedback"""
    config = Config()
    analytics = AdvancedAnalytics(config)
    
    # Get data from previous task
    ti = context['task_instance']
    pos_insights = json.loads(
        ti.xcom_pull(task_ids='process_pos_data', key='pos_insights')
    )
    
    emotion_analysis = {}
    
    for restaurant_id, insights in pos_insights.items():
        try:
            # Get customer feedback texts
            # TODO: Get actual feedback from database
            feedback_texts = [
                f"Sample feedback for {restaurant_id}",
                f"Another feedback for {restaurant_id}"
            ]
            
            results = analytics.analyze_customer_emotions(feedback_texts)
            emotion_analysis[restaurant_id] = results
            logger.info(f"Analyzed emotions for {restaurant_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing emotions for {restaurant_id}: {str(e)}")
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(
        key='emotion_analysis',
        value=json.dumps(emotion_analysis)
    )
    
    return len(emotion_analysis)

def track_customer_patterns(**context):
    """Track customer migration patterns"""
    config = Config()
    analytics = AdvancedAnalytics(config)
    restaurants = get_monitored_restaurants()
    
    migration_patterns = {}
    
    for restaurant_id in restaurants:
        try:
            patterns = analytics.track_customer_migration(
                restaurant_id=restaurant_id,
                timeframe_days=30
            )
            migration_patterns[restaurant_id] = patterns
            logger.info(f"Tracked customer patterns for {restaurant_id}")
            
        except Exception as e:
            logger.error(f"Error tracking patterns for {restaurant_id}: {str(e)}")
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(
        key='migration_patterns',
        value=json.dumps(migration_patterns)
    )
    
    return len(migration_patterns)

def generate_forecasts(**context):
    """Generate demand forecasts"""
    config = Config()
    analytics = AdvancedAnalytics(config)
    restaurants = get_monitored_restaurants()
    
    forecasts = {}
    
    for restaurant_id in restaurants:
        try:
            forecast = analytics.forecast_demand(
                restaurant_id=restaurant_id,
                forecast_days=30
            )
            forecasts[restaurant_id] = forecast
            logger.info(f"Generated forecast for {restaurant_id}")
            
        except Exception as e:
            logger.error(f"Error generating forecast for {restaurant_id}: {str(e)}")
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(
        key='forecasts',
        value=json.dumps(forecasts)
    )
    
    return len(forecasts)

def store_analytics_results(**context):
    """Store all analytics results"""
    ti = context['task_instance']
    
    # Get results from previous tasks
    pos_insights = json.loads(
        ti.xcom_pull(task_ids='process_pos_data', key='pos_insights')
    )
    emotion_analysis = json.loads(
        ti.xcom_pull(task_ids='analyze_customer_emotions', key='emotion_analysis')
    )
    migration_patterns = json.loads(
        ti.xcom_pull(task_ids='track_customer_patterns', key='migration_patterns')
    )
    forecasts = json.loads(
        ti.xcom_pull(task_ids='generate_forecasts', key='forecasts')
    )
    
    # TODO: Store results in appropriate databases
    logger.info("Stored analytics results")
    
    return {
        "pos_insights_count": len(pos_insights),
        "emotion_analysis_count": len(emotion_analysis),
        "migration_patterns_count": len(migration_patterns),
        "forecasts_count": len(forecasts)
    }

# Create DAG
dag = DAG(
    'advanced_restaurant_analytics',
    default_args=default_args,
    description='Advanced analytics for restaurant insights',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['restaurant_bi', 'analytics', 'advanced']
)

# Define tasks
process_pos = PythonOperator(
    task_id='process_pos_data',
    python_callable=process_pos_data,
    provide_context=True,
    dag=dag,
)

analyze_emotions = PythonOperator(
    task_id='analyze_customer_emotions',
    python_callable=analyze_customer_emotions,
    provide_context=True,
    dag=dag,
)

track_patterns = PythonOperator(
    task_id='track_customer_patterns',
    python_callable=track_customer_patterns,
    provide_context=True,
    dag=dag,
)

generate_demand_forecasts = PythonOperator(
    task_id='generate_forecasts',
    python_callable=generate_forecasts,
    provide_context=True,
    dag=dag,
)

store_results = PythonOperator(
    task_id='store_analytics_results',
    python_callable=store_analytics_results,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
process_pos >> analyze_emotions >> track_patterns >> generate_demand_forecasts >> store_results